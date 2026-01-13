#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.
#  #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
#
#

"""
Helper utilities for datamodels.

Factory helpers and field encoders/decoders used across dataclasses.
"""

import dataclasses as dc
import warnings
from dataclasses import MISSING, dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, cast

from dataclasses_json import config
from marshmallow import fields
from strenum import StrEnum


def iso_to_datetime(value: Union[str, None]) -> Union[datetime, None]:
    """
    Parser for parsing ISO times strings to python datetime
    
    :param value:
    :return:
    """
    if value is None:
        return None
    try:
        date = datetime.fromisoformat(value)
        return date
    except TypeError:
        return None
    except ValueError:
        return None


def date_time_to_iso(value: Union[datetime, None]) -> Union[str, None]:
    """
    Converts python datetime to ISO string

    :param value:
    :return:
    """
    if value is None:
        return None
    return value.isoformat()


isodateFieldConfig = config(
    encoder=date_time_to_iso,
    decoder=iso_to_datetime,
    mm_field=fields.DateTime(format='iso')
)
isodateFieldConfigHide = {
    "encoder": lambda dt: dt.isoformat(),
    "decoder": lambda dt_str: datetime.fromisoformat(dt_str),
}
isodateOptional = field(default=None, metadata=isodateFieldConfig)


def MakeIsodateOptionalField():
    return field(default=None, metadata=isodateFieldConfig)



WarnPredicate = Callable[[Any, Any, bool], bool]
T = TypeVar("T")


@dataclass(frozen=True)
class DeprecatedFieldInfo:
    """Metadata describing a deprecated dataclass field."""

    warning: str
    warn_if: Optional[WarnPredicate] = None

    def should_warn(self, value: Any, default_value: Any, *, is_init: bool) -> bool:
        if self.warn_if is not None:
            return self.warn_if(value, default_value, is_init)
        if is_init and default_value is not MISSING:
            return value != default_value
        return value is not None


def deprecated_field(
    *,
    info: DeprecatedFieldInfo,
    metadata: Optional[Dict[str, Any]] = None,
    **field_kwargs: Any,
) -> Any:
    """Create a dataclass field tagged with deprecation metadata."""
    merged_metadata: Dict[str, Any] = dict(metadata or {})
    merged_metadata['deprecated'] = info
    return field(metadata=merged_metadata, **field_kwargs)


def with_field_deprecations(cls: Type[T]) -> Type[T]:
    """Class decorator that wires DeprecationWarnings for fields tagged via deprecated_field."""
    if not dc.is_dataclass(cls):
        raise TypeError("with_field_deprecations expects a dataclass")

    deprecated_map: Dict[str, DeprecatedFieldInfo] = {}
    defaults: Dict[str, Any] = {}

    for f in dc.fields(cls):
        info = f.metadata.get('deprecated')
        if isinstance(info, DeprecatedFieldInfo):
            deprecated_map[f.name] = info
            if f.default is not MISSING:
                defaults[f.name] = f.default
            elif f.default_factory is not MISSING:  # type: ignore[attr-defined]
                try:
                    defaults[f.name] = f.default_factory()
                except TypeError:
                    defaults[f.name] = MISSING
            else:
                defaults[f.name] = MISSING

    if not deprecated_map:
        return cls

    original_post_init = getattr(cls, '__post_init__', None)

    def __post_init__(self, *args, **kwargs):
        if original_post_init is not None:
            original_post_init(self, *args, **kwargs)
        for name, info in deprecated_map.items():
            value = getattr(self, name, None)
            default_value = defaults[name]
            if info.should_warn(value, default_value, is_init=True):
                warnings.warn(info.warning, DeprecationWarning, stacklevel=2)
        setattr(self, '_deprecated_fields_ready', True)

    setattr(cls, '__post_init__', __post_init__)

    original_setattr = cast(Callable[[Any, str, Any], None], cls.__setattr__)

    def __setattr__(self, name, value):
        if name in deprecated_map and getattr(self, '_deprecated_fields_ready', False):
            info = deprecated_map[name]
            default_value = defaults[name]
            if info.should_warn(value, default_value, is_init=False):
                warnings.warn(info.warning, DeprecationWarning, stacklevel=2)
        original_setattr(self, name, value)

    setattr(cls, '__setattr__', __setattr__)

    return cls





