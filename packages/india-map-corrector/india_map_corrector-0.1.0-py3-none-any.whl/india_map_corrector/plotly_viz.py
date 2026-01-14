"""
Plotly Visualization Module for India Map Corrector
====================================================

This module provides interactive map visualization using Plotly,
which creates rich, interactive web-based visualizations.

These visualizations are ideal for:
- Interactive dashboards
- Data exploration with hover details
- Jupyter notebook visualizations
- Web applications
"""

from typing import Union, Optional, Any, List, Dict

import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd

from .core import get_corrected_geojson, get_geojson_interface, get_india_center
from .styles import PLOTLY_STYLES, get_border_style_for_map


def create_plotly_map(
    data: Optional[Union[pd.DataFrame, gpd.GeoDataFrame]] = None,
    locations: Optional[str] = None,
    color: Optional[str] = None,
    hover_name: Optional[str] = None,
    hover_data: Optional[List[str]] = None,
    color_continuous_scale: str = "Blues",
    color_discrete_sequence: Optional[List[str]] = None,
    mapbox_style: str = "open-street-map",
    center: Optional[Dict[str, float]] = None,
    zoom: float = 3.5,
    opacity: float = 0.7,
    line_color: str = "black",
    line_width: float = 1,
    title: Optional[str] = None,
    height: int = 600,
    width: Optional[int] = None,
    focus_india: bool = True,
    auto_style: bool = True,
    **kwargs: Any
) -> go.Figure:
    """
    Create an interactive Plotly choropleth map with correct world/India borders.
    
    This function creates a Plotly-based interactive map that can be
    embedded in Jupyter notebooks, Dash applications, or exported to HTML.
    
    Parameters
    ----------
    data : pandas.DataFrame or geopandas.GeoDataFrame, optional
        Data to visualize on the map. If not provided, shows only borders.
    
    locations : str, optional
        Column name containing location identifiers to match with geometry.
    
    color : str, optional
        Column name to use for color-coding the map (choropleth).
    
    hover_name : str, optional
        Column name to use as the main label in hover tooltip.
    
    hover_data : list[str], optional
        Additional column names to include in hover tooltip.
    
    color_continuous_scale : str, default "Blues"
        Plotly color scale for continuous data. Options include:
        - Sequential: 'Blues', 'Greens', 'Reds', 'Oranges', 'Purples'
        - Sequential (multi-hue): 'Viridis', 'Plasma', 'Inferno', 'Magma'
        - Diverging: 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral'
        
        Full list at: https://plotly.com/python/colorscales/
    
    color_discrete_sequence : list[str], optional
        List of colors to use for categorical data.
    
    mapbox_style : str, default "open-street-map"
        Mapbox/map style. Free options (no token required):
        - "open-street-map": Standard OSM tiles
        - "carto-positron": Light, minimal background
        - "carto-darkmatter": Dark theme
        - "white-bg": Plain white background
        
        Require Mapbox token:
        - "satellite": Satellite imagery
        - "satellite-streets": Satellite with labels
        - "outdoors": Terrain focused
        - "light": Mapbox light theme
        - "dark": Mapbox dark theme
        
        Use `from india_map_corrector import get_available_plotly_styles`
        to see all options.
    
    center : dict, optional
        Map center as {"lat": float, "lon": float}.
        Defaults to India center if focus_india=True.
    
    zoom : float, default 3.5
        Initial zoom level. Higher = more zoomed in.
    
    opacity : float, default 0.7
        Fill opacity from 0 (transparent) to 1 (opaque).
    
    line_color : str, default "black"
        Color for border lines.
    
    line_width : float, default 1
        Width of border lines.
    
    title : str, optional
        Chart title displayed above the map.
    
    height : int, default 600
        Figure height in pixels.
    
    width : int, optional
        Figure width in pixels. If None, uses auto-width.
    
    focus_india : bool, default True
        If True, centers and zooms on India.
        If False, shows world view.
    
    **kwargs
        Additional arguments passed to px.choropleth_mapbox().
    
    Returns
    -------
    plotly.graph_objects.Figure
        Interactive Plotly figure. Display in notebooks with fig.show()
        or save with fig.write_html("output.html").
    
    Examples
    --------
    Basic map with borders:
    
    >>> from india_map_corrector import create_plotly_map
    >>> fig = create_plotly_map(title="India with Correct Borders")
    >>> fig.show()
    
    Dark theme:
    
    >>> fig = create_plotly_map(
    ...     mapbox_style="carto-darkmatter",
    ...     line_color="white",
    ...     opacity=0.5
    ... )
    >>> fig.show()
    
    World view:
    
    >>> fig = create_plotly_map(
    ...     focus_india=False,
    ...     zoom=1.5,
    ...     title="World Map with Correct India Borders"
    ... )
    
    Save to HTML:
    
    >>> fig = create_plotly_map()
    >>> fig.write_html("my_plotly_map.html")
    
    Notes
    -----
    - For Mapbox token styles (satellite, etc.), set the token with:
      `px.set_mapbox_access_token("your-token-here")`
    - The figure can be customized further using Plotly's update methods:
      `fig.update_layout(...)`, `fig.update_traces(...)`, etc.
    """
    # Load corrected GeoJSON
    gdf = get_corrected_geojson(as_geodataframe=True)
    geojson_data = gdf.__geo_interface__
    
    # Determine center
    if center is None:
        if focus_india:
            lat, lon = get_india_center()
            center = {"lat": lat, "lon": lon}
        else:
            center = {"lat": 20, "lon": 0}
            if zoom == 3.5:  # Default value, adjust for world
                zoom = 1.5
    
    # Create the choropleth map
    fig = px.choropleth_mapbox(
        gdf,
        geojson=geojson_data,
        locations=gdf.index,
        color_discrete_sequence=color_discrete_sequence or ["lightblue"],
        mapbox_style=mapbox_style,
        center=center,
        zoom=zoom,
        opacity=opacity,
        **kwargs
    )
    
    # Apply auto-styling for border colors
    actual_line_color = line_color
    actual_line_width = line_width if line_width != 1 else 3.0  # Increase default significantly
    
    if auto_style:
        adaptive_style = get_border_style_for_map(mapbox_style)
        actual_line_color = adaptive_style.get("line_color", line_color)
        actual_line_width = adaptive_style.get("line_width", actual_line_width)
    
    # Update choropleth styling (for fill)
    fig.update_traces(
        marker_line_color=actual_line_color,
        marker_line_width=actual_line_width
    )
    
    # Add dedicated mapbox layer for highly visible border lines
    border_layer = {
        'source': geojson_data,
        'type': 'line',
        'color': actual_line_color,
        'line': {'width': actual_line_width}
    }
    
    # Update layout with border layer
    layout_updates = {
        "margin": {"r": 0, "t": 50 if title else 0, "l": 0, "b": 0},
        "height": height,
        "mapbox": {"layers": [border_layer]}
    }
    
    if width:
        layout_updates["width"] = width
    
    if title:
        layout_updates["title"] = {
            "text": title,
            "x": 0.5,
            "xanchor": "center"
        }
    
    fig.update_layout(**layout_updates)
    
    return fig


def create_dark_map(
    title: Optional[str] = None,
    save_html: Optional[str] = None,
    **kwargs: Any
) -> go.Figure:
    """
    Create a dark-themed Plotly map.
    
    Convenience function with dark styling preset.
    
    Parameters
    ----------
    title : str, optional
        Map title.
    
    save_html : str, optional
        Path to save as HTML.
    
    **kwargs
        Additional arguments passed to create_plotly_map().
    
    Returns
    -------
    plotly.graph_objects.Figure
        The Plotly figure.
    
    Examples
    --------
    >>> from india_map_corrector import create_dark_map
    >>> fig = create_dark_map(title="Dark Theme Map")
    >>> fig.show()
    """
    fig = create_plotly_map(
        mapbox_style="carto-darkmatter",
        line_color="#ffffff",
        opacity=0.6,
        title=title,
        **kwargs
    )
    
    fig.update_layout(
        paper_bgcolor="#1a1a2e",
        font_color="#ffffff"
    )
    
    if save_html:
        fig.write_html(save_html)
    
    return fig


def create_minimal_map(
    title: Optional[str] = None,
    save_html: Optional[str] = None,
    **kwargs: Any
) -> go.Figure:
    """
    Create a minimal, clean Plotly map.
    
    Convenience function with light, minimal styling preset.
    
    Parameters
    ----------
    title : str, optional
        Map title.
    
    save_html : str, optional
        Path to save as HTML.
    
    **kwargs
        Additional arguments passed to create_plotly_map().
    
    Returns
    -------
    plotly.graph_objects.Figure
        The Plotly figure.
    
    Examples
    --------
    >>> from india_map_corrector import create_minimal_map
    >>> fig = create_minimal_map(title="Clean Map")
    >>> fig.show()
    """
    fig = create_plotly_map(
        mapbox_style="white-bg",
        line_color="#333333",
        opacity=0.8,
        title=title,
        **kwargs
    )
    
    if save_html:
        fig.write_html(save_html)
    
    return fig
