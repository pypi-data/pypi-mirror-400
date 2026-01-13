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
Wellbore trajectory survey.

Defines survey metadata and stations comprising the actual or planned path of the wellbore.
"""
import math
from dataclasses import dataclass, field
from typing import List, Optional, Protocol, Sequence, Union

from dataclasses_json import config
from strenum import StrEnum

from ...datamodels.DataModel import DataModel
from ...datamodels.wells.Station import Station


class DeviationSurveyUsageEnum(StrEnum):
    """Whether a deviation survey is a plan or an actual run."""
    Plan = 'Plan'
    Actual = 'Actual'


class AzimuthReferenceEnum(StrEnum):
    """Reference for azimuth readings (true, magnetic, grid)."""
    Unknown = 'Unknown'
    TrueNorth = 'TrueNorth'
    MagneticNorth = 'MagneticNorth'
    GridNorth = 'GridNorth'


@dataclass
class Survey(DataModel):
    """
    A well deviation survey
    """
    description: Optional[str] = None
    azimuth_reference: Optional[AzimuthReferenceEnum] = AzimuthReferenceEnum.Unknown
    azimuth_offset: Optional[float] = 0
    usage: Optional[DeviationSurveyUsageEnum] = DeviationSurveyUsageEnum.Actual
    is_default: Optional[bool] = False
    stations: list[Station] = field(default_factory=list[Station])
    landing_md: Optional[float] = field(default=None, metadata=config(field_name="LandingMD"))

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, Survey):
            DataModel.merge_lists(self.stations, source.stations)

    @property
    def valid_stations(self) -> List[Station]:
        valid_stations = [s for s in self.stations if s.valid]
        return valid_stations
    
    def compute_landing_md(self) -> Optional[float]:
        """
        Compute MD at which the well is considered landed.

        Landing is defined as the first station (measured depth order) whose inclination is
        >= 88 degrees (approaching horizontal). If raw inclination data are missing (e.g. a
        position log giving only coordinates), we synthesize inclination/azimuth using
        coordinate deltas between stations and retry.

        Returns
        -------
        Optional[float]
            The MD at landing, or None if it can't be determined.
        """
        stations = self.valid_stations
        if not stations:
            return None

        # First try to use raw Incl information if it is available
        idx = _find_landing_index(stations)
        if idx is not None:
            return stations[idx].md

        # Could be a 'position log', in which case we'll have to synthesize incl information
        derivs = _symmetric_station_derivatives(stations)
        synth = _synthesize_incl_azi(derivs)
        idx2 = _find_landing_index(synth)
        if idx2 is not None:
            return stations[idx2].md
        return None

    def find_md(self, tvd: float, extrapolate: bool = False) -> Union[float, None]:
        # Search for the MD corresponding to the provided TVD in the monotonic portion of the wellbore
        try:
            stations = self.stations
            if len(stations) == 0:
                return tvd # Treat as vertical straight hole where md == tvd
            station_first = stations[0]
            station_last = stations[-1]
            if len(stations) == 1:
                if station_first.tvd == 0 and station_first.md == 0:
                    return tvd # Treat as vertical straight hole where md == tvd
            if tvd == station_last.tvd:
                return station_last.md
            for n in range(len(stations) - 1):
                s1 = stations[n]
                s2 = stations[n + 1]
                if s1.tvd is None or s2.tvd is None:
                    continue
                if s2.tvd <= s1.tvd:
                    return None     # We have reached the non-monotonic portion of the well bore so give up.

                if s1.tvd <= tvd < s2.tvd:
                    dtvd = s2.tvd - s1.tvd
                    dmd = s2.md - s1.md
                    md = s1.md + dmd * (tvd - s1.tvd) / dtvd
                    return md
            return None
        except Exception as err:
            return None

        # return tvd

    def find_tvd(self, md: float) -> Union[float, None]:
        """
        Search for the TVD corresponding to the provided MD
        
        :param md: MD to search for
        :return: TVD for the provided MD
        """
        try:
            stations = self.stations
            if len(stations) == 0:
                return md # Treat as vertical straight hole where md == tvd
            station_first = stations[0]
            station_last = stations[-1]
            if len(stations) == 1:
                if station_first.tvd == 0 and station_first.md == 0:
                    return md # Treat as vertical straight hole where md == tvd
            if md < station_first.md or md > station_last.md:
                return None
            if md == station_last.md:
                return station_last.tvd
            for n in range(len(stations) - 1):
                s1 = stations[n]
                s2 = stations[n + 1]
                if s1.md <= md < s2.md:
                    if s1.tvd is None or s2.tvd is None:
                        return None
                    dmd = s2.md - s1.md
                    dtvd = s2.tvd - s1.tvd
                    tvd = s1.tvd + dtvd * (md - s1.md) / dmd
                    return tvd
            return None
        except Exception as err:
            return None

class InclAzi(Protocol):
    inclination: Optional[float]
    azimuth: Optional[float]

class InclAziImpl:
    def __init__(self, inclination: Optional[float], azimuth: Optional[float]):
        self.inclination = inclination
        self.azimuth = azimuth

def _find_landing_index(
    stations: Sequence[Optional[InclAzi]],
) -> Optional[int]:
    """
    Return index of first station with inclination >= 88 degrees.

    Parameters
    ----------
    stations : list[InclAzi]
        Original station objects.
    """
    min_landing_incl = 88.0
    for i, st in enumerate(stations):
        if st is None:
            continue
        incl = st.inclination
        if incl is not None and incl >= min_landing_incl:
            return i
    return None


def _compute_station_direction_vectors(
    stations: List[Station],
) -> List[Optional[tuple[float, float, float]]]:
    """
    Compute approximate direction vectors (dx, dy, dtvd) between adjacent stations.

    Returns a list sized len(stations)-1 for segment derivatives using coordinate deltas.
    If delta coordinates or tvd are missing, entry is None.
    """
    segs: List[Optional[tuple[float, float, float]]] = []
    n = len(stations)
    for i in range(1, n):
        s0 = stations[i-1]
        s1 = stations[i]
        if (s0.delta_x is None or s0.delta_y is None or s0.tvd is None or
            s1.delta_x is None or s1.delta_y is None or s1.tvd is None):
            segs.append(None)
            continue
        dx = s1.delta_x - s0.delta_x
        dy = s1.delta_y - s0.delta_y
        dtvd = s1.tvd - s0.tvd
        segs.append((dx, dy, dtvd))
    return segs


def _symmetric_station_derivatives(stations: List[Station]) -> List[Optional[tuple[float, float, float]]]:
    segs = _compute_station_direction_vectors(stations)
    n = len(stations)
    derivs: List[Optional[tuple[float, float, float]]] = [None] * n
    for i in range(n):
        back = segs[i-1] if i-1 >= 0 and i-1 < len(segs) else None
        fwd = segs[i] if i < len(segs) else None
        if back and fwd:
            derivs[i] = ((back[0]+fwd[0]) * 0.5, (back[1]+fwd[1]) * 0.5, (back[2]+fwd[2]) * 0.5)
        elif back:
            derivs[i] = back
        elif fwd:
            derivs[i] = fwd
    return derivs


def _synthesize_incl_azi(
    derivs: List[tuple[float, float, float] | None],
) -> List[Optional[InclAzi]]:
    """
    Synthesize inclination & azimuth from coordinate derivatives.

    Returns list parallel to derivs containing InclAzi or None. Azimuth is
    computed from dx, dy using math.atan2(dx, dy) or standard bearing: atan2(dx, dy) * 180/pi.
    Inclination derived from vertical vs horizontal components
    """
    out: List[Optional[InclAzi]] = []
    for d in derivs:
        if not d:
            out.append(None)
            continue
        dx, dy, dz = d
        # Horizontal magnitude
        dxy = (dx**2 + dy**2) ** 0.5
        azi_rad = math.atan2(dx, dy)  # yields angle from north (y) clockwise to east (x)
        azi_deg = (azi_rad * 180.0 / math.pi) % 360.0
        if dxy == 0 and dz == 0:
            incl_deg = 0.0
        else:
            theta = math.atan2(dz, dxy)  # angle above horizontal complement to inclination definition
            incl_deg = 90.0 - (theta * 180.0 / math.pi)
        out.append(InclAziImpl(incl_deg, azi_deg))
    return out
