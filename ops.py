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
from functools import reduce
import operator

for m in meridians:
    m["probability"] = reduce(operator.mul, [t["trait_count"]/1000 for t in m["traits"]], 1) * 1000
    if m["sell_orders"] is None:
        m["price"] = "-"
    else:
        so = m["sell_orders"][0]
        m["price"] = float(so["current_price"]) / 10 ** int(so["payment_token_contract"]["decimals"])
    if m["last_sale"] is None:
        m["last_price"] = "-"
    else:
        ls = m["last_sale"]
        m["last_price"] = float(ls["total_price"]) / 10 ** int(ls["payment_token"]["decimals"])

def print_asset(a, i="", extended=False):
    if i != "":
        i = str(f"{i:4d}")
    print(f"{i}{a['name']:>14s}: {a['probability']:1.5f} {str(a['price']):>6s} {str(a['last_price'])} {a['permalink']}")
    if extended:
        print("   ", ", ".join(f'{t["value"]} ({float(t["trait_count"])/1000})' for t in a["traits"] if t["value"] != "All Meridians"))


#%% Show all sorted by probability:
i=1000
for m in sorted(meridians, key=lambda x: x["probability"], reverse=True):
    print_asset(m, extended=True)
    i -= 1

# %% Show only the ones that have a price, sorted by price:
for m in sorted(meridians, key=lambda x: float(x["price"]) if x["price"] != "-" else float("inf"), reverse=True):
    if m["price"] != "-":
        print_asset(m, extended=True)

# FIXME: Also check the past transactions
# %%

# %% Dive deeper into certain candidates:
candidate_meridian_ids = ["#589", "#386", "#666", "#799", "#316", "#338", "#609", "#357", "#635", "#834"]
candidates = [m for m in meridians for mid in candidate_meridian_ids if m["name"].endswith(mid)]
for c in sorted(candidates, key=lambda x: x["probability"]):
    print_asset(c, extended=True)

# %%
xx = [m for m in meridians if m["name"].endswith("#386")]
# %%

traitstats = []
for m in meridians:
    traitstats.extend(x["value"] for x in m["traits"] if x["value"].startswith("Style"))
from collections import Counter
c = Counter(traitstats)
c


# %% How to find all meridians with a certain trait:
def find_trait(asset, trait: str):
    for t in asset["traits"]:
        for k in t.keys():
            if t[k] and trait.lower() in str(t[k]).lower():
                return True
    return False

# %%
[m["permalink"] for m in meridians if find_trait(m, "newsprint")]
# %%
