import json
import logging
import sys
from typing import Optional, List

import typer
from pystac import Item, ItemCollection, STACTypeError

import rss_da_stac


def setup_logging(verbose: int):
    """Setup logging based on verbosity level."""
    if verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    else:  # verbose >= 2
        level = logging.DEBUG
    
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        stream=sys.stderr  # Log to stderr so it doesn't interfere with JSON output to stdout
    )


def read_item(src: Optional[str] = None) -> ItemCollection:
    """
    Get JSON data either from file or stdin pipe.
    Should work for either item or itemcollection

    this is almost a duplicate of rss_da_stac.read_items which
    might cause confusion
    """
    if src:
        # Read from file
        try:
            item = Item.from_file(src)
            item_coll = ItemCollection(items=[item])
        except STACTypeError:
            item_coll = ItemCollection.from_file(src)
    else:
        stdin_data = sys.stdin.read()
        jsondata = json.loads(stdin_data)
        try:
            item = Item.from_dict(jsondata)
            item_coll = ItemCollection(items=[item])
        except STACTypeError:
            item_coll = ItemCollection.from_dict(jsondata)
    return item_coll

app = typer.Typer()

@app.callback()
def main(
    verbose: int = typer.Option(0, "-v", "--verbose", count=True, 
                               help="Increase verbosity. Use -v for info, -vv for debug")
):
    """
    CLI tool for STAC item processing.
    
    Use -v for info logging, -vv for debug logging.
    """
    setup_logging(verbose)

@app.command()
def qvf2item(
    qvfnames: List[str] = typer.Argument(None, help="One or more valid S2 QVF filenames"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="File containing QVF filenames (one per line)"),
    provider: str = typer.Option('element84', '--provider', help="STAC provider: element84, planetary-computer, or CDSE"),
    level: str = typer.Option('l2a', '--level', help="Processing level (l2a, l2apre, or l1c)"),
    geom: Optional[str] = typer.Option(None, help="Geometry to help in filtering duplicates"),
    pretty: bool = typer.Option(False, '--pretty', help="Pretty-print the JSON output")
):
    """
    Convert one or more QVF files to a STAC ItemCollection.

    Args:
        qvfnames (List[str]): One or more QVF filenames to process (positional arguments).
        file (Optional[str]): Path to a file containing QVF filenames (one per line).
        provider (str): The STAC provider (element84, planetary-computer, or CDSE).
        level (str): The processing level (l2a, l2apre, or l1c).
        pretty (bool): Whether to pretty-print the JSON output.
    """

    # Combine filenames from command-line arguments and file (if provided)
    if qvfnames:
        filenames = list(qvfnames)  # Start with filenames from command-line arguments
    else:
        filenames = []
    if file:
        try:
            with open(file, 'r') as f:
                file_lines = [line.strip() for line in f if line.strip()]  # Read non-empty lines
                filenames.extend(file_lines)  # Add filenames from the file
        except Exception as e:
            typer.echo(f"Error reading file '{file}': {e}", err=True)
            raise typer.Exit(1)

    # Ensure at least one filename is provided
    if not filenames:
        typer.echo("Error: No QVF filenames provided. Use positional arguments or the --file option.", err=True)
        raise typer.Exit(1)

    # Map provider to STAC provider constants
    match provider.lower():
        case 'element84':
            stac_prov = rss_da_stac.ELEMENT84
        case 'copernicus' | 'cdse':
            stac_prov = rss_da_stac.CDSE
        case 'planetary-computer' | 'planetary_computer' | 'planetarycomputer':
            stac_prov = rss_da_stac.PLANETARYCOMPUTER
        case _:
            typer.echo(f"Error: provider '{provider}' not recognised. Use 'element84', 'planetary-computer', or 'CDSE'.", err=True)
            raise typer.Exit(1)

    # Process each QVF file and collect the resulting STAC Items
    items = []
    for qvfname in filenames:
        try:
            itemcoll = rss_da_stac.qvf_to_stac(qvfname, dst_provider=stac_prov, level=level, geom=geom)
            items.extend(itemcoll.items)
        except Exception as e:
            typer.echo(f"Error processing QVF file '{qvfname}': {e}", err=True)
            raise typer.Exit(1)

    # Create an ItemCollection from the collected items
    item_collection = ItemCollection(items=items)
    output = json.dumps(item_collection.to_dict(), indent=4 if pretty else None)
    print(output)



@app.command()
def item2qvf(json_src: Optional[str] = typer.Argument(None, help="JSON file path"),
             stage: str = typer.Option("adc", "--stage", help="Stage parameter")):
    """
    Given a stac item or itemcollection, provide the equivalent qvf compliant
    name for each item. Use the option '--stage' to set the output stage

    Example

    rss_da_stac qvf2item cfmsre_t56kkv_20221223_adbm6.tif|s2stac item2qvf  --stage adc
    
    """
    item_coll = read_item(json_src)
    for item in item_coll.items:
        qvfname = rss_da_stac.stac_to_qvf(item, stage=stage)
        print(qvfname)

@app.command()
def item2item(json_src: Optional[str] = typer.Argument(None, help="JSON file path"),
             provider: str = typer.Option('element84', '--provider', help="STAC provider: element84 or CDSE")): 
    """Convert item to item format."""
    match provider.lower():
        case 'element84':
            stac_prov = rss_da_stac.ELEMENT84
        case 'copernicus':
            stac_prov = rss_da_stac.CDSE
        case 'cdse':
            stac_prov = rss_da_stac.CDSE
        case _:
            typer.echo(f"Error: provider '{provider}' not recognised. Use 'element84' or 'CDSE'", err=True)
            raise typer.Exit(1)
        
    item_coll = read_item(json_src)
    new_items = []
    for item in item_coll.items:
        newitem = rss_da_stac.convert_item(item, stac_prov)
        new_items.append(newitem)
    new_item_coll = ItemCollection(items=new_items)
    print(json.dumps(new_item_coll.to_dict()))


@app.command()
def relevel(json_src: Optional[str] = typer.Argument(None, help="JSON file path")):
    item_coll = read_item(json_src)
    new_items = []
    for item in item_coll.items:
        newitem = rss_da_stac.change_processing_level(item)
        new_items.append(newitem)
    new_item_coll = ItemCollection(items=new_items)
    print(json.dumps(new_item_coll.to_dict()))



@app.command()
def histitem(tif_file: str = typer.Argument(..., help="geotiff with item in metadata")):
    item = rss_da_stac.extract_stac_item_from_tiff(tif_file)
    print(json.dumps(item.to_dict(transform_hrefs=False)))
    

@app.command()
def cat(
    files: List[str] = typer.Argument(..., help="List of JSON file paths to concatenate")
):
    """
    Concatenate items from a list of files into a single ItemCollection.

    Args:
        files (List[str]): A list of file paths containing STAC Items or ItemCollections.
    """
    all_items = []
    for fname in files:
        all_items += read_item(fname).items  # Read items from each file and add to the list
    icoll = ItemCollection(items=all_items)
    print(json.dumps(icoll.to_dict()))  # Output the concatenated ItemCollection as JSON


if __name__ == "__main__":
    app()
