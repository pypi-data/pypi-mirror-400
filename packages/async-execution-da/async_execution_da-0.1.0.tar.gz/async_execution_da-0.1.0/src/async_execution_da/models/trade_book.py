from collections import defaultdict
from typing import Callable, Dict, List
from .trade_record import TradeRecord


class TradeBook:
    """Store full TradeRecord for orders and allow subscription updates."""

    def __init__(self):
        self.records: Dict[str, TradeRecord] = {}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, local_no: str, callback: Callable):
        """Allow OrderManager to subscribe to order state changes."""
        self.subscribers[local_no].append(callback)

    def update(self, data: dict):
        """Order update from FutureApi.onRtnOrder."""

        local_no = data.get("LocalNo")
        if not local_no:
            return

        # ---- Lookup existing record or create a new one ----
        rec = self.records.get(local_no)
        if not rec:
            rec = TradeRecord(local_no=local_no)
            self.records[local_no] = rec

        # ---- Update all fields ----
        rec.system_no = data.get("SystemNo")
        rec.order_no = data.get("OrderNo")
        rec.order_price = data.get("OrderPrice")
        rec.trigger_price = data.get("TriggerPrice")
        rec.order_qty = data.get("OrderQty")

        rec.filled_qty = data.get("FilledQty", 0)
        rec.filled_avg_price = data.get("FilledAvgPrice", 0.0)

        rec.long_position_qty = data.get("LongPositionQty", 0)
        rec.long_pos_avg_price = data.get("LongPosAveragePrx", 0.0)
        rec.short_position_qty = data.get("ShortPositionQty", 0)
        rec.short_pos_avg_price = data.get("ShortPosAveragePrx", 0.0)

        rec.is_canceled = data.get("IsCanceled") == "1"
        rec.order_state = data.get("OrderState")

        # ---- Notify subscribers ----
        for cb in self.subscribers.get(local_no, []):
            cb(rec)
