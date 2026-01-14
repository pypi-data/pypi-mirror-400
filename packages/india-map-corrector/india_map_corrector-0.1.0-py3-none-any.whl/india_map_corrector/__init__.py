"""
India Map Corrector
===================

A Python module to visualize maps with correct (de jure) India borders.

This package provides easy-to-use functions for creating static and
interactive maps that display India's legally recognized boundaries,
replacing the incorrect de facto borders shown by default in most
mapping libraries.

Features
--------
- Static map visualization with Matplotlib
- Interactive HTML maps with Folium
- Interactive Plotly maps for notebooks and dashboards
- Wrapper functions to fix existing Plotly visualizations
- Multiple map styles including satellite, terrain, and artistic options

Quick Start
-----------
>>> from india_map_corrector import create_folium_map, create_plotly_map
>>> 
>>> # Create an interactive Folium map
>>> m = create_folium_map(save_html="my_map.html")
>>> 
>>> # Create a Plotly map
>>> fig = create_plotly_map()
>>> fig.show()

Fix existing Plotly maps:

>>> from india_map_corrector import correct_map
>>> fig = px.choropleth_mapbox(data, ...)
>>> fig = correct_map(fig)  # Adds correct borders!
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# Core functions
from .core import (
    get_corrected_geojson,
    get_geojson_interface,
    get_india_bounds,
    get_india_center,
    get_world_center,
)

# Static visualization (Matplotlib)
from .static import (
    plot_static,
    plot_world_static,
)

# Dynamic visualization (Folium)
from .dynamic import (
    create_folium_map,
    create_blank_map,
    create_satellite_map,
    create_bhuvan_map,
)

# Plotly visualization
from .plotly_viz import (
    create_plotly_map,
    create_dark_map,
    create_minimal_map,
)

# Wrapper functions
from .wrappers import (
    correct_map,
    with_correct_borders,
    apply_correct_borders_to_figure,
)

# Style utilities
from .styles import (
    get_available_folium_styles,
    get_available_plotly_styles,
    describe_style,
    print_all_styles,
    get_border_style_for_map,
    FOLIUM_STYLES,
    PLOTLY_STYLES,
    BORDER_STYLE_PRESETS,
)


__all__ = [
    # Version
    "__version__",
    
    # Core
    "get_corrected_geojson",
    "get_geojson_interface",
    "get_india_bounds",
    "get_india_center",
    "get_world_center",
    
    # Static
    "plot_static",
    "plot_world_static",
    
    # Folium
    "create_folium_map",
    "create_blank_map",
    "create_satellite_map",
    
    # Plotly
    "create_plotly_map",
    "create_dark_map",
    "create_minimal_map",
    
    # Wrappers
    "correct_map",
    "with_correct_borders",
    "apply_correct_borders_to_figure",
    
    # Styles
    "get_available_folium_styles",
    "get_available_plotly_styles",
    "describe_style",
    "print_all_styles",
    "get_border_style_for_map",
    "FOLIUM_STYLES",
    "PLOTLY_STYLES",
    "BORDER_STYLE_PRESETS",
]
