"""custom type hints"""
from enum import IntEnum, Enum
from typing import TypedDict

from affine import Affine
from numpy import ndarray
from pydantic import BaseModel

from samgis_core.utilities.type_hints import StrEnum


tuple_ndarray_transform = tuple[ndarray, Affine]


class WorldFile(StrEnum):
    """Default xyz provider names"""
    pgw = "pgw"
    tfw = "tfw"


class XYZDefaultProvidersNames(StrEnum):
    """Default xyz provider names"""
    DEFAULT_TILES_NAME_SHORT = "openstreetmap"
    DEFAULT_TILES_NAME = "openstreetmap.mapnik"


class XYZTerrainProvidersNames(StrEnum):
    """Custom xyz provider names for digital elevation models"""
    MAPBOX_TERRAIN_TILES_NAME = "mapbox.terrain-rgb"
    NEXTZEN_TERRAIN_TILES_NAME = "nextzen.terrarium"


class LatLngDict(BaseModel):
    """Generic geographic latitude-longitude type"""
    lat: float
    lng: float


class ContentTypes(str, Enum):
    """Segment Anything: validation point prompt type"""
    APPLICATION_JSON = "application/json"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"


class PromptPointType(str, Enum):
    """Segment Anything: validation point prompt type"""
    point = "point"


class PromptRectangleType(str, Enum):
    """Segment Anything: validation rectangle prompt type"""
    rectangle = "rectangle"


class PromptLabel(IntEnum):
    """Valid prompt label type"""
    EXCLUDE = 0
    INCLUDE = 1


class ImagePixelCoordinates(TypedDict):
    """Image pixel coordinates type"""
    x: int
    y: int


class RawBBox(BaseModel):
    """Input lambda bbox request type (not yet parsed)"""
    ne: LatLngDict
    sw: LatLngDict


class RawPromptPoint(BaseModel):
    """Input lambda prompt request of type 'PromptPointType' - point (not yet parsed)"""
    type: PromptPointType
    data: LatLngDict
    label: PromptLabel


class RawPromptRectangle(BaseModel):
    """Input lambda prompt request of type 'PromptRectangleType' - rectangle (not yet parsed)"""
    type: PromptRectangleType
    data: RawBBox

    def get_type_str(self):
        return self.type


class ApiRequestBody(BaseModel):
    """Input request validator type (not yet parsed)"""
    id: str = ""
    bbox: RawBBox
    prompt: list[RawPromptPoint | RawPromptRectangle]
    zoom: int | float
    source_type: str = "OpenStreetMap.Mapnik"
    debug: bool = False


class StringPromptApiRequestBody(BaseModel):
    """Input lambda request validator type (not yet parsed)"""
    id: str = ""
    bbox: RawBBox
    string_prompt: str
    zoom: int | float
    source_type: str = "OpenStreetMap.Mapnik"
    debug: bool = False


class ApiResponseBodyFailure(BaseModel):
    """SamGIS API Response; handle only case of failure"""
    duration_run: float
    message: str
    request_id: str


class ApiResponseBodySuccess(ApiResponseBodyFailure):
    """SamGIS API Response; handle both case of success and failure"""
    n_predictions: int
    geojson: str
    n_shapes_geojson: int
