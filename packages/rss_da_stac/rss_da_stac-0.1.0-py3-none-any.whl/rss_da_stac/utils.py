"""
rss_da_stac: A Python package for working with Sentinel-2 STAC items across different providers
"""

import base64
import json
import logging
import re
import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass
from datetime import datetime, timedelta

from typing import Any, Dict, Optional
from typing import List

import tifftools
from pystac import Item, ItemCollection, STACTypeError
from pystac_client import Client

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class S2Scene:
    """
    Represents a Sentinel-2 scene identifier with validation.

    Attributes:
        s2scene (str): The Sentinel-2 scene identifier.

    Methods:
        validate_s2scene(value: str) -> str : Class method to validate
            the s2scene identifier format, ensuring it follows either
            'tXXYYY' format or the 'MGRS-XXYYY' format.

    
    Examples:
        Using positional argument:
            scene = S2Scene('MGRS-32TNL')

        Using keyword argument:
            scene = S2Scene(s2scene='t01cdn')

    """
    s2scene: str
    def __post_init__(self):
        value = self.s2scene
        if value.upper().startswith('MGRS-'):
            value = value[5:]  # Remove the 'MGRS-' prefix
            if len(value) == 5 and all(part.isalnum() for part in value):
                return f't{value.lower()}'
            else:
                raise ValueError(f'S2 scene format must be either "tXXYYY" or "MGRS-XXYYY", received: {value}')
        if len(value) == 6 and value.startswith('t') and all(part.isalnum() for part in value[1:]):
            return value.lower()
        else:
            raise ValueError(f'S2 scene format must be either "tXXYYY" or "MGRS-XXYYY", received: {value}')

    def qvf_style(self):
        if self.s2scene.upper().startswith('MGRS-'):
            return f"t{self.s2scene[5:].lower()}"
        else:
            return(self.s2scene)

    def mgrs_style(self):
        if self.s2scene.startswith('t'):
            return f"MGRS-{self.s2scene[1:].upper()}"
        else:
            return(self.s2scene)



@dataclass
class StacProvider:
    """Represents a STAC provider with its endpoints and collection names."""
    name: str
    url: str
    l1c: str 
    l2a: str
    l2apre :str
    l2aold :str
    mgrs_tile: str 

    def __post_init__(self):
        """Validate provider configuration."""
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL for provider {self.name}: {self.url}")


# Provider configurations
CDSE = StacProvider(
    'CDSE', 
    url="https://stac.dataspace.copernicus.eu/v1", 
    l1c='sentinel-2-l1c', 
    l2a="sentinel-2-l2a",
    l2apre="sentinel-2-l2a",
    l2aold="sentinel-2-l2a",
    mgrs_tile="grid:code"
)

ELEMENT84 = StacProvider(
    'Element84', 
    url="https://earth-search.aws.element84.com/v1",
    l1c='sentinel-2-l1c',
    l2a='sentinel-2-c1-l2a',
    l2apre='sentinel-2-pre-c1-l2a',
    l2aold="sentinel-2-l2a",
    mgrs_tile="grid:code"
)


PLANETARYCOMPUTER = StacProvider(
    'planetary-computer', 
    url="https://planetarycomputer.microsoft.com/api/stac/v1/",
    l1c=None,
    l2a='sentinel-2-l2a',
    l2apre=None,
    l2aold=None,
    mgrs_tile="s2:mgrs_tile"
    )


#https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a


class S2StacError(Exception):
    """Base exception for rss_da_stac operations."""
    pass


class ProductIdParseError(S2StacError):
    """Raised when a Sentinel-2 product ID cannot be parsed."""
    pass


class ProviderNotFoundError(S2StacError):
    """Raised when a provider cannot be determined from an item."""
    pass


class ItemNotFoundError(S2StacError):
    """Raised when an item cannot be found in a STAC catalog."""
    pass


def parse_cdse_s2_id(product_id: str) -> Dict[str, Any]:
    """
    Parse Sentinel-2 product ID to extract key metadata.
    
    Format: S2A_MSIL1C_20170118T001201_N0204_R073_T55HED_20170118T001250[.SAFE]
    This is the CDSE format.
    
    Args:
        product_id: Sentinel-2 product identifier
        
    Returns:
        Dictionary containing parsed metadata
        
    Raises:
        ProductIdParseError: If the product ID format is invalid
    """
    if not isinstance(product_id, str):
        raise ProductIdParseError(f"Product ID must be a string, got {type(product_id)}")
    
    # Remove .SAFE suffix if present
    clean_id = product_id.replace('.SAFE', '')
    
    # Parse using regex
    pattern = r'S2([ABC])_(MSIL1C|MSIL2A)_(\d{8}T\d{6})_N\d{4}_R(\d{3})_T(\w{5})_(\d{8}T\d{6})'
    match = re.match(pattern, clean_id)
    
    if not match:
        raise ProductIdParseError(f"Could not parse product ID: {product_id}")
    
    satellite = match.group(1)  # A, B, or C
    s2level = match.group(2)    # MSIL1C or MSIL2A
    datatake_start_time = match.group(3)  # 20170118T001201
    relative_orbit = match.group(4)  # 073
    tile_id = match.group(5)    # 55HED
    product_disc_time = match.group(6)
    # Convert sensing time to datetime
    try:
        datatake_start_time = datetime.strptime(datatake_start_time, '%Y%m%dT%H%M%S')
    except ValueError as e:
        raise ProductIdParseError(f"Invalid sensing time format in {product_id}: {e}")
    try:
        product_disc_time = datetime.strptime(product_disc_time, '%Y%m%dT%H%M%S')
    except ValueError as e:
        raise ProductIdParseError(f"Invalid sensing time format in {product_id}: {e}")
    
    return {
        'satellite': satellite,
        'datatake_start_time': datatake_start_time,
        's2level': s2level,
        'relative_orbit': relative_orbit,
        'grid:code': f"MGRS-{tile_id}",
        'tile_id': tile_id,
        'product_disc_time': product_disc_time,
        'original_id': product_id
    }


def get_provider(item: Item) -> Optional[StacProvider]:
    """
    Determine the STAC provider for a given item.
    
    Args:
        item: STAC Item to analyze
        
    Returns:
        StacProvider instance or None if provider cannot be determined
    """
    if not isinstance(item, Item):
        raise TypeError(f"Expected pystac.Item, got {type(item)}")
    
    if not item.self_href:
        logger.warning(f"Item {item.id} has no self_href")
        return None
    for link in item.links:
        if link.target.startswith('https://earth-search.aws.element84.com/'):
            return ELEMENT84
        if link.target.startswith('https://stac.dataspace.copernicus.eu'):
            return CDSE
        if link.target.startswith('https://planetarycomputer.microsoft.com/'):
            return PLANETARYCOMPUTER
    logger.warning(f"Unknown provider for URL: {item.self_href}")
    return None


def convert_item(item: Item, dst_provider: StacProvider, timeout_hours: int = 1) -> Optional[Item]:
    """
    Convert a STAC item from one provider to another.
    
    Args:
        item: Source STAC Item
        dst_provider: Target provider
        timeout_hours: Time window to search for matching items
        
    Returns:
        Converted STAC Item or None if not found
        
    Raises:
        ProviderNotFoundError: If source provider cannot be determined
        S2StacError: If collection type cannot be matched
    """
    src_provider = get_provider(item)
    if src_provider is None:
        raise ProviderNotFoundError(f"Cannot determine provider for item {item.id}")
    
    # Determine target collection
    if src_provider.l2a == item.collection_id:
        collection = dst_provider.l2a
    elif src_provider.l2aold == item.collection_id:
        collection = dst_provider.l2aold
    elif src_provider.l1c == item.collection_id:
        collection = dst_provider.l1c
    else:
        # 
        raise S2StacError(f"Collection {item.collection_id} not matched for provider {src_provider.name}")
    
    # Search for matching item
    try:
        client = Client.open(dst_provider.url)
        start_time = item.datetime - timedelta(hours=timeout_hours)
        end_time = item.datetime + timedelta(hours=timeout_hours)
        grid_code_key = src_provider.__getattribute__('mgrs_tile')
        grid_code = item.properties.get(grid_code_key)
        if src_provider.name == 'planetary-computer':
            grid_code = f"MGRS-{grid_code}"

        dst_code_key = dst_provider.__getattribute__('mgrs_tile')
        dst_grid_code = grid_code
        if dst_provider.name == 'planetary-computer':
            dst_grid_code = dst_grid_code.replace("MgRS-",'')
        search = client.search(
            collections=[collection],
            datetime=[start_time, end_time],
            query={
                dst_code_key: {"eq": dst_grid_code}
            }
        )
        
        coll = search.item_collection()
        items = list(coll.items)
        
        if not items:
            logger.warning(f"No {dst_provider.name} product found for item {item.id}")
            return None
            
        if len(items) > 1:
            # we filter
            logger.info(f"Multiple {dst_provider.name} products found for item {item.id}, filtering by geom")
            selitem = filter_items(items, item.geometry)
            return selitem
        return items[0]
        
    except Exception as e:
        logger.error(f"Error searching {dst_provider.name} for item {item.id}: {e}")
        raise S2StacError(f"Failed to search provider {dst_provider.name}: {e}")


def change_processing_level(item: Item, timeout_hours: int = 1) -> Optional[Item]:
    """
    Convert an item between L1C and L2A processing levels within the same provider.
    
    Args:
        item: Source STAC Item
        timeout_hours: Time window to search for matching items
        
    Returns:
        Item with different processing level or None if not found
        
    Raises:
        ProviderNotFoundError: If source provider cannot be determined
        S2StacError: If collection type cannot be matched
    """
    src_provider = get_provider(item)
    if src_provider is None:
        raise ProviderNotFoundError(f"Cannot determine provider for item {item.id}")
    
    # Determine target collection (opposite level)
    if item.collection_id in [src_provider.l2a,  src_provider.l2aold]:
        collection = src_provider.l1c
    elif src_provider.l1c == item.collection_id:
        collection = src_provider.l2a
    else:
        raise S2StacError(f"Collection {item.collection_id} not matched for provider {src_provider.name}")
    
    try:
        client = Client.open(src_provider.url)
        start_time = item.datetime - timedelta(hours=timeout_hours)
        end_time = item.datetime + timedelta(hours=timeout_hours)
        
        search = client.search(
            collections=[collection],
            datetime=[start_time, end_time],
            query={
                "grid:code": {"eq": item.properties.get('grid:code')}
            }
        )
        
        coll = search.item_collection()
        items = list(coll.items)
        
        if not items:
            logger.warning(f"No {src_provider.name} product found for item {item.id}")
            return None
            
        if len(items) > 1:
            logger.warning(f"Multiple {src_provider.name} products found for item {item.id}, using first")
            itemids = [item.id for item in items]
            logger.info(itemids)
        
        return items[0]
        
    except Exception as e:
        logger.error(f"Error changing level for item {item.id}: {e}")
        raise S2StacError(f"Failed to change processing level: {e}")


def get_item_by_id(product_id: str, timeout_hours: int = 1) -> Optional[Item]:
    """
    Retrieve a STAC item by its product ID.
    
    Args:
        product_id: Sentinel-2 product identifier
        timeout_hours: Search timeout (unused for ID-based search)
        
    Returns:
        STAC Item or None if not found
        
    Raises:
        S2StacError: If provider cannot be determined from ID
    """
    if not isinstance(product_id, str):
        raise TypeError(f"Product ID must be a string, got {type(product_id)}")
    
    clean_id = product_id.replace('.SAFE', '')
    
    # Determine provider based on ID format

    if 'MSIL2A' in clean_id or 'MSIL1C' in clean_id:
        if len(clean_id.split('_')) == 6:
            src_provider = PLANETARYCOMPUTER
        else:
            src_provider = CDSE
    elif clean_id.endswith('L2A') or clean_id.endswith("L1C"):
        src_provider = ELEMENT84
    else:
        raise S2StacError(f"Cannot determine provider from ID: {product_id}")
    
    try:
        client = Client.open(src_provider.url)
        search = client.search(ids=[clean_id])
        coll = search.item_collection()
        items = list(coll.items)
        
        if not items:
            logger.warning(f"No {src_provider.name} product found for ID: {product_id}")
            return None
            
        return items[0]
        
    except Exception as e:
        logger.error(f"Error retrieving item {product_id}: {e}")
        raise S2StacError(f"Failed to retrieve item {product_id}: {e}")




def stac_to_qvf(item, stage="adb"):
    # TODO: some zone codes are 2 digits
    # we'll try to deal with either element84 or planetary computer style
    # 
    satellite = item.properties['platform']
    try:
        grid_code = item.properties['grid:code']
        tile = S2Scene(grid_code)
    except KeyError:
        grid_code = item.properties['s2:mgrs_tile']
        tile = S2Scene(f"t{grid_code.lower()}")

    when = item.datetime.strftime("%Y%m%d")

    match satellite.lower():
        case "sentinel-2a":
            qsensor = "cemsre"
        case "sentinel-2b":
            qsensor = "cfmsre"
        case "sentinel-2c":
            qsensor = "cgmsre"
        case _:
            raise ValueError(f"satellite {satellite} not recognized")
    # s2scene will be t54kjf
    # so we want the 3rd element
    zonecode = tile.qvf_style()[2]
    qvf_name = f"{qsensor}_{tile.qvf_style()}_{when}_{stage}m{zonecode}.tif"
    return qvf_name


def qvf_to_stac(
    qvfname: str, 
    dst_provider: StacProvider = ELEMENT84, 
    level: str = "l2a",
    geom: Optional[str] = None
) -> ItemCollection:
    """
    Given a qvf name, find the matching stac item according to the stac provider
    eg cfmsre_t56jlq_20170808_adbm6.tif

    Args:
        qvfname: QVF filename to parse
        dst_provider: STAC provider to search
        level: Processing level (e.g., 'l2a')
        geom: Optional geometry as JSON string to filter when there are multiple matches

    Returns:
        ItemCollection with matching STAC items

    Raises:
        ValueError: If satellite identifier is not recognized
    """
    what, where, when, _ = qvfname.split('_')
    satellite = what[1]
    match satellite.lower():
        case "e":
            platform = "sentinel-2a"
        case "f":
            platform = "sentinel-2b"
        case "g":
            platform = "sentinel-2c"
        case _:
            raise ValueError(f"satellite {satellite} not recognized")

    date_format = '%Y%m%d'
    naive_datetime = datetime.strptime(when, date_format)
    datestring = naive_datetime.strftime("%Y-%m-%d")
    
    grid_code = S2Scene(where).mgrs_style()
    # pc uses slightly different format
    if dst_provider.name == 'planetary-computer':
        grid_code = grid_code.replace('MGRS-','')
    grid_code_key = dst_provider.__getattribute__("mgrs_tile")

    client = Client.open(dst_provider.url)
    collection = dst_provider.__getattribute__(level)
    logger.debug(f"{collection=}, {grid_code=}")
    search = client.search(
        collections=[collection],
        datetime=[datestring],
        query={
            grid_code_key: {"eq": grid_code}
        }
    )
    coll = search.item_collection()
    
    # Filter collections since element84 doesn't use 'in'
    filtered_items = []
    for item in coll.items:
        if item.properties.get('platform', '').lower() == platform:
            filtered_items.append(item)
    coll.items = filtered_items

    if len(coll.items) > 1 and geom is not None:
        matching_item = filter_items(coll.items, geom)
        coll.items = [matching_item]
    
    return coll 



def load_polygon_from_geojson(geom_data: str | dict) -> list:
    """
    Load polygon coordinates from GeoJSON-like data structure
    
    Args:
        geom_data: GeoJSON geometry as string or dictionary
        
    Returns:
        List of coordinate pairs [(lon, lat), ...]
    """
    if isinstance(geom_data, str):
        geom_data = json.loads(geom_data)
    
    return geom_data['coordinates'][0]  # Get exterior ring


def point_in_polygon(point: tuple, polygon: list) -> bool:
    """
    Ray casting algorithm to check if point is inside polygon
    
    Args:
        point: (x, y) coordinate
        polygon: List of (x, y) coordinates
        
    Returns:
        True if point is inside polygon
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def polygon_area(coords: list) -> float:
    """
    Calculate polygon area using the Shoelace formula
    
    Args:
        coords: List of (x, y) coordinate pairs
        
    Returns:
        Absolute area of the polygon
    """
    n = len(coords)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0


def calculate_intersection_over_union(poly1: list, poly2: list) -> float:
    """
    Approximate IoU by sampling points within bounding box
    
    Args:
        poly1: First polygon coordinates
        poly2: Second polygon coordinates
        
    Returns:
        Approximate IoU score between 0 and 1
    """
    # Get bounding box of both polygons
    all_x = [p[0] for p in poly1] + [p[0] for p in poly2]
    all_y = [p[1] for p in poly1] + [p[1] for p in poly2]
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Sample points in a grid
    samples = 1000
    grid_size = int(samples ** 0.5)
    
    intersection_count = 0
    union_count = 0
    
    x_step = (max_x - min_x) / grid_size
    y_step = (max_y - min_y) / grid_size
    
    for i in range(grid_size):
        for j in range(grid_size):
            point = (min_x + i * x_step, min_y + j * y_step)
            
            in_poly1 = point_in_polygon(point, poly1)
            in_poly2 = point_in_polygon(point, poly2)
            
            if in_poly1 or in_poly2:
                union_count += 1
                if in_poly1 and in_poly2:
                    intersection_count += 1
    
    if union_count == 0:
        return 0.0
    
    return intersection_count / union_count


def get_largest_polygon(geojson: dict) -> dict:
    """
    Extract the largest polygon from GeoJSON
    
    Args:
        geojson: A GeoJSON dict (Polygon or MultiPolygon)
        
    Returns:
        A GeoJSON Polygon dict with the largest polygon
    """
    geom_type = geojson.get('type')
    
    if geom_type == 'Polygon':
        return geojson
    
    if geom_type == 'MultiPolygon':
        polygons = geojson['coordinates']
        largest_poly = max(polygons, key=lambda p: polygon_area(p[0]))
        return {
            'type': 'Polygon',
            'coordinates': largest_poly
        }
    
    raise ValueError(f"Unsupported geometry type: {geom_type}")



def filter_items(items: List[Item], refgeom: str) -> Item:
    """
    Filter items by geometry similarity, returning the one with highest IoU
    
    In case of IoU ties, returns the item with the most recent 'created' timestamp.
    
    Args:
        items: List of STAC items to filter (must contain at least 1 item)
        refgeom: Reference geometry as JSON string
        
    Returns:
        STAC item with highest IoU score against reference geometry
        
    Raises:
        ValueError: If items list is empty
    """
    if len(items) == 0:
        raise ValueError("Expected at least 1 item for filtering, got 0")
    
    if len(items) == 1:
        return items[0]
    
    if len(items) > 2:
        logger.warning(f"Filtering {len(items)} items, expected a maximum of 2")
    
    refpoly = load_polygon_from_geojson(refgeom)
    
    # Store all items with their IoU scores
    items_with_iou = []
    
    for item in items:
        poly_geom = get_largest_polygon(item.geometry)
        poly = load_polygon_from_geojson(poly_geom)
        iou = calculate_intersection_over_union(poly, refpoly)
        logger.debug(f"{item.id} {iou=}")
        items_with_iou.append((item, iou))
    
    # Find maximum IoU
    max_iou = max(iou for _, iou in items_with_iou)
    
    # Get all items with maximum IoU
    best_items = [item for item, iou in items_with_iou if iou == max_iou]
    
    # Handle ties
    if len(best_items) > 1:
        logger.warning(
            f"Found {len(best_items)} items with identical IoU ({max_iou:.4f}). "
            f"Selecting most recently created item."
        )
        
        # Sort by created timestamp (most recent first)
        best_items.sort(
            key=lambda item: datetime.fromisoformat(
                item.properties['created'].replace('Z', '+00:00')
            ),
            reverse=True
        )
        
        return best_items[0]
    
    return best_items[0]







def extract_stac_item_from_tiff(tif_file: str) -> Item:
    """
    Extract STAC item metadata from a TIFF file.
    
    Args:
        tif_file (str): Path to the TIFF file
        
    Returns:
        pystac.Item: The STAC item object
        
    Raises:
        ValueError: If no SLATS metadata found or metadata cannot be processed
        ET.ParseError: If GDAL metadata XML cannot be parsed
    """
    info = tifftools.read_tiff(str(tif_file))
    
    # should be in ifd 0
    ifd = 0
    ifd_info = info['ifds'][ifd]
    tags = ifd_info.get('tags', {})
    
    gdal_metadata = None
    slats_metadata = None
    
    for tag_name, tag_data in tags.items():
        if isinstance(tag_data, dict) and 'data' in tag_data:
            tag_value = tag_data['data']
            
            # Convert tag data to string if it's bytes or a list
            if isinstance(tag_value, list):
                try:
                    tag_value = ''.join([str(x) for x in tag_value])
                except TypeError:
                    tag_value = str(tag_value)
            elif isinstance(tag_value, bytes):
                tag_value = tag_value.decode('utf-8', errors='ignore')
            
            # Check if this is GDAL metadata XML
            if isinstance(tag_value, str) and tag_value.strip().startswith('<GDALMetadata>'):
                gdal_metadata = tag_value
                break
            # Check if this looks like direct SLATS metadata
            elif ('SLATS_Metadata2_zipped' in str(tag_name) or 
                    (isinstance(tag_value, str) and 'SLATS' in tag_value)):
                slats_metadata = tag_value
                break

    # Parse GDAL metadata XML to find SLATS_Metadata2_zipped
    if gdal_metadata and not slats_metadata:
        try:
            root = ET.fromstring(gdal_metadata)
            for item in root.findall('Item'):
                if item.get('name') == 'SLATS_Metadata2_zipped':
                    slats_metadata = item.text
                    break
        except ET.ParseError as e:
            raise ET.ParseError(f"Error parsing GDAL metadata XML: {e}")
    
    if not slats_metadata:
        raise ValueError("No SLATS metadata found in TIFF file")
    
    # Extract and process metadata
    mdata = slats_metadata
    if mdata.startswith(r"b'"):
        mdata = mdata[2:-1]
        
    try:
        # Decompress and parse
        decompressed = zlib.decompress(base64.b64decode(mdata))
        hobj = json.loads(decompressed)
        json_item = json.loads(hobj['thismeta']['STAC_ITEM'])
        return Item.from_dict(json_item)
    except (zlib.error, base64.binascii.Error, json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Error processing SLATS metadata: {e}")


# concatenate items to create an item collection
# these may in fact be feature collections

def read_items(url: str)-> List[Item]:
    """
    Reads and returns a list of STAC  items from a given URL or file path.

    The input URL or file is expected to represent either a single STAC Item or an ItemCollection.
    If the input is a single Item, it is wrapped in a list. If it is an ItemCollection, all items
    within the collection are returned as a list.

    Args:
        url (str): The URL or file path pointing to a STAC Item or ItemCollection.

    Returns:
        List[Item]: A list of STAC Items.

    Raises:
        STACTypeError: If the input file is not a valid STAC Item or ItemCollection.
    """

    try:
        items = [Item.from_file(url)]
    except STACTypeError:
        jcol = ItemCollection.from_file(url)
        items = jcol.items 
    return items
