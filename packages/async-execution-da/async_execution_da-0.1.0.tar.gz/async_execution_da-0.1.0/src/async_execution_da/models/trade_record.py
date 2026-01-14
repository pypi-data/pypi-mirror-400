from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TradeRecord:
    # ---- Order identifiers ----
    local_no: str
    system_no: Optional[str] = None
    order_no: Optional[str] = None

    # ---- Order info ----
    side: Optional[str] = None
    order_price: Optional[float] = None
    trigger_price: Optional[float] = None
    order_qty: Optional[int] = None

    # ---- Fill info ----
    filled_qty: int = 0
    filled_avg_price: float = 0.0

    # ---- Current position snapshot ----
    long_position_qty: int = 0
    long_pos_avg_price: float = 0.0
    short_position_qty: int = 0
    short_pos_avg_price: float = 0.0

    # ---- Status ----
    is_canceled: bool = False
    order_state: Optional[str] = None     # Exchange-native OrderState
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # -----------------------------------------
    # Helper properties
    # -----------------------------------------
    @property
    def is_filled(self):
        return self.filled_qty > 0 and self.filled_qty == self.order_qty

    @property
    def is_partial_filled(self):
        return 0 < self.filled_qty < self.order_qty

    @property
    def avg_fill(self):
        return self.filled_avg_price

    @staticmethod
    def from_api(data: dict) -> "TradeRecord":
        """
        Convert DA trade callbacks (onRtnOrder/onRtnTrade) to TradeRecord.
        Includes type coercion and missing-field guards.
        """
        def to_int(x):
            try:
                return int(float(x))
            except:
                return 0

        def to_float(x):
            try:
                return float(x)
            except:
                return 0.0

        return TradeRecord(
            # ---- Order identifiers ----
            local_no=data.get("LocalNo"),
            system_no=data.get("SystemNo") or data.get("system_no"),
            order_no=data.get("OrderNo") or data.get("order_no"),

            # ---- Basic order info ----
            side=data.get("BidAskFlag"),
            order_price=to_float(data.get("OrderPrice")),
            trigger_price=to_float(data.get("TriggerPrice")),
            order_qty=to_int(data.get("OrderQty")),

            # ---- Fill info ----
            filled_qty=to_int(data.get("FilledQty")),
            filled_avg_price=to_float(data.get("FilledAvgPrice")),

            # ---- Position snapshot ----
            long_position_qty=to_int(data.get("LongPositionQty")),
            long_pos_avg_price=to_float(data.get("LongPosAveragePrx")),
            short_position_qty=to_int(data.get("ShortPositionQty")),
            short_pos_avg_price=to_float(data.get("ShortPosAveragePrx")),

            # ---- Status ----
            is_canceled=str(data.get("IsCanceled", "0")) == "1",
            order_state=data.get("OrderState"),
        )
