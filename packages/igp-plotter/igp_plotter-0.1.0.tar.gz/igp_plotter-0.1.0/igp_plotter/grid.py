# igp_plotter/grid.py

import csv


def load_grid(grid_csv_path):
    """
    Load grid.csv
    Returns: dict[(band, igp)] = (lon, lat)
    """
    grid = {}

    with open(grid_csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

        for row in reader:
            band = int(row["band"])
            igp = int(row["igp_mask"])
            lat = float(row["lat"])
            lon = float(row["lon"])

            grid[(band, igp)] = (lon, lat)

    return grid
