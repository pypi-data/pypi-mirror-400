# async-execution-da

> **Async execution layer for futures trading**, built on top of a broker-provided Python SDK.
>
> This project provides an **async-first, production-oriented wrapper** around a proprietary
> futures trading API, focusing on order execution, account queries, and event-driven workflows.

---

## 🚦 Project Status

* **Status**: Active development
* **Stability**: Used in live / paper trading environments by the author
* **Python**: 3.10 (tested)
* **License**: MIT

---

## ✨ What This Project Is

`async-execution-da` is an **asynchronous execution layer** designed for:

* Futures / derivatives trading systems
* Quantitative trading infrastructure
* Event-driven execution engines
* Developers who need **non-blocking broker interactions**

It wraps a broker-provided synchronous SDK and adds:

* Async connection & login flows
* Deterministic account mapping
* Structured capital queries
* Robust order helpers (market / limit / stop)
* Local `OrderBook` for order ID reconciliation
* Async event queue for broker callbacks

---

## 🚫 What This Project Is NOT

* ❌ A trading strategy or signal generator
* ❌ A backtesting framework
* ❌ A broker SDK
* ❌ A replacement for risk management

This project focuses **strictly on execution and broker interaction**.

---

## ⚠️ Important Notice (Proprietary Dependency)

This project **does NOT include or redistribute** any proprietary broker SDKs.

You must obtain and install the broker-provided Python package (`pyda`) **separately**.

Reasons:

* The broker SDK is **not open-source**
* It is **not published on PyPI**
* Redistribution may violate broker licensing terms

This repository only contains **original open-source code** written by the author.

---

## 📦 Requirements

* Python **3.10+** (3.11 not yet supported)
* Broker SDK providing:

  * `pyda.api`
  * `pyda.api.td_constant`

> ℹ️ If `pyda` is not installed, importing execution APIs will raise a clear `ImportError`
> explaining the missing dependency.

---

## 📥 Installation

### Option 1: Editable install (recommended for development)

```bash
pip install -e .
```

### Option 2: Install directly from GitHub

```bash
pip install git+https://github.com/Reece-Lu/async-execution-da.git
```

> ⚠️ Ensure the broker SDK is installed **before** running the code.

---

## 🚀 Quickstart

```python
import asyncio
from async_execution_da.api_layer.future_api import EnhancedFutureApi


async def main():
    api = EnhancedFutureApi(
        userid="YOUR_USER",
        password="YOUR_PASS",
        author_code="YOUR_AUTH",
        computer_name="M3Server",
        software_name="M3Algo",
        software_version="1.0",
        tag50="TAG",
        address="HOST:PORT",
        heartbeat=180,
        symbol="ES2603",
        exchange="CME",
    )

    await api.connect_and_login_with_accounts()

    account_no = api.getAccountNo("USD")
    print("Account No:", account_no)

    usd_info = await api.query_account("USD")
    if usd_info:
        print("Available Funds:", usd_info.TodayTradableFund)

asyncio.run(main())
```

---

## 🧩 Core Usage

### Connect & Login

```python
await api.connect_and_login_with_accounts()
```

---

### Query Account / Capital

```python
usd_info = await api.query_account("USD")
if usd_info:
    print(usd_info.FundAccountNo, usd_info.TodayRealtimeBalance)
```

---

### Place Orders

#### Limit Order

```python
result = await api.limit_order(
    local_no="11080745123456_entry",
    side="buy",
    price=4510.25,
    volume=2,
)
```

#### Market Order

```python
result = await api.market_order(
    local_no="11080745123456_market",
    side="sell",
    volume=2,
)
```

#### Stop-Limit Order

```python
result = await api.stop_limit_order(
    local_no="11080745123456_stoplimit",
    side="buy",
    trigger_price=4500.0,
    price=4501.0,
    volume=2,
)
```

#### Stop-Market Order

```python
result = await api.stop_market_order(
    local_no="11080745123456_stopmarket",
    side="sell",
    trigger_price=4515.0,
    volume=2,
)
```

---

### Query & Manage Orders

```python
orders = await api.query_order()
active = await api.query_active_orders()
```

---

### Cancel Orders

```python
await api.cancel_order_async("LOCAL_NO")
await api.cancel_all_active("USD")
```

---

### Modify Orders

```python
await api.modify_order_async(
    local_id="LOCAL_NO",
    side="buy",
    new_volume=3,
    orig_volume=2,
    order_type=4,
    new_trigger_price=5805.25,
    orig_trigger_price=5900.25,
)
```

---

### Close Open Positions

```python
await api.check_and_close_positions()
```

---

## 📡 Events & Callbacks

Broker callbacks are converted into async events and published to `event_queue`.

```python
async def event_listener(api):
    while True:
        evt = await api.event_queue.get()
        print("EVENT:", evt)
```

This allows **non-blocking, event-driven execution logic**.

---

## 📘 OrderBook

`OrderBook` maintains a local mapping between:

* `local_no`
* `system_no`
* `order_no`

This is critical for:

* Reliable order cancellation
* Order state reconciliation
* Handling async broker callbacks

---

## 🗺️ Roadmap

* [ ] Better type hints and dataclasses
* [ ] Explicit order state machine
* [ ] Retry & reconnect policies
* [ ] Structured logging hooks
* [ ] Unit tests with mocked broker SDK

---

## ⚖️ License

MIT License

---

## ⚠️ Disclaimer

This project is an **independent open-source wrapper**.

It is **not affiliated with, endorsed by, or supported by** any broker or trading venue.

All proprietary SDKs, APIs, and trademarks remain the property of their respective owners.
