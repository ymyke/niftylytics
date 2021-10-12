
# NOTE! 
#
# This bruteforce approach unfortunately doesn't work because the Opensea API doesn't
# allow offsets > 10'000 and there are unfortunately no other filter options that can be
# used to drill down into specific projects.
#
# Here's Opensea's errror message: 
# b'{"offset":["ensure this value is less than or equal to 10000"]}'
#
# The preferred approach to get the tokenids for an Artblock project is to simply lookup
# the entire gallery on artblocks.io and get the first and last piece's tokenid.








#%%
import requests


def get_opensea_collection(collection: str) -> list:
    """Retrieve all assets of collection on OpenSea and return a list of all assets found."""

    def get_page(offset: int):
        """Retrieve one page of 50 assets at offset."""
        opensea_url = "https://api.opensea.io/api/v1/assets"
        querystring = {
            "order_direction": "desc",
            "offset": offset,
            "limit": "50",
            "collection": collection,
        }
        return requests.request("GET", opensea_url, params=querystring)

    assets = []
    offset = 0
    while True:
        print(offset, end=", ")
        response = get_page(offset)
        if not response.ok:
            print(f"\nDone ({response.status_code} {response.reason})")
            break
        assets.extend(response.json()["assets"])
        offset += 50

    return assets


#%%
all_assets = get_opensea_collection("art-blocks-playground")

# %%
which_project = "Fidenza"
assets = [a for a in all_assets if a["name"].startswith(which_project)]
