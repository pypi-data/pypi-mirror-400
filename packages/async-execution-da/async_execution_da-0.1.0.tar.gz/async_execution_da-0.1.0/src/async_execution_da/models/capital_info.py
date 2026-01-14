from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CapitalInfo:
    """Capital account data structure (full fields)."""

    # Basic fields
    UserId: str = ""
    Deposit: str = ""
    Withdraw: str = ""
    TodayTradableFund: float = 0.0
    TodayInitialBalance: float = 0.0
    TodayRealtimeBalance: float = 0.0
    FrozenFund: float = 0.0
    Commission: float = 0.0
    InitialMargin: float = 0.0
    YdTradableFund: float = 0.0
    YdInitialBalance: float = 0.0
    YdFinalBalance: float = 0.0
    ProfitLoss: float = 0.0

    # Currency and account fields
    CurrencyNo: str = ""
    CurrencyRate: float = 0.0
    LMEUnexpiredPL: float = 0.0
    LMEUnaccountPL: float = 0.0
    MaintenanceMargin: float = 0.0
    Premium: float = 0.0
    CreditAmount: float = 0.0
    IntialFund: float = 0.0
    FundAccountNo: str = ""
    TradeLimit: float = 0.0
    CanCashOutMoneyAmount: float = 0.0
    DepositInterest: float = 0.0
    LoanInterest: float = 0.0
    ErrorDescription: str = ""

    # Auto-added timestamp (non-API field)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    # ----------------------------------------------------------
    # Factory methods
    # ----------------------------------------------------------
    @classmethod
    def from_api(cls, data: dict) -> "CapitalInfo":
        """Build a CapitalInfo instance from broker API dict."""
        def safe_float(x):
            try:
                return float(x)
            except Exception:
                return 0.0

        return cls(
            UserId=data.get("UserId", ""),
            Deposit=data.get("Deposit", ""),
            Withdraw=data.get("Withdraw", ""),
            TodayTradableFund=safe_float(data.get("TodayTradableFund")),
            TodayInitialBalance=safe_float(data.get("TodayInitialBalance")),
            TodayRealtimeBalance=safe_float(data.get("TodayRealtimeBalance")),
            FrozenFund=safe_float(data.get("FrozenFund")),
            Commission=safe_float(data.get("Commission")),
            InitialMargin=safe_float(data.get("InitialMargin")),
            YdTradableFund=safe_float(data.get("YdTradableFund")),
            YdInitialBalance=safe_float(data.get("YdInitialBalance")),
            YdFinalBalance=safe_float(data.get("YdFinalBalance")),
            ProfitLoss=safe_float(data.get("ProfitLoss")),
            CurrencyNo=data.get("CurrencyNo", ""),
            CurrencyRate=safe_float(data.get("CurrencyRate")),
            LMEUnexpiredPL=safe_float(data.get("LMEUnexpiredPL")),
            LMEUnaccountPL=safe_float(data.get("LMEUnaccountPL")),
            MaintenanceMargin=safe_float(data.get("MaintenanceMargin")),
            Premium=safe_float(data.get("Premium")),
            CreditAmount=safe_float(data.get("CreditAmount")),
            IntialFund=safe_float(data.get("IntialFund")),
            FundAccountNo=data.get("FundAccountNo", ""),
            TradeLimit=safe_float(data.get("TradeLimit")),
            CanCashOutMoneyAmount=safe_float(data.get("CanCashOutMoneyAmount")),
            DepositInterest=safe_float(data.get("DepositInterest")),
            LoanInterest=safe_float(data.get("LoanInterest")),
            ErrorDescription=data.get("ErrorDescription", ""),
        )

    # ----------------------------------------------------------
    # Helper methods
    # ----------------------------------------------------------
    def to_json(self) -> dict:
        """Return a JSON-serializable dict."""
        return self.__dict__.copy()
