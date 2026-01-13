from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from zonevu.datamodels.geospatial.Coordinate import Coordinate as Coordinate
from zonevu.datamodels.geospatial.GeoLocation import GeoLocation as GeoLocation

@dataclass
class Position(DataClassJsonMixin):
    dataclass_json_config = ...
    coordinate: Coordinate = ...
    loc: GeoLocation = ...
