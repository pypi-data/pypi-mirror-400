"""
Map Style Configurations for India Map Corrector
=================================================

This module provides comprehensive map style configurations for both
Folium (Leaflet-based) and Plotly visualizations.

Available styles include standard maps, satellite imagery, terrain maps,
and artistic styles.
"""

from typing import TypedDict


class TileConfig(TypedDict, total=False):
    """Configuration for a map tile provider."""
    name: str
    url: str
    attribution: str
    description: str


# =============================================================================
# FOLIUM / LEAFLET TILE STYLES
# =============================================================================

FOLIUM_STYLES: dict[str, TileConfig] = {
    # Standard Map Styles
    "OpenStreetMap": {
        "name": "OpenStreetMap",
        "url": None,  # Built-in, uses default
        "attribution": "OpenStreetMap contributors",
        "description": "Standard OpenStreetMap tiles with roads, buildings, and labels. "
                       "Best for general purpose mapping with detailed street-level information."
    },
    
    "CartoDB positron": {
        "name": "CartoDB positron",
        "url": None,  # Built-in
        "attribution": "CartoDB",
        "description": "Light, minimal background with subtle gray tones. "
                       "Ideal for data visualization where the overlay should stand out. "
                       "Perfect for presentations and clean dashboards."
    },
    
    "CartoDB dark_matter": {
        "name": "CartoDB dark_matter",
        "url": None,  # Built-in
        "attribution": "CartoDB",
        "description": "Dark theme with muted colors and bright labels. "
                       "Excellent for dark mode dashboards, night displays, and "
                       "making colorful data overlays pop."
    },
    
    # Esri Styles
    "Esri.WorldImagery": {
        "name": "Esri World Imagery",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attribution": "Esri, Maxar, Earthstar Geographics",
        "description": "High-resolution satellite imagery of the entire world. "
                       "Best for geographic analysis, land use studies, and "
                       "seeing actual terrain features."
    },
    
    "Esri.WorldStreetMap": {
        "name": "Esri World Street Map",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        "attribution": "Esri",
        "description": "Professional street map style from Esri. "
                       "Alternative to OpenStreetMap with a cleaner, more professional look."
    },
    
    "Esri.WorldTopoMap": {
        "name": "Esri World Topographic Map",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        "attribution": "Esri",
        "description": "Topographic map showing elevation contours and terrain features. "
                       "Ideal for terrain analysis, hiking, and outdoor planning."
    },
    
    "Esri.NatGeoWorldMap": {
        "name": "Esri National Geographic",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}",
        "attribution": "Esri, National Geographic",
        "description": "National Geographic style map with artistic shading and labeling. "
                       "Great for educational and publication purposes."
    },
    
    # Stamen Styles (now hosted by Stadia)
    "Stamen Terrain": {
        "name": "Stamen Terrain",
        "url": "https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png",
        "attribution": "Stamen Design, Stadia Maps",
        "description": "Terrain map with artistic hill shading showing elevation. "
                       "Excellent for geographic presentations and showing topography."
    },
    
    "Stamen Toner": {
        "name": "Stamen Toner",
        "url": "https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}{r}.png",
        "attribution": "Stamen Design, Stadia Maps",
        "description": "High contrast black and white map. "
                       "Perfect for print-ready maps and when you need maximum clarity."
    },
    
    "Stamen Watercolor": {
        "name": "Stamen Watercolor",
        "url": "https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg",
        "attribution": "Stamen Design, Stadia Maps",
        "description": "Artistic watercolor-style rendering of the map. "
                       "Ideal for creative visualizations and artistic presentations."
    },
    
    # Blank / No tiles
    "blank": {
        "name": "Blank",
        "url": None,
        "attribution": "",
        "description": "No background tiles - completely blank canvas. "
                       "Use when you only want to show your overlay without any base map."
    },
}


# =============================================================================
# PLOTLY MAPBOX STYLES
# =============================================================================

PLOTLY_STYLES: dict[str, dict] = {
    "open-street-map": {
        "name": "OpenStreetMap",
        "requires_token": False,
        "description": "Standard OpenStreetMap tiles. Free to use, shows roads, "
                       "buildings, and points of interest."
    },
    
    "carto-positron": {
        "name": "Carto Positron (Light)",
        "requires_token": False,
        "description": "Light, minimal map with gray tones. Ideal for data visualization "
                       "where overlays should be prominent."
    },
    
    "carto-darkmatter": {
        "name": "Carto Dark Matter",
        "requires_token": False,
        "description": "Dark-themed map. Perfect for dark mode applications and "
                       "making colorful data stand out."
    },
    
    "white-bg": {
        "name": "White Background",
        "requires_token": False,
        "description": "Plain white background with no map features. "
                       "Use for overlay-only visualizations."
    },
    
    "satellite": {
        "name": "Satellite Imagery",
        "requires_token": True,
        "description": "Satellite imagery. Requires a Mapbox access token. "
                       "Shows actual Earth imagery."
    },
    
    "satellite-streets": {
        "name": "Satellite with Streets",
        "requires_token": True,
        "description": "Satellite imagery with street labels overlay. "
                       "Requires Mapbox token. Best of both worlds."
    },
    
    "outdoors": {
        "name": "Outdoors",
        "requires_token": True,
        "description": "Outdoor/hiking focused map with trails and terrain. "
                       "Requires Mapbox token."
    },
    
    "light": {
        "name": "Mapbox Light",
        "requires_token": True,
        "description": "Mapbox light theme. Requires token. "
                       "Similar to carto-positron but from Mapbox."
    },
    
    "dark": {
        "name": "Mapbox Dark",
        "requires_token": True,
        "description": "Mapbox dark theme. Requires token. "
                       "Similar to carto-darkmatter but from Mapbox."
    },
}


def get_available_folium_styles() -> list[str]:
    """
    Get a list of all available Folium/Leaflet map styles.
    
    Returns
    -------
    list[str]
        List of style names that can be used with create_folium_map().
    
    Example
    -------
    >>> from india_map_corrector import get_available_folium_styles
    >>> styles = get_available_folium_styles()
    >>> print(styles)
    ['OpenStreetMap', 'CartoDB positron', 'CartoDB dark_matter', ...]
    """
    return list(FOLIUM_STYLES.keys())


def get_available_plotly_styles(include_token_required: bool = True) -> list[str]:
    """
    Get a list of all available Plotly Mapbox styles.
    
    Parameters
    ----------
    include_token_required : bool, default True
        If True, includes styles that require a Mapbox token.
        If False, only returns free styles.
    
    Returns
    -------
    list[str]
        List of style names that can be used with create_plotly_map().
    
    Example
    -------
    >>> from india_map_corrector import get_available_plotly_styles
    >>> # Get only free styles
    >>> free_styles = get_available_plotly_styles(include_token_required=False)
    >>> print(free_styles)
    ['open-street-map', 'carto-positron', 'carto-darkmatter', 'white-bg']
    """
    if include_token_required:
        return list(PLOTLY_STYLES.keys())
    return [k for k, v in PLOTLY_STYLES.items() if not v.get("requires_token", False)]


def describe_style(style_name: str) -> str:
    """
    Get a detailed description of a map style.
    
    Parameters
    ----------
    style_name : str
        Name of the style to describe.
    
    Returns
    -------
    str
        Detailed description of the style including best use cases.
    
    Raises
    ------
    ValueError
        If the style name is not recognized.
    
    Example
    -------
    >>> from india_map_corrector import describe_style
    >>> print(describe_style("Esri.WorldImagery"))
    'High-resolution satellite imagery of the entire world...'
    """
    if style_name in FOLIUM_STYLES:
        return FOLIUM_STYLES[style_name]["description"]
    elif style_name in PLOTLY_STYLES:
        return PLOTLY_STYLES[style_name]["description"]
    else:
        available = list(FOLIUM_STYLES.keys()) + list(PLOTLY_STYLES.keys())
        raise ValueError(
            f"Unknown style: '{style_name}'. "
            f"Available styles: {available}"
        )


def print_all_styles() -> None:
    """
    Print a formatted table of all available map styles with descriptions.
    
    This is a convenience function to help users discover available styles.
    
    Example
    -------
    >>> from india_map_corrector import print_all_styles
    >>> print_all_styles()
    """
    print("=" * 80)
    print("FOLIUM / LEAFLET STYLES")
    print("=" * 80)
    for name, config in FOLIUM_STYLES.items():
        print(f"\n📍 {name}")
        print(f"   {config['description']}")
    
    print("\n" + "=" * 80)
    print("PLOTLY MAPBOX STYLES")
    print("=" * 80)
    for name, config in PLOTLY_STYLES.items():
        token_note = " 🔑 (requires Mapbox token)" if config.get("requires_token") else " ✓ (free)"
        print(f"\n📍 {name}{token_note}")
        print(f"   {config['description']}")


# =============================================================================
# ADAPTIVE BORDER STYLE PRESETS
# =============================================================================

BORDER_STYLE_PRESETS: dict[str, dict] = {
    # Folium styles - using #ebd9da (light rose)
    "CartoDB positron": {"line_color": "#ebd9da", "line_width": 1.5, "line_opacity": 0.9, "fill_color": "rgba(235, 217, 218, 0.15)", "fill_opacity": 0.15},
    "CartoDB dark_matter": {"line_color": "#ebd9da", "line_width": 1.5, "line_opacity": 0.9, "fill_color": "rgba(235, 217, 218, 0.1)", "fill_opacity": 0.1},
    "OpenStreetMap": {"line_color": "#ebd9da", "line_width": 1.5, "line_opacity": 0.9, "fill_color": "rgba(235, 217, 218, 0.2)", "fill_opacity": 0.2},
    "Esri.WorldImagery": {"line_color": "#ebd9da", "line_width": 1.8, "line_opacity": 0.95, "fill_color": "rgba(235, 217, 218, 0.08)", "fill_opacity": 0.08},
    "white-bg": {"line_color": "#d6c2be", "line_width": 2.0, "line_opacity": 0.9, "fill_color": "rgba(214, 194, 190, 0.3)", "fill_opacity": 0.3},
    "blank": {"line_color": "#ebd9da", "line_width": 1.5, "line_opacity": 1.0, "fill_color": "rgba(235, 217, 218, 0.5)", "fill_opacity": 0.5},
    # Plotly styles - using #d6c2be (dusty mauve)
    "carto-positron": {"line_color": "#d6c2be", "line_width": 3.0, "line_opacity": 0.95, "fill_color": "rgba(214, 194, 190, 0.1)", "fill_opacity": 0.1},
    "open-street-map": {"line_color": "#d6c2be", "line_width": 3.0, "line_opacity": 0.95, "fill_color": "rgba(214, 194, 190, 0.15)", "fill_opacity": 0.15},
    # Dark theme - using #252525 (dark gray)
    "carto-darkmatter": {"line_color": "#252525", "line_width": 3.0, "line_opacity": 0.95, "fill_color": "rgba(37, 37, 37, 0.08)", "fill_opacity": 0.08},
}

# Default and wrapper style - using #c4afbf (light purple/mauve)
DEFAULT_BORDER_STYLE = {"line_color": "#c4afbf", "line_width": 2.5, "line_opacity": 0.9, "fill_color": "rgba(196, 175, 191, 0.2)", "fill_opacity": 0.2}


def get_border_style_for_map(map_style: str) -> dict:
    """Get optimal border styling for a given map style."""
    return BORDER_STYLE_PRESETS.get(map_style, DEFAULT_BORDER_STYLE).copy()

