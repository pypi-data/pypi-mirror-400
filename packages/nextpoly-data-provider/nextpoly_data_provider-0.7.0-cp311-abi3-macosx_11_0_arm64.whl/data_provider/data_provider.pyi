from __future__ import annotations

from decimal import Decimal
from typing import Self, TypeAlias, final

# Type aliases used in public signatures.
UnixTimestamp: TypeAlias = int
JsonPrimitive: TypeAlias = str | int | Decimal | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

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
    "UnixTimestamp",
]

@final
class DataProvider:
    """Main data provider for on-chain, off-chain, and trading data."""

    def __new__(
        cls,
        onchain_db_path: str = "data/onchain.duckdb",
        offchain_db_path: str = "data/offchain.duckdb",
        simulation_time: UnixTimestamp | None = None,
    ) -> Self:
        """Create a data provider.

        Args:
            onchain_db_path: Path to the on-chain DuckDB database.
            offchain_db_path: Path to the off-chain DuckDB database.
            simulation_time: Unix timestamp in UTC seconds. None disables filtering.
        """
        ...

    @property
    def on_chain(self) -> OnChain:
        """On-chain data (order filled events, FPMM transactions)."""
        ...

    @property
    def off_chain(self) -> OffChain:
        """Off-chain data (markets, market tokens)."""
        ...

    @property
    def trading(self) -> Trading:
        """Trading data (timeseries)."""
        ...

    def set_simulation_time(self, simulation_time: UnixTimestamp | None) -> None:
        """Set simulation time (UTC seconds) for off-chain and trading queries."""
        ...

    def get_simulation_time(self) -> UnixTimestamp | None:
        """Get current simulation time (UTC seconds), or None if unset."""
        ...

    def __repr__(self) -> str: ...

@final
class OnChain:
    """On-chain data provider."""

    def list_orders(
        self,
        token_id: str | None = None,
        start_ts: UnixTimestamp | None = None,
        end_ts: UnixTimestamp | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order: str | None = None,
        ascending: bool = True,
    ) -> list[OrderFilledEvent]:
        """List order filled events.

        Args:
            token_id: Filter by CLOB token id (maker or taker asset).
            start_ts: Optional start timestamp (unix seconds).
            end_ts: Optional end timestamp (unix seconds).
            limit: Maximum number of rows to return.
            offset: Rows to skip.
            order: Comma-separated list of fields to order by.
            ascending: Sort order (default: True).
        """
        ...

    def list_fpmm_transactions(
        self,
        condition_id: str | None = None,
        start_ts: UnixTimestamp | None = None,
        end_ts: UnixTimestamp | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order: str | None = None,
        ascending: bool = True,
        transaction_type: str | None = None,
    ) -> list[FpmmTransaction]:
        """List FPMM transactions.

        Args:
            condition_id: Filter by condition id.
            start_ts: Optional start timestamp (unix seconds).
            end_ts: Optional end timestamp (unix seconds).
            limit: Maximum number of rows to return.
            offset: Rows to skip.
            order: Comma-separated list of fields to order by.
            ascending: Sort order (default: True).
            transaction_type: Filter by transaction type.
        """
        ...

    def __repr__(self) -> str: ...

@final
class OrderFilledEvent:
    """Immutable view of an order_filled_event row."""

    @property
    def id(self) -> str: ...
    @property
    def transaction_hash(self) -> str: ...
    @property
    def timestamp(self) -> UnixTimestamp: ...
    @property
    def order_hash(self) -> str: ...
    @property
    def maker(self) -> str: ...
    @property
    def taker(self) -> str: ...
    @property
    def maker_asset_id(self) -> str: ...
    @property
    def taker_asset_id(self) -> str: ...
    @property
    def maker_amount_filled(self) -> str: ...
    @property
    def taker_amount_filled(self) -> str: ...
    @property
    def fee(self) -> str: ...
    def __repr__(self) -> str: ...

@final
class FpmmTransaction:
    """Immutable view of an fpmm_transaction row."""

    @property
    def id(self) -> str: ...
    @property
    def timestamp(self) -> UnixTimestamp: ...
    @property
    def condition_id(self) -> str: ...
    @property
    def user(self) -> str: ...
    @property
    def transaction_type(self) -> str: ...
    @property
    def trade_amount(self) -> str: ...
    @property
    def fee_amount(self) -> str: ...
    @property
    def outcome_index(self) -> int: ...
    @property
    def outcome_tokens_amount(self) -> str: ...
    def __repr__(self) -> str: ...

@final
class OffChain:
    """Off-chain data provider."""

    def list_markets(
        self,
        limit: int | None = None,
        offset: int | None = None,
        order: str | None = None,
        ascending: bool | None = None,
        id: list[int] | None = None,
        slug: list[str] | None = None,
        clob_token_ids: list[str] | None = None,
        condition_ids: list[str] | None = None,
        market_maker_address: list[str] | None = None,
        liquidity_num_min: Decimal | int | str | None = None,
        liquidity_num_max: Decimal | int | str | None = None,
        volume_num_min: Decimal | int | str | None = None,
        volume_num_max: Decimal | int | str | None = None,
        start_date_min: str | None = None,
        start_date_max: str | None = None,
        end_date_min: str | None = None,
        end_date_max: str | None = None,
        tag_id: int | None = None,
        related_tags: bool | None = None,
        cyom: bool | None = None,
        uma_resolution_status: str | None = None,
        game_id: str | None = None,
        sports_market_types: list[str] | None = None,
        rewards_min_size: Decimal | int | str | None = None,
        question_ids: list[str] | None = None,
        include_tag: bool | None = None,
        closed: bool | None = None,
    ) -> list[Market]:
        """List markets with Polymarket-style query parameters.

        Args:
            limit: Maximum number of rows to return.
            offset: Rows to skip for pagination.
            order: Comma-separated list of fields to order by (e.g., "volume_num", "id").
            ascending: Sort order (default: False for descending).
            id: Filter by market IDs.
            slug: Filter by market slugs.
            clob_token_ids: Filter by CLOB token IDs.
            condition_ids: Filter by condition IDs.
            market_maker_address: Filter by market maker addresses.
            liquidity_num_min: Minimum liquidity filter.
            liquidity_num_max: Maximum liquidity filter.
            volume_num_min: Minimum volume filter.
            volume_num_max: Maximum volume filter.
            start_date_min: Minimum start date (ISO 8601 string).
            start_date_max: Maximum start date (ISO 8601 string).
            end_date_min: Minimum end date (ISO 8601 string).
            end_date_max: Maximum end date (ISO 8601 string).
            tag_id: Filter by tag ID (searches raw_data.tags array).
            related_tags: Not implemented; raises error if provided.
            cyom: Filter by "Create Your Own Market" flag.
            uma_resolution_status: Filter by UMA resolution status.
            game_id: Filter by game ID (sports markets).
            sports_market_types: Filter by sports market types.
            rewards_min_size: Minimum rewards size filter.
            question_ids: Filter by question IDs.
            include_tag: If True, include tags in response; if False (default), strip tags.
            closed: Filter by closed status.

        Returns:
            List of Market objects with raw_data dictionaries.

        Note:
            related_tags is not implemented as it requires server-side tag relationship data.
        """
        ...

    def get_market(self, market_id: int) -> Market | None:
        """Get a single market by id."""
        ...

    def list_market_tokens(self, market_id: int | None = None) -> list[MarketToken]:
        """List market tokens, optionally filtered by market id."""
        ...

    def __repr__(self) -> str: ...

@final
class Market:
    """Market record backed by raw JSON data."""

    @property
    def raw_data(self) -> JsonObject:
        """Raw market payload from the database."""
        ...

    def __repr__(self) -> str: ...

@final
class MarketToken:
    """Market token record."""

    @property
    def token_id(self) -> str: ...
    @property
    def market_id(self) -> int: ...
    @property
    def outcome(self) -> str | None: ...
    @property
    def outcome_index(self) -> int: ...
    @property
    def outcome_price(self) -> str | None: ...
    def __repr__(self) -> str: ...

@final
class Trading:
    """Trading data provider (timeseries)."""

    def get_timeseries(
        self,
        token_id: str,
        start_ts: UnixTimestamp | None = None,
        end_ts: UnixTimestamp | None = None,
    ) -> Timeseries:
        """Get timeseries data for a token."""
        ...

    def __repr__(self) -> str: ...

@final
class Timeseries:
    """Timeseries response containing history points."""

    @property
    def history(self) -> list[HistoryPoint]:
        """Ordered list of history points."""
        ...

    def __repr__(self) -> str: ...

@final
class HistoryPoint:
    """Single timeseries point."""

    @property
    def t(self) -> UnixTimestamp:
        """Timestamp in unix seconds."""
        ...

    @property
    def p(self) -> Decimal:
        """Price at timestamp (Decimal)."""
        ...

    def __repr__(self) -> str: ...
