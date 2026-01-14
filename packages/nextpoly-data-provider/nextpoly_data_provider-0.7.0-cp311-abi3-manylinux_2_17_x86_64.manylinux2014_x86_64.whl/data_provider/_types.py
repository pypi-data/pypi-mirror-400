from __future__ import annotations

from decimal import Decimal
from typing import TypeAlias

JsonPrimitive: TypeAlias = str | int | Decimal | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
