#%%
from gsheets import Sheets
from matplotlib.pyplot import legend, subplot
from numpy import rot90
import yaml
import pandas as pd

#%%
sheets = Sheets.from_files("src/client_secrets.json")

with open("config.yml", "r") as yml_file:
    config = yaml.safe_load(yml_file)

s = sheets[config["gsheet_id"]]
mySheet = s.sheets[0]  # type: ignore
df = mySheet.to_frame()
# %%
df.columns
# %%
df = df[["N°Obs", "Niveau de prix", "Segment de marché"]]

# %%
df["N°Obs"] = df["N°Obs"].str.upper()
# %%
df
# %%

# %%
df_2 = s.sheets[1].to_frame()
# %%
df_2
# %%
completionner = {df_2.iloc[i, 1]: df_2.iloc[i, 2] for i in range(10)}

# %%
completionner
# %%
df.dropna(thresh=2, inplace=True, axis=0)
df["Segment de marché"].isna().sum
df["Niveau de prix"] = df.apply(
    lambda row: completionner[row["Segment de marché"]]
    if pd.isna(row["Niveau de prix"])
    else row["Niveau de prix"],
    axis=1,
)
#%%
df


# %%
df_shirt = pd.read_csv("data/treated/tshirts.csv").drop(
    ["Unnamed: 0"], axis=1, inplace=False
)

# %%
df.set_index(["N°Obs"], inplace=True)

#%%
df_shirt.set_index("Marque", inplace=True)


df_shirt = df_shirt[df_shirt.index.notnull()]
#%%
df_shirt[["Niveau de prix", "Segment de marché"]] = df.loc[df_shirt.index].values


# %%
import numpy as np

not_in = set(np.setdiff1d(df_shirt.index, df.index, assume_unique=False))
#%%
filtered_df_shirt = df_shirt.drop(not_in)

#%%
filtered_df_shirt[["Niveau de prix", "Segment de marché"]] = df.loc[
    filtered_df_shirt.index
].values
# %%
filtered_df_shirt = filtered_df_shirt[
    ["Niveau de prix", "Prix", "Segment de marché", "État"]
]


filtered_df_shirt.to_csv("data/final/final_shirts.csv")
