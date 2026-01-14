"""helpers for computer vision duties"""
from pathlib import Path

import numpy as np
from affine import Affine
from numpy import ndarray, bitwise_not
from rasterio import open as rasterio_open

from samgis_core import app_logger
from samgis_web.utilities.type_hints import XYZTerrainProvidersNames, WorldFile
from samgis_web.utilities.constants import OUTPUT_CRS_STRING, MSG_WRITE_TMP_ON_DISK


def get_nextzen_terrain_rgb_formula(red: ndarray, green: ndarray, blue: ndarray, casted_type = np.uint16) -> ndarray:
    """
    Compute a 32-bits 2d digital elevation model from a nextzen 'terrarium' (terrain-rgb) raster.
    'Terrarium' format PNG tiles contain raw elevation data in meters, in Mercator projection (EPSG:3857).
    All values are positive with a 32,768 offset, split into the red, green, and blue channels,
    with 16 bits of integer and 8 bits of fraction. To decode:

        (red * 256 + green + blue / 256) - 32768

    More details on https://www.mapzen.com/blog/elevation/

    Args:
        red: red-valued channel image array
        green: green-valued channel image array
        blue: blue-valued channel image array
        casted_type: numpy type needed to avoid OverflowError

    Returns:
        ndarray: nextzen 'terrarium' 2d digital elevation model raster at 32 bits

    """
    try:
        return (red * 256 + green + blue / 256) - 32768
    except OverflowError:
        red1 = red.astype(casted_type)
        green1 = green.astype(casted_type)
        blue1 = blue.astype(casted_type)
        output = (red1 * 256 + green1 + blue1 / 256) - 32768
        return output


def get_mapbox__terrain_rgb_formula(red: ndarray, green: ndarray, blue: ndarray, casted_type = np.uint16) -> ndarray:
    """
    Mapbox Terrain-DEM v1 is a Mapbox-provided raster tileset is a global elevation layer.
    This tileset contains raw height values in meters in the Red, Green, and Blue channels of PNG tiles that can be
    decoded to raw heights in meters.
    Mapbox Terrain-DEM is an optimized version of the Mapbox Terrain-RGB v1 tileset, with some updated data and some
    compression to reduce precision at lower zoom levels, making smaller, faster-loading tiles.
    You can use Terrain-DEM for a wide variety of applications, both visual and analytical, from styling terrain slope
    and hillshades to generating 3D terrain meshes for video games.

    # Data sources and updates
    Elevation data is not improved on a set schedule and is updated when and where it becomes available.

    # Attribution
    When using this tileset publicly in a design or application you must provide
    [proper attribution](https://docs.mapbox.com/help/dive-deeper/attribution/).

    # Terrain-RGB tiles
    The Mapbox Terrain-DEM tileset contains Terrain-RGB tiles. Terrain-RGB tiles include elevation data that is encoded
    using each color channel as a position in a base-256 numbering system. This approach allows for 16,777,216 unique
    values which can be mapped to 0.1 meter height increments, enabling vertical precision necessary for cartographic
    and 3D applications.
    To learn how to retrieve a Terrain-RGB tile and decode elevation data from its RGB values, see Mapbox Access
    elevation data guide.

    # Layer Reference
    This tileset contains one layer with raster data.

    - Data up to zoom 15. The data is encoded to the equivalent of zoom 15 at 256 tile resolution
      (and zoom 14 for 512 tiles).
      Any higher zoom levels will not increase the resolution of the data loaded by your application.
    - 0.1 meter height increments. Elevation data is mapped to 0.1 meter height increments, which gives it the vertical
      precision necessary for cartographic and 3D applications.
    - Buffered tiles. Each map tile includes a 1-pixel buffer around the edges to enable tile interpolation in uses
      cases like terrain meshes.

    # Elevation data
    Mapbox Terrain-DEM uses multiple data sources depending on the zoom level and location.
    Different sources often use different vertical datum references, including but not limited to NAVD 88, EGM 96,
    and Ordnance Datum Newlyn.

    Different sources often use different vertical datum references; thus, attempting to normalize Mapbox elevation
    data to a particular geoid or vertical datum may lead to inaccuracies in data.

    After retrieving tiles via one of Mapbox Mobile SDKs or Mapbox GL JS, you can use this equation to decode pixel
    values to height values:

            height = -10000 + ((R * 256 * 256 + G * 256 + B) * 0.1)

    Text from https://docs.mapbox.com/data/tilesets/reference/mapbox-terrain-dem-v1/#elevation-data

        Args:
        red: red-valued channel image array
        green: green-valued channel image array
        blue: blue-valued channel image array
        casted_type: numpy type needed to avoid OverflowError

    Returns:
        ndarray: Mapbox Terrain-DEM 2d digital elevation model raster

    """
    try:
        return ((red * 256 * 256 + green * 256 + blue) * 0.1) - 10000
    except OverflowError:
        red1 = red.astype(casted_type)
        green1 = green.astype(casted_type)
        blue1 = blue.astype(casted_type)
        output = ((red1 * 256 * 256 + green1 * 256 + blue1) * 0.1) - 10000
        return output


providers_terrain_rgb_formulas = {
    # if ever used, we need to test the mapbox formula with data from real mapbox terrain-rgb tiles
    XYZTerrainProvidersNames.MAPBOX_TERRAIN_TILES_NAME: get_mapbox__terrain_rgb_formula,
    XYZTerrainProvidersNames.NEXTZEN_TERRAIN_TILES_NAME: get_nextzen_terrain_rgb_formula
}


def _get_2d_array_from_3d(arr: ndarray) -> ndarray:
    return arr.reshape(arr.shape[0], arr.shape[1])


def _channel_split(arr: ndarray) -> list[ndarray]:
    from numpy import dsplit

    return dsplit(arr, arr.shape[-1])


def get_raster_terrain_rgb_like(arr: ndarray, xyz_provider_name, nan_value_int: int = -12000, casted_type = np.uint16):
    """
    Compute a 32-bits 2d digital elevation model from a terrain-rgb raster.

    Args:
        arr: rgb raster
        xyz_provider_name: xyz provider
        nan_value_int: threshold int value to replace NaN
        casted_type: numpy type needed to avoid OverflowError

    Returns:
        ndarray: 2d digital elevation model raster at 32 bits
    """
    red, green, blue = _channel_split(arr)
    fn = providers_terrain_rgb_formulas[xyz_provider_name]
    dem_rgb = fn(red, green, blue, casted_type=casted_type)
    output = _get_2d_array_from_3d(dem_rgb)
    output[output < nan_value_int] = np.nan
    return output


def get_rgb_prediction_image(raster_cropped: ndarray, slope_cellsize: int, invert_image: bool = True) -> ndarray:
    """
    Return an RGB image from input numpy array
    
    Args:
        raster_cropped: input numpy array
        slope_cellsize: window size to calculate slope and curvature (1st and 2nd degree array derivative)
        invert_image: 

    Returns:
        tuple of str: image filename, image path (with filename)
    """
    from samgis_web.utilities.constants import CHANNEL_EXAGGERATIONS_LIST

    try:
        slope, curvature = get_slope_curvature(raster_cropped, slope_cellsize=slope_cellsize)

        channel0 = raster_cropped
        channel1 = normalize_array_list(
            [raster_cropped, slope, curvature], CHANNEL_EXAGGERATIONS_LIST, title="channel1_normlist")
        channel2 = curvature

        return get_rgb_image(channel0, channel1, channel2, invert_image=invert_image)
    except ValueError as ve_get_rgb_prediction_image:
        msg = f"ve_get_rgb_prediction_image:{ve_get_rgb_prediction_image}."
        app_logger.error(msg)
        raise ve_get_rgb_prediction_image


def get_rgb_image(arr_channel0: ndarray, arr_channel1: ndarray, arr_channel2: ndarray,
                  invert_image: bool = True) -> ndarray:
    """
    Return an RGB image from input R,G,B channel arrays

    Args:
        arr_channel0: channel image 0
        arr_channel1: channel image 1
        arr_channel2: channel image 2
        invert_image: invert the RGB image channel order

    Returns:
        ndarray: RGB image

    """
    try:
        # RED curvature, GREEN slope, BLUE dem, invert_image=True
        if len(arr_channel0.shape) != 2:
            msg = f"arr_size, wrong type:{type(arr_channel0)} or arr_size:{arr_channel0.shape}."
            app_logger.error(msg)
            raise ValueError(msg)
        data_rgb = np.zeros((arr_channel0.shape[0], arr_channel0.shape[1], 3), dtype=np.uint8)
        app_logger.debug(f"arr_container data_rgb, type:{type(data_rgb)}, arr_shape:{data_rgb.shape}.")
        data_rgb[:, :, 0] = normalize_array(
            arr_channel0.astype(float), high=1, norm_type="float", title="RGB:channel0") * 64
        data_rgb[:, :, 1] = normalize_array(
            arr_channel1.astype(float), high=1, norm_type="float", title="RGB:channel1") * 128
        data_rgb[:, :, 2] = normalize_array(
            arr_channel2.astype(float), high=1, norm_type="float", title="RGB:channel2") * 192
        if invert_image:
            app_logger.debug(f"data_rgb:{type(data_rgb)}, {data_rgb.dtype}.")
            data_rgb = bitwise_not(data_rgb)
        return data_rgb
    except ValueError as ve_get_rgb_image:
        msg = f"ve_get_rgb_image:{ve_get_rgb_image}."
        app_logger.error(msg)
        raise ve_get_rgb_image


def get_slope_curvature(dem: ndarray, slope_cellsize: int, title: str = "") -> tuple[ndarray, ndarray]:
    """
    Return a tuple of two numpy arrays representing slope and curvature (1st grade derivative and 2nd grade derivative)

    Args:
        dem: input numpy array
        slope_cellsize: window size to calculate slope and curvature
        title: array name

    Returns:
        tuple of ndarrays: slope image, curvature image

    """

    app_logger.info(f"dem shape:{dem.shape}, slope_cellsize:{slope_cellsize}.")

    try:
        dem = dem.astype(float)
        app_logger.debug("get_slope_curvature:: start")
        slope = calculate_slope(dem, slope_cellsize)
        app_logger.debug("get_slope_curvature:: created slope raster")
        s2c = calculate_slope(slope, slope_cellsize)
        curvature = normalize_array(s2c, norm_type="float", title=f"SC:curvature_{title}")
        app_logger.debug("get_slope_curvature:: created curvature raster")

        return slope, curvature
    except ValueError as ve_get_slope_curvature:
        msg = f"ve_get_slope_curvature:{ve_get_slope_curvature}."
        app_logger.error(msg)
        raise ve_get_slope_curvature


def calculate_slope(dem_array: ndarray, cell_size: int, calctype: str = "degree") -> ndarray:
    """
    Return a numpy array representing slope (1st grade derivative)

    Args:
        dem_array: input numpy array
        cell_size: window size to calculate slope
        calctype: calculus type

    Returns:
        ndarray: slope image

    """

    try:
        gradx, grady = np.gradient(dem_array, cell_size)
        dem_slope = np.sqrt(gradx ** 2 + grady ** 2)
        if calctype == "degree":
            dem_slope = np.degrees(np.arctan(dem_slope))
        app_logger.debug(f"extracted slope with calctype:{calctype}.")
        return dem_slope
    except ValueError as ve_calculate_slope:
        msg = f"ve_calculate_slope:{ve_calculate_slope}."
        app_logger.error(msg)
        raise ve_calculate_slope


def normalize_array(arr: ndarray, high: int = 255, norm_type: str = "float", invert: bool = False, title: str = ""
                    ) -> ndarray:
    """
    Return normalized numpy array between 0 and 'high' value. Default normalization type is int
    
    Args:
        arr: input numpy array
        high: max value to use for normalization
        norm_type: type of normalization: could be 'float' or 'int'
        invert: bool to choose if invert the normalized numpy array
        title: array title name

    Returns:
        ndarray: normalized numpy array

    """
    np.seterr("raise")

    h_min_arr = np.nanmin(arr)
    h_arr_max = np.nanmax(arr)
    try:
        h_diff = h_arr_max - h_min_arr
        app_logger.debug(
            f"normalize_array:: '{title}',h_min_arr:{h_min_arr},h_arr_max:{h_arr_max},h_diff:{h_diff}, dtype:{arr.dtype}.")
    except Exception as e_h_diff:
        app_logger.error(f"e_h_diff:{e_h_diff}.")
        raise ValueError(e_h_diff)

    if check_empty_array(arr, high) or check_empty_array(arr, h_diff):
        msg_ve = "normalize_array::empty array"
        msg_ve = f"{msg_ve} '{title}',h_min_arr:{h_min_arr},h_arr_max:{h_arr_max},h_diff:{h_diff}, dtype:{arr.dtype}."
        app_logger.error(msg_ve)
        raise ValueError(msg_ve)
    try:
        normalized = high * (arr - h_min_arr) / h_diff
        normalized = np.nanmax(normalized) - normalized if invert else normalized
        return normalized.astype(int) if norm_type == "int" else normalized
    except FloatingPointError as fe:
        msg = f"normalize_array::{title}:h_arr_max:{h_arr_max},h_min_arr:{h_min_arr},fe:{fe}."
        app_logger.error(msg)
        raise ValueError(msg)


def normalize_array_list(arr_list: list[ndarray], exaggerations_list: list[float] = None, title: str = "") -> ndarray:
    """
    Return a normalized numpy array from a list of numpy array and an optional list of exaggeration values.
    
    Args:
        arr_list: list of array to use for normalization
        exaggerations_list: list of exaggeration values
        title: array title name

    Returns:
        ndarray: normalized numpy array

    """

    if not arr_list:
        msg = f"input list can't be empty:{arr_list}."
        app_logger.error(msg)
        raise ValueError(msg)
    if exaggerations_list is None:
        exaggerations_list = list(np.ones(len(arr_list)))
    arr_tmp = np.zeros(arr_list[0].shape)
    for a, exaggeration in zip(arr_list, exaggerations_list):
        app_logger.debug(f"normalize_array_list::exaggeration:{exaggeration}.")
        arr_tmp += normalize_array(a, norm_type="float", title=f"ARRLIST:{title}.") * exaggeration
    return arr_tmp / len(arr_list)


def check_empty_array(arr: ndarray, val: float) -> bool:
    """
    Return True if the input numpy array is empy. Check if
        - all values are all the same value (0, 1 or given 'val' input float value)
        - all values that are not NaN are a given 'val' float value

    Args:
        arr: input numpy array
        val: value to use for check if array is empty

    Returns:
        bool: True if the input numpy array is empty, False otherwise

    """

    arr_check5_tmp = np.copy(arr)
    arr_size = arr.shape[0]
    arr_check3 = np.ones((arr_size, arr_size))
    check1 = np.array_equal(arr, arr_check3)
    check2 = np.array_equal(arr, np.zeros((arr_size, arr_size)))
    arr_check3 *= val
    check3 = np.array_equal(arr, arr_check3)
    arr[np.isnan(arr)] = 0
    check4 = np.array_equal(arr, np.zeros((arr_size, arr_size)))
    arr_check5 = np.ones((arr_size, arr_size)) * val
    arr_check5_tmp[np.isnan(arr_check5_tmp)] = val
    check5 = np.array_equal(arr_check5_tmp, arr_check5)
    app_logger.debug(f"array checks:{check1}, {check2}, {check3}, {check4}, {check5}.")
    return check1 or check2 or check3 or check4 or check5


def write_raster_png(
        arr: ndarray, transform: Affine, prefix: str, suffix: str, folder_output_path: str | Path = "/tmp"
    ) -> tuple[Path, Path]:
    """
    Write a raster PNG image on disk, using a given Affine transformation.
    Write also an [WorldFile](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/What-are-the-TFW-JGW-or-PGW-files.html)
    containing the geographic transformation.

    Args:
        arr: (3-band) ndarray image to write on disk
        transform: Affine geographic transformation
        prefix: string prefix used in image filename
        suffix: string suffix used in image filename
        folder_output_path: parent folder where to write the image

    Returns:
        tuple of written file Paths
        (a ndarray image and a geographic transformation file - WorldFile with TFW extension)

    """
    from pathlib import Path
    from rasterio.plot import reshape_as_raster

    output_filename = Path(folder_output_path) / f"{prefix}_{suffix}.png"
    msg = f"{MSG_WRITE_TMP_ON_DISK} PNG, coords/prefix {prefix}, suffix {suffix}, shape:{arr.shape}, {len(arr.shape)}."
    app_logger.debug(msg)
    worldfile_path = write_worldfile(transform, folder_output_path, prefix, WorldFile.pgw)

    with rasterio_open(
            output_filename, 'w', driver='PNG',
            height=arr.shape[0],
            width=arr.shape[1],
            count=3,
            dtype=str(arr.dtype),
            crs=OUTPUT_CRS_STRING,
            transform=transform) as dst:
        dst.write(reshape_as_raster(arr))
    app_logger.info(f"written:{output_filename} as PGW:{worldfile_path}, use {OUTPUT_CRS_STRING} as CRS.")
    return worldfile_path, output_filename


def write_raster_tiff(arr, transform: Affine, prefix: str, suffix: str, folder_output_path="/tmp") -> tuple[Path, Path]:
    """
    Write a raster TIF image on disk, using a given Affine transformation.
    Write also an [WorldFile](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/What-are-the-TFW-JGW-or-PGW-files.html)
    containing the geographic transformation.

    Args:
        arr: (1-band) ndarray image to write on disk
        transform: Affine geographic transformation
        prefix: string prefix used in image filename
        suffix: string suffix used in image filename
        folder_output_path: parent folder where to write the image

    Returns:
        tuple of written file Paths
        (a ndarray image and a geographic transformation file - WorldFile with TFW extension)

    """
    from pathlib import Path
    output_filename = Path(folder_output_path) / f"{prefix}_{suffix}.tiff"
    msg = MSG_WRITE_TMP_ON_DISK + f"TIF, coords/prefix {prefix}, suffix {suffix}, shape:{arr.shape}, {len(arr.shape)}."
    app_logger.debug(msg)
    worldfile_path = write_worldfile(transform, folder_output_path, prefix, WorldFile.tfw)

    with rasterio_open(
            output_filename, 'w', driver='GTiff',
            height=arr.shape[0],
            width=arr.shape[1],
            count=1,
            dtype=str(arr.dtype),
            crs=OUTPUT_CRS_STRING,
            transform=transform) as dst:
        dst.write(arr, 1)
    app_logger.info(f"written:{output_filename} as TFW:{worldfile_path}, use {OUTPUT_CRS_STRING} as CRS.")
    return worldfile_path, output_filename


def write_worldfile(transform: Affine, output_folder: Path | str, prefix: str, extension: WorldFile):
    """
    Write an [WorldFile](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/What-are-the-TFW-JGW-or-PGW-files.html)
    containing the geographic transformation.

    Args:
        transform: Affine geographic transformation
        output_folder: parent folder where to write the image
        prefix: string prefix used in image filename
        extension: WorldFile extension

    Returns:
        Path of written WorldFile geographic transformation file

    """
    msg = MSG_WRITE_TMP_ON_DISK + f"WorldFile, coords/prefix {prefix}, extension:{extension}."
    app_logger.debug(msg)
    transform_dumped = [str(t) for t in transform.to_shapely()]
    content_affine = "\n".join(transform_dumped)
    app_logger.debug(f"content_affine:{content_affine}.")
    ext = extension if isinstance(extension, str) else extension.value
    worldfile_path = Path(output_folder) / f"{prefix}.{ext}"
    app_logger.debug(f"worldfile_path:{worldfile_path}.")
    with open(worldfile_path, "w") as worldfile_dst:
        worldfile_dst.write(content_affine)
    app_logger.info(f"written:{worldfile_path} using {transform} (type {type(transform)}) as {extension} WorldFile.")
    return worldfile_path


def write_geojson_on_disk(geojson_content: str, prefix: str, suffix: str, folder_output_path="/tmp") -> Path:
    """
    Write a [geojson](https://geojson.org) on disk.

    Args:
        geojson_content: json to write on disk
        prefix: string prefix used in image filename
        suffix: string prefix used in image filename
        folder_output_path: parent folder where to write the image

    Returns:
        Path of written geojson file.

    """
    msg = MSG_WRITE_TMP_ON_DISK + f"GeoJSON, coords/prefix {prefix}."
    app_logger.debug(msg)
    app_logger.debug(f"geojson content:{geojson_content}.")
    output_geojson_filename = Path(folder_output_path) / f"{prefix}_{suffix}.json"
    app_logger.debug(f"output_geojson_filename:{output_geojson_filename}.")
    with open(output_geojson_filename, "w") as output_geojson_dst:
        output_geojson_dst.write(geojson_content)
    app_logger.info(f"written:{output_geojson_filename} as geojson.")
    return output_geojson_filename
