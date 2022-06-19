#%%
from numpy import quantile
import pandas as pd
import os
from gsheets import Sheets
from pyparsing import unicode_string
from unidecode import unidecode
import yaml

#%%
def get_brands_list():

    sheets = Sheets.from_files("../client_secrets.json")

    with open("../../config.yml", "r") as yml_file:
        config = yaml.safe_load(yml_file)

    s = sheets[config["gsheet_id"]]
    mySheet = s.sheets[0]  # type: ignore
    df = mySheet.to_frame()
    return df["N°Obs"].unique(), df


# %%
brands_name, sheet_df = get_brands_list()

#%%
sheet_df.loc[:, "N°Obs"] = sheet_df["N°Obs"].str.lower()
sheet_df = sheet_df.set_index("N°Obs")
#%%
prix_neufs = pd.read_excel("../prix_selection.xlsx", sheet_name=None)
# %%
vinted_articles = {}
for file in os.listdir("vinted/article_scrapping"):
    prod, *check = file.split("_")
    if check[0] == "vinted.csv":
        vinted_articles[prod] = pd.read_csv("vinted/article_scrapping/" + file)[
            ["brand", "prix"]
        ]

# %%
prix_neufs.keys()
# %%
for el in prix_neufs:
    df = prix_neufs[el]
    prix_neufs[el] = df.set_index(el)
    prix_neufs[el].index = prix_neufs[el].index.str.lower()
    vinted_articles[el].loc[:, "brand"] = (
        vinted_articles[el].loc[:, "brand"].str.lower()
    )
    vinted_articles[el].loc[:, "prix"] = (
        vinted_articles[el].prix.str.replace(",", ".").str.replace(" €", "")
    )

# %%

# %%


for el in prix_neufs:
    vinted_articles[el]["Segment de marché"] = vinted_articles[el]["brand"].apply(
        lambda x: sheet_df.loc[x, "Segment de marché"]
    )
    vinted_articles[el]["min"] = vinted_articles[el]["brand"].apply(
        lambda x: prix_neufs[el].loc[x, "min"]
    )
    vinted_articles[el]["max"] = vinted_articles[el]["brand"].apply(
        lambda x: prix_neufs[el].loc[x, "max"]
    )

    vinted_articles[el].to_csv(f"vinted/focus_vinted_{el}.csv")

# %%
vinted_articles["jean"]
# %%

# %%
vestco_articles = {}
for file in os.listdir("vestco/article_scrapping"):
    prod, *check = file.split("_")
    if check[0] == "vestco":
        vestco_articles[prod] = pd.read_csv(
            "vestco/article_scrapping/" + file, quotechar='"', dtype=str, encoding = "utf-8" 
        )[["brand", "prix"]]

# %%
prix_neufs = pd.read_excel("../prix_selection.xlsx", sheet_name=None)

#%%
prix_neufs.keys()
# %%
for el in prix_neufs:
    df = prix_neufs[el]
    prix_neufs[el] = df.set_index(el)
    prix_neufs[el].index = prix_neufs[el].index.str.lower()
    vestco_articles[el].loc[:, "brand"] = (
        vestco_articles[el].loc[:, "brand"].str.lower()
    )
    vestco_articles[el].loc[:, "prix"] = vestco_articles[el]["prix"].apply(lambda x: unidecode.unidecode(x).replace(' ',''))
# %%
# %%


for el in prix_neufs:

    vestco_articles[el].loc[:, "prix"] = (
        vestco_articles[el].loc[:, "prix"].str.replace(',','.').astype(float)
    )
    vestco_articles[el]["Segment de marché"] = vestco_articles[el]["brand"].apply(
        lambda x: sheet_df.loc[x, "Segment de marché"]
    )
    vestco_articles[el]["min"] = vestco_articles[el]["brand"].apply(
        lambda x: prix_neufs[el].loc[x, "min"]
    )
    vestco_articles[el]["max"] = vestco_articles[el]["brand"].apply(
        lambda x: prix_neufs[el].loc[x, "max"]
    )

    vestco_articles[el].to_csv(f"vestco/focus/focus_vestco_{el}.csv")


# %%
