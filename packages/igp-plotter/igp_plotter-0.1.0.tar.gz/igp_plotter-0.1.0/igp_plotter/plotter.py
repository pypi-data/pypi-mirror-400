# igp_plotter/plotter.py

import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import geodatasets


def plot_igp_points(df, title="IGP Coverage"):
    """
    Plot IGP points on world map
    """
    world = gpd.read_file(geodatasets.get_path("naturalearth.land"))

    geometry = [Point(lon, lat) for lon, lat in zip(df["lon"], df["lat"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    ax = world.plot(
        figsize=(12, 10),
        color="lightyellow",
        edgecolor="black",
        linewidth=0.3
    )

    gdf.plot(ax=ax, color="red", markersize=10)
    plt.title(title)
    plt.grid(True)
    plt.show()
