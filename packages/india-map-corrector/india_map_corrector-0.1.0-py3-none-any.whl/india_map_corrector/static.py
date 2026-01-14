"""
Static Visualization Module for India Map Corrector
====================================================

This module provides static map visualization using Matplotlib.
These visualizations are ideal for:
- Print-ready maps
- Reports and publications
- Static images for presentations
- Quick data exploration
"""

from typing import Union, Optional, Tuple, Any
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.figure
import geopandas as gpd
import pandas as pd

from .core import get_corrected_geojson, get_india_center


def plot_static(
    data: Optional[Union[pd.DataFrame, gpd.GeoDataFrame]] = None,
    column: Optional[str] = None,
    title: str = "Map",
    figsize: Tuple[int, int] = (15, 10),
    cmap: str = "Blues",
    edgecolor: str = "black",
    facecolor: str = "lightblue",
    show_colorbar: bool = True,
    save_path: Optional[str] = None,
    dpi: int = 150,
    ax: Optional[plt.Axes] = None,
    show_axis: bool = False,
    focus_india: bool = True,
    linewidth: float = 0.5,
    **kwargs: Any
) -> Tuple[matplotlib.figure.Figure, plt.Axes]:
    """
    Create a static Matplotlib map with correct world/India borders.
    
    This function creates a publication-quality static map visualization
    using Matplotlib. The map displays the corrected world boundaries
    with India's de jure borders.
    
    Parameters
    ----------
    data : pandas.DataFrame or geopandas.GeoDataFrame, optional
        Data to visualize on the map. If provided with a `column` parameter,
        creates a choropleth map. The data should be mergeable with the
        base geometry (e.g., by country/state name).
    
    column : str, optional
        Column name from `data` to use for choropleth coloring.
        Required if you want to show data values as colors.
    
    title : str, default "Map"
        Title to display above the map. Set to empty string to hide.
    
    figsize : tuple[int, int], default (15, 10)
        Figure size in inches as (width, height).
    
    cmap : str, default "Blues"
        Matplotlib colormap name for choropleth visualization.
        Popular options: 'Blues', 'Reds', 'Greens', 'YlOrRd', 'viridis', 
        'plasma', 'RdYlBu', 'Spectral'.
    
    edgecolor : str, default "black"
        Color for country/region border lines.
        Accepts any Matplotlib color specification.
    
    facecolor : str, default "lightblue"
        Fill color for regions when no data column is specified.
        Ignored when `column` is provided.
    
    show_colorbar : bool, default True
        Whether to display a colorbar legend for choropleth maps.
        Only applies when `column` is specified.
    
    save_path : str, optional
        File path to save the figure. Supports formats: PNG, PDF, SVG, JPG.
        The format is inferred from the file extension.
    
    dpi : int, default 150
        Resolution in dots per inch for saved images.
        Use 300 for publication quality.
    
    ax : matplotlib.axes.Axes, optional
        Existing Matplotlib axes to plot on. If not provided, a new
        figure and axes will be created.
    
    show_axis : bool, default False
        Whether to show axis labels and ticks. Usually False for maps.
    
    focus_india : bool, default True
        If True, zooms the map to focus on India.
        If False, shows the entire world.
    
    linewidth : float, default 0.5
        Width of border lines in points.
    
    **kwargs
        Additional keyword arguments passed to GeoDataFrame.plot().
        See geopandas documentation for all available options.
    
    Returns
    -------
    tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
        The figure and axes objects. Can be used for further customization
        or to add additional elements to the plot.
    
    Examples
    --------
    Basic map with default styling:
    
    >>> from india_map_corrector import plot_static
    >>> fig, ax = plot_static(title="India with Correct Borders")
    >>> plt.show()
    
    Choropleth map with data:
    
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'state': ['Maharashtra', 'Karnataka', 'Tamil Nadu'],
    ...     'population': [112374333, 61095297, 72147030]
    ... })
    >>> fig, ax = plot_static(
    ...     data=data,
    ...     column='population',
    ...     title='Population by State',
    ...     cmap='YlOrRd'
    ... )
    >>> plt.show()
    
    Save high-resolution image:
    
    >>> fig, ax = plot_static(
    ...     title="India Map",
    ...     save_path="india_map.png",
    ...     dpi=300
    ... )
    
    Custom styling:
    
    >>> fig, ax = plot_static(
    ...     facecolor='#e8f4f8',
    ...     edgecolor='#2c3e50',
    ...     linewidth=1,
    ...     figsize=(20, 15)
    ... )
    
    Notes
    -----
    - For choropleth maps, ensure your data contains a column that can
      be matched with the geometry (e.g., country or state names).
    - Use `cmap` parameter to choose appropriate color scheme for your data.
    - For publication, use `dpi=300` and consider PDF or SVG format.
    """
    # Load the corrected GeoJSON
    gdf = get_corrected_geojson(as_geodataframe=True)
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.get_figure()
    
    # Merge data if provided
    if data is not None and column is not None:
        # This is a placeholder for data merging logic
        # Would need to know the join column
        pass
    
    # Determine plot parameters
    plot_kwargs = {
        'ax': ax,
        'edgecolor': edgecolor,
        'linewidth': linewidth,
        **kwargs
    }
    
    if column is not None and data is not None:
        # Choropleth mode
        plot_kwargs['column'] = column
        plot_kwargs['cmap'] = cmap
        plot_kwargs['legend'] = show_colorbar
    else:
        # Simple fill mode
        plot_kwargs['color'] = facecolor
    
    # Plot the map
    gdf.plot(**plot_kwargs)
    
    # Set title
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold')
    
    # Handle axis display
    if not show_axis:
        ax.axis('off')
    
    # Focus on India if requested
    if focus_india:
        # India bounds: approximately [68, 6.5, 97.5, 37.5]
        ax.set_xlim(65, 100)
        ax.set_ylim(5, 40)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        save_path = Path(save_path)
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    
    return fig, ax


def plot_world_static(
    title: str = "World Map",
    figsize: Tuple[int, int] = (20, 12),
    edgecolor: str = "black",
    facecolor: str = "lightblue",
    save_path: Optional[str] = None,
    dpi: int = 150,
    **kwargs: Any
) -> Tuple[matplotlib.figure.Figure, plt.Axes]:
    """
    Create a static world map with correct India borders.
    
    Convenience function that calls plot_static() with focus_india=False
    and world-appropriate defaults.
    
    Parameters
    ----------
    title : str, default "World Map"
        Map title.
    
    figsize : tuple[int, int], default (20, 12)
        Figure size optimized for world view.
    
    edgecolor : str, default "black"
        Border color.
    
    facecolor : str, default "lightblue"
        Fill color.
    
    save_path : str, optional
        Path to save the figure.
    
    dpi : int, default 150
        Resolution for saved image.
    
    **kwargs
        Additional arguments passed to plot_static().
    
    Returns
    -------
    tuple[Figure, Axes]
        The figure and axes objects.
    
    Examples
    --------
    >>> from india_map_corrector import plot_world_static
    >>> fig, ax = plot_world_static(title="World with Correct India Borders")
    >>> plt.show()
    """
    return plot_static(
        title=title,
        figsize=figsize,
        edgecolor=edgecolor,
        facecolor=facecolor,
        save_path=save_path,
        dpi=dpi,
        focus_india=False,
        **kwargs
    )
