"""
Core Module for India Map Corrector
====================================

This module provides core functionality for loading and working with
the corrected world boundaries GeoJSON that includes accurate (de jure)
India borders.

The GeoJSON file contains world country boundaries with India's borders
corrected to show the legal boundaries as recognized by the Government of India.
"""

from pathlib import Path
from typing import Union
import json

import geopandas as gpd


# Path to the bundled GeoJSON data
_DATA_DIR = Path(__file__).parent / "data"
_GEOJSON_PATH = _DATA_DIR / "world_corrected.geojson"


def get_corrected_geojson(
    as_geodataframe: bool = True,
    simplify: float | None = None
) -> Union[gpd.GeoDataFrame, dict]:
    """
    Load and return the corrected world boundaries GeoJSON.
    
    This function loads the bundled GeoJSON file that contains world country
    boundaries with India's borders corrected to show the legal (de jure)
    boundaries. The borders include:
    - Correct boundary for Jammu & Kashmir
    - Correct boundary for Arunachal Pradesh
    - Correct boundary for Aksai Chin region
    
    Parameters
    ----------
    as_geodataframe : bool, default True
        If True, returns a GeoDataFrame for easy manipulation with GeoPandas.
        If False, returns the raw GeoJSON as a Python dictionary.
    
    simplify : float | None, default None
        Optional simplification tolerance for the geometry. Higher values
        result in more simplified (smaller file size) but less accurate
        boundaries. Recommended values:
        - None: No simplification (full detail)
        - 0.001: Very slight simplification
        - 0.01: Moderate simplification
        - 0.1: Heavy simplification (may lose detail)
    
    Returns
    -------
    geopandas.GeoDataFrame or dict
        The corrected world boundaries. If as_geodataframe=True, returns
        a GeoDataFrame. Otherwise, returns a GeoJSON dictionary.
    
    Raises
    ------
    FileNotFoundError
        If the bundled GeoJSON file is not found.
    
    Examples
    --------
    >>> from india_map_corrector import get_corrected_geojson
    >>> 
    >>> # Get as GeoDataFrame
    >>> gdf = get_corrected_geojson()
    >>> print(gdf.head())
    >>> 
    >>> # Get as raw GeoJSON dict
    >>> geojson = get_corrected_geojson(as_geodataframe=False)
    >>> print(geojson.keys())
    >>> 
    >>> # Get simplified version for faster rendering
    >>> gdf_simple = get_corrected_geojson(simplify=0.01)
    
    Notes
    -----
    The GeoJSON file is bundled with the package and does not require
    any external downloads or API calls.
    """
    if not _GEOJSON_PATH.exists():
        raise FileNotFoundError(
            f"GeoJSON file not found at {_GEOJSON_PATH}. "
            "Please ensure the package is installed correctly."
        )
    
    if as_geodataframe:
        gdf = gpd.read_file(_GEOJSON_PATH)
        
        if simplify is not None:
            gdf = gdf.copy()
            gdf['geometry'] = gdf['geometry'].simplify(tolerance=simplify)
        
        return gdf
    else:
        with open(_GEOJSON_PATH, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        return geojson_data


def get_geojson_interface(simplify: float | None = None) -> dict:
    """
    Get the GeoJSON as a __geo_interface__ compatible dictionary.
    
    This format is commonly used by visualization libraries like Plotly
    for efficient rendering of geographic data.
    
    Parameters
    ----------
    simplify : float | None, default None
        Optional simplification tolerance. See get_corrected_geojson()
        for details.
    
    Returns
    -------
    dict
        GeoJSON-like dictionary compatible with __geo_interface__ protocol.
    
    Examples
    --------
    >>> from india_map_corrector import get_geojson_interface
    >>> 
    >>> # Use with Plotly
    >>> geojson = get_geojson_interface()
    >>> fig = px.choropleth_mapbox(df, geojson=geojson, ...)
    """
    gdf = get_corrected_geojson(as_geodataframe=True, simplify=simplify)
    return gdf.__geo_interface__


def get_india_bounds() -> tuple[float, float, float, float]:
    """
    Get the bounding box coordinates for India.
    
    Returns
    -------
    tuple[float, float, float, float]
        Bounding box as (min_lon, min_lat, max_lon, max_lat).
        Also known as (west, south, east, north).
    
    Examples
    --------
    >>> from india_map_corrector import get_india_bounds
    >>> west, south, east, north = get_india_bounds()
    >>> print(f"India extends from {south}°N to {north}°N latitude")
    """
    # India's approximate bounds (including all claimed territories)
    return (68.0, 6.5, 97.5, 37.5)


def get_india_center() -> tuple[float, float]:
    """
    Get the center coordinates for India.
    
    Returns
    -------
    tuple[float, float]
        Center coordinates as (latitude, longitude).
    
    Examples
    --------
    >>> from india_map_corrector import get_india_center
    >>> lat, lon = get_india_center()
    >>> print(f"India center: {lat}°N, {lon}°E")
    """
    return (22.5, 82.5)


def get_world_center() -> tuple[float, float]:
    """
    Get the center coordinates for world view.
    
    Returns
    -------
    tuple[float, float]
        Center coordinates as (latitude, longitude).
    """
    return (20.0, 0.0)
