from libc.stdint cimport uint64_t as u64

from .core cimport CoreAdvancedOrderbook
from .level.level cimport OrderbookLevel, OrderbookLevels
from .enum.enums cimport CyOrderbookSortedness


cdef class AdvancedOrderbook:
    cdef CoreAdvancedOrderbook _core

    cdef void clear(self)
    cdef void consume_snapshot(self, OrderbookLevels asks, OrderbookLevels bids)
    cdef void consume_deltas(self, OrderbookLevels asks, OrderbookLevels bids)
    cdef void consume_bbo(self, OrderbookLevel ask, OrderbookLevel bid)

    cdef double get_mid_price(self)
    cdef double get_bbo_spread(self)
    cdef double get_wmid_price(self)
    cdef double get_volume_weighted_mid_price(self, double size, bint is_base_currency)
    cdef double get_price_impact(self, double size, bint is_buy, bint is_base_currency)
    cdef bint is_bbo_crossed(self, double other_bid_price, double other_ask_price)
    cdef bint does_bbo_price_change(self, double bid_price, double ask_price)

    @staticmethod
    cdef OrderbookLevel create_orderbook_level(double price, double size, u64 norders=*) noexcept
    @staticmethod
    cdef OrderbookLevel create_orderbook_level_with_ticks_and_lots(double price, double size, double tick_size, double lot_size, u64 norders=*) noexcept
    @staticmethod
    cdef OrderbookLevels create_orderbook_levels_from_array(OrderbookLevel* levels_ptr, u64 num_levels) noexcept
    @staticmethod
    cdef OrderbookLevels create_orderbook_levels_allocated(u64 num_levels) noexcept
    @staticmethod
    cdef void free_orderbook_levels(OrderbookLevels* levels) noexcept nogil


