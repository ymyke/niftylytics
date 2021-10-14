"""Some helpers"""

from typing import Union
from functools import reduce
import operator
import pandas as pd
import numpy as np

pd.set_option("display.max_rows", None)


def turn_assets_into_df(assets: list) -> Union[pd.DataFrame, list]:
    """Turn a list of assets as returned by the OpenSea API, grab some of the relevant
    information and turn it all into a dataframe. Return that dataframe along with all
    the traits found.

    This code is geared towards Artblocks and makes the following assumptions:
    - All assets have the same set of traits.
    - Traits are of the form: <trait name>: <trait value>.
    - The code therefore ignores all traits w/o a ":" as they are expected to add no
      value, e.g. "All Fidenzas".
    """

    _tt = []
    for a in assets:

        # Calc probability score:
        prob_score = (
            reduce(operator.mul, [t["trait_count"] / 1000 for t in a["traits"]], 1)
            * 1000
        )

        # Get current price:
        price = price_symbol = np.nan
        if a["sell_orders"] is not None:
            so = a["sell_orders"][0]
            price = float(so["current_price"]) / 10 ** int(
                so["payment_token_contract"]["decimals"]
            )
            price_symbol = so["payment_token_contract"]["symbol"]
            # Convert to ETH if necessary:
            if price_symbol not in ["ETH", "WETH"]:
                price *= float(so["payment_token_contract"]["eth_price"])
                price_symbol = "ETH"

        # Get last price:
        last_price = last_price_symbol = last_sale_date = np.nan
        if a["last_sale"] is not None:
            ls = a["last_sale"]
            last_price = float(ls["total_price"]) / 10 ** int(
                ls["payment_token"]["decimals"]
            )
            last_price_symbol = ls["payment_token"]["symbol"]
            # Convert to ETH if necessary:
            if last_price_symbol not in ["ETH", "WETH"]:
                last_price *= float(ls["payment_token"]["eth_price"])
                last_price_symbol = "ETH"
            last_sale_date = ls["event_timestamp"]

        # Add everything to the table:
        _tt.append(
            [
                a["name"].split("#")[1],
                a["name"],
                price,
                price_symbol,
                last_price,
                last_price_symbol,
                last_sale_date,
                prob_score,
                *[  # All the traits:
                    t["value"].split(":")[1].strip()
                    for t in sorted(a["traits"], key=lambda x: x["value"])
                    if ":" in t["value"]  # In order to ignore the "All xxx" trait
                ],
                a["permalink"],
            ]
        )

    # Get the traits names:
    traits = [  # All the traits:
        t["value"].split(":")[0].strip()  # Take the first part here!
        for t in sorted(a["traits"], key=lambda x: x["value"])
        if ":" in t["value"]  # In order to ignore the "All xxx" trait
    ]

    # Turn table into df:
    df = pd.DataFrame(_tt)
    df.columns = [
        "ID",
        "Name",
        "Price",
        "Psymbol",
        "Lastprice",
        "LPsymbol",
        "LPdate",
        "Probscore",
        *traits,
        "Link",
    ]
    df["LPdate"] = pd.to_datetime(df.LPdate)
    df = df.set_index("ID").sort_values("Lastprice", ascending=False)

    return df, traits


def turn_assets_into_df_generalized(assets: list) -> Union[pd.DataFrame, list]:
    """This is a variant of the above function that should work with any OpenSea asset.

    Works also with:
    - Different assets having different numbers of traits. That's what the
      trait_bluprint is for.
    - One asset can have traits with the same name (i.e. "Celestial Body" in "The
      Wanderers" project). The values are currently simply concatenated. There might be
      different strategies (e.g., counting, binary map, ...) in the future.
    """

    trait_blueprint = {
        k: np.nan for k in set([t["trait_type"] for a in assets for t in a["traits"]])
    }

    _tt = []
    for a in assets:

        # Calc probability score:
        prob_score = (
            reduce(operator.mul, [t["trait_count"] / 1000 for t in a["traits"]], 1)
            * 1000
        )

        # Get current price:
        price = price_symbol = np.nan
        if a["sell_orders"] is not None:
            so = a["sell_orders"][0]
            price = float(so["current_price"]) / 10 ** int(
                so["payment_token_contract"]["decimals"]
            )
            price_symbol = so["payment_token_contract"]["symbol"]
            # Convert to ETH if necessary:
            if price_symbol not in ["ETH", "WETH"]:
                price *= float(so["payment_token_contract"]["eth_price"])
                price_symbol = "ETH"

        # Get last price:
        last_price = last_price_symbol = last_sale_date = np.nan
        if a["last_sale"] is not None:
            ls = a["last_sale"]
            last_price = float(ls["total_price"]) / 10 ** int(
                ls["payment_token"]["decimals"]
            )
            last_price_symbol = ls["payment_token"]["symbol"]
            # Convert to ETH if necessary:
            if last_price_symbol not in ["ETH", "WETH"]:
                last_price *= float(ls["payment_token"]["eth_price"])
                last_price_symbol = "ETH"
            last_sale_date = ls["event_timestamp"]

        # Traits:
        traits = trait_blueprint.copy()
        for t in a["traits"]:
            if traits[t["trait_type"]] is np.nan:
                traits[t["trait_type"]] = t["value"]
            else:
                traits[t["trait_type"]] += ", " + t["value"]

        # Add everything to the table:
        _tt.append(
            [
                a["token_id"],
                a[
                    "token_id"
                ],  # FIXME Not really a nice solution // but they don't have names and I need some attribute that is not the index to expose via hover in the Plotly charts.
                price,
                price_symbol,
                last_price,
                last_price_symbol,
                last_sale_date,
                prob_score,
                *[  # All the traits:
                    v for _, v in sorted(traits.items(), key=lambda x: x[0])
                ],
                a["permalink"],
            ]
        )

    # Get the traits names:
    trait_names = [  # All the traits:
        k for k, _ in sorted(trait_blueprint.items(), key=lambda x: x[0])
    ]

    # Turn table into df:
    df = pd.DataFrame(_tt)
    df.columns = [
        "ID",
        "Name",
        "Price",
        "Psymbol",
        "Lastprice",
        "LPsymbol",
        "LPdate",
        "Probscore",
        *trait_names,
        "Link",
    ]
    df["LPdate"] = pd.to_datetime(df.LPdate)
    df = df.set_index("ID").sort_values("Lastprice", ascending=False)

    return df, traits


def turn_assets_into_df_wanderers_variant(assets: list) -> Union[pd.DataFrame, list]:
    """This function specifically for The Wanderers collection; derived from the
    generalized variant above.
    """

    trait_blueprint = {
        k: "-" for k in set([t["trait_type"] for a in assets for t in a["traits"]])
    }
    trait_blueprint["Stars"] = 0
    trait_blueprint["Galaxies"] = 0
    trait_blueprint["Celestial Bodies"] = 0
    del trait_blueprint["Celestial Body"]

    _tt = []
    for a in assets:

        # Calc probability score:
        prob_score = (
            reduce(operator.mul, [t["trait_count"] / 1000 for t in a["traits"]], 1)
            * 1000
        )

        # Get current price:
        price = price_symbol = np.nan
        if a["sell_orders"] is not None:
            so = a["sell_orders"][0]
            price = float(so["current_price"]) / 10 ** int(
                so["payment_token_contract"]["decimals"]
            )
            price_symbol = so["payment_token_contract"]["symbol"]
            # Convert to ETH if necessary:
            if price_symbol not in ["ETH", "WETH"]:
                price *= float(so["payment_token_contract"]["eth_price"])
                price_symbol = "ETH"

        # Get last price:
        last_price = last_price_symbol = last_sale_date = np.nan
        if a["last_sale"] is not None:
            ls = a["last_sale"]
            last_price = float(ls["total_price"]) / 10 ** int(
                ls["payment_token"]["decimals"]
            )
            last_price_symbol = ls["payment_token"]["symbol"]
            # Convert to ETH if necessary:
            if last_price_symbol not in ["ETH", "WETH"]:
                last_price *= float(ls["payment_token"]["eth_price"])
                last_price_symbol = "ETH"
            last_sale_date = ls["event_timestamp"]

        # Traits:
        traits = trait_blueprint.copy()
        for t in a["traits"]:
            if t["trait_type"] == "Celestial Body":
                traits["Celestial Bodies"] += 1
                if "Galaxy" in t["value"]:
                    traits["Galaxies"] += 1
                else:
                    traits["Stars"] += 1
            else:
                if traits[t["trait_type"]] == "-":
                    traits[t["trait_type"]] = t["value"]
                else:
                    traits[t["trait_type"]] += ", " + t["value"]

        # Add everything to the table:
        _tt.append(
            [
                a["token_id"],
                a[
                    "token_id"
                ],  # FIXME Not really a nice solution // but they don't have names and I need some attribute that is not the index to expose via hover in the Plotly charts.
                price,
                price_symbol,
                last_price,
                last_price_symbol,
                last_sale_date,
                prob_score,
                *[  # All the traits:
                    v for _, v in sorted(traits.items(), key=lambda x: x[0])
                ],
                a["permalink"],
            ]
        )

    # Get the traits names:
    trait_names = [  # All the traits:
        k for k, _ in sorted(trait_blueprint.items(), key=lambda x: x[0])
    ]

    # Turn table into df:
    df = pd.DataFrame(_tt)
    df.columns = [
        "ID",
        "Name",
        "Price",
        "Psymbol",
        "Lastprice",
        "LPsymbol",
        "LPdate",
        "Probscore",
        *trait_names,
        "Link",
    ]
    df["LPdate"] = pd.to_datetime(df.LPdate)
    df = df.set_index("ID").sort_values("Lastprice", ascending=False)

    return df, traits
