# igp_plotter/processor.py

import pandas as pd


def build_igp_dataframe(sbas_data, grid):
    """
    Convert decoded SBAS + grid into DataFrames
    Returns: dict[(prn, band)] -> DataFrame
    """
    result = {}

    for prn in sbas_data:
        for band in sbas_data[prn]:

            rows = []
            for igp in sorted(sbas_data[prn][band]):
                if (band, igp) in grid:
                    lon, lat = grid[(band, igp)]
                    rows.append({
                        "prn": prn,
                        "band": band,
                        "igp": igp,
                        "lon": lon,
                        "lat": lat
                    })

            result[(prn, band)] = pd.DataFrame(rows)

    return result
