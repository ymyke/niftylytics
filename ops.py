#%%
import requests

opensea_url = "https://api.opensea.io/api/v1/assets"


def get_page(offset: int):
    opensea_url = "https://api.opensea.io/api/v1/assets"
    querystring = {
        "order_direction": "desc",
        "offset": offset,
        "limit": "50",
        "collection": "art-blocks-playground",
    }
    return requests.request("GET", opensea_url, params=querystring)


#%%
import time

assets = []
offset = 0
while True:
    print(offset, end=", ")
    response = get_page(offset)
    if not response.ok:
        print(response.status_code)
        break
    assets.extend(response.json()["assets"])
    offset += 50
    time.sleep(0.1)


#%%
x = response.json()
# %%
len(x)

# %%
x.keys()
# %%
len(x["assets"])
# %%
y = x["assets"][0]
# %%
y.keys()
# %%
names = [a["name"] for a in assets]

# %%
meridians = [a for a in assets if a["name"].startswith("Meridian")]
# %%
len(meridians)
# %%
import json

with open("meridians.json", "w") as fout:
    json.dump(meridians, fout)


#%%
def got_trait(asset, trait):
    return trait in [t["value"] for t in asset["traits"]]


len([a for a in meridians if got_trait(a, "Palette: Peninsula")])
# %%
# Find all with sell orders
# Calculate the metric for those
# -> But the information is stale!


#%% Try to get a specific meridian id:
whichtoken = meridians[0]["token_id"]
#%%
querystring = {
    "order_direction": "desc",
    "offset": 0,
    "limit": "50",
    "token_ids": whichtoken,
    "asset_contract_address": "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
}
x = requests.request("GET", opensea_url, params=querystring)
x

#%% Let's try to only get the Meridian ids:
meridian_ids = list(range(163000000, 163001000))

#%%
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#%%

def get_meridians():
    querystring = {
        "order_direction": "desc",
        # "token_ids": meridian_ids[0:3],
        "asset_contract_address": "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
    }
    assets = []
    for token_ids in chunks(meridian_ids, 20):
        querystring["token_ids"] = token_ids
        response = requests.request("GET", opensea_url, params=querystring)
        response.raise_for_status()
        assets.extend(response.json()["assets"])

    return assets

x = get_meridians()


#%% Play around with listing_date:
