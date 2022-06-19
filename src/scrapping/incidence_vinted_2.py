#%%
import contextlib
import itertools
from multiprocessing.connection import wait
from operator import index
from time import time
from webbrowser import Chrome
from gsheets import Sheets
from tenacity import sleep
from selenium.webdriver.common.keys import Keys
import yaml
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
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


def recurr_find(default_url: str, driver: Chrome, page_min: int, page_max: int):

    mid = int((page_max + page_min) / 2)

    if page_max - page_min <= 1:
        return page_min

    driver.get(default_url + str(mid))

    try:
        el = driver.find_element(
            by=By.CSS_SELECTOR,
            value="h1.Text_text__QBn4-.Text_heading__gV4um.Text_center__1au2s",
        )
        return recurr_find(default_url, driver, page_min=page_min, page_max=mid)

    except NoSuchElementException:
        if mid == 125:
            return 125
        else:
            return recurr_find(default_url, driver, page_min=mid, page_max=page_max)


#%%
driver = webdriver.Chrome(
    executable_path="/Users/g0bel1n/scrapped/src/scrapping/chromedriver"
)
data = {"brand": [], "incidence": []}
url_tshirt = "https://www.vinted.fr/vetements?catalog[]=221&catalog[]=1806&catalog[]=1807&catalog[]=1808"
url_jean = "https://www.vinted.fr/vetements?catalog[]=257&catalog[]=183"
url_veste_costume = "https://www.vinted.fr/vetements?catalog[]=1786&catalog[]=532"
url_baskets = "https://www.vinted.fr/vetements?catalog[]=1242&catalog[]=214"
url = url_baskets

driver.get(url)
sleep(3)

try:
    bouton_cookie = driver.find_element(
        by=By.CSS_SELECTOR, value="button#onetrust-reject-all-handler"
    ).click()
    sleep(2)
except NoSuchElementException:
    pass

driver.find_element(
    by=By.XPATH,
    value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/button",
).click()
el = driver.find_element(
    by=By.XPATH,
    value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/label/div/input",
)

for i, brand in tqdm(enumerate(brands_name)):
    if i > 0 and i % 50 == 0:
        pd.DataFrame(data).to_csv(f"fuckdisshit_{i}.csv")
    el.send_keys(brand + " ")
    el.send_keys(Keys.RETURN)
    sleep(2.5)
    data["brand"].append(brand)
    try:
        xpath_fname = "/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[1]/div/div[1]/div/h2"
        fname = (
            driver.find_element(by=By.XPATH, value=xpath_fname)
            .text.split(" ")[0]
            .split("-")[0]
            .lower()
        )
        # print(fname)
        if unidecode.unidecode(
            brand.split(" ")[0].split("-")[0].lower()
        ) != unidecode.unidecode(fname):
            found = False
            for i in range(2, 10):
                try:
                    xpath_fname = f"/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[{i}]/div/div[1]/div/h2"
                    fname = (
                        driver.find_element(by=By.XPATH, value=xpath_fname)
                        .text.split(" ")[0]
                        .split("-")[0]
                        .lower()
                    )
                    # print(fname)
                    if unidecode.unidecode(
                        brand.split(" ")[0].split("-")[0].lower()
                    ) == unidecode.unidecode(fname):
                        div = driver.find_element(
                            by=By.XPATH,
                            value=f"/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[{i}]/div",
                        )

                        found = True
                        break
                except NoSuchElementException:
                    break
            if not found:
                data["incidence"].append(0)
                el.clear()
        else:
            found = True
            div = driver.find_element(
                by=By.XPATH,
                value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[1]/div",
            )

    except NoSuchElementException:
        found = False
        data["incidence"].append(0)
        el.clear()
    if found:
        sleep(2)
        brand_id = div.get_attribute("id").split("-")[-1]
        driver.get(url + f"&brand_id={brand_id}")
        sleep(1)

        try:
            nb = driver.find_element(by=By.CSS_SELECTOR, value="h3.Text_text__QBn4-")

            if nb.text.split(" ")[0] == "500+":

                data["incidence"].append(
                    recurr_find(driver.current_url + "&page=", driver, 20, 230) * 24
                )

            else:
                data["incidence"].append(nb.text.split(" ")[0])
        except NoSuchElementException:
            data["incidence"].append(0)

        driver.get(url)
        sleep(2)
        driver.find_element(
            by=By.XPATH,
            value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/button",
        ).click()
        el = driver.find_element(
            by=By.XPATH,
            value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/label/div/input",
        )
        # print(data["brand"][-1], data["incidence"][-1])
driver.close()
df = pd.DataFrame(data)

df.to_csv("incidence_vinted_jeans_2.csv")
#%%
sheet_df = sheet_df.set_index("N°Obs")
#%%
import os

#%%
dfs = {}
global_incidence = pd.read_csv("vinted/global_incidence_vinted.csv")
global_incidence["brand"] = global_incidence["brand"].apply(
    lambda x: unidecode.unidecode(x)
)
global_incidence = global_incidence.set_index("brand")
global_incidence.index = global_incidence.index.str.lower().str.replace(" ", "")
sheet_df['brand'] = sheet_df["N°Obs"] 
sheet_df["N°Obs"] = sheet_df["N°Obs"].apply(
    lambda x: unidecode.unidecode(x.lower().replace(" ", ""))
)
for product in [el for el in os.listdir("vinted/incidence") if el.endswith("csv")]:
    df = pd.read_csv("vinted/incidence/" + product)
    df["brand"] = (
        df["brand"].apply(lambda x: unidecode.unidecode(x)).str.replace(" ", "")
    )
    df = df.set_index("brand")
    df.index = df.index.str.lower()
    df.drop(["eram", "courir"], inplace=True)
    df["global_incidence"] = [0] * 404

    df.loc[df["incidence"] == 3000, "global_incidence"] = global_incidence.loc[
        df[df["incidence"] == 3000].index.values, "incidence"
    ]

    df = df.merge(sheet_df, left_index=True, right_on="N°Obs")[
        [
            "incidence",
            "global_incidence",
            "N°Obs",
            "Segment de marché",
            "Niveau de prix",
            "brand"
        ]
    ].set_index("brand")

    dfs[product.split(".")[0].split("_")[-1]] = df


#%%

dfs["baskets"].sort_values(by=["incidence", "global_incidence"]).groupby(
    by="Segment de marché"
).tail(5)
#%%

brands2scrap_from = {
    key: value.sort_values(by=["incidence", "global_incidence"])
    .groupby(by="Segment de marché")
    .tail(5)
    .index
    for key, value in dfs.items()
}

# %%
brands2scrap_from["baskets"]


#%%

driver = webdriver.Chrome(
    executable_path="/Users/g0bel1n/scrapped/src/scrapping/chromedriver"
)
data = {"brand": [], "prix": []}
url_tshirt = "https://www.vinted.fr/vetements?catalog[]=221&catalog[]=1806&catalog[]=1807&catalog[]=1808"
url_jean = "https://www.vinted.fr/vetements?catalog[]=257&catalog[]=183"
url_veste_costume = "https://www.vinted.fr/vetements?catalog[]=1786&catalog[]=532"
url_baskets = "https://www.vinted.fr/vetements?catalog[]=1242&catalog[]=214"
url = url_tshirt

driver.get(url)
sleep(3)

try:
    bouton_cookie = driver.find_element(
        by=By.CSS_SELECTOR, value="button#onetrust-reject-all-handler"
    ).click()
    sleep(2)
except NoSuchElementException:
    pass

driver.find_element(
    by=By.XPATH,
    value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/button",
).click()
el = driver.find_element(
    by=By.XPATH,
    value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/label/div/input",
)

for i, brand in tqdm(enumerate(brands2scrap_from["tshirt"]
)):
    if i > 0 and i % 8 == 0:
        pd.DataFrame(data).to_csv(f"fuckdisshit_{i}.csv")
    el.send_keys(brand + " ")
    el.send_keys(Keys.RETURN)
    sleep(2.5)
    try:
        xpath_fname = "/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[1]/div/div[1]/div/h2"
        fname = (
            driver.find_element(by=By.XPATH, value=xpath_fname)
            .text.split(" ")[0]
            .split("-")[0]
            .lower()
        )
        # print(fname)
        if unidecode.unidecode(
            brand.split(" ")[0].split("-")[0].lower()
        ) != unidecode.unidecode(fname):
            found = False
            for i in range(2, 10):
                try:
                    xpath_fname = f"/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[{i}]/div/div[1]/div/h2"
                    fname = (
                        driver.find_element(by=By.XPATH, value=xpath_fname)
                        .text.split(" ")[0]
                        .split("-")[0]
                        .lower()
                    )
                    # print(fname)
                    if unidecode.unidecode(
                        brand.split(" ")[0].split("-")[0].lower()
                    ) == unidecode.unidecode(fname):
                        div = driver.find_element(
                            by=By.XPATH,
                            value=f"/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[{i}]/div",
                        )

                        found = True
                        break
                except NoSuchElementException:
                    break
            if not found:
                el.clear()
        else:
            found = True
            div = driver.find_element(
                by=By.XPATH,
                value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[1]/div",
            )

    except NoSuchElementException:
        found = False
        el.clear()
    if found:
        sleep(2)
        brand_id = div.get_attribute("id").split("-")[-1]
        driver.get(url + f"&brand_id={brand_id}")
        sleep(1)
        page_nb = 1
        base_url = driver.current_url + "&page="
        while True:

            try:
                driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="h1.Text_text__QBn4-.Text_heading__gV4um.Text_center__1au2s",
                )
                break

            except NoSuchElementException  or StaleElementReferenceException :
                for el in driver.find_elements(
                    by=By.CLASS_NAME, value="feed-grid__item-content"
                ):
                    try :
                        prix = el.find_element(
                        by=By.CLASS_NAME,
                        value="Text_text__QBn4-.Text_subtitle__1I9iB.Text_left__3s3CR.Text_amplified__2ccjx.Text_bold__1scEZ",
                    ).text
                        print(prix)
                        data["brand"].append(brand)
                        data["prix"].append(prix)
                    except NoSuchElementException or StaleElementReferenceException:
                        pass
            page_nb += 1
            driver.get(base_url + str(page_nb))
            sleep(1)

        driver.get(url)
        sleep(2)
        driver.find_element(
            by=By.XPATH,
            value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/button",
        ).click()
        el = driver.find_element(
            by=By.XPATH,
            value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/label/div/input",
        )
        # print(data["brand"][-1], data["incidence"][-1])
driver.close()
df = pd.DataFrame(data)

df.to_csv("jeans_vinted.csv")


#%%
import contextlib


def get_brand(brand: str, driver: Chrome):
    data = {"brand": [], "prix": []}
    page = 1
    default_url = f"https://www.vinted.fr/brand/{brand}?catalog[]=1806&catalog[]=1807&catalog[]=1808&page="
    driver.get(default_url + str(page))
    while True:
        articles = driver.find_elements(
            by=By.CSS_SELECTOR,
            value="h3.Text_text__QBn4-.Text_subtitle__1I9iB.Text_left__3s3CR.Text_amplified__2ccjx.Text_bold__1scEZ",
        )
        for article in articles:
            data["brand"].append(brand)
            data["prix"].append(article.text.split(",")[0])
        page += 1
        driver.get(default_url + str(page))
        with contextlib.suppress(NoSuchElementException):
            driver.find_element(
                by=By.CSS_SELECTOR,
                value="h1.Text_text__QBn4-.Text_heading__gV4um.Text_center__1au2s",
            )
            break
    pd.DataFrame(data).to_csv(f"brands/{brand}.csv")
#%%
brands2scrap_from["jeans"][13:]
# %%
#%%

driver = webdriver.Chrome(
    executable_path="/Users/g0bel1n/scrapped/src/scrapping/chromedriver"
)
data = {"brand": [], "prix": []}
url_tshirt = "https://www.vinted.fr/vetements?catalog[]=221&catalog[]=1806&catalog[]=1807&catalog[]=1808"
url_jean = "https://www.vinted.fr/vetements?catalog[]=257&catalog[]=183"
url_veste_costume = "https://www.vinted.fr/vetements?catalog[]=1786&catalog[]=532"
url_baskets = "https://www.vinted.fr/vetements?catalog[]=1242&catalog[]=214"
url = url_veste_costume

driver.get(url)
sleep(3)

try:
    bouton_cookie = driver.find_element(
        by=By.CSS_SELECTOR, value="button#onetrust-reject-all-handler"
    ).click()
    sleep(2)
except NoSuchElementException:
    pass

driver.find_element(
    by=By.XPATH,
    value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/button",
).click()
el = driver.find_element(
    by=By.XPATH,
    value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/label/div/input",
)

for i, brand in tqdm(enumerate(brands2scrap_from["costume"]
)):
    if i > 0 and i % 8 == 0:
        pd.DataFrame(data).to_csv(f"fuckdisshit_{i}.csv")
    el.send_keys(brand + " ")
    el.send_keys(Keys.RETURN)
    sleep(2.5)
    try:
        xpath_fname = "/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[1]/div/div[1]/div/h2"
        fname = (
            driver.find_element(by=By.XPATH, value=xpath_fname)
            .text.split(" ")[0]
            .split("-")[0]
            .lower()
        )
        # print(fname)
        if unidecode.unidecode(
            brand.split(" ")[0].split("-")[0].lower()
        ) != unidecode.unidecode(fname):
            found = False
            for i in range(2, 10):
                try:
                    xpath_fname = f"/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[{i}]/div/div[1]/div/h2"
                    fname = (
                        driver.find_element(by=By.XPATH, value=xpath_fname)
                        .text.split(" ")[0]
                        .split("-")[0]
                        .lower()
                    )
                    # print(fname)
                    if unidecode.unidecode(
                        brand.split(" ")[0].split("-")[0].lower()
                    ) == unidecode.unidecode(fname):
                        div = driver.find_element(
                            by=By.XPATH,
                            value=f"/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[{i}]/div",
                        )

                        found = True
                        break
                except NoSuchElementException:
                    break
            if not found:
                el.clear()
        else:
            found = True
            div = driver.find_element(
                by=By.XPATH,
                value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/div/ul/li[1]/div",
            )

    except NoSuchElementException:
        found = False
        el.clear()
    if found:
        sleep(2)
        brand_id = div.get_attribute("id").split("-")[-1]
        driver.get(url + f"&brand_id={brand_id}")
        sleep(1)
        page_nb = 1
        base_url = driver.current_url + "&page="
        while True:

            try:
                driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="h1.Text_text__QBn4-.Text_heading__gV4um.Text_center__1au2s",
                )
                break

            except NoSuchElementException  or StaleElementReferenceException :
                for el in driver.find_elements(
                    by=By.CLASS_NAME, value="feed-grid__item-content"
                ):
                    try :
                        prix = el.find_element(
                        by=By.CLASS_NAME,
                        value="Text_text__QBn4-.Text_subtitle__1I9iB.Text_left__3s3CR.Text_amplified__2ccjx.Text_bold__1scEZ",
                    ).text
                        print(prix)
                        data["brand"].append(brand)
                        data["prix"].append(prix)
                    except NoSuchElementException or StaleElementReferenceException:
                        pass
            page_nb += 1
            driver.get(base_url + str(page_nb))
            sleep(1)

        driver.get(url)
        sleep(2)
        driver.find_element(
            by=By.XPATH,
            value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/button",
        ).click()
        el = driver.find_element(
            by=By.XPATH,
            value="/html/body/main/div/section/div/div[2]/section/div/div/div[5]/div[4]/div/div/div/div/div/label/div/input",
        )
        # print(data["brand"][-1], data["incidence"][-1])
driver.close()
df = pd.DataFrame(data)

df.to_csv("costume_vinted.csv")
# %%
