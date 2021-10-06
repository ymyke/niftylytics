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

#
# %% Let's get all the Meridians at once:
import requests

meridian_ids = list(range(163000000, 163001000))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_meridians():
    querystring = {
        "order_direction": "desc",
        "asset_contract_address": "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
    }
    assets = []
    for token_ids in chunks(meridian_ids, 20):
        print("Getting more assets...")
        querystring["token_ids"] = token_ids
        response = requests.request("GET", opensea_url, params=querystring)
        response.raise_for_status()
        assets.extend(response.json()["assets"])
    print(f"All {len(assets)} assets retrieved.")
    return assets


meridians = get_meridians()

# %% Add probabilities and prices:
import math
for m in meridians:
    m["probability"] = math.prod([t["trait_count"]/1000 for t in m["traits"]]) * 1000
    if m["sell_orders"] is None:
        m["price"] = "-"
    else:
        so = m["sell_orders"][0]
        m["price"] = float(so["current_price"]) / 10 ** int(so["payment_token_contract"]["decimals"])

#%% Show all sorted by probability:
i=1000
for m in sorted(meridians, key=lambda x: x["probability"], reverse=True):
    print(f"{i:4d} {m['name']:>14s}: {m['probability']:1.5f} {str(m['price']):>6s} {m['permalink']}")
    i -= 1

# %% Show only the ones that have a price, sorted by price:
for m in sorted(meridians, key=lambda x: float(x["price"]) if x["price"] != "-" else float("inf"), reverse=True):
    if m["price"] != "-":
        print(f"{m['name']:>14s}: {m['probability']:1.5f} {str(m['price']):>6s} {m['permalink']}")


# FIXME: Also check the past transactions
# %%