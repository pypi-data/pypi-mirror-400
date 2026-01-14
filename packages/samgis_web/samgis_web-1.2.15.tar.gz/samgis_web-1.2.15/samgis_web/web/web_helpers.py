"""web helper functions"""
from typing import Dict

from xyzservices import providers, TileProvider
from samgis_core import app_logger
from samgis_web.io_package.coordinates_pixel_conversion import get_latlng_to_pixel_coordinates
from samgis_web.utilities.constants import COMPLETE_URL_TILES_MAPBOX, COMPLETE_URL_TILES_NEXTZEN
from samgis_web.utilities.type_hints import ApiRequestBody, XYZTerrainProvidersNames, XYZDefaultProvidersNames


def get_parsed_bbox_points_with_dictlist_prompt(request_input: ApiRequestBody | str) -> Dict:
    """
    Parse the raw input request into bbox, prompt and zoom.
    If the request is a string this function use 'model_validate_json()' method from instance Pydantic BaseModel.

    Args:
        request_input: input dict

    Returns:
        dict with bounding box, prompt and zoom

    """
    app_logger.info(f"try to parsing input request: {type(request_input)}, {request_input}...")
    if isinstance(request_input, str):
        app_logger.info(f"string/json input, parsing it to {type(ApiRequestBody)}...")
        request_input = ApiRequestBody.model_validate_json(request_input)
        app_logger.info(f"parsed input, now of type {type(request_input)}...")

    bbox = request_input.bbox
    app_logger.debug(f"request bbox: {type(bbox)}, value:{bbox}.")
    ne = bbox.ne
    sw = bbox.sw
    app_logger.debug(f"request ne: {type(ne)}, value:{ne}.")
    app_logger.debug(f"request sw: {type(sw)}, value:{sw}.")
    ne_latlng = [float(ne.lat), float(ne.lng)]
    sw_latlng = [float(sw.lat), float(sw.lng)]
    new_zoom = int(request_input.zoom)
    new_prompt_list = _get_parsed_prompt_list(ne, sw, new_zoom, request_input.prompt)

    app_logger.debug(f"bbox => {bbox}.")
    app_logger.debug(f'request_input-prompt updated => {new_prompt_list}.')

    app_logger.info("unpacking elaborated request...")
    return {
        "bbox": [ne_latlng, sw_latlng],
        "prompt": new_prompt_list,
        "zoom": new_zoom,
        "source": get_source_tile(request_input.source_type),
        "source_name": get_source_name(request_input.source_type)
    }


def _get_parsed_prompt_list(bbox_ne, bbox_sw, zoom, prompt_list):
    new_prompt_list = []
    for prompt in prompt_list:
        app_logger.debug(f"current prompt: {type(prompt)}, value:{prompt}.")
        new_prompt = {"type": prompt.type.value}
        if prompt.type == "point":
            new_prompt_data = _get_new_prompt_data_point(bbox_ne, bbox_sw, prompt, zoom)
            new_prompt["label"] = prompt.label.value
        elif prompt.type == "rectangle":
            new_prompt_data = _get_new_prompt_data_rectangle(bbox_ne, bbox_sw, prompt, zoom)
        else:
            msg = "Valid prompt type: 'point' or 'rectangle', not '{}'. Check ApiRequestBody parsing/validation."
            raise TypeError(msg.format(prompt.type))
        app_logger.debug(f"new_prompt_data: {type(new_prompt_data)}, value:{new_prompt_data}.")
        new_prompt["data"] = new_prompt_data
        new_prompt_list.append(new_prompt)
    return new_prompt_list


def _get_new_prompt_data_point(bbox_ne, bbox_sw, prompt, zoom):
    current_point = get_latlng_to_pixel_coordinates(bbox_ne, bbox_sw, prompt.data, zoom, prompt.type)
    app_logger.debug(f"current prompt: {type(current_point)}, value:{current_point}, label: {prompt.label}.")
    return [current_point['x'], current_point['y']]


def _get_new_prompt_data_rectangle(bbox_ne, bbox_sw, prompt, zoom):
    current_point_ne = get_latlng_to_pixel_coordinates(bbox_ne, bbox_sw, prompt.data.ne, zoom, prompt.type)
    app_logger.debug(
        f"rectangle:: current_point_ne prompt: {type(current_point_ne)}, value:{current_point_ne}.")
    current_point_sw = get_latlng_to_pixel_coordinates(bbox_ne, bbox_sw, prompt.data.sw, zoom, prompt.type)
    app_logger.debug(
        f"rectangle:: current_point_sw prompt: {type(current_point_sw)}, value:{current_point_sw}.")
    # correct order for rectangle prompt
    return [
        current_point_sw["x"],
        current_point_ne["y"],
        current_point_ne["x"],
        current_point_sw["y"]
    ]


mapbox_terrain_rgb = TileProvider(
    name=XYZTerrainProvidersNames.MAPBOX_TERRAIN_TILES_NAME,
    url=COMPLETE_URL_TILES_MAPBOX,
    attribution=""
)
nextzen_terrain_rgb = TileProvider(
    name=XYZTerrainProvidersNames.NEXTZEN_TERRAIN_TILES_NAME,
    url=COMPLETE_URL_TILES_NEXTZEN,
    attribution=""
)


def get_source_tile(source_type: str) -> TileProvider:
    """
    Return `TileProvider` instance based on the name query.
    See examples in xyzservices.lib.py, query_name() for details.

    Args:
        source_type: source name to use in query_name()

    Returns:
        a TileProvider instance
    """
    try:
        match source_type.lower():
            case XYZDefaultProvidersNames.DEFAULT_TILES_NAME_SHORT:
                return providers.query_name(XYZDefaultProvidersNames.DEFAULT_TILES_NAME)
            case XYZTerrainProvidersNames.MAPBOX_TERRAIN_TILES_NAME:
                app_logger.info(f"mapbox_terrain_rgb:{mapbox_terrain_rgb.name}.")
                return mapbox_terrain_rgb
            case XYZTerrainProvidersNames.NEXTZEN_TERRAIN_TILES_NAME:
                app_logger.info(f"nextzen_terrain_rgb:{nextzen_terrain_rgb.name}.")
                return nextzen_terrain_rgb
            case _:
                return providers.query_name(source_type)
    except ValueError as ve:
        from pydantic_core import ValidationError

        app_logger.error(f"ve:{ve}.")
        ve_title = str(ve)
        raise ValidationError.from_exception_data(title=ve_title, line_errors=[])


get_url_tile = get_source_tile


def check_source_type_is_terrain(source: str | TileProvider) -> bool:
    """Check if the given source string or TileProvider is a terrain one, see

     - Digital Elevation Model ([DEM](https://www.usgs.gov/faqs/what-a-digital-elevation-model-dem))
     - Digital Terrain Model ([DTM](https://www.usgs.gov/news/how-create-quality-digital-terrain-model))

     Args:
        source: source string or TileProvider

     Returns:
        a boolean (True if is a DEM/DTM/terrain TileProvider, False otherwise)

    """
    return isinstance(source, TileProvider) and source.name in list(XYZTerrainProvidersNames)


def get_source_name(source: str | TileProvider) -> str | bool:
    """
    Return `TileProvider.name` string based on the output from query_name().
    See examples in xyzservices.lib.py, query_name() for details.

    Args:
        source: source string or TileProvider

    Returns:
        a string name representing the input TileProvider or source string

    """
    try:
        match source.lower():
            case XYZDefaultProvidersNames.DEFAULT_TILES_NAME_SHORT:
                source_output = providers.query_name(XYZDefaultProvidersNames.DEFAULT_TILES_NAME)
            case _:
                source_output = providers.query_name(source)
        if isinstance(source_output, str):
            return source_output
        try:
            source_dict = dict(source_output)
            app_logger.info(f"source_dict:{type(source_dict)}, {'name' in source_dict}, source_dict:{source_dict}.")
            return source_dict["name"]
        except KeyError as ke:
            app_logger.error(f"ke:{ke}.")
    except ValueError as ve:
        app_logger.info(f"source name::{source}, ve:{ve}.")
    app_logger.info(f"source name::{source}.")

    return False
