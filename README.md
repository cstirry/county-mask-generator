# CountyMaskGenerator

The `CountyMaskGenerator` package provides a module to generate spatial weight mask for U.S. counties, which can be used to 
regrid netCDF latitude/longitude data to county-level resolution.

## Installation

You can install the `CountyMaskGenerator` package via `pip` from GitHub:

```bash
pip install git+https://github.com/cstirry/county-mask-generator.git
```

## Usage
To use the CountyMaskGenerator, you will need a shapefile containing county boundaries. An option is downloading the most recent U.S. Counties shapefile from the National Weather Service (https://www.weather.gov/gis/AWIPSShapefiles)

CountyMaskGenerator allows you to generate an Xarray dataset that can then be applied to aggregate and regrid lat/lon data.

## Example
```bash
from county_mask_generator import CountyMaskGenerator

SHAPEFILE_PATH = "data/c_05mr24.shp"
OUTPUT_PATH = "data/mask.nc"

lat_min, lat_max = 39.0, 39.5 # Baltimore
lon_min, lon_max = -77.0, -75.0 # Baltimore
lat_steps = int(((lat_max - lat_min) * 111)/5)
lon_steps = int(((lon_max - lon_min) * 85)/5)

mask_generator = CountyMaskGenerator(SHAPEFILE_PATH, county_identifier="FIPS")
mask_generator.generate_grid_points(lat_range=(lat_min, lat_max), lon_range=(lon_min, lon_max), lat_steps=lat_steps, lon_steps=lon_steps)
mask_generator.assign_grid_to_county()
county_mask = mask_generator.create_weight_mask()
county_mask.to_netcdf(OUTPUT_PATH)


# VISUALIZE RESULTS ---------------------
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Convert xarray dataset to a DataFrame
df = county_mask.to_dataframe().reset_index()
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))

# Load the county shapefile
counties_shapefile = gpd.read_file(SHAPEFILE_PATH)
filtered_counties = counties_shapefile.cx[lon_min:lon_max, lat_min:lat_max]

# Convert xarray dataset to a DataFrame
df = county_mask.to_dataframe().reset_index()
gdf = gpd.GeoDataFrame(
    df,  # Assuming 'df' was created from your xarray dataset
    geometry=gpd.points_from_xy(df.lon, df.lat),
    crs="EPSG:4326"
)

# Plot the filtered counties and overlay the filtered grid points
fig, ax = plt.subplots(figsize=(10, 7))
filtered_counties.plot(ax=ax, edgecolor='black', facecolor='none')
filtered_gdf.plot(ax=ax, column='weights', legend=True, cmap='OrRd')
plt.show()
```