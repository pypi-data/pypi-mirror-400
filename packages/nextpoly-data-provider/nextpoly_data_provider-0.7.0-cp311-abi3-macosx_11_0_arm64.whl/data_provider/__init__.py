"""Data provider for Python."""

from importlib.metadata import PackageNotFoundError, version

from data_provider.data_provider import (
    DataProvider,
    FpmmTransaction,
    HistoryPoint,
    Market,
    MarketToken,
    OffChain,
    OnChain,
    OrderFilledEvent,
    Timeseries,
    Trading,
)

__all__ = [
    "DataProvider",
    "OnChain",
    "OffChain",
    "Trading",
    "OrderFilledEvent",
    "FpmmTransaction",
    "Market",
    "MarketToken",
    "HistoryPoint",
    "Timeseries",
]

try:
    __version__ = version("nextpoly-data-provider")
except PackageNotFoundError:
    __version__ = "0.0.0"
