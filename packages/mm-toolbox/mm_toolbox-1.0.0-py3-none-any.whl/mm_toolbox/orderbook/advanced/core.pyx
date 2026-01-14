# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

from libc.math cimport floor
from libc.float cimport DBL_MAX as INFINITY_DOUBLE
from libc.stdint cimport uint64_t as u64

from .level.level cimport OrderbookLevel, OrderbookLevels
from .level.helpers cimport (
    convert_price_from_tick,
    convert_price_to_tick,
    convert_size_from_lot,
    convert_size_to_lot,
    inplace_sort_levels_by_ticks,
    reverse_levels,
)
from .ladder.ladder cimport OrderbookLadder, OrderbookLadderData
from .enum.enums cimport CyOrderbookSortedness


cdef class CoreAdvancedOrderbook:
    """Core orderbook engine managing bids and asks with efficient in-place updates."""
    def __cinit__(
        self,
        double tick_size,
        double lot_size,
        u64 num_levels,
        CyOrderbookSortedness delta_sortedness,
        CyOrderbookSortedness snapshot_sortedness,
        bint has_ticks_and_lots=False,
    ):
        if tick_size <= 0.0:
            raise ValueError(f"Invalid tick_size; expected >0 but got {tick_size}")
        if lot_size <= 0.0:
            raise ValueError(f"Invalid lot_size; expected >0 but got {lot_size}")
        if num_levels <= 0:
            raise ValueError(f"Invalid num_levels; expected >0 but got {num_levels}")
        # if 1 <= num_levels < 5:
        #     raise ValueError(
        #         f"Invalid num_levels; expected >=5 but got...{num_levels}? What's the point?!"
        #     )
        self._tick_size = tick_size
        self._lot_size = lot_size
        self._max_levels = num_levels
        self._delta_sortedness = delta_sortedness
        self._snapshot_sortedness = snapshot_sortedness
        self._has_ticks_and_lots = has_ticks_and_lots
        self._bids = OrderbookLadder(max_levels=self._max_levels, is_price_ascending=False)
        self._asks = OrderbookLadder(max_levels=self._max_levels, is_price_ascending=True)
        self._bids_data = self._bids.get_data()
        self._asks_data = self._asks.get_data()

    cdef inline void _ensure_not_empty(self):
        """Ensures the orderbook has been populated."""
        if self._bids.is_empty() or self._asks.is_empty():
            raise RuntimeError("Empty view on one/both sides of orderbook; cannot compute without data")

    cdef inline bint _check_if_empty(self):
        """Checks if the orderbook is not empty."""
        return not self._bids.is_empty() and not self._asks.is_empty()

    cdef void _normalize_incoming_levels(
        self,
        OrderbookLevels asks,
        OrderbookLevels bids,
        bint is_snapshot,
    ):
        """Normalize incoming levels to the orderbook's internal representation."""
        cdef:
            CyOrderbookSortedness sortedness_code = (
                self._snapshot_sortedness 
                if is_snapshot else 
                self._delta_sortedness
            )
            OrderbookLevel* ask_level
            OrderbookLevel* bid_level
            u64 i

        if not self._has_ticks_and_lots:
            for i in range(asks.num_levels):
                ask_level = &asks.levels[i]
                ask_level.ticks = convert_price_to_tick(ask_level.price, self._tick_size)
                ask_level.lots = convert_size_to_lot(ask_level.size, self._lot_size)
            for i in range(bids.num_levels):
                bid_level = &bids.levels[i]
                bid_level.ticks = convert_price_to_tick(bid_level.price, self._tick_size)
                bid_level.lots = convert_size_to_lot(bid_level.size, self._lot_size)

        # Likely most common user choice due to sortedness being unspecified
        if sortedness_code == CyOrderbookSortedness.UNKNOWN:
            inplace_sort_levels_by_ticks(levels=asks, ascending=True)
            inplace_sort_levels_by_ticks(levels=bids, ascending=False)
        
        # Used by most exchanges for delta updates, preferred path internally
        elif sortedness_code == CyOrderbookSortedness.BIDS_DESCENDING_ASKS_ASCENDING:
            pass

        # Used by most exchanges for snapshot updates
        elif sortedness_code == CyOrderbookSortedness.ASCENDING:
            reverse_levels(levels=bids)
        
        # Unlikely, should never really happen.
        elif sortedness_code == CyOrderbookSortedness.DESCENDING:
            reverse_levels(levels=asks)

        # Unlikely, should never really happen.
        elif sortedness_code == CyOrderbookSortedness.BIDS_ASCENDING_ASKS_DESCENDING:
            reverse_levels(levels=asks)
            reverse_levels(levels=bids)

    cdef void _process_matching_ask_ticks(self, OrderbookLevel* ask):
        """Rolls the ask level array left (removing the top-of-book ask) if lots=0, otherwise updates size/lots/norders."""
        cdef:
            OrderbookLadderData* asks = self._asks_data
            OrderbookLevel* top_of_book_ask = &asks.levels[0]
        if ask.lots == 0:
            self._asks.roll_left(0)
            self._asks.decrement_count()
        else:
            top_of_book_ask.size = ask.size
            top_of_book_ask.lots = ask.lots
            top_of_book_ask.norders = ask.norders

    cdef void _process_matching_bid_ticks(self, OrderbookLevel* bid):
        """Rolls the bid level array left (removing the top-of-book bid) if lots=0, otherwise updates size/lots/norders."""
        cdef:
            OrderbookLadderData* bids = self._bids_data
            OrderbookLevel* top_of_book_bid = &bids.levels[0]
        if bid.lots == 0:
            self._bids.roll_left(0)
            self._bids.decrement_count()
        else:
            top_of_book_bid.size = bid.size
            top_of_book_bid.lots = bid.lots
            top_of_book_bid.norders = bid.norders

    cdef void _process_lower_ask_ticks(self, OrderbookLevel* ask):
        """Rolls the ask level array right (adding a new ask level) then corrects for any overlapping bids"""
        cdef:
            OrderbookLadderData* bids = self._bids_data
            OrderbookLadderData* asks = self._asks_data
            OrderbookLevel* top_of_book_bid
            OrderbookLevel* top_of_book_ask

        self._asks.roll_right(0)
        self._asks.increment_count()

        top_of_book_ask = &asks.levels[0]
        top_of_book_ask.price = ask.price
        top_of_book_ask.ticks = ask.ticks
        top_of_book_ask.size = ask.size
        top_of_book_ask.lots = ask.lots
        top_of_book_ask.norders = ask.norders

        # Remove overlapping bids (fix: check num_levels before dereferencing)
        while bids.num_levels > 0:
            top_of_book_bid = &bids.levels[0]
            if ask.ticks > top_of_book_bid.ticks:
                break
            self._bids.roll_left(0)
            self._bids.decrement_count()

    cdef void _process_higher_bid_ticks(self, OrderbookLevel* bid):
        """Rolls the bid level array right (adding a new bid level) then corrects for any overlapping asks"""
        cdef:
            OrderbookLadderData* bids = self._bids_data
            OrderbookLadderData* asks = self._asks_data
            OrderbookLevel* top_of_book_bid
            OrderbookLevel* top_of_book_ask

        self._bids.roll_right(0)
        self._bids.increment_count()

        top_of_book_bid = &bids.levels[0]
        top_of_book_bid.price = bid.price
        top_of_book_bid.ticks = bid.ticks
        top_of_book_bid.size = bid.size
        top_of_book_bid.lots = bid.lots
        top_of_book_bid.norders = bid.norders

        # Remove overlapping asks (fix: check num_levels before dereferencing)
        while asks.num_levels > 0:
            top_of_book_ask = &asks.levels[0]
            if bid.ticks < top_of_book_ask.ticks:
                break
            self._asks.roll_left(0)
            self._asks.decrement_count()

    cdef void _process_middle_ask_ticks(self, OrderbookLevel* ask):
        """Process an ask level that falls in the middle of the existing ask levels."""
        cdef:
            OrderbookLadderData* bids = self._bids_data
            OrderbookLadderData* asks = self._asks_data
            OrderbookLevel* ask_insertion_level
            u64 i
            u64 current_ask_ticks
            u64 last_idx = asks.num_levels
            u64 insert_idx = last_idx
            bint is_matching = False

        for i in range(1, last_idx):
            current_ask_ticks = asks.levels[i].ticks
            if current_ask_ticks >= ask.ticks:
                insert_idx = i
                if current_ask_ticks == ask.ticks:
                    is_matching = True
                break

        if is_matching:
            if ask.lots == 0:
                self._asks.roll_left(insert_idx)
                self._asks.decrement_count()
            else:
                ask_insertion_level = &asks.levels[insert_idx]
                ask_insertion_level.size = ask.size
                ask_insertion_level.lots = ask.lots
                ask_insertion_level.norders = ask.norders
        else:
            if ask.lots == 0:
                return
            self._asks.roll_right(insert_idx)
            self._asks.increment_count()
            ask_insertion_level = &asks.levels[insert_idx]
            ask_insertion_level.price = ask.price
            ask_insertion_level.ticks = ask.ticks
            ask_insertion_level.size = ask.size
            ask_insertion_level.lots = ask.lots
            ask_insertion_level.norders = ask.norders

    cdef void _process_middle_bid_ticks(self, OrderbookLevel* bid):
        """Process a bid level that falls in the middle of the existing bid levels."""
        cdef:
            OrderbookLadderData* bids = self._bids_data
            OrderbookLadderData* asks = self._asks_data
            OrderbookLevel* bid_insertion_level
            u64 i
            u64 current_bid_ticks
            u64 last_idx = bids.num_levels
            u64 insert_idx = last_idx
            bint is_matching = False

        for i in range(1, last_idx):
            current_bid_ticks = bids.levels[i].ticks
            if current_bid_ticks <= bid.ticks:
                insert_idx = i
                if current_bid_ticks == bid.ticks:
                    is_matching = True
                break

        if is_matching:
            if bid.lots == 0:
                self._bids.roll_left(insert_idx)
                self._bids.decrement_count()
            else:
                bid_insertion_level = &bids.levels[insert_idx]
                bid_insertion_level.size = bid.size
                bid_insertion_level.lots = bid.lots
                bid_insertion_level.norders = bid.norders
        else:
            if bid.lots == 0:
                return
                
            self._bids.roll_right(insert_idx)
            self._bids.increment_count()
            bid_insertion_level = &bids.levels[insert_idx]
            bid_insertion_level.price = bid.price
            bid_insertion_level.ticks = bid.ticks
            bid_insertion_level.size = bid.size
            bid_insertion_level.lots = bid.lots
            bid_insertion_level.norders = bid.norders

    cdef inline void clear(self):
        """Clear all levels from both sides of the orderbook."""
        self._bids.reset()
        self._asks.reset()

    cdef inline void consume_snapshot(self, OrderbookLevels new_asks, OrderbookLevels new_bids):
        """Replace the entire orderbook state with new snapshot data."""
        cdef:
            OrderbookLadderData* bids_data = self._bids.get_data()
            OrderbookLadderData* asks_data = self._asks.get_data()
            OrderbookLevel new_level
            u64 i, copy_n

        self._normalize_incoming_levels(new_asks, new_bids, True)

        self._asks.reset()
        copy_n = new_asks.num_levels if new_asks.num_levels <= asks_data.max_levels else asks_data.max_levels
        for i in range(copy_n):
            new_level = new_asks.levels[i]
            self._asks.insert_level(i, new_level)
            self._asks.increment_count()

        self._bids.reset()
        copy_n = new_bids.num_levels if new_bids.num_levels <= bids_data.max_levels else bids_data.max_levels
        for i in range(copy_n):
            new_level = new_bids.levels[i]
            self._bids.insert_level(i, new_level)
            self._bids.increment_count()

    cdef inline void consume_deltas(self, OrderbookLevels asks, OrderbookLevels bids):
        """Apply incremental delta updates to the orderbook."""
        if not self._check_if_empty():
            return

        cdef:
            OrderbookLadderData* bids_data = self._bids.get_data()
            OrderbookLadderData* asks_data = self._asks.get_data()
            OrderbookLevel* ask_level
            OrderbookLevel* bid_level
            u64 best_bid_ticks, best_ask_ticks
            u64 worst_bid_ticks, worst_ask_ticks
            u64 i

        self._normalize_incoming_levels(asks, bids, False)

        best_bid_ticks = bids_data.levels[0].ticks
        best_ask_ticks = asks_data.levels[0].ticks
        worst_bid_ticks = bids_data.levels[bids_data.num_levels - 1].ticks
        worst_ask_ticks = asks_data.levels[asks_data.num_levels - 1].ticks

        i = 0
        while i < asks.num_levels:
            ask_level = &asks.levels[i]
            if ask_level.ticks < best_ask_ticks:
                self._process_lower_ask_ticks(ask_level)
                best_ask_ticks = ask_level.ticks
                i += 1
            else:
                break

        if i < asks.num_levels:
            ask_level = &asks.levels[i]
            if ask_level.ticks == best_ask_ticks:
                self._process_matching_ask_ticks(ask_level)
                i += 1

        if asks_data.num_levels > 0:
            worst_ask_ticks = asks_data.levels[asks_data.num_levels - 1].ticks

        cdef u64 ask_idx = 1
        while i < asks.num_levels:
            ask_level = &asks.levels[i]
            if ask_level.ticks > worst_ask_ticks and asks_data.num_levels == asks_data.max_levels:
                break
            while ask_idx < asks_data.num_levels and asks_data.levels[ask_idx].ticks < ask_level.ticks:
                ask_idx += 1
            if ask_idx < asks_data.num_levels and asks_data.levels[ask_idx].ticks == ask_level.ticks:
                if ask_level.lots == 0:
                    self._asks.roll_left(ask_idx)
                    self._asks.decrement_count()
                else:
                    asks_data.levels[ask_idx].size = ask_level.size
                    asks_data.levels[ask_idx].lots = ask_level.lots
                    asks_data.levels[ask_idx].norders = ask_level.norders
            else:
                if ask_level.lots != 0:
                    self._asks.roll_right(ask_idx)
                    self._asks.increment_count()
                    asks_data.levels[ask_idx].price = ask_level.price
                    asks_data.levels[ask_idx].ticks = ask_level.ticks
                    asks_data.levels[ask_idx].size = ask_level.size
                    asks_data.levels[ask_idx].lots = ask_level.lots
                    asks_data.levels[ask_idx].norders = ask_level.norders
                    ask_idx += 1
            if asks_data.num_levels > 0:
                worst_ask_ticks = asks_data.levels[asks_data.num_levels - 1].ticks
            i += 1

        i = 0
        if i < bids.num_levels:
            bid_level = &bids.levels[i]
            if bid_level.ticks > best_bid_ticks:
                self._process_higher_bid_ticks(bid_level)
                best_bid_ticks = bid_level.ticks
                i += 1
        while i < bids.num_levels:
            bid_level = &bids.levels[i]
            if bid_level.ticks == best_bid_ticks:
                self._process_matching_bid_ticks(bid_level)
                i += 1
            else:
                break


        if bids_data.num_levels > 0:
            worst_bid_ticks = bids_data.levels[bids_data.num_levels - 1].ticks

        cdef u64 bid_idx = 1
        while i < bids.num_levels:
            bid_level = &bids.levels[i]
            if bid_level.ticks < worst_bid_ticks and bids_data.num_levels == bids_data.max_levels:
                break
            while bid_idx < bids_data.num_levels and bids_data.levels[bid_idx].ticks > bid_level.ticks:
                bid_idx += 1
            if bid_idx < bids_data.num_levels and bids_data.levels[bid_idx].ticks == bid_level.ticks:
                if bid_level.lots == 0:
                    self._bids.roll_left(bid_idx)
                    self._bids.decrement_count()
                else:
                    bids_data.levels[bid_idx].size = bid_level.size
                    bids_data.levels[bid_idx].lots = bid_level.lots
                    bids_data.levels[bid_idx].norders = bid_level.norders
            else:
                if bid_level.lots != 0:
                    self._bids.roll_right(bid_idx)
                    self._bids.increment_count()
                    bids_data.levels[bid_idx].price = bid_level.price
                    bids_data.levels[bid_idx].ticks = bid_level.ticks
                    bids_data.levels[bid_idx].size = bid_level.size
                    bids_data.levels[bid_idx].lots = bid_level.lots
                    bids_data.levels[bid_idx].norders = bid_level.norders
                    bid_idx += 1
            if bids_data.num_levels > 0:
                worst_bid_ticks = bids_data.levels[bids_data.num_levels - 1].ticks
            i += 1

    cdef inline void consume_bbo(self, OrderbookLevel ask, OrderbookLevel bid):
        """Update only the best bid and offer (top of book)."""
        if not self._check_if_empty():
            return

        cdef:
            OrderbookLadderData* asks_data = self._asks.get_data()
            OrderbookLadderData* bids_data = self._bids.get_data()
            OrderbookLevel* top_of_book_ask
            OrderbookLevel* top_of_book_bid
            u64 ask_ticks, bid_ticks, ask_lots, bid_lots
        if not self._has_ticks_and_lots:
            ask_ticks = convert_price_to_tick(ask.price, self._tick_size)
            bid_ticks = convert_price_to_tick(bid.price, self._tick_size)
            ask_lots = convert_size_to_lot(ask.size, self._lot_size)
            bid_lots = convert_size_to_lot(bid.size, self._lot_size)
        else:
            ask_ticks = ask.ticks
            bid_ticks = bid.ticks
            ask_lots = ask.lots
            bid_lots = bid.lots
        
        if not self._asks.is_empty():
            top_of_book_ask = &asks_data.levels[0]
            if ask_lots == 0 and ask_ticks == top_of_book_ask.ticks:
                self._asks.roll_left(0)
                self._asks.decrement_count()
            else:
                if top_of_book_ask.ticks == ask_ticks:
                    top_of_book_ask.size = ask.size
                    top_of_book_ask.lots = ask_lots
                    top_of_book_ask.norders = ask.norders
                elif ask_ticks < top_of_book_ask.ticks:
                    self._asks.roll_right(0)
                    self._asks.increment_count()
                    top_of_book_ask = &asks_data.levels[0]
                    top_of_book_ask.price = ask.price
                    top_of_book_ask.ticks = ask_ticks
                    top_of_book_ask.size = ask.size
                    top_of_book_ask.lots = ask_lots
                    top_of_book_ask.norders = ask.norders
                else:
                    self._asks.roll_left(0)
                    self._asks.decrement_count()
                    if not self._asks.is_empty():
                        top_of_book_ask = &asks_data.levels[0]
                        top_of_book_ask.price = ask.price
                        top_of_book_ask.ticks = ask_ticks
                        top_of_book_ask.size = ask.size
                        top_of_book_ask.lots = ask_lots
                        top_of_book_ask.norders = ask.norders
        else:
            if ask_lots != 0:
                self._asks.roll_right(0)
                self._asks.increment_count()
                top_of_book_ask = &asks_data.levels[0]
                top_of_book_ask.price = ask.price
                top_of_book_ask.ticks = ask_ticks
                top_of_book_ask.size = ask.size
                top_of_book_ask.lots = ask_lots
                top_of_book_ask.norders = ask.norders
        
        if not self._bids.is_empty():
            top_of_book_bid = &bids_data.levels[0]
            if bid_lots == 0 and bid_ticks == top_of_book_bid.ticks:
                self._bids.roll_left(0)
                self._bids.decrement_count()
            else:
                if top_of_book_bid.ticks == bid_ticks:
                    top_of_book_bid.size = bid.size
                    top_of_book_bid.lots = bid_lots
                    top_of_book_bid.norders = bid.norders
                elif bid_ticks > top_of_book_bid.ticks:
                    self._bids.roll_right(0)
                    self._bids.increment_count()
                    top_of_book_bid = &bids_data.levels[0]
                    top_of_book_bid.price = bid.price
                    top_of_book_bid.ticks = bid_ticks
                    top_of_book_bid.size = bid.size
                    top_of_book_bid.lots = bid_lots
                    top_of_book_bid.norders = bid.norders
                else:
                    self._bids.roll_left(0)
                    self._bids.decrement_count()
                    if not self._bids.is_empty():
                        top_of_book_bid = &bids_data.levels[0]
                        top_of_book_bid.price = bid.price
                        top_of_book_bid.ticks = bid_ticks
                        top_of_book_bid.size = bid.size
                        top_of_book_bid.lots = bid_lots
                        top_of_book_bid.norders = bid.norders
        else:
            if bid_lots != 0:
                self._bids.roll_right(0)
                self._bids.increment_count()
                top_of_book_bid = &bids_data.levels[0]
                top_of_book_bid.price = bid.price
                top_of_book_bid.ticks = bid_ticks
                top_of_book_bid.size = bid.size
                top_of_book_bid.lots = bid_lots
                top_of_book_bid.norders = bid.norders

        # Remove crossed bids/asks (fix: check count before accessing)
        while (
            bids_data.num_levels > 0
            and asks_data.num_levels > 0
            and bids_data.levels[0].ticks >= asks_data.levels[0].ticks
        ):
            self._asks.roll_left(0)
            self._asks.decrement_count()

    cdef inline double get_mid_price(self):
        """Calculate the mid price from best bid and ask."""
        self._ensure_not_empty()
        cdef:
            OrderbookLadderData* bids_data = self._bids_data
            OrderbookLadderData* asks_data = self._asks_data
            u64 bid_ticks = bids_data.levels[0].ticks
            u64 ask_ticks = asks_data.levels[0].ticks
        return convert_price_from_tick(
            tick=(bid_ticks + ask_ticks) // 2,
            tick_size=self._tick_size,
        )

    cdef inline double get_bbo_spread(self):
        """Calculate the spread between best bid and ask."""
        self._ensure_not_empty()
        cdef:
            OrderbookLadderData* bids_data = self._bids_data
            OrderbookLadderData* asks_data = self._asks_data
            u64 bid_ticks = bids_data.levels[0].ticks
            u64 ask_ticks = asks_data.levels[0].ticks
        return convert_price_from_tick(
            tick=ask_ticks - bid_ticks,
            tick_size=self._tick_size,
        )

    cdef inline double get_wmid_price(self):
        """Calculate weighted mid price using best bid/ask volumes."""
        self._ensure_not_empty()
        cdef:
            OrderbookLadderData* bids_data = self._bids_data
            OrderbookLadderData* asks_data = self._asks_data
            u64 bid_ticks = bids_data.levels[0].ticks
            u64 bid_lots = bids_data.levels[0].lots
            u64 ask_ticks = asks_data.levels[0].ticks
            u64 ask_lots = asks_data.levels[0].lots
            u64 total_lots = bid_lots + ask_lots
        if total_lots == 0:
            return 0.0
        return convert_price_from_tick(
            tick=(bid_ticks * bid_lots + ask_ticks * ask_lots) // total_lots,
            tick_size=self._tick_size,
        )

    cdef inline double get_volume_weighted_mid_price(self, double size, bint is_base_currency):
        """Calculate volume-weighted mid price for a given trade size."""
        self._ensure_not_empty()
        cdef double mid_price = self.get_mid_price()
        if size <= 0.0:
            return mid_price
        cdef:
            double target = size if is_base_currency else (size / mid_price)
            u64 target_lots = convert_size_to_lot(target, self._lot_size)
            OrderbookLadderData* asks_data = self._asks_data
            OrderbookLadderData* bids_data = self._bids_data
            u64 cum_ask_lots = 0
            u64 cum_bid_lots = 0
            u64 final_buy_ticks = 0
            u64 final_sell_ticks = 0
            u64 i
        for i in range(asks_data.num_levels):
            cum_ask_lots += asks_data.levels[i].lots
            if cum_ask_lots >= target_lots:
                final_buy_ticks = asks_data.levels[i].ticks
                break
        for i in range(bids_data.num_levels):
            cum_bid_lots += bids_data.levels[i].lots
            if cum_bid_lots >= target_lots:
                final_sell_ticks = bids_data.levels[i].ticks
                break
        if final_buy_ticks == 0 or final_sell_ticks == 0:
            return INFINITY_DOUBLE
        return convert_price_from_tick((final_buy_ticks + final_sell_ticks) // 2, self._tick_size)

    cdef inline double get_price_impact(self, double size, bint is_buy, bint is_base_currency):
        """Calculate price impact of executing a trade of given size."""
        self._ensure_not_empty()
        if size <= 0.0:
            return 0.0
        cdef:
            double mid_price = self.get_mid_price()
            double target_base = size if is_base_currency else (size / mid_price)
            u64 target_lots = convert_size_to_lot(target_base, self._lot_size)
            OrderbookLadderData* side_data = self._asks_data if is_buy else self._bids_data
            u64 remaining_lots = target_lots
            u64 consumed_lots, available_lots
            u64 total_ticks_times_lots = 0
            u64 i
        if target_lots == 0:
            return 0.0
        for i in range(side_data.num_levels):
            available_lots = side_data.levels[i].lots
            consumed_lots = available_lots if available_lots < remaining_lots else remaining_lots
            total_ticks_times_lots += consumed_lots * side_data.levels[i].ticks
            remaining_lots -= consumed_lots
            if remaining_lots == 0:
                break
        if remaining_lots > 0:
            return INFINITY_DOUBLE
        cdef double avg_px = (self._tick_size * <double> total_ticks_times_lots) / <double> target_lots
        return abs(avg_px - mid_price)

    cdef inline bint is_bbo_crossed(self, double other_bid_price, double other_ask_price):
        """Check if this orderbook's BBO crosses with another orderbook's BBO."""
        self._ensure_not_empty()
        cdef:
            OrderbookLadderData* bids_data = self._bids_data
            OrderbookLadderData* asks_data = self._asks_data
            u64 my_bid_ticks = bids_data.levels[0].ticks
            u64 my_ask_ticks = asks_data.levels[0].ticks
            u64 other_bid_ticks = convert_price_to_tick(other_bid_price, self._tick_size)
            u64 other_ask_ticks = convert_price_to_tick(other_ask_price, self._tick_size)
        return my_bid_ticks > other_ask_ticks or my_ask_ticks < other_bid_ticks

    cdef inline bint does_bbo_price_change(self, double bid_price, double ask_price):
        """Check if the given prices differ from current BBO."""
        self._ensure_not_empty()
        cdef:
            OrderbookLadderData* bids_data = self._bids_data
            OrderbookLadderData* asks_data = self._asks_data
            u64 my_bid_ticks = bids_data.levels[0].ticks
            u64 my_ask_ticks = asks_data.levels[0].ticks
            u64 other_bid_ticks = convert_price_to_tick(bid_price, self._tick_size)
            u64 other_ask_ticks = convert_price_to_tick(ask_price, self._tick_size)
        return my_bid_ticks != other_bid_ticks or my_ask_ticks != other_ask_ticks

    cdef inline OrderbookLadderData* get_bids_data(self) noexcept:
        """Get the bids ladder data.

        Returns:
            Pointer to OrderbookLadderData for bids
        """
        return self._bids_data

    cdef inline OrderbookLadderData* get_asks_data(self) noexcept:
        """Get the asks ladder data.

        Returns:
            Pointer to OrderbookLadderData for asks
        """
        return self._asks_data


