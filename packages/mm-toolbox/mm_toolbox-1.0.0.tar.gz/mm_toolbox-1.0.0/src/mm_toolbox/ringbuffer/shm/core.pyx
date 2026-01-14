# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""SPSC shared-memory bytes ring buffer."""

import time
from libc.stdint cimport uint64_t as u64
from libc.string cimport memcpy
from libc.stddef cimport size_t
from libc.errno cimport errno

cdef extern from "sys/mman.h":
    void* mmap(void* addr, size_t length, int prot, int flags, int fd, long offset)
    int munmap(void* addr, size_t length)
    int PROT_READ
    int PROT_WRITE
    int MAP_SHARED

cdef extern from "fcntl.h":
    int open(const char* path, int oflag, ...)
    int O_RDWR
    int O_CREAT

cdef extern from "unistd.h":
    int ftruncate(int fd, long length)
    int close(int fd)

from .atomics cimport atomic_add, atomic_load_acquire, atomic_store_release, atomic_sub
from .header cimport ShmHeader
from .memory cimport (
    align_up,
    copy_from_ring,
    copy_into_ring,
    pow2_at_least,
    read_u64_le,
    write_u64_le,
)


cdef u64 _MAGIC = 0x53484252  # 'SHBR' (Shared Bytes Ring)
cdef size_t _HEADER_ALIGN = 64
cdef size_t _HEADER_SIZE = align_up(sizeof(ShmHeader), _HEADER_ALIGN)


cdef class _SharedBytesRing:
    """Common mapping and lifecycle for shared ring buffers."""

    def __cinit__(self) -> None:
        self._hdr = NULL
        self._data = NULL
        self._map_len = 0
        self._fd = -1
        self._owner = False
        self._unlink_on_close = False
        self._capacity = 0
        self._mask = 0
        self._cached_read = 0
        self._cached_write = 0
        self._spin_wait = 1024
        self._path_py = None
        self._path = NULL

    cdef void _map_create(self, bytes path_b, u64 capacity_bytes, bint unlink_on_close, int spin_wait):
        """Create and initialize a shared ring."""
        cdef:
            int fd
            size_t cap = <size_t>pow2_at_least(capacity_bytes if capacity_bytes > 0 else 1)
            size_t total_len = _HEADER_SIZE + cap
            void* base
        fd = open(path_b, O_CREAT | O_RDWR, 0o600)
        if fd < 0:
            raise OSError(errno, "open failed for shared ring")
        if ftruncate(fd, <long>total_len) != 0:
            close(fd)
            raise OSError(errno, "ftruncate failed for shared ring")
        base = mmap(NULL, total_len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)
        if <long>base == -1:
            close(fd)
            try:
                import os
                os.unlink(path_b)
            except Exception:
                pass
            finally:
                raise OSError(errno, "mmap failed for shared ring")

        self._fd = fd
        self._map_len = total_len
        self._hdr = <ShmHeader*>base
        self._data = <unsigned char*>base + _HEADER_SIZE
        self._owner = True
        self._unlink_on_close = unlink_on_close
        self._spin_wait = spin_wait if spin_wait > 0 else 1024
        self._capacity = <u64>cap
        self._mask = <u64>(cap - 1)
        self._cached_read = 0
        self._cached_write = 0

        self._hdr.magic = _MAGIC
        self._hdr.capacity = <u64>cap
        self._hdr.mask = <u64>(cap - 1)
        self._hdr.write_pos = 0
        self._hdr.read_pos = 0
        self._hdr.msg_count = 0
        self._hdr.latest_insert_time_ns = 0
        self._hdr.latest_consume_time_ns = 0

    cdef void _map_attach(self, bytes path_b, int spin_wait):
        """Attach to an existing shared ring."""
        cdef:
            int fd
            void* base
            size_t total_len
            u64 capacity
        fd = open(path_b, O_RDWR, 0o600)
        if fd < 0:
            raise OSError(errno, "open failed for shared ring")
        base = mmap(NULL, _HEADER_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)
        if <long>base == -1:
            close(fd)
            raise OSError(errno, "mmap header failed for shared ring")
        self._hdr = <ShmHeader*>base
        if self._hdr.magic != _MAGIC:
            munmap(base, _HEADER_SIZE)
            close(fd)
            raise RuntimeError("Shared ring header mismatch")
        capacity = self._hdr.capacity
        munmap(base, _HEADER_SIZE)

        total_len = _HEADER_SIZE + <size_t>capacity
        base = mmap(NULL, total_len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)
        if <long>base == -1:
            close(fd)
            raise OSError(errno, "mmap failed for shared ring")

        self._fd = fd
        self._map_len = total_len
        self._hdr = <ShmHeader*>base
        self._data = <unsigned char*>base + _HEADER_SIZE
        self._owner = False
        self._unlink_on_close = False
        self._spin_wait = spin_wait if spin_wait > 0 else 1024
        self._capacity = capacity
        self._mask = self._hdr.mask
        self._cached_read = self._hdr.read_pos
        self._cached_write = self._hdr.write_pos

    cdef inline void _close_map(self):
        """Unmap and close backing file."""
        if self._hdr != NULL:
            munmap(<void*>self._hdr, self._map_len)
            self._hdr = NULL
            self._data = NULL
            self._map_len = 0
        if self._fd >= 0:
            close(self._fd)
            self._fd = -1

    def __dealloc__(self):
        try:
            self.close()
        except Exception:
            pass

    cpdef void close(self):
        self._close_map()
        if self._owner and self._unlink_on_close and self._path_py is not None:
            try:
                import os
                os.unlink(self._path_py)
            except Exception:
                pass
        self._owner = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def __len__(self) -> int:
        cdef u64 count
        with nogil:
            count = atomic_load_acquire(&self._hdr.msg_count)
        return <Py_ssize_t>count

    @property
    def latest_insert_time_ns(self) -> int:
        cdef u64 ts
        with nogil:
            ts = atomic_load_acquire(&self._hdr.latest_insert_time_ns)
        return <int>ts

    @property
    def latest_consume_time_ns(self) -> int:
        cdef u64 ts
        with nogil:
            ts = atomic_load_acquire(&self._hdr.latest_consume_time_ns)
        return <int>ts


cdef class SharedBytesRingBufferProducer(_SharedBytesRing):
    """Shared-memory SPSC producer for bytes payloads."""

    def __cinit__(
        self,
        path: str,
        int capacity_bytes,
        *,
        bint create=True,
        bint unlink_on_close=False,
        int spin_wait=1024,
    ) -> None:
        self._path_py = path
        path_b = (<str>path).encode()
        self._path = path_b
        if create:
            self._map_create(path_b, <u64>capacity_bytes, unlink_on_close, spin_wait)
        else:
            self._map_attach(path_b, spin_wait)

    cdef inline bint _reserve(self, size_t need, u64* dropped_msgs):
        """Ensure space; drop oldest messages if required."""
        cdef u64 capacity = self._capacity
        cdef u64 mask = self._mask
        cdef u64 write_pos = self._cached_write
        cdef u64 read_pos
        cdef u64 free_bytes
        cdef u64 msg_len
        cdef u64 dropped_pos = 0
        dropped_msgs[0] = 0
        with nogil:
            read_pos = atomic_load_acquire(&self._hdr.read_pos)
        self._cached_read = read_pos
        free_bytes = capacity - (write_pos - read_pos)
        if free_bytes >= <u64>need:
            return True
        dropped_pos = read_pos
        while True:
            msg_len = read_u64_le(self._data, dropped_pos & mask, mask)
            if msg_len > capacity or (dropped_pos + 8 + msg_len) < dropped_pos:
                return False
            dropped_pos += 8 + msg_len
            dropped_msgs[0] += 1
            free_bytes = capacity - (write_pos - dropped_pos)
            if free_bytes >= <u64>need:
                with nogil:
                    atomic_store_release(&self._hdr.read_pos, dropped_pos)
                    if dropped_msgs[0]:
                        atomic_sub(&self._hdr.msg_count, dropped_msgs[0])
                self._cached_read = dropped_pos
                return True

    cdef inline bint _can_reserve_once(self, size_t need):
        """Fast check that space is available without dropping."""
        cdef u64 capacity = self._capacity
        cdef u64 write_pos = self._cached_write
        cdef u64 read_pos
        with nogil:
            read_pos = atomic_load_acquire(&self._hdr.read_pos)
        self._cached_read = read_pos
        return (capacity - (write_pos - read_pos)) >= <u64>need

    cpdef bint insert(self, bytes item):
        """Insert a single item."""
        cdef:
            Py_ssize_t payload_len = len(item)
            size_t total_len = <size_t>(8 + payload_len)
            u64 capacity = self._capacity
            u64 mask = self._mask
            u64 write_pos = self._cached_write
            u64 dropped = 0
            u64 now_ns
        if payload_len < 0:
            return False
        if total_len > capacity:
            return False
        if not self._reserve(total_len, &dropped):
            return False
        write_u64_le(self._data, write_pos & mask, mask, <u64>payload_len)
        copy_into_ring(self._data, write_pos + 8, mask, <const unsigned char*>item, <size_t>payload_len, capacity)
        write_pos += total_len
        now_ns = <u64>time.monotonic_ns()
        with nogil:
            atomic_store_release(&self._hdr.write_pos, write_pos)
            atomic_add(&self._hdr.msg_count, 1)
            atomic_store_release(&self._hdr.latest_insert_time_ns, now_ns)
        self._cached_write = write_pos
        return True

    cpdef bint insert_char(self, const char* data, size_t n):
        """Insert a raw buffer of length n from a char* pointer."""
        cdef size_t total = 8 + n
        cdef u64 capacity = self._capacity
        cdef u64 mask = self._mask
        cdef u64 write_pos = self._cached_write
        cdef u64 dropped = 0
        cdef u64 now_ns
        if n == 0:
            return True
        if total > capacity:
            return False
        if not self._reserve(total, &dropped):
            return False
        write_u64_le(self._data, write_pos & mask, mask, <u64>n)
        copy_into_ring(self._data, write_pos + 8, mask, <const unsigned char*>data, <size_t>n, capacity)
        write_pos += total
        now_ns = <u64>time.monotonic_ns()
        with nogil:
            atomic_store_release(&self._hdr.write_pos, write_pos)
            atomic_add(&self._hdr.msg_count, 1)
            atomic_store_release(&self._hdr.latest_insert_time_ns, now_ns)
        self._cached_write = write_pos
        return True

    cpdef bint insert_batch(self, list[bytes] items):
        """Insert multiple items with one commit."""
        cdef:
            Py_ssize_t i, n = len(items)
            u64 capacity = self._capacity
            u64 mask = self._mask
            u64 write_pos = self._cached_write
            size_t total = 0
            bytes it
            u64 msg_len
            u64 dropped = 0
            u64 now_ns
        if n == 0:
            return True
        for i in range(n):
            it = items[i]
            msg_len = <u64>len(it)
            if <u64>(8) + msg_len > capacity:
                return False
            total += <size_t>(8 + msg_len)
        if <u64>total > capacity:
            return False
        if not self._reserve(total, &dropped):
            return False
        for i in range(n):
            it = items[i]
            msg_len = <u64>len(it)
            write_u64_le(self._data, write_pos & mask, mask, msg_len)
            copy_into_ring(self._data, write_pos + 8, mask, <const unsigned char*>it, <size_t>msg_len, capacity)
            write_pos += 8 + msg_len
        now_ns = <u64>time.monotonic_ns()
        with nogil:
            atomic_store_release(&self._hdr.write_pos, write_pos)
            atomic_add(&self._hdr.msg_count, <u64>n)
            atomic_store_release(&self._hdr.latest_insert_time_ns, now_ns)
        self._cached_write = write_pos
        return True

    cpdef bint insert_packed(self, list[bytes] items):
        """Insert items packed into one message."""
        cdef Py_ssize_t i, n = len(items)
        cdef Py_ssize_t total = 0
        cdef bytes it
        if n == 0:
            return True
        for i in range(n):
            it = items[i]
            total += 4 + len(it)
        if total <= 0:
            return True
        if <u64>(8 + total) > self._capacity:
            return False
        cdef bytearray buf = bytearray(<int>total)
        cdef unsigned char* p = <unsigned char*>buf
        cdef size_t off = 0
        cdef Py_ssize_t L
        for i in range(n):
            it = items[i]
            L = len(it)
            p[off + 0] = <unsigned char>(L & 0xFF)
            p[off + 1] = <unsigned char>((L >> 8) & 0xFF)
            p[off + 2] = <unsigned char>((L >> 16) & 0xFF)
            p[off + 3] = <unsigned char>((L >> 24) & 0xFF)
            off += 4
            memcpy(p + off, <const unsigned char*>it, <size_t>L)
            off += <size_t>L
        return self.insert(bytes(buf))


cdef class SharedBytesRingBufferConsumer(_SharedBytesRing):
    """Shared-memory SPSC consumer for bytes payloads."""

    def __cinit__(self, path: str, *, int spin_wait=1024) -> None:
        self._path_py = path
        path_b = (<str>path).encode()
        self._path = path_b
        self._map_attach(path_b, spin_wait)

    cdef inline bint _peek_available(self, u64* out_len, u64* out_read_pos) nogil:
        """Check availability of a complete message without advancing."""
        cdef u64 read_pos = atomic_load_acquire(&self._hdr.read_pos)
        cdef u64 write_pos = atomic_load_acquire(&self._hdr.write_pos)
        cdef u64 avail = write_pos - read_pos
        if avail < 8:
            return False
        cdef u64 msg_len = read_u64_le(self._data, read_pos & self._mask, self._mask)
        if avail < 8 + msg_len:
            return False
        out_len[0] = <u64>msg_len
        out_read_pos[0] = read_pos
        return True

    cpdef bytes consume(self):
        """Consume a single item, blocking until available."""
        cdef:
            u64 msg_len = 0
            u64 read_pos = 0
            u64 read_pos_check = 0
            u64 mask = self._mask
            u64 cap = self._capacity
            int spin_count = 0
            bint available = False
            u64 now_ns
        while True:
            with nogil:
                available = self._peek_available(&msg_len, &read_pos)
            if not available:
                spin_count += 1
                if spin_count < self._spin_wait:
                    continue
                time.sleep(0.0001)
                spin_count = 0
                continue
            with nogil:
                read_pos_check = atomic_load_acquire(&self._hdr.read_pos)
            if read_pos_check != read_pos:
                continue
            break
        cdef bytes out = bytes(<Py_ssize_t>msg_len)
        copy_from_ring(<unsigned char*>out, self._data, read_pos + 8, mask, <size_t>msg_len, cap)
        read_pos += 8 + msg_len
        now_ns = <u64>time.monotonic_ns()
        with nogil:
            atomic_store_release(&self._hdr.read_pos, read_pos)
            atomic_sub(&self._hdr.msg_count, 1)
            atomic_store_release(&self._hdr.latest_consume_time_ns, now_ns)
        self._cached_read = read_pos
        return out
    cpdef object peekleft(self):
        """Peek at the next item without consuming; returns None if empty."""
        cdef u64 msg_len = 0
        cdef u64 read_pos = 0
        cdef u64 read_pos_check = 0
        cdef u64 mask = self._mask
        cdef u64 cap = self._capacity
        with nogil:
            if not self._peek_available(&msg_len, &read_pos):
                return None
            read_pos_check = atomic_load_acquire(&self._hdr.read_pos)
        if read_pos_check != read_pos:
            return None
        cdef bytes out = bytes(<Py_ssize_t>msg_len)
        copy_from_ring(<unsigned char*>out, self._data, read_pos + 8, mask, <size_t>msg_len, cap)
        return out

    cpdef object peekright(self):
        """Peek at the most recently inserted item; returns None if empty."""
        cdef u64 count
        cdef u64 w
        cdef u64 last_len
        cdef u64 total
        cdef u64 start
        cdef u64 mask = self._mask
        cdef u64 cap = self._capacity
        with nogil:
            count = atomic_load_acquire(&self._hdr.msg_count)
        if count == 0:
            return None
        with nogil:
            w = atomic_load_acquire(&self._hdr.write_pos)
        if w < 8:
            return None
        last_len = read_u64_le(self._data, (w - 8) & mask, mask)
        if last_len > cap:
            return None
        total = 8 + last_len
        start = w - total
        cdef bytes out = bytes(<Py_ssize_t>last_len)
        copy_from_ring(<unsigned char*>out, self._data, start + 8, mask, <size_t>last_len, cap)
        return out

    cpdef list consume_all(self):
        """Drain all items currently available without blocking."""
        cdef list res = []
        cdef u64 msg_len = 0
        cdef u64 read_pos = 0
        cdef u64 read_pos_check = 0
        cdef u64 mask = self._mask
        cdef u64 cap = self._capacity
        cdef u64 now_ns
        cdef bytes out
        while True:
            with nogil:
                if not self._peek_available(&msg_len, &read_pos):
                    break
                read_pos_check = atomic_load_acquire(&self._hdr.read_pos)
            if read_pos_check != read_pos:
                continue
            out = bytes(<Py_ssize_t>msg_len)
            copy_from_ring(<unsigned char*>out, self._data, read_pos + 8, mask, <size_t>msg_len, cap)
            res.append(out)
            read_pos += 8 + msg_len
            now_ns = <u64>time.monotonic_ns()
            with nogil:
                atomic_store_release(&self._hdr.read_pos, read_pos)
                atomic_sub(&self._hdr.msg_count, 1)
                atomic_store_release(&self._hdr.latest_consume_time_ns, now_ns)
            self._cached_read = read_pos
        return res

    cpdef list consume_packed(self):
        """Consume and unpack a packed message."""
        cdef bytes buf = self.consume()
        cdef memoryview mv = memoryview(buf)
        cdef Py_ssize_t n = mv.shape[0]
        cdef Py_ssize_t off = 0
        cdef list items = []
        cdef u64 L
        while off + 4 <= n:
            L = (
                (<u64>mv[off])
                | (<u64>mv[off + 1] << 8)
                | (<u64>mv[off + 2] << 16)
                | (<u64>mv[off + 3] << 24)
            )
            off += 4
            if off + L > n:
                raise ValueError("Corrupted packed message")
            items.append(bytes(mv[off : off + L]))
            off += L
        return items
