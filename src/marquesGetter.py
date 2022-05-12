#%%
from gsheets import Sheets
import yaml
import pandas as pd
#%%


def getCategories():

#%%
    sheets = Sheets.from_files("client_secrets.json")

    with open("../config.yml", "r") as yml_file:
        config = yaml.safe_load(yml_file)

    s = sheets[config["gsheet_id"]]
    mySheet = s.sheets[1]  # type: ignore
#%%
print(mySheet[:])
#%%
    Marques = []
    data = {}
    for col in "BCDEFGHI":
        col_name = mySheet[f"{col}{1}"]
        data[col_name] = []
#%%
data =mySheet.get_all_values()
#%%
    for col in "BCDEFGHI":
        row = 2
        col_name = mySheet[f"{col}{1}"]
        marque = mySheet[f"{col}{row}"]
        while True:
            data[col_name].append(marque)
            row += 1
            try:
                marque = mySheet[f"{col}{row}"]
            except IndexError:
                break

#%%
list(data.values())[7]
#%%
df = pd.DataFrame(mySheet[1:], columns=mySheet[0])
#%%
    new_cols = mySheet["H4":"H8"]
    df.columns = ["Marques"] + new_cols

    return df
# %%
df = pd.DataFrame(mySheet[1:], columns= mySheet[0])
# %%
df = mySheet.to_frame()
# %%
df
# %%
