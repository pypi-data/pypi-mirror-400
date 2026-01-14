"""
Wrapper Functions for India Map Corrector
==========================================

This module provides wrapper functions and decorators to easily add
correct India/world borders to existing Plotly visualizations.

Use these when you have existing code that creates Plotly maps
and you want to add the correct border overlay.
"""

from typing import Callable, Optional, Dict, Any
from functools import wraps

import plotly.graph_objects as go
import plotly.express as px

from .core import get_corrected_geojson
from .styles import get_border_style_for_map


def correct_map(
    fig: go.Figure,
    overlay_style: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """
    Add correct world/India border overlay to an existing Plotly figure.
    
    This is the main wrapper function that takes any Plotly figure
    (especially choropleth or mapbox figures) and adds a GeoJSON
    layer with the corrected world boundaries.
    
    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The existing Plotly figure to add borders to.
        Works best with choropleth_mapbox, scattermapbox, or similar.
    
    overlay_style : dict, optional
        Style options for the border overlay. Available keys:
        - 'line_color': str, default "black"
            Color of border lines
        - 'line_width': float, default 1.5
            Width of border lines
        - 'fill_color': str, default "rgba(0,0,0,0)"
            Fill color (default is transparent)
        - 'fill_opacity': float, default 0
            Fill opacity (default is fully transparent)
        - 'below': str, optional
            Mapbox layer to place this below
    
    Returns
    -------
    plotly.graph_objects.Figure
        The modified figure with correct border overlay added.
    
    Examples
    --------
    Basic usage with existing Plotly choropleth:
    
    >>> import plotly.express as px
    >>> from india_map_corrector import correct_map
    >>> 
    >>> # Your existing code
    >>> fig = px.choropleth_mapbox(
    ...     my_data,
    ...     geojson=my_geojson,
    ...     locations='state',
    ...     color='value',
    ...     mapbox_style="carto-positron",
    ...     center={"lat": 22, "lon": 82},
    ...     zoom=3.5
    ... )
    >>> 
    >>> # Add correct borders
    >>> fig = correct_map(fig)
    >>> fig.show()
    
    With custom overlay style:
    
    >>> fig = correct_map(fig, overlay_style={
    ...     'line_color': 'red',
    ...     'line_width': 2,
    ...     'fill_color': 'rgba(255, 0, 0, 0.1)'
    ... })
    
    Notes
    -----
    - The overlay is added as a mapbox layer, so it works best with
      mapbox-based Plotly figures.
    - For choropleth (non-mapbox) figures, consider using
      `create_plotly_map()` instead.
    """
    # Try to auto-detect map style from figure
    detected_style = None
    try:
        detected_style = fig.layout.mapbox.style
    except:
        pass
    
    # Default style with adaptive colors
    if detected_style and overlay_style is None:
        adaptive = get_border_style_for_map(detected_style)
        style = {
            'line_color': adaptive.get('line_color', '#2c3e50'),
            'line_width': adaptive.get('line_width', 2.0),
            'fill_color': 'rgba(0,0,0,0)',
            'fill_opacity': 0
        }
    else:
        style = {
            'line_color': '#2c3e50',
            'line_width': 2.0,
            'fill_color': 'rgba(0,0,0,0)',
            'fill_opacity': 0
        }
    
    if overlay_style:
        style.update(overlay_style)
    
    # Get the corrected GeoJSON
    gdf = get_corrected_geojson(as_geodataframe=True)
    geojson_data = gdf.__geo_interface__
    
    # Create the mapbox layer
    layer = {
        'source': geojson_data,
        'type': 'line',
        'color': style['line_color'],
        'line': {'width': style['line_width']}
    }
    
    # Add fill layer if opacity > 0
    layers = [layer]
    if style.get('fill_opacity', 0) > 0 or style.get('fill_color', 'rgba(0,0,0,0)') != 'rgba(0,0,0,0)':
        fill_layer = {
            'source': geojson_data,
            'type': 'fill',
            'color': style['fill_color'],
            'opacity': style.get('fill_opacity', 0.3)
        }
        if style.get('below'):
            fill_layer['below'] = style['below']
        layers.insert(0, fill_layer)
    
    # Get existing layers and add new ones
    existing_layers = list(fig.layout.mapbox.layers) if fig.layout.mapbox.layers else []
    existing_layers.extend(layers)
    
    # Update figure
    fig.update_layout(
        mapbox=dict(layers=existing_layers)
    )
    
    return fig


def with_correct_borders(
    overlay_style: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator to automatically add correct border overlay to Plotly functions.
    
    Use this decorator on any function that returns a Plotly figure.
    The decorator will automatically apply the correct world/India
    border overlay to the returned figure.
    
    Parameters
    ----------
    overlay_style : dict, optional
        Style options for the border overlay. See correct_map() for details.
    
    Returns
    -------
    Callable
        A decorator function.
    
    Examples
    --------
    Basic usage:
    
    >>> from india_map_corrector import with_correct_borders
    >>> import plotly.express as px
    >>> 
    >>> @with_correct_borders()
    >>> def create_my_dashboard_map(data):
    ...     return px.choropleth_mapbox(
    ...         data,
    ...         geojson=my_geojson,
    ...         locations='state',
    ...         color='value',
    ...         mapbox_style="carto-positron"
    ...     )
    >>> 
    >>> # The returned figure automatically has correct borders
    >>> fig = create_my_dashboard_map(my_data)
    >>> fig.show()
    
    With custom styling:
    
    >>> @with_correct_borders(overlay_style={
    ...     'line_color': 'navy',
    ...     'line_width': 2
    ... })
    >>> def create_styled_map(data):
    ...     return px.choropleth_mapbox(data, ...)
    
    Class method usage:
    
    >>> class MapDashboard:
    ...     @with_correct_borders()
    ...     def create_overview_map(self, data):
    ...         return px.choropleth_mapbox(data, ...)
    
    Notes
    -----
    - The decorator preserves the original function's signature and docstring.
    - It only modifies the return value if it's a Plotly Figure.
    - If the decorated function doesn't return a Figure, it returns as-is.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Only apply correction if result is a Plotly Figure
            if isinstance(result, go.Figure):
                return correct_map(result, overlay_style)
            
            return result
        
        return wrapper
    
    return decorator


def apply_correct_borders_to_figure(
    chart_function: Callable,
    *args,
    overlay_style: Optional[Dict[str, Any]] = None,
    **kwargs
) -> go.Figure:
    """
    Apply correct borders to a Plotly chart function call.
    
    This is an alternative to the decorator pattern for one-off usage.
    
    Parameters
    ----------
    chart_function : Callable
        A Plotly chart function (e.g., px.choropleth_mapbox).
    
    *args
        Positional arguments to pass to the chart function.
    
    overlay_style : dict, optional
        Style options for the border overlay.
    
    **kwargs
        Keyword arguments to pass to the chart function.
    
    Returns
    -------
    plotly.graph_objects.Figure
        The figure with correct border overlay.
    
    Examples
    --------
    >>> from india_map_corrector import apply_correct_borders_to_figure
    >>> import plotly.express as px
    >>> 
    >>> fig = apply_correct_borders_to_figure(
    ...     px.choropleth_mapbox,
    ...     my_data,
    ...     geojson=my_geojson,
    ...     locations='state',
    ...     color='value',
    ...     overlay_style={'line_color': 'red'}
    ... )
    >>> fig.show()
    """
    fig = chart_function(*args, **kwargs)
    return correct_map(fig, overlay_style)
