import os

import requests

from api_classes import PathRequest


def get_blockheight():
    """
    Fetch the current block height from the mempool API.

    Returns:
        int: The current block height.
    """
    return requests.get('https://mempool.space/api/blocks/tip/height', timeout=10).json()


def get_top_nodes(limit):
    with open("top_nodes.txt") as fileobj:
        lines = fileobj.readlines()
        pubkeys = [line.strip("\n") for line in lines]
    if limit:
        pubkeys = pubkeys[:limit]
    return pubkeys


def query_paths_reflex(path_request: PathRequest):
    url = "https://reflex.amboss.space/graphql"
    amount = path_request.amount
    destination = path_request.destination
    origin = path_request.origin

    payload = {
        "query": "query Find_enhanced_path($input: PathfindingInput!) {  getPaths {    find_enhanced_path(input: $input) {      lnd {        fee        hops {          channel          channel_capacity          fee          fee_mtokens          forward          forward_mtokens          public_key          timeout        }        timeout        tokens      }    }  }}",
        "variables": {
            "input": {
                "origin": origin,
                "payment": {
                    "amount": amount,
                    "destination": destination
                }
            }
        }
    }
    headers = {
        'Authorization': f"Bearer {os.getenv('REFLEX_API_KEY')}",
        'content-type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.ok:
        try:
            reflex_path = response.json()['data']['getPaths']['find_enhanced_path']['lnd']
            return reflex_path
        except:
            return None
    else:
        return None


def convert_short_channel_id(short_channel_id):
    """
    Convert a short channel ID back to a long channel ID format.

    Args:
        short_channel_id (str): The short channel ID: 'block_height:block_index:output_index'.

    Returns:
        int: The long channel ID.
    """
    if "x" in short_channel_id:
        parts = short_channel_id.split('x')
    elif ":" in short_channel_id:
        parts = short_channel_id.split(':')
    else:
        raise Exception("unknown sentinel value when converting channel id")
    block_height = int(parts[0])
    block_index = int(parts[1])
    output_index = int(parts[2])
    channel_id = (block_height << 40) + (block_index << 16) + output_index
    return channel_id
