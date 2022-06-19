#%%
from gsheets import Sheets
from matplotlib.pyplot import legend, subplot
from numpy import rot90
import yaml
import pandas as pd
from VintedScrap import runVintedScrapping


def get_brands_list():

    sheets = Sheets.from_files("src/client_secrets.json")

    with open("../../config.yml", "r") as yml_file:
        config = yaml.safe_load(yml_file)

    s = sheets[config["gsheet_id"]]
    mySheet = s.sheets[0]  # type: ignore
    df = mySheet.to_frame()
    return df["N°Obs"].str.upper().str.replace("&", "").str.replace(" ", "%20").unique()


# %%
brands[0]
#%%
df = runVintedScrapping(
    10000, f"t-shirt%20{brands[0]}", spec_url=None, filename="a", save=False
)
for brand in brands[1:]:
    df = pd.concat(
        (
            df,
            runVintedScrapping(
                10000, f"t-shirt {brands}", spec_url=None, filename="a", save=False
            ),
        )
    )

# %%
