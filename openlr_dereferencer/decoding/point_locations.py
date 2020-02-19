"Decoding logic for point (along line, ...) locations"

from typing import NamedTuple, List
from openlr import Coordinates, PointAlongLineLocation
from ..maps import MapReader, path_length
from ..maps.abstract import Line
from ..maps.wgs84 import point_along_path
from .line_decoding import dereference_path
from . import LRDecodeError

class PointAlongLine(NamedTuple):
    """A dereferenced point along line location.

    Contains the coordinates as well as the road on which it was located."""
    line: Line
    meters_into: float

    def location(self) -> Coordinates:
        "Returns the actual geo coordinate"
        return point_along_path(list(self.line.coordinates()), self.meters_into)

def point_along_linelocation(path: List[Line], length: float) -> PointAlongLine:
    """Steps `length` meters into the `path` and returns the and the Line + offset in meters.

    If the path is exhausted (`length` longer than `path`), raises an LRDecodeError."""
    leftover_length = length
    for road in path:
        if leftover_length > road.length:
            leftover_length -= road.length
        else:
            return PointAlongLine(road, leftover_length)
    raise LRDecodeError("Path length exceeded while projecting point")

def decode_pointalongline(
        reference: PointAlongLineLocation, reader: MapReader, radius: float
    ) -> PointAlongLine:
    "Decodes a point along line location reference into a Coordinates tuple"
    path = dereference_path(reference.points, reader, radius)
    absolute_offset = path_length(path) * reference.poffs
    return point_along_linelocation(path, absolute_offset)