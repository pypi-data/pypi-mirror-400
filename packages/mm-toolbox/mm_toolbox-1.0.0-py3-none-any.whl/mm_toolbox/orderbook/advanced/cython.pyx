# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

from libc.stdint cimport uint64_t as u64
from libc.stdlib cimport malloc

from .core cimport CoreAdvancedOrderbook
from .enum.enums cimport CyOrderbookSortedness
from .level.level cimport (
    OrderbookLevel,
    OrderbookLevels,
    create_orderbook_level as _create_orderbook_level,
    create_orderbook_level_with_ticks_and_lots as _create_orderbook_level_with_ticks_and_lots,
    free_orderbook_levels as _free_orderbook_levels,
)


cdef class AdvancedOrderbook:
    """Cython-facing API for the advanced orderbook with efficient in-place updates.
    
    This class provides a Cython API wrapper around CoreAdvancedOrderbook, designed
    for use in Cython code that needs high-performance orderbook operations. Methods
    that modify the orderbook (consume_*) are marked noexcept for use in nogil contexts.
    Methods that query the orderbook may raise RuntimeError if the orderbook is empty.
    
    The orderbook maintains separate bid and ask sides, each with a fixed maximum
    number of levels. Levels are stored internally using integer arithmetic (ticks
    and lots) for precision and performance.
    """
    def __cinit__(
        self,
        double tick_size,
        double lot_size,
        u64 num_levels,
        CyOrderbookSortedness delta_sortedness=CyOrderbookSortedness.UNKNOWN,
        CyOrderbookSortedness snapshot_sortedness=CyOrderbookSortedness.UNKNOWN,
        bint has_ticks_and_lots=False,
    ):
        """Initialize a new AdvancedOrderbook instance.
        
        Args:
            tick_size: Minimum price increment (must be > 0)
            lot_size: Minimum size increment (must be > 0)
            num_levels: Maximum number of levels per side (must be > 0)
            delta_sortedness: Expected sort order for delta updates (default: UNKNOWN)
            snapshot_sortedness: Expected sort order for snapshot updates (default: UNKNOWN)
            has_ticks_and_lots: If True, all incoming levels will have ticks/lots pre-computed (default: False)
        """
        self._core = CoreAdvancedOrderbook(
            tick_size,
            lot_size,
            num_levels,
            delta_sortedness,
            snapshot_sortedness,
            has_ticks_and_lots,
        )

    cdef void clear(self):
        """Clear all levels from both sides of the orderbook."""
        self._core.clear()

    cdef void consume_snapshot(self, OrderbookLevels asks, OrderbookLevels bids):
        """Replace the entire orderbook state with new snapshot data.
        
        Args:
            asks: OrderbookLevels struct containing ask levels
            bids: OrderbookLevels struct containing bid levels
        """
        self._core.consume_snapshot(asks, bids)

    cdef void consume_deltas(self, OrderbookLevels asks, OrderbookLevels bids):
        """Apply incremental updates to the orderbook.
        
        Args:
            asks: OrderbookLevels struct containing ask level updates
            bids: OrderbookLevels struct containing bid level updates
        """
        self._core.consume_deltas(asks, bids)

    cdef void consume_bbo(self, OrderbookLevel ask, OrderbookLevel bid):
        """Update only the best bid and offer (top of book).
        
        Args:
            ask: OrderbookLevel struct for the best ask
            bid: OrderbookLevel struct for the best bid
        """
        self._core.consume_bbo(ask, bid)

    cdef double get_mid_price(self):
        """Calculate the mid price (average of best bid and ask).
        
        Returns:
            Mid price, or infinity if orderbook is empty
        
        Raises:
            RuntimeError: If orderbook is empty
        """
        return self._core.get_mid_price()

    cdef double get_bbo_spread(self):
        """Calculate the spread between best bid and ask.
        
        Returns:
            Spread in price units, or infinity if orderbook is empty
        
        Raises:
            RuntimeError: If orderbook is empty
        """
        return self._core.get_bbo_spread()

    cdef double get_wmid_price(self):
        """Calculate the weighted mid price (volume-weighted average of best bid and ask).
        
        Returns:
            Weighted mid price, or infinity if orderbook is empty
        
        Raises:
            RuntimeError: If orderbook is empty
        """
        return self._core.get_wmid_price()

    cdef double get_volume_weighted_mid_price(self, double size, bint is_base_currency):
        """Calculate volume-weighted mid price for a given trade size.
        
        Args:
            size: Trade size to calculate weighted price for
            is_base_currency: If True, size is in base currency; if False, in quote currency
        
        Returns:
            Volume-weighted mid price, or infinity if orderbook is empty or size cannot be filled
        
        Raises:
            RuntimeError: If orderbook is empty
        """
        return self._core.get_volume_weighted_mid_price(size, is_base_currency)

    cdef double get_price_impact(self, double size, bint is_buy, bint is_base_currency):
        """Calculate price impact of executing a trade of given size.
        
        Args:
            size: Trade size
            is_buy: If True, calculate impact for buying; if False, for selling
            is_base_currency: If True, size is in base currency; if False, in quote currency
        
        Returns:
            Price impact (absolute difference from mid price), or infinity if size cannot be filled
        
        Raises:
            RuntimeError: If orderbook is empty
        """
        return self._core.get_price_impact(size, is_buy, is_base_currency)

    cdef bint is_bbo_crossed(self, double other_bid_price, double other_ask_price):
        """Check if this orderbook's BBO crosses with another orderbook's BBO.
        
        Args:
            other_bid_price: Best bid price from another orderbook
            other_ask_price: Best ask price from another orderbook
        
        Returns:
            True if the BBOs cross (this bid >= other ask or this ask <= other bid)
        
        Raises:
            RuntimeError: If orderbook is empty
        """
        return self._core.is_bbo_crossed(other_bid_price, other_ask_price)

    cdef bint does_bbo_price_change(self, double bid_price, double ask_price):
        """Check if the given prices differ from current BBO.
        
        Args:
            bid_price: Bid price to compare
            ask_price: Ask price to compare
        
        Returns:
            True if either price differs from current BBO
        
        Raises:
            RuntimeError: If orderbook is empty
        """
        return self._core.does_bbo_price_change(bid_price, ask_price)

    @staticmethod
    cdef OrderbookLevel create_orderbook_level(double price, double size, u64 norders=1) noexcept:
        """Create an OrderbookLevel struct without pre-computing ticks/lots.
        
        This is a convenience function for users of AdvancedOrderbook.
        The ticks and lots will be computed by the orderbook when consumed.
        """
        return _create_orderbook_level(price, size, norders)

    @staticmethod
    cdef OrderbookLevel create_orderbook_level_with_ticks_and_lots(
        double price,
        double size,
        double tick_size,
        double lot_size,
        u64 norders=1,
    ) noexcept:
        """Create an OrderbookLevel struct with pre-computed ticks and lots.
        
        This is a convenience function for users of AdvancedOrderbook.
        Pre-computing ticks and lots can improve performance when consuming many levels.
        """
        return _create_orderbook_level_with_ticks_and_lots(price, size, tick_size, lot_size, norders)

    @staticmethod
    cdef OrderbookLevels create_orderbook_levels_from_array(
        OrderbookLevel* levels_ptr,
        u64 num_levels,
    ) noexcept:
        """Create an OrderbookLevels struct from an array pointer and count.
        
        This wraps an existing array of OrderbookLevel structs.
        The caller is responsible for managing the memory lifetime of levels_ptr.
        """
        cdef OrderbookLevels levels_struct = OrderbookLevels()
        levels_struct.num_levels = num_levels
        levels_struct.levels = levels_ptr
        return levels_struct

    @staticmethod
    cdef OrderbookLevels create_orderbook_levels_allocated(
        u64 num_levels,
    ) noexcept:
        """Allocate and return an OrderbookLevels struct with uninitialized levels.
        
        The caller must initialize the levels array and is responsible for freeing
        the memory using free_orderbook_levels().
        """
        cdef OrderbookLevels levels_struct = OrderbookLevels()
        cdef u64 size = sizeof(OrderbookLevel) * num_levels
        cdef OrderbookLevel* levels_ptr = <OrderbookLevel*> malloc(size)
        if levels_ptr == NULL:
            levels_struct.num_levels = 0
            levels_struct.levels = NULL
            return levels_struct
        levels_struct.num_levels = num_levels
        levels_struct.levels = levels_ptr
        return levels_struct

    @staticmethod
    cdef void free_orderbook_levels(OrderbookLevels* levels) noexcept nogil:
        """Free the memory allocated for OrderbookLevels.levels if not NULL."""
        _free_orderbook_levels(levels)
