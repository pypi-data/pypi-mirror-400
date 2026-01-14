"""
Dynamic Map Visualization Module (Folium)
==========================================

This module provides interactive map visualization using Folium,
which creates Leaflet.js-based interactive maps.

These visualizations are ideal for:
- Interactive exploration in Jupyter notebooks
- Web-based map applications
- HTML export for sharing
- Zoom, pan, and hover interactions
"""

from typing import Union, Optional, Callable, Any, List
from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd

from .core import get_corrected_geojson, get_india_center, get_world_center
from .styles import FOLIUM_STYLES, get_border_style_for_map


def create_folium_map(
    data: Optional[Union[pd.DataFrame, gpd.GeoDataFrame]] = None,
    column: Optional[str] = None,
    location: Optional[List[float]] = None,
    zoom_start: int = 4,
    tiles: str = "CartoDB positron",
    style_function: Optional[Callable] = None,
    fill_color: str = "lightblue",
    line_color: str = "black",
    fill_opacity: float = 0.7,
    line_weight: int = 1,
    highlight_function: Optional[Callable] = None,
    tooltip_fields: Optional[List[str]] = None,
    popup_fields: Optional[List[str]] = None,
    layer_name: str = "Borders",
    save_html: Optional[str] = None,
    focus_india: bool = True,
    auto_style: bool = True,
    **kwargs: Any
) -> folium.Map:
    """
    Create an interactive Folium map with correct world/India borders.
    
    This function creates a web-based interactive map using Folium (Leaflet.js).
    The map includes the corrected world boundaries overlay with India's
    de jure borders.
    
    Parameters
    ----------
    data : pandas.DataFrame or geopandas.GeoDataFrame, optional
        Additional data to merge with the map for choropleth visualization.
    
    column : str, optional
        Column name to use for choropleth coloring when data is provided.
    
    location : list[float], optional
        Initial map center as [latitude, longitude].
        Defaults to India center [22.5, 82.5] if focus_india=True,
        or world center [20, 0] otherwise.
    
    zoom_start : int, default 4
        Initial zoom level. Range is typically 1-18.
        - 1-3: World/continent view
        - 4-6: Country view
        - 7-10: State/region view
        - 11-15: City view
        - 16-18: Street view
    
    tiles : str, default "CartoDB positron"
        Base map tile style. Available options:
        
        **Standard Maps:**
        - "OpenStreetMap": Classic OSM with roads and labels
        - "CartoDB positron": Light, minimal (great for data viz)
        - "CartoDB dark_matter": Dark theme
        
        **Satellite & Terrain:**
        - "Esri.WorldImagery": Satellite imagery
        - "Esri.WorldStreetMap": Professional street map
        - "Esri.WorldTopoMap": Topographic with elevation
        - "Esri.NatGeoWorldMap": National Geographic style
        
        **Artistic:**
        - "Stamen Terrain": Terrain with hill shading
        - "Stamen Toner": High contrast black/white
        - "Stamen Watercolor": Artistic watercolor style
        
        **Minimal:**
        - "blank" or None: No background (overlay only)
        
        Use `from india_map_corrector import print_all_styles` to see
        all options with descriptions.
    
    style_function : Callable, optional
        Custom function to style each GeoJSON feature.
        Should accept a feature dict and return a style dict.
        Example:
        ```python
        def my_style(feature):
            return {
                'fillColor': 'blue',
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.5
            }
        ```
    
    fill_color : str, default "lightblue"
        Fill color for regions. Accepts CSS color names or hex codes.
        Ignored if style_function is provided.
    
    line_color : str, default "black"
        Border line color. Accepts CSS color names or hex codes.
        Ignored if style_function is provided.
    
    fill_opacity : float, default 0.7
        Fill opacity from 0 (transparent) to 1 (opaque).
        Ignored if style_function is provided.
    
    line_weight : int, default 1
        Border line width in pixels.
        Ignored if style_function is provided.
    
    highlight_function : Callable, optional
        Function to define highlight style on hover.
        Example:
        ```python
        def highlight(feature):
            return {'fillOpacity': 0.9, 'weight': 3}
        ```
    
    tooltip_fields : list[str], optional
        GeoJSON property names to show in tooltip on hover.
    
    popup_fields : list[str], optional
        GeoJSON property names to show in popup on click.
    
    layer_name : str, default "Borders"
        Name for the GeoJSON layer (shown in layer control).
    
    save_html : str, optional
        File path to save the map as an HTML file.
        If provided, the map will be saved after creation.
    
    focus_india : bool, default True
        If True, centers map on India. If False, centers on world.
    
    **kwargs
        Additional arguments passed to folium.GeoJson().
    
    Returns
    -------
    folium.Map
        The Folium map object. Can be displayed in Jupyter notebooks
        or saved to HTML.
    
    Examples
    --------
    Basic map:
    
    >>> from india_map_corrector import create_folium_map
    >>> m = create_folium_map()
    >>> m  # Display in Jupyter
    
    Satellite background:
    
    >>> m = create_folium_map(
    ...     tiles="Esri.WorldImagery",
    ...     fill_opacity=0.3,
    ...     save_html="satellite_map.html"
    ... )
    
    Custom styling:
    
    >>> m = create_folium_map(
    ...     tiles="CartoDB dark_matter",
    ...     fill_color="#3498db",
    ...     line_color="#ecf0f1",
    ...     fill_opacity=0.6,
    ...     line_weight=2
    ... )
    
    With custom style function:
    
    >>> def style_by_name(feature):
    ...     name = feature['properties'].get('name', '')
    ...     if 'India' in name:
    ...         return {'fillColor': 'orange', 'color': 'red', 'weight': 2}
    ...     return {'fillColor': 'lightblue', 'color': 'gray', 'weight': 1}
    >>> 
    >>> m = create_folium_map(style_function=style_by_name)
    
    World view:
    
    >>> m = create_folium_map(
    ...     focus_india=False,
    ...     zoom_start=2,
    ...     tiles="Stamen Watercolor"
    ... )
    
    Save to HTML:
    
    >>> m = create_folium_map(save_html="my_map.html")
    
    Notes
    -----
    - The map is displayed directly in Jupyter notebooks by just
      typing the variable name (e.g., `m`).
    - For non-notebook environments, save to HTML and open in browser.
    - Layer control is automatically added when tiles are not None.
    """
    # Determine center location
    if location is None:
        if focus_india:
            location = list(get_india_center())
        else:
            location = list(get_world_center())
    
    # Adjust zoom for world view
    if not focus_india and zoom_start == 4:
        zoom_start = 2
    
    # Handle tile configuration
    if tiles is None or tiles == "blank":
        # Create map with no tiles
        m = folium.Map(location=location, zoom_start=zoom_start, tiles=None)
    elif tiles in ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]:
        # Built-in tiles
        m = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)
    elif tiles in FOLIUM_STYLES:
        # Custom tile URL
        style_config = FOLIUM_STYLES[tiles]
        m = folium.Map(location=location, zoom_start=zoom_start, tiles=None)
        if style_config.get("url"):
            folium.TileLayer(
                tiles=style_config["url"],
                attr=style_config.get("attribution", ""),
                name=style_config.get("name", tiles)
            ).add_to(m)
    else:
        # Try as direct tiles parameter
        m = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)
    
    # Load corrected GeoJSON
    gdf = get_corrected_geojson(as_geodataframe=True)
    
    # Apply auto-styling if enabled and no custom style function provided
    actual_fill_color = fill_color
    actual_line_color = line_color
    actual_line_weight = line_weight
    actual_fill_opacity = fill_opacity
    
    if auto_style and style_function is None:
        adaptive_style = get_border_style_for_map(tiles if tiles else "blank")
        actual_line_color = adaptive_style.get("line_color", line_color)
        actual_line_weight = adaptive_style.get("line_width", line_weight)
        actual_fill_opacity = adaptive_style.get("fill_opacity", fill_opacity)
        actual_fill_color = adaptive_style.get("fill_color", fill_color)
    
    # Create default style function if not provided
    if style_function is None:
        def style_function(feature):
            return {
                'fillColor': actual_fill_color,
                'color': actual_line_color,
                'weight': actual_line_weight,
                'fillOpacity': actual_fill_opacity
            }
    
    # Create default highlight function if not provided
    if highlight_function is None:
        def highlight_function(feature):
            return {
                'fillOpacity': min(fill_opacity + 0.2, 1.0),
                'weight': line_weight + 1
            }
    
    # Build GeoJSON parameters
    geojson_params = {
        'name': layer_name,
        'style_function': style_function,
        'highlight_function': highlight_function,
        **kwargs
    }
    
    # Add tooltip if specified
    if tooltip_fields:
        geojson_params['tooltip'] = folium.GeoJsonTooltip(fields=tooltip_fields)
    
    # Add popup if specified
    if popup_fields:
        geojson_params['popup'] = folium.GeoJsonPopup(fields=popup_fields)
    
    # Add GeoJSON layer
    folium.GeoJson(gdf, **geojson_params).add_to(m)
    
    # Add layer control if tiles exist
    if tiles is not None and tiles != "blank":
        folium.LayerControl().add_to(m)
    
    # Save if path provided
    if save_html:
        save_path = Path(save_html)
        m.save(str(save_path))
    
    return m


def create_blank_map(
    fill_color: str = "lightblue",
    line_color: str = "black",
    save_html: Optional[str] = None,
    focus_india: bool = True,
    **kwargs: Any
) -> folium.Map:
    """
    Create an interactive map with no background tiles (overlay only).
    
    This is a convenience function that creates a map with only the
    corrected border overlay and no underlying map tiles.
    
    Parameters
    ----------
    fill_color : str, default "lightblue"
        Fill color for regions.
    
    line_color : str, default "black"
        Border line color.
    
    save_html : str, optional
        Path to save as HTML.
    
    focus_india : bool, default True
        Whether to focus on India.
    
    **kwargs
        Additional arguments passed to create_folium_map().
    
    Returns
    -------
    folium.Map
        The Folium map object.
    
    Examples
    --------
    >>> from india_map_corrector import create_blank_map
    >>> m = create_blank_map(save_html="overlay_only.html")
    """
    return create_folium_map(
        tiles=None,
        fill_color=fill_color,
        line_color=line_color,
        save_html=save_html,
        focus_india=focus_india,
        **kwargs
    )


def create_satellite_map(
    fill_opacity: float = 0.3,
    save_html: Optional[str] = None,
    focus_india: bool = True,
    **kwargs: Any
) -> folium.Map:
    """
    Create an interactive map with satellite imagery background.
    
    This is a convenience function that creates a map with Esri
    satellite imagery and a semi-transparent border overlay.
    
    Parameters
    ----------
    fill_opacity : float, default 0.3
        Fill opacity. Lower values show more satellite imagery.
    
    save_html : str, optional
        Path to save as HTML.
    
    focus_india : bool, default True
        Whether to focus on India.
    
    **kwargs
        Additional arguments passed to create_folium_map().
    
    Returns
    -------
    folium.Map
        The Folium map object.
    
    Examples
    --------
    >>> from india_map_corrector import create_satellite_map
    >>> m = create_satellite_map(save_html="satellite.html")
    """
    return create_folium_map(
        tiles="Esri.WorldImagery",
        fill_opacity=fill_opacity,
        save_html=save_html,
        focus_india=focus_india,
        **kwargs
    )


def create_bhuvan_map(
    zoom_start: int = 5,
    fill_color: str = "rgba(196,175,191,0.2)",
    line_color: str = "#c4afbf",
    fill_opacity: float = 0.2,
    line_weight: int = 2,
    save_html: Optional[str] = None,
    **kwargs: Any
) -> folium.Map:
    """
    Create an interactive map with official ISRO Bhuvan base tiles.
    
    This function creates a map using the official Indian Space Research
    Organisation (ISRO) Bhuvan WMS tiles as the base layer. The Bhuvan
    platform shows India with correct de jure borders as recognized by
    the Government of India.
    
    Parameters
    ----------
    zoom_start : int, default 5
        Initial zoom level for the map.
    
    fill_color : str, default "rgba(144,238,144,0.3)"
        Fill color for the India overlay. Use low opacity to see base map.
    
    line_color : str, default "#2c3e50"
        Border line color for the overlay.
    
    fill_opacity : float, default 0.3
        Fill opacity. Lower values show more of the Bhuvan base map.
    
    line_weight : int, default 2
        Width of border lines in pixels.
    
    save_html : str, optional
        Path to save as HTML file.
    
    **kwargs
        Additional arguments passed to folium.Map.
    
    Returns
    -------
    folium.Map
        The Folium map object with ISRO Bhuvan tiles.
    
    Examples
    --------
    >>> from india_map_corrector import create_bhuvan_map
    >>> m = create_bhuvan_map(save_html="official_india.html")
    >>> m  # Display in Jupyter
    
    Notes
    -----
    - Uses ISRO Bhuvan WMS service (https://bhuvan.nrsc.gov.in)
    - The base tiles show official India boundaries
    - Requires internet connection to load WMS tiles
    - ISRO Bhuvan is a Government of India initiative
    """
    # Create base map centered on India
    location = list(get_india_center())
    m = folium.Map(
        location=location,
        zoom_start=zoom_start,
        tiles=None,
        **kwargs
    )
    
    # Add ISRO Bhuvan WMS tiles as base layer
    # Using the official India base map from NRSC/ISRO
    # Note: Bhuvan layer includes some thematic data overlay
    folium.WmsTileLayer(
        url="https://bhuvan-vec2.nrsc.gov.in/bhuvan/gwc/service/wms",
        layers="sisdp_base:sisdp_basemap",
        name="ISRO Bhuvan (with data)",
        fmt="image/png",
        transparent=True,
        control=True,
        show=False,  # Hidden by default - user can enable
        attr="© ISRO/NRSC Bhuvan"
    ).add_to(m)
    
    # Add clean CartoDB positron as primary (no dotted borders)
    folium.TileLayer(
        tiles="CartoDB positron",
        name="Clean Base Map",
        control=True
    ).add_to(m)
    
    # Load and add corrected India borders overlay
    gdf = get_corrected_geojson(as_geodataframe=True)
    
    def style_function(feature):
        return {
            'fillColor': fill_color,
            'color': line_color,
            'weight': line_weight,
            'fillOpacity': fill_opacity
        }
    
    def highlight_function(feature):
        return {
            'fillOpacity': min(fill_opacity + 0.2, 1.0),
            'weight': line_weight + 1
        }
    
    folium.GeoJson(
        gdf,
        name="India Borders (De Jure)",
        style_function=style_function,
        highlight_function=highlight_function
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save if path provided
    if save_html:
        save_path = Path(save_html)
        m.save(str(save_path))
    
    return m

