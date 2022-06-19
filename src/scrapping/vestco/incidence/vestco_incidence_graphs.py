#%%

#%%



import pandas as pd
import unidecode
import yaml
from gsheets import Sheets
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
sheet_df
#%%
import os
dfs = {}
for file in os.listdir('vestco/incidence'):
    if file.endswith('.csv'):
        key = file.split('.')[0].split('_')[-1]
        df = pd.read_csv('vestco/incidence/' + file)
        df = df.merge(sheet_df, left_on='brand', right_on='N°Obs')[['incidence', 'N°Obs', 'Segment de marché','Niveau de prix']].set_index('N°Obs')
        dfs[key] = df

#%%
dfs['basket']['incidence'].sort_values()
#%%
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
    fig.write_image(f"vestco/incidence/incidence_vestco_{key}.png")

# %%
