import asyncio
from datetime import datetime
from async_execution_da.utils.time_utils import log


class OrderBook:
    """
    📘 Order book / order tracker
    --------------------------------------------
    Tracks only:
      - local_no ↔ system_no ↔ order_no mapping
      - async Future states
      - current status (SUBMITTED / ACKNOWLEDGED / CONFIRMED)
    Does not store business fields (price/qty, etc.)
    --------------------------------------------
    """

    def __init__(self):
        self.orders: dict[str, dict] = {}
        self.system_to_local: dict[str, str] = {}
        self.order_to_local: dict[str, str] = {}
        self.pending_futures: dict[str, asyncio.Future] = {}

    # =====================================================
    # 🟢 New order registration
    # =====================================================
    def register_local_order(self, local_no: str):
        """Register local order number when submitting an order."""
        self.orders[local_no] = {
            "local_no": local_no,
            "system_no": None,
            "order_no": None,
            "status": "PENDING",
            "created_at": datetime.now(),
        }
        log(f"[OrderBook] 📝 New order registered local_no={local_no}, status=PENDING")

    # =====================================================
    # 🧩 Update broker response mappings
    # =====================================================
    def update_system_no(self, local_no: str, system_no: str | None):
        """Update broker-returned system_no."""
        if not system_no or local_no not in self.orders:
            return
        order = self.orders[local_no]
        existing = order.get("system_no")

        if not existing:
            order["system_no"] = system_no
            order["status"] = "ACKNOWLEDGED"
            self.system_to_local[system_no] = local_no
            log(f"[OrderBook] 🟢 system_no mapped local_no={local_no}, system_no={system_no}")
        elif existing == system_no:
            return
        else:
            log(f"[OrderBook] ⚠️ system_no mismatch local_no={local_no}, old={existing}, new={system_no}")
            order["system_no"] = system_no

    def update_order_no(self, local_no: str, order_no: str | None):
        """Update broker-returned order_no."""
        if not order_no or local_no not in self.orders:
            return
        order = self.orders[local_no]
        existing = order.get("order_no")

        if not existing:
            order["order_no"] = order_no
            order["status"] = "CONFIRMED"
            self.order_to_local[order_no] = local_no
            log(f"[OrderBook] 🟩 order_no mapped local_no={local_no}, order_no={order_no}")
        elif existing != order_no:
            log(f"[OrderBook] ⚠️ order_no mismatch local_no={local_no}, old={existing}, new={order_no}")
            order["order_no"] = order_no

    # =====================================================
    # 🔁 Future management
    # =====================================================
    def create_future(self, local_no: str) -> asyncio.Future:
        fut = asyncio.get_running_loop().create_future()
        self.pending_futures[local_no] = fut
        return fut

    def resolve_future(self, local_no: str, result: dict):
        fut = self.pending_futures.pop(local_no, None)
        if fut and not fut.done():
            fut.set_result(result)

    def reject_future(self, local_no: str, exc: Exception):
        fut = self.pending_futures.pop(local_no, None)
        if fut and not fut.done():
            fut.set_exception(exc)

    # =====================================================
    # 🔍 Lookups
    # =====================================================
    def get_by_local(self, local_no: str):
        """Get order by local number."""
        return self.orders.get(local_no)

    def get_by_system_no(self, system_no: str):
        """Get order by broker system_no."""
        local_no = self.system_to_local.get(system_no)
        if not local_no:
            return None
        return self.orders.get(local_no)

    def get_by_order_no(self, order_no: str):
        """Get order by broker order_no."""
        local_no = self.order_to_local.get(order_no)
        if not local_no:
            return None
        return self.orders.get(local_no)

    # =====================================================
    # 🔄 Status updates
    # =====================================================
    def update_status(self, local_no: str, new_status: str):
        """Update order status and log; ignore if not found."""
        order = self.orders.get(local_no)
        if not order:
            return
        order["status"] = new_status
        log(f"[OrderBook] 🔄 Status update local_no={local_no} → {new_status}")

    # =====================================================
    # 📦 Load existing orders (used on login sync)
    # =====================================================
    def load_existing_order(self, local_no: str, system_no: str, order_no: str, state_code: str | None):
        """
        Load existing order records during initial login or sync.
        Convert broker status codes to normalized status names.
        """
        status_map = {
            "1": "REQUESTED",
            "2": "QUEUED",
            "3": "PARTIALLY_FILLED",
            "6": "CANCELED",
            "7": "FILLED",
        }

        status = status_map.get(str(state_code), "UNKNOWN")

        self.orders[local_no] = {
            "local_no": local_no,
            "system_no": system_no,
            "order_no": order_no,
            "status": status,
            "created_at": datetime.now(),
        }

        # Build mapping relationships
        if system_no:
            self.system_to_local[system_no] = local_no
        if order_no:
            self.order_to_local[order_no] = local_no
