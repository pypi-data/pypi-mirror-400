#  Copyright (c) 2025 Ubiterra Corporation. All rights reserved.
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
A 3D coordinate (x, y, z) with its geographic CRS
"""

from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
from zonevu.datamodels.geospatial.Coordinate import Coordinate
from zonevu.datamodels.geospatial.GeoLocation import GeoLocation

@dataclass
class Position(DataClassJsonMixin):
    """3D coordinate with its geographic location."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]

    coordinate: Coordinate = None
    loc: GeoLocation = None
