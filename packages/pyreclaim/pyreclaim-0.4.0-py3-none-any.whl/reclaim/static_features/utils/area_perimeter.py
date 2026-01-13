import numpy as np
from shapely.ops import transform

def calculate_length_area_meters(geometry, area= True):
    """
    Calculate the length and area of a geometry in meters and square meters using
    approximate conversion factors based on the geometry's centroid latitude.

    Parameters:
    geometry (shapely.geometry): Geometry in WGS84 (EPSG:4326) to calculate length and area.

    Returns:
    tuple: (length in meters, area in square meters)
    """
    # Get centroid for latitude reference
    centroid = geometry.centroid
    reference_latitude = centroid.y  # latitude of the centroid

    # Conversion factors
    lat_factor = 111_000  # meters per degree latitude
    lon_factor = 111_320 * np.cos(np.radians(reference_latitude))  # meters per degree longitude at given latitude

    # Transform function to scale degrees to meters
    def scale_degrees_to_meters(x, y):
        return (x * lon_factor, y * lat_factor)

    # Scale geometry from degrees to meters using the conversion factors
    scaled_geometry = transform(scale_degrees_to_meters, geometry)
    
    # Calculate length and area in meters and square meters
    length_meters = scaled_geometry.length
    if area: 
        area_square_meters = scaled_geometry.area
        return length_meters, area_square_meters
    else:
        return length_meters