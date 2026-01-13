# IGP Plotter

IGP Plotter is a Python library for decoding SBAS18 IGP masks and
visualizing ionospheric grid point (IGP) coverage using latitude–longitude grids.

## Features
- Decode SBAS18 IGP bit masks
- Map IGP indices to geographic coordinates
- Visualize global IGP coverage
- Designed for GNSS / AAI / CNS research

## Installation
```bash
pip install -e .


## Example
'''python
from igp_plotter import decode_sbas_asc, load_grid, build_igp_dataframe, plot_igp_points

sbas = decode_sbas_asc("15_dec.ASC")
grid = load_grid("grid.csv")

dfs = build_igp_dataframe(sbas, grid)

for (prn, band), df in dfs.items():
    plot_igp_points(df, title=f"PRN {prn} | Band {band}")'''