"""Retrieve information from OpenSea."""

import requests

_OPENSEA_URL = "https://api.opensea.io/api/v1/assets"
ARTBLOCK_CONTRACT = "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270"


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def retrieve_assets(token_ids: list, contract: str) -> list:
    """Get list of token_ids from contract from OpenSea and return those assets as a
    list.
    """
    # (Could be implemented as a generator. However, returning the full list makes
    # debugging / rerunning w/o hitting the API easier.)
    querystring = {
        "asset_contract_address": contract,
    }
    assets = []
    for token_ids in chunks(token_ids, 20):
        print(".", end="")
        querystring["token_ids"] = token_ids
        response = requests.request("GET", _OPENSEA_URL, params=querystring)
        response.raise_for_status()
        assets.extend(response.json()["assets"])
    print(f" -- All {len(assets)} assets retrieved.")
    return assets
