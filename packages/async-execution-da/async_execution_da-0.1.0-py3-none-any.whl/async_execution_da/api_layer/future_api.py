import asyncio
import os
import time
from datetime import datetime
from async_execution_da.base_api.future_demo import MyFutureApi
from async_execution_da.models.trade_book import TradeBook
from async_execution_da.utils.time_utils import log
from async_execution_da.models.order_book import OrderBook
from async_execution_da.models.capital_info import CapitalInfo
try:
    from pyda.api.td_constant import (
        DERIVATIVE_LIMIT_ORDER,
        DERIVATIVE_STOP_LOSS_ORDER,
        DERIVATIVE_LIMIT_STOP_ORDER,
        DERIVATIVE_TDY_TIF,
        DERIVATIVE_BID,
        DERIVATIVE_ASK,
        DERIVATIVE_MARKET_ORDER,
        DERIVATIVE_ORD_FILTER_L
    )
except ImportError as e:
    raise ImportError(
        "The proprietary broker SDK `pyda` is required.\n"
        "Please install it before using async-execution-da.\n"
        "This project does not bundle broker SDKs."
    ) from e


ORDER_TYPE_MAP = {
    1: DERIVATIVE_LIMIT_ORDER,        # Limit order
    2: DERIVATIVE_MARKET_ORDER,       # Market order
    3: DERIVATIVE_LIMIT_STOP_ORDER,   # Stop limit order
    4: DERIVATIVE_STOP_LOSS_ORDER,    # Stop loss order
}


class EnhancedFutureApi(MyFutureApi):
    """Extended Future API wrapper."""

    def __init__(
            self,
            userid: str,
            password: str,
            author_code: str,
            computer_name: str = "",
            software_name: str = "",
            software_version: str = "1.0",
            tag50: str = "",
            address: str = "",
            heartbeat: int = 180,
            symbol: str = "",
            exchange: str = "",
    ) -> None:
        """Initialize API session state and helpers."""
        super().__init__(userid, password, author_code, computer_name, software_name, software_version, tag50)

        # Connection and login
        self.address = address
        self.heartbeat = heartbeat
        self.order_book = OrderBook()
        self.trade_book = TradeBook()
        self.symbol = symbol
        self.exchange = exchange

        # State management
        self.is_connected = False
        self.is_logged_in = False
        self.reqid = 0

        # Async Future objects
        self.loop = asyncio.get_running_loop()
        self._connected_future: asyncio.Future | None = None
        self._login_future: asyncio.Future | None = None
        self._capital_future: asyncio.Future | None = None
        self._order_future: asyncio.Future | None = None
        self._cancel_future: asyncio.Future | None = None
        self._position_future: asyncio.Future | None = None
        self._modify_future: asyncio.Future | None = None

        # Mapping structures
        self.currency_account_map: dict[str, str] = {}
        self.capital_info: dict[str, dict] = {}

        # Account queries
        self.target_currency = None
        self.capital_info_obj = None

        # Event emitter queue
        self.event_queue: asyncio.Queue = asyncio.Queue()

        # Order queries
        self._order_buffer: list[dict] = []

        # Query cooldown control (seconds)
        self._last_query_order_time: float = 0.0
        self._query_order_cooldown: float = 1.0  # At least 1 second apart

    # ==========================================================
    # Connection management
    # ==========================================================
    async def connect(self) -> None:
        """Establish a TCP connection to the trading server.

        Raises:
            ValueError: Raised when address is missing.
            TimeoutError: Raised when connection is not established within timeout.
        """
        if not self.address:
            raise ValueError("address is required before calling connect()")

        log(f"[FutureApi] Connecting to tcp://{self.address}")

        os.makedirs("log/future_api/", exist_ok=True)
        self.createFutureApi(True, "future_log.txt", "log/future_api/")
        self.registerNameServer("tcp://" + self.address)
        self.setHeartBeatTimeout(self.heartbeat)
        self.init()

        if not await self._wait_until_connected(timeout=10.0):
            raise TimeoutError("Front connection timeout")

        log("[FutureApi] Connected")

    # ==========================================================
    # Login and account mapping
    # ==========================================================
    async def login_and_fetch_accounts(self) -> bool:
        """Log in and wait for account mappings to complete.

        Returns:
            True if login and account mapping succeed; otherwise False.
        """
        if not self.is_connected:
            log("[FutureApi] Login aborted: not connected.")
            return False

        self.reqid += 1
        req = {
            "UserId": self.userid,
            "UserPwd": self.password,
            "AuthorCode": self.author_code,
            "ComputerName": self.computer_name,
            "SoftwareName": self.software_name,
            "SoftwareVersion": self.software_version,
            "Tag50": self.tag50,
        }

        log("[FutureApi] Login request sent.")
        self.reqUserLogin(req, self.reqid)

        # ✅ Wait for login and account mapping
        success = await self._wait_until_logged_in(timeout=8.0)
        if success:
            log(f"[FutureApi] Login complete. accounts={len(self.currency_account_map)}")
            return True
        log("[FutureApi] Login failed or account mapping incomplete.")
        return False

    # ==========================================================
    # 🔁 connect_and_login_with_accounts(): connect + login + account mapping
    # ==========================================================
    async def connect_and_login_with_accounts(self) -> bool:
        """Connect, log in, fetch account mappings, and sync orders.

        Returns:
            True if all steps succeed; otherwise False.
        """
        await self.connect()
        if not await self.login_and_fetch_accounts():
            return False
        await self.sync_orders_to_orderbook()
        return True

    # ==========================================================
    # Query capital info
    # ==========================================================
    async def query_account(self, currency: str = "USD") -> CapitalInfo | None:
        """Query capital info for a target currency."""
        self.reqid += 1
        reqid = self.reqid
        self._capital_future = self.loop.create_future()
        self.capital_info_obj: CapitalInfo | None = None
        self.target_currency = currency

        log(f"[FutureApi] Query capital currency={currency}")
        self.reqQryCapital({}, reqid)

        try:
            data = await asyncio.wait_for(self._capital_future, timeout=8.0)
            if data:
                self.capital_info_obj = CapitalInfo.from_api(data)
                log(
                    f"[FutureApi] Capital saved currency={self.capital_info_obj.CurrencyNo} "
                    f"value={self.capital_info_obj.TodayTradableFund}"
                )
                return self.capital_info_obj
            return None
        except asyncio.TimeoutError:
            log("[FutureApi] Capital query timeout")
            return None

    # ==========================================================
    # Place an order and wait for the async response
    # ==========================================================
    async def place_order_basic_async(
            self,
            local_no: str,
            exchange: str,
            symbol: str,
            side: str,
            price: float | None,
            volume: int,
            currency: str = "USD",
            order_type: str = DERIVATIVE_LIMIT_ORDER,
            tif: str = DERIVATIVE_TDY_TIF,
            open_close_flag: int = 1,
            trigger_price: float | None = None,
            timeout: float = 3.0,
    ) -> dict:
        """Place an order and wait for the async response."""
        account_no = self.currency_account_map.get(currency)
        if not account_no:
            raise RuntimeError(f"No account found for currency {currency}")

        # Record start time
        start_time = datetime.now()

        # 1️⃣ Register in OrderBook
        self.order_book.register_local_order(local_no)

        # 2️⃣ Create Future
        fut = self.order_book.create_future(local_no)

        # 3️⃣ Build request
        self.reqid += 1
        order_req = {
            "UserId": self.userid,
            "AccountNo": account_no,
            "LocalNo": local_no,
            "ExchangeCode": exchange,
            "ContractCode": symbol,
            "BidAskFlag": side,
            "OpenCloseFlag": str(open_close_flag),
            "OrderQty": str(volume),
            "OrderType": order_type,
            "TIF": tif,
            "Tag50": self.userid,
            "IsProgram": 1,
        }

        if price is not None:
            order_req["OrderPrice"] = str(price)
        if trigger_price is not None:
            order_req["TriggerPrice"] = str(trigger_price)

        # 4️⃣ Log
        log(
            "[FutureApi] Order submit "
            f"symbol={symbol} local_no={local_no} type={order_type} price={price or trigger_price}"
        )

        # 5️⃣ Send order
        self.reqOrderInsert(order_req, self.reqid)

        # 6️⃣ Wait for async result
        try:
            result = await asyncio.wait_for(fut, timeout=timeout)

            end_time = datetime.now()
            elapsed_ms = round((end_time - start_time).total_seconds() * 1000, 3)

            final_result = {
                "local_no": local_no,
                "system_no": result.get("system_no"),
                "order_no": result.get("order_no"),
                "status": result.get("status", "PENDING"),
                "error_id": result.get("error_id", 0),
                "error_msg": result.get("error_msg", ""),
                "elapsed_ms": elapsed_ms,
                "timestamp": end_time.isoformat(),
            }

            if final_result["error_id"] != 0:
                log(
                    "[FutureApi] Order submit error "
                    f"local_no={local_no} error_id={final_result['error_id']} "
                    f"error_msg={final_result['error_msg']}"
                )
            else:
                log(
                    "[FutureApi] Order complete "
                    f"local_no={local_no} system_no={final_result['system_no']} "
                    f"order_no={final_result['order_no']} status={final_result['status']} "
                    f"elapsed_ms={elapsed_ms}"
                )

            return final_result

        except asyncio.TimeoutError:
            log(f"[FutureApi] Order timeout local_no={local_no}")
            self.order_book.reject_future(local_no, RuntimeError("Timeout waiting for response"))
            raise

    async def limit_order(self, local_no: str, side: str, price: float, volume: int,
                          symbol: str | None = None, exchange: str | None = None,
                          tif: str = DERIVATIVE_TDY_TIF) -> dict:
        """Place a limit order."""
        symbol = symbol or self.symbol
        exchange = exchange or self.exchange
        direction = DERIVATIVE_BID if side.lower() == "buy" else DERIVATIVE_ASK
        return await self.place_order_basic_async(
            local_no=local_no,
            exchange=exchange,
            symbol=symbol,
            side=direction,
            price=price,
            volume=volume,
            order_type=DERIVATIVE_LIMIT_ORDER,
            tif=tif,
        )

    async def market_order(self, local_no: str, side: str, volume: int,
                           symbol: str | None = None, exchange: str | None = None,
                           tif: str = DERIVATIVE_TDY_TIF) -> dict:
        """Place a market order."""
        symbol = symbol or self.symbol
        exchange = exchange or self.exchange
        direction = DERIVATIVE_BID if side.lower() == "buy" else DERIVATIVE_ASK
        return await self.place_order_basic_async(
            local_no=local_no,
            exchange=exchange,
            symbol=symbol,
            side=direction,
            price=None,
            volume=volume,
            order_type=DERIVATIVE_MARKET_ORDER,
            tif=tif,
        )

    async def stop_limit_order(self, local_no: str, side: str, trigger_price: float, price: float, volume: int,
                               symbol: str | None = None, exchange: str | None = None,
                               tif: str = DERIVATIVE_TDY_TIF) -> dict:
        """Place a stop-limit order."""
        symbol = symbol or self.symbol
        exchange = exchange or self.exchange
        direction = DERIVATIVE_BID if side.lower() == "buy" else DERIVATIVE_ASK
        return await self.place_order_basic_async(
            local_no=local_no,
            exchange=exchange,
            symbol=symbol,
            side=direction,
            price=price,
            trigger_price=trigger_price,
            volume=volume,
            order_type=DERIVATIVE_LIMIT_STOP_ORDER,
            tif=tif,
        )

    async def stop_market_order(self, local_no: str, side: str, trigger_price: float, volume: int,
                                symbol: str | None = None, exchange: str | None = None,
                                tif: str = DERIVATIVE_TDY_TIF) -> dict:
        """Place a stop-market order."""
        symbol = symbol or self.symbol
        exchange = exchange or self.exchange
        direction = DERIVATIVE_BID if side.lower() == "buy" else DERIVATIVE_ASK
        return await self.place_order_basic_async(
            local_no=local_no,
            exchange=exchange,
            symbol=symbol,
            side=direction,
            price=None,
            trigger_price=trigger_price,
            volume=volume,
            order_type=DERIVATIVE_STOP_LOSS_ORDER,
            tif=tif,
        )

    # ==========================================================
    # 📋 Query orders
    # ==========================================================
    async def query_order(self, timeout: float = 5.0) -> list[dict]:
        """Query all orders with cooldown enforcement."""

        # --- Query interval limit ---
        now = time.time()
        elapsed = now - self._last_query_order_time
        if elapsed < self._query_order_cooldown:
            wait_time = self._query_order_cooldown - elapsed
            log(f"[FutureApi] Query throttled, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        self._last_query_order_time = time.time()

        self.reqid += 1
        reqid = self.reqid
        self._order_future = self.loop.create_future()
        self._order_buffer: list[dict] = []

        req = {"UserId": self.userid}
        log(f"[FutureApi] Query orders")
        self.reqQryOrder(req, reqid)

        try:
            orders = await asyncio.wait_for(self._order_future, timeout=timeout)
            log(f"[FutureApi] Orders received count={len(orders)}")
            return orders
        except asyncio.TimeoutError:
            log("[FutureApi] Order query timeout")
            return []

    async def query_active_orders(self, timeout: float = 5.0) -> dict[str, tuple[str, str]]:
        """Query active orders derived from all orders."""
        orders = await self.query_order(timeout=timeout)
        active_states = {"1", "2", "3"}
        active_orders = {
            o.get("LocalNo"): (o.get("SystemNo"), o.get("OrderNo"))
            for o in orders
            if o.get("OrderState") in active_states
        }
        log(f"[FutureApi] Active orders count={len(active_orders)}")
        return active_orders

    # ==========================================================
    # ❌ Cancel order
    # ==========================================================
    async def cancel_order_async(self, local_no: str, currency: str = "USD", timeout: float = 3.0) -> dict:
        """Cancel a single order by local_no."""
        order = self.order_book.get_by_local(local_no)
        if not order:
            log(f"[FutureApi] Cancel failed: not found local_no={local_no}")
            return {"local_no": local_no, "success": False, "message": "not found"}

        system_no = order.get("system_no")
        order_no = order.get("order_no")
        account_no = self.currency_account_map.get(currency)
        if not all([system_no, order_no, account_no]):
            log(f"[FutureApi] Cancel failed: invalid params local_no={local_no}")
            return {"local_no": local_no, "success": False, "message": "invalid params"}

        # Log start
        log(f"[FutureApi] Cancel start local_no={local_no}")

        # Build cancel request
        self.reqid += 1
        reqid = self.reqid
        self._cancel_future = self.loop.create_future()
        cancel_req = {
            "UserId": self.userid,
            "AccountNo": account_no,
            "LocalNo": local_no,
            "SystemNo": system_no,
            "OrderNo": order_no,
        }

        self.reqOrderCancel(cancel_req, reqid)

        try:
            result = await asyncio.wait_for(self._cancel_future, timeout=timeout)
            success = (result.get("error_id", 0) == 0)

            # Update status
            self.order_book.update_status(local_no, "CANCELED" if success else "CANCEL_FAILED")

            if success:
                log(f"[FutureApi] Cancel success local_no={local_no}")
            else:
                log(f"[FutureApi] Cancel failed local_no={local_no} msg={result.get('error_msg')}")

            return {
                "local_no": local_no,
                "success": success,
                "error_id": result.get("error_id", 0),
                "error_msg": result.get("error_msg", ""),
                "ts": result.get("ts"),
            }

        except asyncio.TimeoutError:
            self.order_book.update_status(local_no, "CANCEL_TIMEOUT")
            log(f"[FutureApi] Cancel timeout local_no={local_no}")
            return {"local_no": local_no, "success": False, "message": "timeout"}

    # ==========================================================
    # 🔁 Cancel all active orders (including partial fills)
    # ==========================================================
    async def cancel_all_active(self, currency: str = "USD") -> list[dict]:
        """Cancel all active orders."""
        log("[FutureApi] Cancel all active orders")

        # Query all orders
        orders = await self.query_order()
        if not orders:
            log("[FutureApi] No orders to cancel")
            return []

        active_states = {"1", "2", "3"}  # REQUESTED / QUEUED / PARTIALLY_FILLED
        cancel_targets = [o for o in orders if o.get("OrderState") in active_states]

        if not cancel_targets:
            log("[FutureApi] No active orders to cancel")
            return []

        results = []
        success_locals = []

        for o in cancel_targets:
            local_no = o.get("LocalNo")
            if not local_no:
                continue
            result = await self.cancel_order_async(local_no, currency)
            results.append(result)
            if result.get("success"):
                success_locals.append(local_no)

        if success_locals:
            joined = ", ".join(success_locals)
            log(f"[FutureApi] Cancelled orders [{joined}]")
        else:
            log("[FutureApi] No orders cancelled")

        return results

    async def query_position_total(self) -> dict:
        """Query total positions and return on last=True."""
        self.reqid += 1
        reqid = self.reqid

        self._position_future = self.loop.create_future()

        da_req = {"AccountNo": self.userid}
        log(f"[FutureApi] Query positions")

        # Send request
        self.reqQryTotalPosition(da_req, reqid)

        try:
            data = await asyncio.wait_for(self._position_future, timeout=3.0)
            log(f"[FutureApi] Positions received long={data['LongPositionQty']} short={data['ShortPositionQty']}")
            return data
        except asyncio.TimeoutError:
            log("[FutureApi] Position query timeout")
            return {}

    async def check_and_close_positions(self, symbol: str | None = None, exchange: str | None = None) -> dict:
        """Close any open positions using a market order."""
        symbol = symbol or self.symbol
        exchange = exchange or self.exchange

        log("[FutureApi] Checking positions")

        pos = await self.query_position_total()

        if not pos:
            log("[FutureApi] No positions to close")
            return {"has_position": False, "details": None}

        long_qty = int(pos.get("LongPositionQty", 0) or 0)
        short_qty = int(pos.get("ShortPositionQty", 0) or 0)

        if long_qty == 0 and short_qty == 0:
            log("[FutureApi] No positions (qty=0)")
            return {"has_position": False, "details": pos}

        # === Long position → sell market order ===
        if long_qty > 0:
            side = "sell"
            qty = long_qty
        else:
            # === Short position → buy market order ===
            side = "buy"
            qty = short_qty

        # Local order number
        local_no = datetime.now().strftime("%m%d%H%M%f") + "_close"

        log(f"[FutureApi] Close order submit side={side} qty={qty}")

        try:
            res = await self.market_order(
                local_no=local_no,
                side=side,
                volume=qty,
                symbol=symbol,
                exchange=exchange
            )
            log(f"[FutureApi] Close order submitted local_no={res.get('local_no')}")

        except Exception as exc:
            log(f"[FutureApi] Close order failed error={exc}")
            return {"error": str(exc)}

        # === Wait for fill response (max 1 second) ===
        await asyncio.sleep(1.0)

        # === Re-query positions ===
        new_pos = await self.query_position_total()

        new_long = int(new_pos.get("LongPositionQty", 0) or 0)
        new_short = int(new_pos.get("ShortPositionQty", 0) or 0)
        position_cleared = (new_long == 0 and new_short == 0)

        if position_cleared:
            log(
                "[FutureApi] Positions cleared "
                f"long={long_qty}->{new_long} short={short_qty}->{new_short}"
            )
        else:
            log(f"[FutureApi] Positions remain long={new_long} short={new_short}")

        return {
            "side": side,
            "qty": qty,
            "order": res,
            "position_cleared": position_cleared,
            "after": new_pos,
        }

    async def modify_order_async(
            self,
            local_no: str,
            side: str,
            new_volume: int,
            orig_volume: int,
            order_type: int,
            new_trigger_price: float,
            orig_trigger_price: float,
            symbol: str | None = None,
            exchange: str | None = None,
            currency: str = "USD",
    ) -> dict:
        """Modify an existing order using OrderBook mappings."""
        order_type_obj = ORDER_TYPE_MAP.get(order_type)
        if order_type_obj is None:
            return {"success": False, "error": f"Unsupported order_type = {order_type}"}

        symbol = symbol or self.symbol
        exchange = exchange or self.exchange

        # ===== 1) Side conversion =====
        side = side.lower()
        if side == "buy":
            bidask = DERIVATIVE_BID       # = "1"
        elif side == "sell":
            bidask = DERIVATIVE_ASK       # = "2"
        else:
            return {"success": False, "error": f"Unsupported side: {side}"}

        # ==== 1) Read original order from OrderBook ====
        order = self.order_book.get_by_local(local_no)
        if not order:
            return {"success": False, "error": f"Order not found in OrderBook local_id={local_no}"}

        system_no = order.get("system_no")
        order_no = order.get("order_no")

        if not system_no or not order_no:
            return {
                "success": False,
                "error": f"Order response mapping incomplete local_id={local_no}, system_no={system_no}, order_no={order_no}"
            }


        # ==== Lookup account ====
        account_no = self.currency_account_map.get(currency)
        if not account_no:
            return {"success": False, "error": f"No account found for currency {currency}"}

        # ==== Create Future ====
        self.reqid += 1
        reqid = self.reqid
        self._modify_future = self.loop.create_future()

        # ==== Send modify request ====
        modify_req = {
            "UserId": self.userid,
            "LocalNo": local_no,
            "OrderNo": order_no,
            "SystemNo": system_no,
            "AccountNo": account_no,
            "ModifyTriggerPrice": str(new_trigger_price),
            "ModifyQty": str(new_volume),
            "TriggerPrice": str(orig_trigger_price),
            "OrderQty": str(orig_volume),
            "ExchangeCode": exchange,
            "ContractCode": symbol,
            "BidAskFlag": bidask,
            "OrderType": DERIVATIVE_STOP_LOSS_ORDER,
        }

        log(
            "[FutureApi] Modify submit "
            f"local_id={local_no} system_no={system_no} order_no={order_no} "
            f"trigger_price={new_trigger_price} volume={new_volume}"
        )

        self.reqOrderModify(modify_req, reqid)

        # ==== 6) Wait for modify response ====
        try:
            result = await asyncio.wait_for(self._modify_future, timeout=3.0)
            log(f"[FutureApi] Modify success local_id={local_no}")
            return result
        except asyncio.TimeoutError:
            log(f"[FutureApi] Modify timeout local_id={local_no}")
            return {"success": False, "error": "modify_order_async timeout"}

    # ==========================================================
    # 🧩 Async wait helpers (Future mode)
    # ==========================================================
    async def _wait_until_connected(self, timeout: float = 5.0) -> bool:
        """Wait for onFrontConnected callback."""
        if self.is_connected:
            return True

        self._connected_future = self.loop.create_future()
        try:
            await asyncio.wait_for(self._connected_future, timeout=timeout)
            return True
        except asyncio.TimeoutError:
            log("[FutureApi] Connect wait timeout")
            return False

    async def _wait_until_logged_in(self, timeout: float = 8.0) -> bool:
        """Wait for login and account mapping to complete."""
        if self.is_logged_in and self.currency_account_map:
            return True

        loop = asyncio.get_event_loop()
        self._login_future = loop.create_future()
        self._account_future = loop.create_future()

        # ✅ Wait for login success
        try:
            await asyncio.wait_for(self._login_future, timeout=timeout)
        except asyncio.TimeoutError:
            log("[FutureApi] Login wait timeout")
            return False

        # ✅ Wait for account mapping
        try:
            await asyncio.wait_for(self._account_future, timeout=timeout)
            return True
        except asyncio.TimeoutError:
            log("[FutureApi] Account mapping wait timeout")
            return False

    # ==========================================================
    # 📡 Callback overrides (event state)
    # ==========================================================
    def onFrontConnected(self) -> None:
        """Handle front connection callback."""
        self.is_connected = True
        log("[FutureApi] Front connected")
        if self._connected_future and not self._connected_future.done():
            self.loop.call_soon_threadsafe(self._resolve_future_once, self._connected_future, True)

    def onFrontDisconnected(self, iReason: int) -> None:
        """Handle front disconnection callback."""
        self.is_connected = False
        self.is_logged_in = False
        log(f"[FutureApi] Front disconnected reason={iReason}")

    def onRspUserLogin(self, error: dict, reqid: int, last: bool) -> None:
        """Handle login response."""
        error_id = error.get("ErrorID", 0)
        if not error_id:
            self.is_logged_in = True
            log(f"[FutureApi] Login success")
            if self._login_future and not self._login_future.done():
                self.loop.call_soon_threadsafe(self._resolve_future_once, self._login_future, True)
        else:
            log(f"[FutureApi] Login failed error_id={error_id}")

    # ==========================================================
    # 📋 Callback: account and capital queries
    # ==========================================================
    def onRspAccount(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle account mapping response."""
        if error["ErrorID"]:
            log(f"[FutureApi] Account error msg={error['ErrorMsg']}")
            return

        currency = data.get("CurrencyNo")
        account_no = data.get("AccountNo")
        if currency and account_no:
            self.currency_account_map[currency] = account_no

        # ✅ Final response (last=True)
        if last:
            if hasattr(self, "_account_future") and not self._account_future.done():
                self.loop.call_soon_threadsafe(self._account_future.set_result, True)
            log(f"[FutureApi] Account mapping complete count={len(self.currency_account_map)}")

    def onRspQryCapital(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle capital query response."""
        if error["ErrorID"]:
            log(f"[FutureApi] Capital query error id={error['ErrorID']} msg={error['ErrorMsg']}")
            if self._capital_future and not self._capital_future.done():
                self._capital_future.set_result(None)
            return

        currency = data.get("CurrencyNo")
        # ✅ Keep only target currency
        if currency == getattr(self, "target_currency", None):
            self.capital_info[currency] = data
            if self._capital_future and not self._capital_future.done():
                self.loop.call_soon_threadsafe(self._resolve_future_once, self._capital_future, data)

        if last:
            # Return None only if no matching currency received
            if self._capital_future and not self._capital_future.done():
                self.loop.call_soon_threadsafe(self._resolve_future_once, self._capital_future, None)

    def onRspOrderInsert(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle order insert response."""
        local_no = data.get("LocalNo") or ""
        system_no = data.get("SystemNo")
        order_no = data.get("OrderNo")

        # Build event (keep broker fields + custom fields)
        evt = {
            **data,  # Preserve original fields
            "type": "rsp_order_insert",
            "local_no": local_no,
            "system_no": system_no,
            "order_no": order_no,
            "error_id": error.get("ErrorID", 0),
            "error_msg": error.get("ErrorMsg", ""),
            "ts": datetime.now().isoformat(),
        }

        # ✅ Update order book
        self.order_book.update_system_no(local_no, system_no)
        self.order_book.update_order_no(local_no, order_no)
        self.publish_event(evt)

        # ✅ Handle Future logic
        fut = self.order_book.pending_futures.get(local_no)
        if not fut:
            return

        # Second response: full info
        if not fut.done() and system_no and order_no:
            self.order_book.resolve_future(local_no, evt)
        else:
            # First response only has system_no
            fut._partial_evt = evt

    def onRtnOrder(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle order update event."""
        local_no = data.get("LocalNo")
        if not local_no:
            return

        self.trade_book.update(data)
        self.publish_event({"type": "on_rtn_order", "data": data})

    def onRspQryOrder(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle order query response."""
        err_id = error.get("ErrorID", 0)
        err_msg = error.get("ErrorMsg", "")
        if err_id == 90003 and err_msg == "Normal body is empty":
            if hasattr(self, "_order_future") and not self._order_future.done():
                self.loop.call_soon_threadsafe(self._order_future.set_result, [])
            return
        if err_id:
            log(f"[FutureApi] Order query error id={err_id} msg={err_msg}")
            if hasattr(self, "_order_future") and not self._order_future.done():
                self.loop.call_soon_threadsafe(self._order_future.set_result, [])
            return

        if not hasattr(self, "_order_buffer"):
            self._order_buffer = []
        self._order_buffer.append(data)

        if last:
            if hasattr(self, "_order_future") and not self._order_future.done():
                self.loop.call_soon_threadsafe(self._resolve_future_once, self._order_future, self._order_buffer)
            log(f"[FutureApi] Order query complete count={len(self._order_buffer)}")

    def onRspOrderCancel(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle cancel response."""
        local_no = data.get("LocalNo", "")
        evt = {
            **data,
            "type": "rsp_order_cancel",
            "local_no": local_no,
            "error_id": error.get("ErrorID", 0),
            "error_msg": error.get("ErrorMsg", ""),
            "ts": datetime.now().isoformat(),
        }
        self.publish_event(evt)

        if error["ErrorID"]:
            log(f"[FutureApi] Cancel failed local_no={local_no} msg={error['ErrorMsg']}")
            self.order_book.orders.get(local_no, {}).update(status="CANCEL_FAILED")
            if hasattr(self, "_cancel_future") and not self._cancel_future.done():
                self.loop.call_soon_threadsafe(self._cancel_future.set_result, evt)
        else:
            log(f"[FutureApi] Cancel success local_no={local_no}")
            self.order_book.orders.get(local_no, {}).update(status="CANCELED")
            if hasattr(self, "_cancel_future") and not self._cancel_future.done():
                self.loop.call_soon_threadsafe(self._cancel_future.set_result, evt)

    def onRspQryTotalPosition(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle total position response."""
        log(f"[FutureApi] Position response last={last}")

        # Return immediately when last=True is received
        if last and self._position_future and not self._position_future.done():
            self._position_future.set_result(data)

    def onRspOrderModify(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle order modify response."""

        evt = {
            **data,
            "type": "rsp_order_modify",
            "local_no": data.get("LocalNo", ""),
            "error_id": error.get("ErrorID", 0),
            "error_msg": error.get("ErrorMsg", ""),
            "ts": datetime.now().isoformat(),
        }

        # Integrate with event queue
        self.publish_event(evt)

        if not hasattr(self, "_modify_future") or not self._modify_future:
            return

        # set result
        if not self._modify_future.done():
            self.loop.call_soon_threadsafe(self._modify_future.set_result, evt)

    def onRtnPosition(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle position update event."""

        # Timestamp (milliseconds)
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        local_no = data.get("LocalNo", "")
        long_qty = data.get("LongPositionQty", 0)
        short_qty = data.get("ShortPositionQty", 0)
        avg_long = data.get("LongPosAveragePrx", 0.0)
        avg_short = data.get("ShortPosAveragePrx", 0.0)

        # Determine current position direction
        if long_qty > 0:
            pos_side = "LONG"
            pos_qty = long_qty
            pos_avg = avg_long
        elif short_qty > 0:
            pos_side = "SHORT"
            pos_qty = short_qty
            pos_avg = avg_short
        else:
            pos_side = "FLAT"
            pos_qty = 0
            pos_avg = 0.0

        log(f"[FutureApi] Position update time={ts} side={pos_side} qty={pos_qty} avg={pos_avg}")

    def onRtnCapital(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle capital update event."""
        log(
            "[FutureApi] Capital update "
            f"Money={data.get('Money'):.2f}, "
            f"Available={data.get('Available'):.2f}, "
            f"FrozenDeposit={data.get('FrozenDeposit'):.2f}, "
            f"UnexpiredProfit={data.get('UnexpiredProfit'):.2f}, "
            f"UnaccountProfit={data.get('UnaccountProfit'):.2f}, "
            f"Fee={data.get('FilledTotalFee'):.2f}, "
            f"Mortgage={data.get('MortgageMoney'):.2f}"
        )

    def onRtnTrade(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """Handle trade event."""

        local_no = data.get("LocalNo", "")
        price = data.get("FilledPrice", "")

        log(f"[FutureApi] Trade local_no={local_no} price={price}")

    # ==========================================================
    # 🔧 Helper functions
    # ==========================================================
    def _resolve_future_once(self, fut: asyncio.Future | None, value: object) -> None:
        """Resolve a Future once if pending."""
        # Re-check during execution to avoid races
        if fut is not None and not fut.done():
            try:
                fut.set_result(value)
            except asyncio.InvalidStateError:
                pass

    def getAccountNo(self, currency: str = "USD") -> str | None:
        """Return account number for a currency."""
        account_no = self.currency_account_map.get(currency)
        if account_no:
            log(f"[FutureApi] Account number found currency={currency}")
            return account_no
        log(f"[FutureApi] Account number missing currency={currency}")
        return None

    def publish_event(self, evt: dict) -> None:
        """Publish an event to the queue."""
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(lambda: self.event_queue.put_nowait(evt))

    # ==========================================================
    # ♻️ Sync orders to local OrderBook at startup
    # ==========================================================
    async def sync_orders_to_orderbook(self) -> int:
        """Sync broker orders into the local OrderBook on startup.

        Returns:
            The number of newly loaded orders.
        """
        log("[FutureApi] Syncing broker orders to local OrderBook.")
        orders = await self.query_order()

        if not orders:
            log("[FutureApi] No orders to sync.")
            return 0

        count_new = 0
        for o in orders:
            local_no = o.get("LocalNo")
            system_no = o.get("SystemNo")
            order_no = o.get("OrderNo")
            state = o.get("OrderState")

            if not local_no:
                continue

            if local_no not in self.order_book.orders:
                self.order_book.load_existing_order(local_no, system_no, order_no, state)
                count_new += 1

        log(f"[FutureApi] OrderBook sync complete. new_orders={count_new}")
        return count_new
