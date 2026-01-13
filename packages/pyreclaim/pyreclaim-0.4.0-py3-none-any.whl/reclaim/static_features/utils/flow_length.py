import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx  # NetworkX library import

from shapely.geometry import shape, Point, LineString, Polygon, GeometryCollection, MultiLineString, MultiPolygon
from shapely.ops import transform, split, linemerge, unary_union
from shapely.geometry.polygon import orient
from shapely.strtree import STRtree
from shapely.validation import explain_validity


def find_optimal_resolution(geometry, min_resolution=0.0001, max_resolution=0.1, complexity_weight=0.38):
    """
    Estimate an optimal grid resolution for pathfinding within a given geometry.
    
    Parameters:
    - geometry (Polygon or MultiPolygon): The geometry to analyze.
    - min_resolution (float): Minimum allowable resolution.
    - max_resolution (float): Maximum allowable resolution.
    - complexity_weight (float): Weight that determines how much the resolution adapts to complexity.

    Returns:
    - float: Suggested resolution.
    """
    # Handle MultiPolygon by taking the union
    if isinstance(geometry, MultiPolygon):
        geometry = geometry.buffer(0)  # Clean union
    
    area = geometry.area
    perimeter = geometry.length

    if area == 0:
        raise ValueError("Geometry has zero area.")

    avg_scale = np.sqrt(area)
    complexity = perimeter / avg_scale  # Higher means more detail

    # Base resolution proportional to avg scale
    base_resolution = avg_scale * complexity_weight / complexity

    # Clamp to user-defined bounds
    resolution = max(min_resolution, min(base_resolution, max_resolution))
    
    return round(resolution, 5)

def get_largest_polygon(geometry):
    """Return the largest polygon from a Polygon or MultiPolygon"""
    if isinstance(geometry, Polygon):
        return geometry
    elif isinstance(geometry, MultiPolygon):
        return max(geometry.geoms, key=lambda p: p.area)
    else:
        raise ValueError("Input must be a Polygon or MultiPolygon.")
    
def extract_valid_lines(geometry):
    """Ensure that only valid LineString segments are returned, regardless of input geometry type."""
    if isinstance(geometry, LineString):
        return [geometry]
    elif isinstance(geometry, (GeometryCollection, MultiLineString)):
        valid_lines = []
        for geom in geometry.geoms:
            if isinstance(geom, LineString):
                valid_lines.append(geom)
        return valid_lines
    return []

def shape_index(polygon):
    return (polygon.length ** 2) / polygon.area

def compute_initial_tolerance(geometry, fraction=0.005):
    """
    Compute a tolerance based on the size of the geometry.
    Smaller fraction = higher fidelity.
    """
    minx, miny, maxx, maxy = geometry.bounds
    diag = ((maxx - minx)**2 + (maxy - miny)**2)**0.5
    return diag * fraction  # 0.5% of diagonal as tolerance

def clean_narrow_necks(geometry, buffer_fraction=0.002):
    """
    Buffer in and out to remove narrow slivers or necks without overly changing geometry.

    Parameters:
    - geometry: Polygon or MultiPolygon
    - buffer_fraction: Fraction of geometry diagonal to use as buffer width.

    Returns:
    - cleaned geometry
    """
    minx, miny, maxx, maxy = geometry.bounds
    diag = ((maxx - minx)**2 + (maxy - miny)**2)**0.5
    buffer_dist = diag * buffer_fraction
    
    # Inward then outward buffer to remove narrow parts
    cleaned = geometry.buffer(-buffer_dist).buffer(buffer_dist)
    
    # Preserve original geometry if buffer killed it
    if cleaned.is_empty or cleaned.area == 0:
        return geometry
    
    # If result is MultiPolygon, merge it
    return unary_union(cleaned)

def filter_narrow_removed_parts(removed, min_area=0.000001, min_aspect_ratio=2):
    """
    Filter out noisy edge slivers by area and shape.

    Parameters:
    - removed: a Polygon or MultiPolygon
    - min_area: minimum area to be considered significant
    - min_aspect_ratio: minimum elongation to count as a narrow feature

    Returns:
    - MultiPolygon of retained significant narrow parts
    """
    filtered_parts = []

    if isinstance(removed, Polygon):
        candidates = [removed]
    elif isinstance(removed, MultiPolygon):
        candidates = list(removed.geoms)
    else:
        return None

    for geom in candidates:
        if geom.area < min_area:
            continue
        
        if min_aspect_ratio:
            minx, miny, maxx, maxy = geom.bounds
            width = maxx - minx
            height = maxy - miny
            aspect_ratio = max(width, height) / max(min(width, height), 1e-6)

            if aspect_ratio >= min_aspect_ratio:
                filtered_parts.append(geom)
            else:
                pass
        else:
            filtered_parts.append(geom)

    return unary_union(filtered_parts) if filtered_parts else None

def compute_adaptive_buffer_dist(polygon, fraction=0.004):
    """
    Compute an adaptive buffer distance based on polygon scale.

    Parameters:
    - polygon: shapely Polygon or MultiPolygon
    - fraction: proportion of diagonal length (e.g. 0.004 = 0.4%)

    Returns:
    - buffer distance (float)
    """
    minx, miny, maxx, maxy = polygon.bounds
    width = maxx - minx
    height = maxy - miny
    diag = (width**2 + height**2)**0.5

    return fraction * diag

def widen_narrow_parts(polygon, fraction=0.0043, min_area_fraction=1e-8, min_aspect_ratio=None):
    """
    Widen narrow regions removed during negative buffering using adaptive buffer distance.

    Parameters:
    - polygon: shapely Polygon or MultiPolygon
    - fraction: % of bbox diagonal to use for buffer distance
    - min_area_fraction: threshold to remove small slivers (as % of polygon area)
    - min_aspect_ratio: minimum elongation to classify as narrow feature. If None, it is ignored. Default is None. 

    Returns:
    - widened polygon
    """
    if polygon.is_empty or polygon.area == 0:
        return polygon

    buffer_dist = compute_adaptive_buffer_dist(polygon, fraction=fraction)

    # Step 1: Apply inward buffer
    simplified = polygon.buffer(-buffer_dist)

    if simplified.is_empty:
        return polygon  # Avoid error if all geometry disappears

    # Step 2: Re-expand it back
    expanded = simplified.buffer(buffer_dist)

    # Step 3: Find what got lost during shrink-expand (mostly narrow parts)
    removed_narrow_parts = polygon.difference(expanded)

    if removed_narrow_parts.is_empty:
        return polygon

    # Step 4: Filter the narrow parts from removed ones and Slightly buffer them wider
    # 🔍 Filter out noisy slivers
    filtered = filter_narrow_removed_parts(removed_narrow_parts, min_area=min_area_fraction * polygon.area, min_aspect_ratio=min_aspect_ratio)

    if filtered:
        widened = filtered.buffer(buffer_dist)
        widened_polygon = unary_union([polygon, widened])
    else:
        widened_polygon = polygon

    return widened_polygon

def simplify_geometry(polygon, shape_index_threshold=800, max_tolerance_fraction=0.05, narrow_portion='widen'):
    """
    Simplify polygon while preserving topology and ensuring shape index is under control.

    Parameters:
    - polygon: shapely.geometry.Polygon or MultiPolygon
    - shape_index_threshold: Target upper bound for shape index (lower = simpler)
    - max_tolerance_fraction: Max allowed simplification (as % of bounding box diagonal)
    - narrow_portion: 'clean' to remove narrow connections before simplification or 'widen' to widen the narrow connections. Default is 'widen'.

    Returns:
    - simplified polygon
    """
    if polygon.is_empty or polygon.area == 0:
        return polygon

    if narrow_portion=='clean':
        polygon = clean_narrow_necks(polygon)
    else:
        polygon = widen_narrow_parts(polygon)

    original_si = shape_index(polygon)
    if original_si <= shape_index_threshold:
        return polygon  # Already simple enough

    # Initial tolerance from geometry scale
    initial_tolerance = compute_initial_tolerance(polygon, fraction=0.005)
    max_tolerance = compute_initial_tolerance(polygon, fraction=max_tolerance_fraction)
    tolerance = initial_tolerance

    # Iteratively simplify until SI drops or max tolerance is reached
    while tolerance <= max_tolerance:
        simplified = polygon.simplify(tolerance, preserve_topology=True)
        si = shape_index(simplified)

        if si <= shape_index_threshold:
            return simplified

        if simplified.equals_exact(polygon, tolerance / 10):
            break

        tolerance *= 2

    return polygon

def simplify_path(points, geometry):
    if not points:
        return points
    simplified = [points[0]]
    i = 0
    while i < len(points) - 1:
        j = len(points) - 1
        while j > i + 1:
            if geometry.contains(LineString([points[i], points[j]])):
                break
            j -= 1
        simplified.append(points[j])
        i = j
    return simplified

def create_continuous_linestring(a, b, geometry, resolution=0.01):
    """
    Create a continuous LineString between two points that lies entirely within a given geometry.

    Parameters
    ----------
    a : tuple
        The coordinates of the first point (x, y).

    b : tuple
        The coordinates of the second point (x, y).

    geometry : shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        The geometry within which the LineString should be created.

    resolution : float, optional
        The resolution of the grid used for pathfinding. Default is 0.5.

    Returns
    -------
    shapely.geometry.LineString or None
        A continuous LineString between points `a` and `b` that does not cross the exterior
        boundary of the geometry. If it is not possible to create such a LineString, `None` is returned.
    """

    # Ensure the geometry is oriented counter-clockwise
    geometry = orient(geometry, sign=1.0)
    
    # Create a grid over the bounding box of the geometry
    minx, miny, maxx, maxy = geometry.bounds
    
    # Get bounding box dimensions
    width = maxx - minx
    height = maxy - miny

    # Compute aspect ratio
    longer, shorter = max(width, height), min(width, height)
    aspect_ratio = longer / shorter if shorter != 0 else 1

    # Threshold to trigger anisotropic resolution (you can tune this)
    aspect_ratio_threshold = 2

    if aspect_ratio > aspect_ratio_threshold:
        # Elongated shape — adjust resolution
        if width > height:
            x_res = resolution * 2  # make x_res coarser
            y_res = resolution  
        else:
            y_res = resolution * 2 # make y_res coarser
            x_res = resolution 
    else:
        x_res = resolution
        y_res = resolution

    x_coords = np.arange(minx, maxx + x_res, x_res)
    y_coords = np.arange(miny, maxy + y_res, y_res)

    # Create points on the grid and filter those within the geometry
    points = []
    for x in x_coords:
        for y in y_coords:
            p = Point(x, y)
            if geometry.contains(p):
                points.append(p)
    
    # Debug: #Print number of valid points
    #print(f"Number of valid points within the geometry: {len(points)}")

    # Check if any valid points exist
    if not points:
        raise ValueError("No valid points within the geometry. Adjust resolution or check the geometry.")

    # Create a spatial index for the points
    tree = STRtree(points)
     
    # Build a dict of coordinate → Point
    point_dict = {(round(p.x, 6), round(p.y, 6)): p for p in points}
    
    # Create a graph for pathfinding using Dijkstra's algorithm
    graph = nx.Graph()

    # Add nodes to the graph
    for point in points:
        graph.add_node((point.x, point.y))
    
    # Connect adjacent points in the grid that are within the geometry (without STRtree: Old method; not working for sharp narrow turns in polygons)
    # for point in points:
        # x, y = point.x, point.y
        # # possible_neighbors = [(x + dx, y + dy) for dx in [-resolution, 0, resolution] for dy in [-resolution, 0, resolution] if (dx, dy) != (0, 0)]
        # radius = 5  # or 3, depending on resolution and geometry size
        # possible_neighbors = [
        #     (x + dx * x_res, y + dy * y_res)
        #     for dx in range(-radius, radius + 1)
        #     for dy in range(-radius, radius + 1)
        #     if not (dx == 0 and dy == 0)
        # ]
        # for (neighbor_x, neighbor_y) in possible_neighbors:
        #     neighbor = Point(neighbor_x, neighbor_y)
        #     # Then during neighbor search:
        #     coord = (round(neighbor_x, 6), round(neighbor_y, 6))
        #     if coord in point_dict:
        #         line = LineString([point, neighbor])
        #         if geometry.covers(line):
        #             distance = point.distance(neighbor)
        #             #print(f"Adding edge between {point} and {neighbor} with distance {distance}")
        #             graph.add_edge((point.x, point.y), (neighbor.x, neighbor.y), weight=distance)
        
    for point in points:
        # Find nearby geometries within a buffer radius
        search_radius = max(x_res, y_res) * 2.5
        nearby = tree.query(point.buffer(search_radius))
        for idx in nearby:
            neighbor = points[idx]  # Index into your original list
            if point.equals(neighbor):
                continue
            line = LineString([point, neighbor])
            if geometry.covers(line):
                distance = point.distance(neighbor)
                graph.add_edge((point.x, point.y), (neighbor.x, neighbor.y), weight=distance)
    

    # If the graph is empty, return None
    if graph.number_of_nodes() == 0:
        raise ValueError("Graph is empty. No valid paths could be constructed within the geometry.")

    # Convert points a and b to nearest grid points
    start = Point(a)
    end = Point(b)
    
    # Check if the exact point exists in the graph, if not, find the nearest one
    nearest_start = min(graph.nodes, key=lambda n: start.distance(Point(n)), default=None)
    nearest_end = min(graph.nodes, key=lambda n: end.distance(Point(n)), default=None)
    
    if nearest_start is None or nearest_end is None:
        raise ValueError("Could not find nearest grid points within the graph. Adjust resolution or check the geometry.")

    # Find the shortest path within the graph using Dijkstra's algorithm
    try:
        path_coords = nx.dijkstra_path(graph, nearest_start, nearest_end, weight='weight')
        path = [Point(x, y) for x, y in path_coords]
        path.insert(0, start)  # Add the start point
        path.append(end)  # Add the end point
        simplified_path = simplify_path(path, geometry)
        return LineString(simplified_path), graph
        # return LineString(path), graph
    except nx.NetworkXNoPath:
        return None, graph



def find_actual_flow_path(dam_point, reservoir_polygon, inlet_point=None, resolution=None):
    """
    This function finds the actual flow path between a dam point and the inlet of the reservoir boundary within the polygon.

    Args:
        dam_point (Point): The point representing the dam location.
        reservoir_polygon (Polygon): The polygon representing the reservoir boundary.
        inlet_point (Point, optional): The point representing the inlet of the reservoir. If not provided, the farthest point on the simplified reservoir boundary is used.
        resolution (float, optional): The resolution to use for simplifying the reservoir boundary. If not provided, the optimal resolution is found.

    Returns:
        simplified_reservoir (Polygon): The simplified reservoir boundary.
        far_end_point (Point): The farthest point on the simplified reservoir boundary.
        path (LineString): The shortest path between the dam point and the far end point.
        graph (Graph): The graph used for pathfinding.
    """
    # Step 1: Simplify the reservoir boundary
    simplified_reservoir = simplify_geometry(reservoir_polygon)
    
    # Step 2: Find optimal resolution for simplified geometry
    if resolution:
        optimal_resolution = resolution
    else:
        optimal_resolution = find_optimal_resolution(simplified_reservoir)
    
    # Step 3: Identify the farthest point on the simplified boundary if inlet point not given.
    if inlet_point:
        farthest_point = inlet_point
        far_end_point = Point(farthest_point)
    else:
        main_polygon = get_largest_polygon(simplified_reservoir)
        farthest_point = max(main_polygon.exterior.coords, key=lambda coord: dam_point.distance(Point(coord)))
        far_end_point = Point(farthest_point)

    # Step4: Find the shortest path within geometry between dam_point and far_end_point
    path, graph = create_continuous_linestring(dam_point,far_end_point, simplified_reservoir, optimal_resolution)

    return simplified_reservoir,far_end_point, path, graph