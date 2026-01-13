import math
from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, config


@dataclass
class HorizonDepths(DataClassJsonMixin):
    """A set of depths of horizons for a pick on a geosteering interpretation"""

    #: Ids of horizons on the interpretation
    horizon_ids: List[int] = field(default_factory=list[int], metadata=config(field_name="HorizonIds"))

    #: Tvd depths for each horizon in the HorizonIds array
    tvds: List[Optional[float]] = field(default_factory=list[Optional[float]], metadata=config(field_name="Tvds"))

    #: Tvt depths (measured from wellbore to horizon) for each horizon in the HorizonIds array
    tvts: List[Optional[float]] = field(default_factory=list[Optional[float]], metadata=config(field_name="Tvts"))

    #: Elevations for each horizon in the HorizonIds array
    elevations: List[Optional[float]] = field(default_factory=list[Optional[float]], metadata=config(field_name="Elevations"))
