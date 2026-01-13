def hex_to_208bit_binary(hex_str):
    """
    Converts hex string to binary string
    Preserves leading zeros
    52 hex chars → 208 bits
    """
    return ''.join(f"{int(c, 16):04b}" for c in hex_str)

def get_active_igp_indices(bin_mask):
    """
    Returns list of IGP indices where bit = 1
    """
    return [i+1 for i, bit in enumerate(bin_mask) if bit == "1"]


sbas_dict = {}

with open("15_dec.asc", "r", encoding="utf-8", errors="ignore") as file:
    for line in file:
        line = line.strip()

        if not line.startswith("#SBAS18"):
            continue

        try:
            # Split header and payload
            header, payload_crc = line.split(";", 1)

            # Remove CRC
            payload = payload_crc.split("*", 1)[0]

            fields = payload.split(",")

            prn = int(fields[0])        # PRN
            prn_band = int(fields[2])   # band number 
            igp_mask_hex = fields[4]    # HEX IGP mask

            if 120 <= prn <= 160:
                igp_mask_bin = hex_to_208bit_binary(igp_mask_hex)

                sbas_dict \
                    .setdefault(prn, {}) \
                    .setdefault(prn_band, set()) \
                    .add(igp_mask_bin)

        except (ValueError, IndexError):
            continue


sbas_igp_arrays = {}

for prn in sbas_dict:
    sbas_igp_arrays[prn] = {}

    for band in sbas_dict[prn]:
        sbas_igp_arrays[prn][band] = []

        for bin_mask in sbas_dict[prn][band]:
            igp_array = get_active_igp_indices(bin_mask)
            sbas_igp_arrays[prn][band].append(igp_array)


import csv

with open("grid.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    
import csv

grid = {}

with open("grid.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    # normalize field names
    reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

    for row in reader:
        band = int(row["band"])
        igp  = int(row["igp_mask"])
        lat  = float(row["lat"])
        lon  = float(row["lon"])

        grid[(band, igp)] = (lon,lat)

import os
os.makedirs("output", exist_ok=True)

for prn in sbas_igp_arrays:
    for band in sbas_igp_arrays[prn]:

        igps = set()
        for msg in sbas_igp_arrays[prn][band]:
            igps.update(msg)

        filename = f"output/PRN_{prn}_BAND_{band}.txt"

        with open(filename, "w") as f:
            f.write("IGP,LON,LAT\n")

            for igp in sorted(igps):
                if (band, igp) in grid:
                    lon, lat = grid[(band, igp)]
                    f.write(f"{igp},{lon},{lat}\n")


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import geodatasets
EXCEL_FOLDER = r"C:\Users\yash patel\Desktop\AAI\week1\igp_task\output"

world = gpd.read_file(geodatasets.get_path("naturalearth.land"))


for file in os.listdir(EXCEL_FOLDER):

    if not file.lower().endswith(".xlsx"):
        continue

    excel_path = os.path.join(EXCEL_FOLDER, file)

    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip().str.lower()

    if "lat" not in df.columns or "lon" not in df.columns:
        print(f"Skipping {file} (lat/lon missing)")
        continue

    geometry = [Point(lon, lat) for lat, lon in zip(df["lat"], df["lon"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")


    ax = world.plot(figsize=(12, 10), color="lightyellow", edgecolor="black", linewidth=0.3, )
    gdf.plot(ax=ax, color="red", markersize=10)

    plt.title(file.replace(".xlsx", "")) 
    plt.grid(True)
    plt.show()
