import geopandas as gpd


def validate_shapefile(shapefile_path: str, required_columns: list) -> bool:
    """
    Validate if the shapefile exists and contains the necessary fields.

    Parameters:
    - shapefile_path: Path to the shapefile.
    - required_columns: List of column names that must exist in the shapefile.

    Returns:
    - True if the shapefile is valid, False otherwise.
    """
    try:
        counties = gpd.read_file(shapefile_path)

        # Print available columns in the shapefile
        print(f"Available columns in shapefile: {counties.columns.tolist()}")

        # Check if required columns are present
        for column in required_columns:
            if column not in counties.columns:
                print(f"Error: Missing required column '{column}' in shapefile.")
                return False

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
