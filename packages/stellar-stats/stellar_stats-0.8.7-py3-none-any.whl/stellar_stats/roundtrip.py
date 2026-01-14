import pandas as pd


def extract_roundtrips(df):
    """Extract round-trips from trades dataframe.
    Use itertuples because it's faster than iterrows.
    If trades_df.side.iloc[0] not in ['BUY', 'SELL'],
    then the df is from a broker that has dual positions,
    meaning they track long and short positions separately.

    Args:
        df (DataFrame): Raw trades dataframe with columns:
            - timestamp: trade timestamp
            - symbol: trading symbol
            - trading_day: trading day for the trade
            - side: trade side string (BUY/SELL for non dual positions, BUY_OPEN/BUY_CLOSE/SELL_OPEN/SELL_CLOSE for dual positions)
            - price: trade price
            - volume: trade volume (always positive)
            - value: trade value (always positive), always use this instead of price * volume because a multiplier could be applied
            - pnl: realized profit/loss for the trade
            - commission: trade commission (always positive)
                when the column is present, needs to be deducted from pnl to get more accurate pnl)

    Returns:
        DataFrame: Round trips with columns:
            - close_dt: close date
            - open_dt: open date
            - symbol: symbol
            - duration: position duration in days
            - pnl: realized profit/loss
            - pnl_pct: profit/loss percentage
            - pos_type: position type (LONG or SHORT)
            - pos_size: position size
    """
    roundtrips = {}  # {(position_id, close_date): roundtrip_data}
    position_counter = 0
    # {(symbol, pos_type): [volume, cost_basis, open_dt, open_commission, position_id]}
    positions = {}

    # Check if using dual positions
    is_dual = df.side.iloc[0] not in ["BUY", "SELL"]

    # Sort trades by timestamp to ensure proper order
    df = df.reset_index()
    trades = sorted(df.itertuples(), key=lambda x: x.timestamp)

    for trade in trades:
        symbol = trade.symbol
        side = trade.side
        volume = trade.volume

        # Determine position type and whether opening or closing
        if is_dual:
            is_opening = side in ["BUY_OPEN", "SELL_OPEN"]
            # For dual positions:
            # - BUY_OPEN/SELL_CLOSE affect long positions
            # - SELL_OPEN/BUY_CLOSE affect short positions
            is_long = side in ["BUY_OPEN", "SELL_CLOSE"]
        else:
            # For simple positions:
            # - BUY opens long or closes short
            # - SELL opens short or closes long
            is_buy = side == "BUY"
            pos_key_long = (symbol, "LONG")
            pos_key_short = (symbol, "SHORT")

            # Check if we have an existing position that this trade would close
            if is_buy and pos_key_short in positions:
                # BUY closing a short position
                is_opening = False
                is_long = False
            elif not is_buy and pos_key_long in positions:
                # SELL closing a long position
                is_opening = False
                is_long = True
            else:
                # Opening a new position
                is_opening = True
                is_long = is_buy

        pos_type = "LONG" if is_long else "SHORT"
        pos_key = (symbol, pos_type)

        if is_opening:
            # Opening or adding to position
            if pos_key not in positions:
                # Store opening commission if available
                open_commission = trade.commission if "commission" in df.columns else 0
                position_counter += 1
                positions[pos_key] = [
                    volume,
                    trade.value,
                    trade.trading_day,
                    open_commission,
                    position_counter,
                ]
            else:
                curr_volume, curr_cost = positions[pos_key][:2]
                new_volume = curr_volume + volume
                new_cost = curr_cost + trade.value
                positions[pos_key][0] = new_volume
                positions[pos_key][1] = new_cost
        else:
            # Closing position
            if pos_key not in positions:
                # This shouldn't happen with proper data - skip this trade
                continue

            position = positions[pos_key][:5]
            curr_volume, curr_cost, open_dt, open_commission, position_id = position
            close_volume = min(volume, curr_volume)
            close_ratio = close_volume / curr_volume

            # Calculate PnL and subtract both opening and closing commissions
            pnl = trade.pnl
            if "commission" in df.columns:
                # Subtract both opening and closing commissions proportionally
                pnl -= (open_commission + trade.commission) * close_ratio

            # Check if there's an existing same-day roundtrip for this position
            trade_date = trade.trading_day
            roundtrip_key = (position_id, trade_date)

            if roundtrip_key in roundtrips:
                # Update existing same-day roundtrip
                rt = roundtrips[roundtrip_key]
                rt["pnl"] += pnl
                rt["pos_size"] += close_volume
                # Add this trade's value and recalculate pnl_pct
                rt["close_value"] += trade.value
                if rt["close_value"] == 0:
                    # For zero accumulated value, use original cost basis from position
                    original_cost = curr_cost * (rt["pos_size"] / curr_volume)
                    rt["pnl_pct"] = (
                        rt["pnl"] / abs(original_cost) if original_cost != 0 else 0
                    )
                else:
                    rt["pnl_pct"] = rt["pnl"] / abs(rt["close_value"])
            else:
                # Create new roundtrip for different day or different position
                if trade.value == 0:
                    # For zero-value trades (like expired options), calculate percentage based on original cost
                    close_cost = curr_cost * close_ratio
                    pnl_pct = pnl / abs(close_cost) if close_cost != 0 else 0
                else:
                    pnl_pct = pnl / abs(trade.value)

                # Round duration to whole days for consistency
                duration = pd.Timedelta(days=(trade.trading_day - open_dt).days)

                roundtrips[roundtrip_key] = {
                    "close_dt": trade.trading_day,
                    "open_dt": open_dt,
                    "symbol": symbol,
                    "duration": duration,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "pos_type": pos_type,
                    "pos_size": close_volume,
                    "close_value": trade.value,
                }

            # Update remaining position if this was a partial close
            if close_volume < curr_volume:
                remaining_ratio = 1 - close_ratio
                # Update position with remaining volume, cost and commission
                positions[pos_key][0] = curr_volume - close_volume
                positions[pos_key][1] = curr_cost * remaining_ratio
                positions[pos_key][3] = open_commission * remaining_ratio
            else:
                del positions[pos_key]
            # If there's excess volume after closing the position,
            # open a new position in the opposite direction
            if volume > close_volume:
                excess_volume = volume - close_volume
                opposite_pos_type = "SHORT" if is_long else "LONG"
                opposite_pos_key = (symbol, opposite_pos_type)
                open_commission = trade.commission if "commission" in df.columns else 0
                position_counter += 1
                positions[opposite_pos_key] = [
                    excess_volume,
                    trade.value * (excess_volume / volume),
                    trade.trading_day,
                    open_commission,
                    position_counter,
                ]

    # Ensure consistent DataFrame structure even when no roundtrips exist
    if not roundtrips:
        return pd.DataFrame(columns=[
            "close_dt",
            "open_dt",
            "symbol",
            "duration",
            "pnl",
            "pnl_pct",
            "pos_type",
            "pos_size",
            "close_value",
        ])

    return pd.DataFrame(list(roundtrips.values()))
