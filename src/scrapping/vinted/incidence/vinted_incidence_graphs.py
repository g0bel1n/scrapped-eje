import os

from gsheets import Sheets

import yaml
import pandas as pd

import unidecode
from tqdm import tqdm


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

#%%
dfs = {}
global_incidence = pd.read_csv("vinted/global_incidence_vinted.csv")
global_incidence['brand'] = global_incidence['brand'].apply(lambda x : unidecode.unidecode(x))
global_incidence = global_incidence.set_index("brand")
global_incidence.index = global_incidence.index.str.lower().str.replace(' ','')
sheet_df['N°Obs']=sheet_df['N°Obs'].apply(lambda x : unidecode.unidecode(x.lower().replace(' ','')))
for product in [
    el for el in os.listdir("vinted/incidence") if el.endswith("csv")
]:
    df = pd.read_csv("vinted/incidence/" + product)
    df['brand'] = df['brand'].apply(lambda x : unidecode.unidecode(x)).str.replace(' ','')
    df = df.set_index("brand")
    df.index = df.index.str.lower()
    df.drop(['eram','courir'], inplace=True)
    df["global_incidence"] = [0] * 404

    df.loc[df["incidence"] == 3000,"global_incidence"] = global_incidence.loc[
        df[df["incidence"] == 3000].index.values,'incidence'
    ]

    df = df.merge(sheet_df, left_index=True, right_on="N°Obs")[['incidence', 'global_incidence', 'N°Obs', 'Segment de marché','Niveau de prix']].set_index('N°Obs')

    dfs[product.split(".")[0].split("_")[-1]] = df


# %%
import pandas as pd
import plotly.express as px

category_orders = {
    "Niveau de prix": [
        "Discount",
        "Bas",
        "Moyen-Bas",
        "Moyen",
        "Moyen-Haut",
        "Haut",
        "Premium Luxury",
        "Luxe",
    ],
    "Segment de marché": [
        "ultra fast fashion / discount",
        "entrée de gamme / mass market",
        "milieu de gamme",
        "premium / luxe abordable",
        "luxe & création",
    ],
    "État": [
        "BON ÉTAT",
        "NEUF AVEC ÉTIQUETTE",
        "NEUF SANS ÉTIQUETTE",
        "SATISFAISANT",
        "TRÈS BON ÉTAT",
    ],
}
pd.options.plotting.backend = "plotly"

for key in dfs :
    fig = px.histogram(
        dfs[key],
        x="Segment de marché",
        y="incidence",
        histfunc="sum",
        category_orders=category_orders,
        text_auto=True,
    )
    fig.show()
    fig.write_image(f"vinted/incidence/incidence_vinted_{key}.png")

