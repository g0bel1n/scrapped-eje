from gsheets import Sheets
import yaml
import pandas as pd


def getCategories():
    sheets = Sheets.from_files("client_secrets.json")

    with open("../config.yml", "r") as yml_file:
        config = yaml.safe_load(yml_file)

    s = sheets[config["gsheet_id"]]
    mySheet = s.sheets[0]

    Marques = []
    data = {}
    for col in "ABCDE":
        col_name = mySheet[f"{col}{1}"]
        data[col_name] = []

    for col in "ABCDE":
        row = 2
        col_name = mySheet[f"{col}{1}"]
        marque = mySheet[f"{col}{row}"]
        while marque != "":
            Marques.append(marque)
            for col_name_, col_values in data.items():
                col_values.append(col_name == col_name_)
            row += 1
            try:
                marque = mySheet[f"{col}{row}"]
            except IndexError:
                marque = ""

    data4df = {"Marques": Marques, **data}

    df = pd.DataFrame(data4df)
    new_cols = mySheet["H4":"H8"]
    df.columns = ["Marques"] + new_cols

    return df
