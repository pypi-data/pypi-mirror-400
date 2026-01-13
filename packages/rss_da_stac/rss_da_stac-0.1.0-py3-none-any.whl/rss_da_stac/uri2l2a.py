"""
This module aims to provide a way of mapping from an L1C item to an L2A item.
Turns out that this isn't quite as easy as it sounds, since there can be
more than one satellite, capture date, tile combinations.

When you get two possible ones, you can't automatically work out which one you want.

For example, if you have an esaid like

S2B_MSIL1C_20250917T003659_N0511_R059_T54KZV_20250917T043259

and you want to find the L2A equivalent, you have to choose between
S2B_MSIL2A_20250917T003659_N0511_R059_T54KZV_20250917T044524

and 

S2B_MSIL2A_20250917T003659_N0511_R059_T54KZV_20250917T035150

Notice that the product discrimination times don't match the original 
(20250917T043259). 

The assumption I'm going to make is that the order will be the same. Which
means you need to find the order of the L1C first, Ie get the candidates
sortd by product discrimination times:

S2B_MSIL1C_20250917T003659_N0511_R059_T54KZV_20250917T033704
S2B_MSIL1C_20250917T003659_N0511_R059_T54KZV_20250917T043259

and notice that our match is the _second_ of these. Therefore we
want the _second_ of the L2A candidates. So we want 

S2B_MSIL2A_20250917T003659_N0511_R059_T54KZV_20250917T044524

maybe there is an easier way.

"""
import json
from typing import List, Optional
from pystac import Item, ItemCollection
from pystac_client import Client
import typer 
from rss_da_stac import StacProvider, get_provider
from rss_da_stac import ELEMENT84, CDSE
from rss_da_stac import parse_cdse_s2_id

app = typer.Typer()


def filter_by_id(item_coll: ItemCollection, product_uri: str) -> Item:
    """
    I'm thinking the reliable way to do this is by checking the order 
    in which these have been created from the source of origin.
    so we might need to get both items from copernicus

    Assume product_uri is an l1c style

    we return the index of the matching item assuming we sort
    by product_disc_time

    we search by the datatake start time. Is that going to be correct?

    """
    details = parse_cdse_s2_id(product_uri)
    client = Client.open(ELEMENT84.url)
    collection = ['sentinel-2-l1c']
    datestring = details['datatake_start_time'].strftime("%Y-%m-%d")
    search = client.search(
        collections=collection,
        datetime=datestring,
        query={
            "grid:code": {"eq": details["grid:code"]}
        }
    )
    coll = search.item_collection()
    product_disc_times = []
    product_uris = []
    for item in coll.items:
        thisuril = item.properties['s2:product_uri'].replace('.SAFE','')
        product_uris.append(thisuril)
        itemdetails = parse_cdse_s2_id(thisuril)
        product_disc_times.append(itemdetails['product_disc_time'])
    sorted_uris = [uri for _, uri in sorted(zip(product_disc_times, product_uris))]
    index = sorted_uris.index(product_uri)

    # now sort our original item_coll 
    # since l2a for both cdse and element84 include the product_disc_time
    # in the id then we can just sort the ids
    ids = [item.id for item in item_coll]
    # if they are cdse style then use parse
    if get_provider(item_coll.items[0]) == CDSE:
        product_disc_times = [parse_cdse_s2_id(id)['product_disc_time'] for id in ids]
    else:
        # you need to do it via 
        product_disc_times = [parse_cdse_s2_id(item.properties['s2:product_uri'])['product_disc_time'] for item in item_coll.items]
    # sort the item
    sorted_items = [item for _, item in sorted(zip(product_disc_times, item_coll.items))]
    return sorted_items[index]



def product_uri_to_l2a(product_uri: str, dst_provider: StacProvider=ELEMENT84) -> Item:
    """ 
    given a product uri, like 'S2B_MSIL1C_20250917T003659_N0511_R059_T54KZV_20250917T043259'
    get the equivalent as an element84 s2l2a
    
    """
    details = parse_cdse_s2_id(product_uri)
    level = 'l2a'
    client = Client.open(dst_provider.url)
    collection = dst_provider.__getattribute__(level)
    #datestring = details['product_disc_time'].strftime("%Y-%m-%d")
    datestring = details['datatake_start_time'].strftime("%Y-%m-%d")
    search = client.search(
        collections=[collection],
        datetime=datestring,
        query={
            "grid:code": {"eq": details["grid:code"]}
        }
    )
    coll = search.item_collection()
    # now filter if needed
    if len(coll.items) == 1:
        selitem = coll.items[0]
        return selitem
    if len(coll.items) > 1:
        sel_item = filter_by_id(coll, product_uri)
        return sel_item
    return None


@app.command()
def updateproduct(
    uris: List[str] = typer.Argument(None, help="One or more valid S2 L1C product uris"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="File containing S2 L1c product uris (one per line)"),
    provider: str = typer.Option('element84', '--provider', help="STAC provider: element84, or CDSE"),
):
    """
    given s1c esa ids, convert to s2l2a and change provider to element84
    
    """
    match provider.lower():
        case 'element84':
            stac_prov = ELEMENT84
        case 'copernicus' | 'cdse':
            stac_prov = CDSE
        case _:
            typer.echo(f"Error: provider '{provider}' not recognised. Use 'element84', 'planetary-computer', or 'CDSE'.", err=True)
            raise typer.Exit(1)

    if uris:
        product_uris = list(uris)  # Start with filenames from command-line arguments
    else:
        product_uris = []
    if file:
        try:
            with open(file, 'r') as f:
                file_lines = [line.strip() for line in f if line.strip()]  # Read non-empty lines
                product_uris.extend(file_lines)  # Add filenames from the file
        except Exception as e:
            typer.echo(f"Error reading file '{file}': {e}", err=True)
            raise typer.Exit(1)
    
    # Process each product uri file and collect the resulting STAC Items
    items = []
    for uri in product_uris:
        try:
            item = product_uri_to_l2a(uri, dst_provider=stac_prov)
            items.append(item)
        except Exception as e:
            typer.echo(f"Error processing uri '{uri}': {e}", err=True)
            raise typer.Exit(1)
    item_collection = ItemCollection(items=items)
    output = json.dumps(item_collection.to_dict())
    print(output)

if __name__ == "__main__":
    app()
