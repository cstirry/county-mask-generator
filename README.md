# CountyMaskGenerator

The `CountyMaskGenerator` package provides tools to generate spatial weight mask for U.S. counties, which can be used to 
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
mask_generator = CountyMaskGenerator(SHAPEFILE_PATH, county_identifier="FIPS")
mask_generator.generate_grid_points(lat_range=(lat.min(), lat.max()), lon_range=(lon.min(), lon.max()), lat_steps=len(lat), lon_steps=len(lon))
mask_generator.assign_grid_to_county()
county_mask = mask_generator.create_weight_mask()
county_mask.to_netcdf(OUTPUT_PATH)
```
