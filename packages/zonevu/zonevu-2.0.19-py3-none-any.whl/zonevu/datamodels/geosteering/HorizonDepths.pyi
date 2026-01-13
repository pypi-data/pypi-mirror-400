from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, config

@dataclass
class HorizonDepths(DataClassJsonMixin):
    horizon_ids: list[int] = field(default_factory=list[int], metadata=config(field_name='HorizonIds'))
    tvds: list[float | None] = field(default_factory=list[float | None], metadata=config(field_name='Tvds'))
    tvts: list[float | None] = field(default_factory=list[float | None], metadata=config(field_name='Tvts'))
    elevations: list[float | None] = field(default_factory=list[float | None], metadata=config(field_name='Elevations'))
