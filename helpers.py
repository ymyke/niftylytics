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

        # Get last price:
        last_price = last_price_symbol = last_sale_date = np.nan
        if a["last_sale"] is not None:
            ls = a["last_sale"]
            last_price = float(ls["total_price"]) / 10 ** int(
                ls["payment_token"]["decimals"]
            )
            last_price_symbol = ls["payment_token"]["symbol"]
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
