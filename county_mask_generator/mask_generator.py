import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import pandas as pd
import xarray as xr
from .utils import validate_shapefile


class CountyMaskGenerator:
    def __init__(self, shapefile_path: str, county_identifier: str):
        """
        Initializes the mask generator with the county shapefile and identifier.

        Parameters:
        - shapefile_path: Path to the shapefile.
        - county_identifier: Column name to be used as the county identifier (e.g., 'FIPS', 'GEOID').
        """
        self.county_identifier = county_identifier

        # Validate the shapefile, making sure the county identifier exists
        required_columns = [county_identifier]
        if not validate_shapefile(shapefile_path, required_columns):
            raise ValueError(f"Shapefile validation failed. Column '{county_identifier}' is required.")

        # Load the shapefile after validation
        self.counties = self.load_county_shapefile(shapefile_path)

    @staticmethod
    def load_county_shapefile(shapefile_path: str) -> gpd.GeoDataFrame:
        """
        Load the county shapefile and return a GeoDataFrame.
        """
        return gpd.read_file(shapefile_path)

    def generate_grid_points(self, lat_range: tuple = None, lon_range: tuple = None, lat_steps: int = None,
                             lon_steps: int = None):
        """
        Generate grid points for the given latitude and longitude ranges.
        If lat_range and lon_range are not provided, default to covering the entire U.S. based on the shapefile.

        Parameters:
        - lat_range: Tuple (min_lat, max_lat), default None (uses full shapefile extent)
        - lon_range: Tuple (min_lon, max_lon), default None (uses full shapefile extent)
        - lat_steps: Number of steps for latitude grid, default None (calculated if not provided)
        - lon_steps: Number of steps for longitude grid, default None (calculated if not provided)
        """
        # If lat_range and lon_range are not provided, calculate from the shapefile bounds
        if lat_range is None or lon_range is None:
            bounds = self.counties.total_bounds  # Get the min/max lat/lon from the shapefile
            min_lon, min_lat, max_lon, max_lat = bounds

            if lat_range is None:
                lat_range = (min_lat, max_lat)
            if lon_range is None:
                lon_range = (min_lon, max_lon)

        # Set default steps if not provided
        if lat_steps is None:
            lat_steps = 100
        if lon_steps is None:
            lon_steps = 100

        # Generate the latitude and longitude grid
        lat = np.linspace(lat_range[0], lat_range[1], lat_steps)
        lon = np.linspace(lon_range[0], lon_range[1], lon_steps)
        lon_grid, lat_grid = np.meshgrid(lon, lat)

        self.grid_points = pd.DataFrame(
            {'lon': lon_grid.ravel(), 'lat': lat_grid.ravel()}
        )

        return self.grid_points

    def assign_grid_to_county(self) -> pd.DataFrame:
        """
        Assign grid points to counties based on the shapefile using a spatial join.
        """
        # Ensure the CRS matches by reprojecting the counties to match lat/lon grid points CRS (EPSG:4326)
        counties_projected = self.counties.to_crs("EPSG:4326")

        grid_points_gdf = gpd.GeoDataFrame(
            self.grid_points,
            geometry=[Point(xy) for xy in zip(self.grid_points["lon"], self.grid_points["lat"])],
            crs="EPSG:4326"
        )
        # Perform spatial join to assign counties to grid points
        grid_with_counties = gpd.sjoin(grid_points_gdf, counties_projected, how="left", predicate="within")
        self.grid_with_counties = grid_with_counties
        return grid_with_counties

    def create_weight_mask(self) -> xr.Dataset:
        """
        Convert the county assignment to a 2D Xarray Dataset with weights.
        Each grid point's weight is calculated based on the number of points in its assigned county.
        """
        # Get the DataFrame where grid points have been assigned to counties
        grid_with_counties = self.grid_with_counties

        # Count the number of grid points for each FIPS (county)
        fips_counts = grid_with_counties['FIPS'].value_counts().to_dict()

        # Initialize an empty 2D array to store the weights for the lat/lon grid
        lat_len = len(grid_with_counties['lat'].unique())  # Number of unique latitudes
        lon_len = len(grid_with_counties['lon'].unique())  # Number of unique longitudes

        # Create an empty array for weights matching the lat/lon grid shape
        weight_mask = np.zeros((lat_len, lon_len))

        # Create an empty array for FIPS matching the lat/lon grid shape
        fips_array = np.full((lat_len, lon_len), np.nan)

        # Iterate through each row in the grid_with_counties DataFrame
        for idx, row in grid_with_counties.iterrows():
            fips = row['FIPS']

            # Handle NaN FIPS
            if pd.isna(fips):
                print(f"Skipping grid point at lat: {row['lat']}, lon: {row['lon']} due to NaN FIPS")
                continue

            # Get latitude and longitude indices
            lat_idx = np.where(grid_with_counties['lat'].unique() == row['lat'])[0][0]
            lon_idx = np.where(grid_with_counties['lon'].unique() == row['lon'])[0][0]

            # Check FIPS in fips_counts and assign weights
            if fips in fips_counts:
                weight = 1.0 / fips_counts[fips]
            else:
                weight = 0.0  # Assign zero weight if FIPS not found

            # Assign the weight to the grid point
            weight_mask[lat_idx, lon_idx] = weight

            # Assign FIPS to the grid point
            fips_array[lat_idx, lon_idx] = fips

        # Convert the 2D weight array and FIPS array into a Xarray Dataset with lat/lon coordinates
        ds = xr.Dataset(
            {
                'FIPS': (('lat', 'lon'), fips_array),
                'weights': (('lat', 'lon'), weight_mask)
            },
            coords={
                'lat': np.sort(grid_with_counties['lat'].unique()),
                'lon': np.sort(grid_with_counties['lon'].unique())
            }
        )

        return ds
