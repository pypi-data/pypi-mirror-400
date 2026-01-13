from _typeshed import Incomplete
from dataclasses import dataclass
from datetime import datetime
from strenum import StrEnum as StrEnum
from typing import Any, Callable, TypeVar

def iso_to_datetime(value: str | None) -> datetime | None: ...
def date_time_to_iso(value: datetime | None) -> str | None: ...

isodateFieldConfig: Incomplete
isodateFieldConfigHide: Incomplete
isodateOptional: Incomplete

def MakeIsodateOptionalField(): ...
WarnPredicate = Callable[[Any, Any, bool], bool]
T = TypeVar('T')

@dataclass(frozen=True)
class DeprecatedFieldInfo:
    warning: str
    warn_if: WarnPredicate | None = ...
    def should_warn(self, value: Any, default_value: Any, *, is_init: bool) -> bool: ...

def deprecated_field(*, info: DeprecatedFieldInfo, metadata: dict[str, Any] | None = None, **field_kwargs: Any) -> Any: ...
def with_field_deprecations(cls) -> type[T]: ...
