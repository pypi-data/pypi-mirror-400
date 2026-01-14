"""Project constants"""
import os

INPUT_CRS_STRING = "EPSG:4326"
OUTPUT_CRS_STRING = "EPSG:3857"
DRIVER_RASTERIO_GTIFF = "GTiff"
ROOT = "/tmp"
CUSTOM_RESPONSE_MESSAGES = {
    200: "ok",
    400: "Bad Request",
    422: "Missing required parameter",
    500: "Internal server error"
}
TILE_SIZE = 256
EARTH_EQUATORIAL_RADIUS = 6378137.0
WKT_3857 = 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,'
WKT_3857 += 'AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],'
WKT_3857 += 'UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],'
WKT_3857 += 'PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],'
WKT_3857 += 'PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],'
WKT_3857 += 'AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
WKT_3857 += '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]'
SERVICE_NAME = "sam-gis"
DEFAULT_LOG_LEVEL = 'INFO'
RETRY_DOWNLOAD = 3
TIMEOUT_DOWNLOAD = 60
CALLBACK_INTERVAL_DOWNLOAD = 0.05
BOOL_USE_CACHE = True
N_WAIT = 0
N_MAX_RETRIES = 2
N_CONNECTION = 2
ZOOM_AUTO = "auto"
DEFAULT_URL_TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
DOMAIN_URL_TILES_MAPBOX = "api.mapbox.com"
RELATIVE_URL_TILES_MAPBOX = "v/mapbox.terrain-rgb/{zoom}/{x}/{y}{@2x}.pngraw?access_token={TOKEN}"
COMPLETE_URL_TILES_MAPBOX = f"https://{DOMAIN_URL_TILES_MAPBOX}/{RELATIVE_URL_TILES_MAPBOX}"
# https://s3.amazonaws.com/elevation-tiles-prod/terrarium/13/1308/3167.png
DOMAIN_URL_TILES_NEXTZEN = "s3.amazonaws.com"
RELATIVE_URL_TILES_NEXTZEN = "elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"  # "terrarium/{z}/{x}/{y}.png"
COMPLETE_URL_TILES_NEXTZEN = f"https://{DOMAIN_URL_TILES_NEXTZEN}/{RELATIVE_URL_TILES_NEXTZEN}"
CHANNEL_EXAGGERATIONS_LIST = [2.5, 1.1, 2.0]
SLOPE_CELLSIZE = 61
MODEL_NAME = os.getenv("MODEL_NAME", "mobile_sam")
MSG_WRITE_TMP_ON_DISK = "found option to write images and geojson output: "
GRADIO_EXAMPLE_BODY_DICTLIST = {
    "bbox": {
        "ne": {"lat": 39.036252959636606, "lng": 15.040283203125002},
        "sw": {"lat": 38.302869955150044, "lng": 13.634033203125002}
    },
    "prompt": [{"type": "point", "data": {"lat": 38.48542007717153, "lng": 14.921846904165468}, "label": 0}],
    "zoom": 10, "source_type": "OpenStreetMap"
}
GRADIO_EXAMPLE_BODY_STRING_PROMPT = {
    "bbox": {
        "ne": {"lat": 46.17271333276639, "lng": 10.079505443573},
        "sw": {"lat": 46.1677724417049, "lng": 10.068830251693727}
    },
    "string_prompt": "",
    "zoom": 17,
    "source_type": "Esri.WorldImagery"
}
GRADIO_EXAMPLES_TEXT_LIST = [
    """You need to identify the areas with trees in this photogrammetric image. Please output segmentation mask.""",
    """You need to identify the areas with streets in this photogrammetric image. Please output segmentation mask.""",
    """You need to identify the houses in this photogrammetric image. Give me a segmentation mask and explain why.""",
    """Describe what do you see in this image.""",
]
GRADIO_MARKDOWN = """# [LISA](https://github.com/dvlab-research/LISA) + [SamGIS](https://github.com/trincadev/samgis-be) on Zero GPU!

This project aims to permit use of [LISA](https://github.com/dvlab-research/LISA) (Reasoning Segmentation via Large Language Model) applied to geospatial data thanks to [SamGIS](https://github.com/trincadev/samgis-be). In this space I adapted LISA to HuggingFace [lisa-on-cuda](https://huggingface.co/spaces/aletrn/lisa-on-cuda) ZeroGPU space.

This [home page project](https://huggingface.co/spaces/aletrn/samgis-lisa-on-zero) is a plane Gradio interface that take a json in input to translate it to a geojson. More information about these API implementation [here](
https://aletrn-samgis-lisa-on-zero.hf.space/docs). On this [blog page](https://trinca.tornidor.com/projects/lisa-adapted-for-samgis) you can find more details, including some request and response examples with the geojson map representations.

You can also find the alternative map interface [here](https://aletrn-samgis-lisa-on-zero.hf.space/lisa/) useful to create on the fly the payload requests and to represent the geojson response.
"""
