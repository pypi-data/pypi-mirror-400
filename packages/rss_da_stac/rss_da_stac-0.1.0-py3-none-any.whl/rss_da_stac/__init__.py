"""
rss_da_stac: A Python package for working with Sentinel-2 STAC items across different providers
"""

# Import all public functions and classes from utils
from .utils import (
    CDSE,
    ELEMENT84,
    PLANETARYCOMPUTER,
    ItemNotFoundError,
    ProductIdParseError,
    ProviderNotFoundError,
    S2Scene,
    # Exceptions
    S2StacError,
    StacProvider,
    change_processing_level,
    convert_item,
    extract_stac_item_from_tiff,
    get_item_by_id,
    get_provider,
    parse_cdse_s2_id,
    qvf_to_stac,
    stac_to_qvf,
    read_items
)


# Define what gets imported with "from rss_da_stac import *"
__all__ = [
    "StacProvider",
    "S2Scene",
    "CDSE", 
    "ELEMENT84",
    "PLANETARYCOMPUTER",
    "parse_cdse_s2_id",
    "get_provider", 
    "convert_item",
    "change_processing_level",
    "get_item_by_id",
    "stac_to_qvf",
    "qvf_to_stac",
    "extract_stac_item_from_tiff",
    "read_items",
    # Exceptions
    "S2StacError",
    "ProductIdParseError", 
    "ProviderNotFoundError",
    "ItemNotFoundError"
]
