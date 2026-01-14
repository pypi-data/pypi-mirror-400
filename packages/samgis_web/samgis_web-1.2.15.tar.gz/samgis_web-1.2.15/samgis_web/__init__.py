"""Get machine learning predictions from geodata raster images (web package)"""
import os
from pathlib import Path

# not used here but contextily_tile is imported in samgis.io.tms2geotiff
from contextily import tile as contextily_tile

PROJECT_ROOT_FOLDER = Path(globals().get("__file__", "./_")).absolute().parent.parent
WORKDIR = os.getenv("WORKDIR", PROJECT_ROOT_FOLDER)
PROJECT_MODEL_FOLDER = Path(PROJECT_ROOT_FOLDER / "machine_learning_models")
MODEL_FOLDER = os.getenv("MODEL_FOLDER", PROJECT_MODEL_FOLDER)
