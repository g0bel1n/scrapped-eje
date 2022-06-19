#%%
import contextlib
import itertools
from multiprocessing.connection import wait
from time import time
from webbrowser import Chrome
from gsheets import Sheets
from tenacity import sleep
from selenium.webdriver.common.keys import Keys
import yaml
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import unidecode


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
driver = webdriver.Chrome(
    executable_path="/Users/g0bel1n/scrapped/src/scrapping/chromedriver"
)
data = {"brand": [], "incidence": []}
# url_tshirt = 'https://fr.vestiairecollective.com/search/?q=t%20shirt#gender=Femme%231-Homme%232_category=V%C3%AAtements%2312%20%3E%20Tee%20shirts%23525-V%C3%AAtements%232%20%3E%20Tops%2316_categoryParent=V%C3%AAtements%2312-V%C3%AAtements%232_sold=0'
# url_jean = 'https://fr.vestiairecollective.com/search/?q=jean#gender=Femme%231-Homme%232_category=V%C3%AAtements%2312%20%3E%20Jeans%2334-V%C3%AAtements%232%20%3E%20Jeans%2323_categoryParent=V%C3%AAtements%2312-V%C3%AAtements%232_sold=0'
url_veste_costume = "https://fr.vestiairecollective.com/search/?q=veste%20de%20costume#gender=Femme%231-Homme%232_category=V%C3%AAtements%2312%20%3E%20Vestes%2C%20Blousons%2339-V%C3%AAtements%232%20%3E%20Vestes%2321_categoryParent=V%C3%AAtements%2312-V%C3%AAtements%232_sold=0"
# url_baskets = 'https://fr.vestiairecollective.com/search/?q=baskets#gender=Femme%231-Homme%232_category=Chaussures%2313%20%3E%20Baskets%2330-Chaussures%233%20%3E%20Baskets%2364_categoryParent=Chaussures%2313-Chaussures%233_sold=0'
driver.get(url_veste_costume)
sleep(4)
try:
    bouton_cookie = driver.find_element(
        by=By.XPATH, value="/html/body/div[1]/div/div[2]/button[3]"
    ).click()
except NoSuchElementException:
    pass
el = driver.find_element(
    by=By.XPATH,
    value="/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/input",
)
for brand in brands_name:
    el.send_keys(brand + " ")
    el.send_keys(Keys.RETURN)
    sleep(2.5)
    data["brand"].append(brand)
    try:
        xpath_fname = "/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/ul/li[1]/label"
        fname = (
            driver.find_element(by=By.XPATH, value=xpath_fname)
            .text.split(" ")[0]
            .split("-")[0]
            .lower()
        )
        print(fname)
        if unidecode.unidecode(
            brand.split(" ")[0].split("-")[0].lower()
        ) != unidecode.unidecode(fname):
            found = False
            for i in range(2, 10):
                try:
                    xpath_fname = f"/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/ul/li[{i}]/label"
                    fname = (
                        driver.find_element(by=By.XPATH, value=xpath_fname)
                        .text.split(" ")[0]
                        .split("-")[0]
                        .lower()
                    )
                    print(fname)
                    if unidecode.unidecode(
                        brand.split(" ")[0].split("-")[0].lower()
                    ) == unidecode.unidecode(fname):
                        nb = driver.find_element(
                            by=By.XPATH,
                            value=f"/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/ul/li[{i}]/label/span",
                        )
                        data["incidence"].append(
                            nb.text.replace("(", "").replace(")", "")
                        )
                        found = True
                        break
                except NoSuchElementException:
                    break
            if not found:
                data["incidence"].append(0)
        else:
            found = True
            nb = driver.find_element(
                by=By.XPATH,
                value="/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/ul/li[1]/label/span",
            )
            data["incidence"].append(nb.text.replace("(", "").replace(")", ""))
    except NoSuchElementException:
        found = False
        data["incidence"].append(0)
    el.clear()
    if found:
        print(data["brand"][-1], data["incidence"][-1])
driver.close()
df = pd.DataFrame(data)
df.to_csv("incidence_vesco_veste_costume.csv")
# %%

df = pd.DataFrame(data)
# %%
df[df["incidence"] == "NaN"]
# %%
df.to_clipboard()
# %%
# %%
df1 = pd.read_csv("incidence_vesco.csv")
# %%
df1 = df1.merge(df, on="brand")
# %%
import numpy as np

df1["incidence"] = df1.incidence_x.apply(
    lambda x: int(x) if not (pd.isna(x) or x == "NaN") else 0
) + df1.incidence_y.apply(lambda x: int(x) if not (pd.isna(x) or x == "NaN") else 0)
# %%
df2 = df1.merge(sheet_df, right_on="N°Obs", left_on="brand")
df2 = df2[["brand", "Segment de marché", "incidence", "Niveau de prix"]]
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
fig = px.histogram(
    df2,
    x="Segment de marché",
    y="incidence",
    histfunc="sum",
    category_orders=category_orders,
    text_auto=True,
)
fig.show()
fig.write_image("incidence_vesco.png")
# %%
dfs = {}
brands_2_scrap_from = {}
for file in [
    "incidence_vesco_basket.csv",
    "incidence_vesco_veste_costume.csv",
    "incidence_vesco_tshirt.csv",
    "incidence_vesco_jeans.csv",
]:
    dfs[file.split('.')[0].split('_')[-1]] = pd.read_csv("vestco/incidence/" + file)
for key in dfs:
    df = dfs[key]
    df = df.merge(sheet_df, right_on="N°Obs", left_on="brand")
    df = df[["brand", "Segment de marché", "incidence", "Niveau de prix"]]
    df = df.set_index("brand")
    # brands_2_scrap_from.append(df.sort_values(by=['incidence']).groupby(by='Segment de marché').tail(5).index.to_list())
    brands_2_scrap_from[key.split('.')[0].split('_')[-1]] = df.sort_values(by=["incidence"]).groupby(by="Segment de marché").tail(5)
    
#%%

brands_2_scrap_from['tshirt']
#%%
dfs['costume'].sort_values(by=["incidence"]).groupby(by="Segment de marché").tail(5)
# %%
pd.DataFrame(brands_2_scrap_from).to_clipboard()
# %%
def scrappinator(outFile: str, url: str, brands_2_scrap_from_: list):
    driver = webdriver.Chrome(
        executable_path="/Users/g0bel1n/scrapped/src/scrapping/chromedriver"
    )
    data = {"brand": [], "prix": []}
    driver.get(url)
    sleep(4)
    with contextlib.suppress(NoSuchElementException):
        bouton_cookie = driver.find_element(
            by=By.XPATH, value="/html/body/div[1]/div/div[2]/button[3]"
        ).click()

    el = driver.find_element(
        by=By.XPATH,
        value="/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/input",
    )
    for brand in brands_2_scrap_from_:
        el.send_keys(brand + " ")
        el.send_keys(Keys.RETURN)
        sleep(3)
        try:
            print("trying")
            xpath_fname = "/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/ul/li[1]/label"
            fname = (
                driver.find_element(by=By.XPATH, value=xpath_fname)
                .text.split(" ")[0]
                .split("-")[0]
                .lower()
            )
            print("did")
            if unidecode.unidecode(
                brand.split(" ")[0].split("-")[0].lower()
            ) != unidecode.unidecode(fname):
                found = False

                for i in range(2, 10):
                    try:
                        xpath_fname = f"/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/ul/li[{i}]/label"
                        fname = (
                            driver.find_element(by=By.XPATH, value=xpath_fname)
                            .text.split(" ")[0]
                            .split("-")[0]
                            .lower()
                        )
                        print(fname)
                        if unidecode.unidecode(
                            brand.split(" ")[0].split("-")[0].lower()
                        ) == unidecode.unidecode(fname):
                            found = True
                            break
                    except NoSuchElementException:
                        break
            else:
                found = True

        except NoSuchElementException:
            found = False

        if found:
            button = driver.find_element(by=By.XPATH, value=xpath_fname)
            print("click")
            button.click()
            sleep(2)
            isNext = True
            while isNext:
                print("looping")
                for grid_el in driver.find_elements(
                    by=By.CSS_SELECTOR,
                    value="li.catalog__flexContainer--item.catalog__flexContainer--item--withFilters",
                ):

                    data["brand"].append(brand)
                    data["prix"].append(
                        grid_el.find_element(
                            by=By.CSS_SELECTOR, value="span.productSnippet__price"
                        ).text.split(" ")[0]
                    )
                try:
                    bouton_suivant = driver.find_elements(
                        by=By.CSS_SELECTOR,
                        value="span.catalogPagination__prevNextButton__text",
                    )[-1]
                    isNext = bouton_suivant.text == "Suivant"
                except IndexError:
                    isNext = False
                if isNext:
                    print("click")
                    bouton_suivant.click()
                    sleep(2)
            df = pd.DataFrame(data)
            df.to_csv("brands_scrapp_vestco.csv")
            driver.get(url)
            sleep(4)
            el = driver.find_element(
                by=By.XPATH,
                value="/html/body/app-root/div/main/catalog-page/vc-catalog/div/div/ais-instantsearch/div/div[1]/div[1]/vc-catalog-filters/nav/div[4]/vc-catalog-widget-checkbox-list/fieldset/div[2]/input",
            )
        el.clear()
    driver.close()
    df = pd.DataFrame(data)
    df.to_csv(outFile)


# %%
url_tshirt = "https://fr.vestiairecollective.com/search/?q=t%20shirt#gender=Femme%231-Homme%232_category=V%C3%AAtements%2312%20%3E%20Tee%20shirts%23525-V%C3%AAtements%232%20%3E%20Tops%2316_categoryParent=V%C3%AAtements%2312-V%C3%AAtements%232_sold=0"
url_jean = "https://fr.vestiairecollective.com/search/?q=jean#gender=Femme%231-Homme%232_category=V%C3%AAtements%2312%20%3E%20Jeans%2334-V%C3%AAtements%232%20%3E%20Jeans%2323_categoryParent=V%C3%AAtements%2312-V%C3%AAtements%232_sold=0"
url_veste_costume = "https://fr.vestiairecollective.com/search/?q=veste%20de%20costume#gender=Femme%231-Homme%232_category=V%C3%AAtements%2312%20%3E%20Vestes%2C%20Blousons%2339-V%C3%AAtements%232%20%3E%20Vestes%2321_categoryParent=V%C3%AAtements%2312-V%C3%AAtements%232_sold=0"
url_baskets = "https://fr.vestiairecollective.com/search/?q=baskets#gender=Femme%231-Homme%232_category=Chaussures%2313%20%3E%20Baskets%2330-Chaussures%233%20%3E%20Baskets%2364_categoryParent=Chaussures%2313-Chaussures%233_sold=0"

# %%
for brand2scrap, url in zip(brands_2_scrap_from[3], [url_jean]):
    print(brand2scrap)
    scrappinator(
        f'{url.split("=")[1].split("%")[0]}_vestco_brands.csv', url, brand2scrap
    )
# %%
brands_2_scrap_from[3]
# %%

scrappinator(
    f'{url.split("=")[1].split("%")[0]}_vestco_brands.csv',
    url_jean,
    brands_2_scrap_from[3],
)
# %%
brands_2_scrap_from[2]
# %%
