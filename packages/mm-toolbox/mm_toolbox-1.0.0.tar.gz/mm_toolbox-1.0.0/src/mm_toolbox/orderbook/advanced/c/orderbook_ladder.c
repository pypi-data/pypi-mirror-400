/**
 * orderbook_ladder.c - Implementation of ladder operations.
 *
 * Provides efficient memory shifting and level insertion for managing
 * ordered price levels in the orderbook, with optimized fast paths for
 * common cases (index 0, small moves).
 */

#include "orderbook_ladder.h"
#include <string.h>

void c_ladder_roll_right(OrderbookLadderData* data, uint64_t start_index) {
    uint64_t count = data->num_levels;

    /* Early exit if start_index is beyond current count */
    if (start_index > count) {
        return;
    }

    uint64_t num_move = count - start_index;
    OrderbookLevel* levels = data->levels;
    
    /* Fast path: start_index == 0 (most common case, ~80% of calls) */
    if (start_index == 0) {
        if (count < data->max_levels) {
            /* Normal case: shift all elements right by one from index 0 */
            if (num_move > 0) {
                /* Optimize small moves with unrolled loops */
                if (num_move <= 4) {
                    /* Unrolled for 1-4 levels */
                    if (num_move >= 4) levels[4] = levels[3];
                    if (num_move >= 3) levels[3] = levels[2];
                    if (num_move >= 2) levels[2] = levels[1];
                    if (num_move >= 1) levels[1] = levels[0];
                } else if (num_move <= 8) {
                    /* Partially unrolled for 5-8 levels */
                    uint64_t i = num_move;
                    while (i > 4) {
                        levels[i] = levels[i - 1];
                        i--;
                    }
                    levels[4] = levels[3];
                    levels[3] = levels[2];
                    levels[2] = levels[1];
                    levels[1] = levels[0];
                } else {
                    /* Larger moves: use memmove */
                    memmove(
                        &levels[1], 
                        &levels[0], 
                        num_move * sizeof(OrderbookLevel)
                    );
                }
            }
        } else {
            /* At max capacity - shift right but drop the last element */
            if (num_move > 1) {
                uint64_t move_size = num_move - 1;
                if (move_size <= 4) {
                    /* Unrolled for small moves */
                    if (move_size >= 4) levels[4] = levels[3];
                    if (move_size >= 3) levels[3] = levels[2];
                    if (move_size >= 2) levels[2] = levels[1];
                    if (move_size >= 1) levels[1] = levels[0];
                } else {
                    memmove(
                        &levels[1], 
                        &levels[0], 
                        move_size * sizeof(OrderbookLevel)
                    );
                }
            }
        }
        return;
    }
    
    /* General case: start_index > 0 */
    if (count < data->max_levels) {
        /* Normal case: shift all elements right by one */
        if (num_move > 0) {
            memmove(
                &levels[start_index + 1],
                &levels[start_index],
                num_move * sizeof(OrderbookLevel)
            );
        }
    } else {
        /* At max capacity - shift right but drop the last element */
        if (num_move > 1) {
            memmove(
                &levels[start_index + 1],
                &levels[start_index],
                (num_move - 1) * sizeof(OrderbookLevel)
            );
        }
    }
}

void c_ladder_roll_left(OrderbookLadderData* data, uint64_t start_index) {
    uint64_t count = data->num_levels;
    
    /* Early exit if start_index is at or beyond current count */
    if (start_index >= count) {
        return;
    }
    
    uint64_t num_move = count - start_index - 1;
    OrderbookLevel* levels = data->levels;
    
    /* Fast path: start_index == 0 (most common case, ~80% of calls) */
    if (start_index == 0) {
        if (num_move > 0) {
            /* Optimize small moves with unrolled loops */
            if (num_move <= 4) {
                /* Unrolled for 1-4 levels */
                if (num_move >= 1) levels[0] = levels[1];
                if (num_move >= 2) levels[1] = levels[2];
                if (num_move >= 3) levels[2] = levels[3];
                if (num_move >= 4) levels[3] = levels[4];
            } else if (num_move <= 8) {
                /* Partially unrolled for 5-8 levels */
                levels[0] = levels[1];
                levels[1] = levels[2];
                levels[2] = levels[3];
                levels[3] = levels[4];
                uint64_t i = 4;
                while (i < num_move) {
                    levels[i] = levels[i + 1];
                    i++;
                }
            } else {
                /* Larger moves: use memmove */
                memmove(
                    &levels[0], 
                    &levels[1], 
                    num_move * sizeof(OrderbookLevel)
                );
            }
        }
        return;
    }
    
    /* General case: start_index > 0 */
    if (num_move > 0) {
        memmove(
            &levels[start_index],
            &levels[start_index + 1],
            num_move * sizeof(OrderbookLevel)
        );
    }
}

void c_ladder_insert_level(OrderbookLevel* levels, uint64_t index, const OrderbookLevel* level) {
    levels[index] = *level;
}

