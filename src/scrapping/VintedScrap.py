import argparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import datetime
import os
import time
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def getUnit(text: str, unit: str) -> int:
    return int(text[7:9]) if unit in text else 0


def getDate(text: str):
    days, minutes, seconds, hours = (
        getUnit(text, "JOURS"),
        getUnit(text, "MINUTES"),
        getUnit(text, "SECONDES"),
        getUnit(text, "HEURES"),
    )
    today = datetime.datetime.now()
    return today - datetime.timedelta(
        days=days, minutes=minutes, seconds=seconds, hours=hours
    )


def preprocessing(df):
    df.AJOUTÉ = df.AJOUTÉ.apply(getDate)
    df.prix = df.prix.apply(lambda x: float(x[:-2].replace(",", ".")))
    df["NOMBRE DE VUES"] = df["NOMBRE DE VUES"].astype(int)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50, help="Number of items to search")
    parser.add_argument("--s", type=str, default="t shirt shein", help="Search query")
    parser.add_argument(
        "--fn", type=str, default="vinted", help="name of the output CSV file"
    )
    parser.add_argument("--url", type=str, default=None, help="special url")
    args = parser.parse_args()
    args.s = args.s.replace(" ", "%20")

    start = time.time()
    n = runVintedScrapping(n=args.n, query=args.s, filename=args.fn, spec_url=args.url)
    duration = time.time() - start
    logger.info(
        f'Scrapped {n} items in {     duration/60.} minutes. ({str(duration/n).split(".")[0]} seconds per it)'
    )


def runVintedScrapping(
    n: int, query: str, filename: str, spec_url: str, save: bool = True
):

    driver = webdriver.Chrome()

    pageNumber = 1
    if spec_url is None:
        base_url = f"https://www.vinted.fr/vetements?search_text={query}&page="
    else:
        base_url = f"{spec_url}&page="
    driver.get(base_url + str(pageNumber))
    colsInDetailsList = [
        "ÉTAT",
        "NOMBRE DE VUES",
        "EMPLACEMENT",
        "MARQUE",
        "TAILLE",
        "AJOUTÉ",
    ]
    data = {
        colName: []
        for colName in colsInDetailsList + ["nom", "prix", "description", "url"]
    }

    with tqdm(total=n, desc="Scrapping", ascii="░▒█") as bbar:
        while len(data["MARQUE"]) < n:
            elements = driver.find_elements(
                by=By.CSS_SELECTOR, value="div.ItemBox_image__3BPYe [href]"
            )
            links = [elem.get_attribute("href") for elem in elements]
            if not len(links):
                break
            for link in links:
                bbar.update(1)
                driver.get(link)
                titles = driver.find_elements(
                    by=By.CLASS_NAME, value="details-list__item-title"
                )
                values = driver.find_elements(
                    by=By.CLASS_NAME, value="details-list__item-value"
                )
                dictVal = {
                    title.text: value.text for title, value in zip(titles, values)
                }
                for col in colsInDetailsList:
                    data[col].append(dictVal[col] if col in dictVal else np.nan)

                data["prix"].append(
                    driver.find_element(
                        by=By.XPATH,
                        value="//div[@class='u-flexbox u-justify-content-between']/h1[@class='Text_text__QBn4- Text_heading__gV4um Text_left__3s3CR']",
                    ).text
                )
                data["nom"].append(
                    driver.find_element(
                        by=By.XPATH, value="//div[@itemprop='name']"
                    ).text
                )
                data["description"].append(
                    driver.find_element(
                        by=By.XPATH, value="//div[@itemprop='description']"
                    ).text
                )

                data["url"].append(link)

                if len(data["MARQUE"]) > n:
                    break

            pageNumber += 1
            driver.get(base_url + str(pageNumber))

    driver.close()

    df = pd.DataFrame(data)
    preprocessing(df)

    if not save:
        return df

    df.to_csv(f"./scrapped/data/raw/{query.replace('%20','_')}.csv")
    return len(data["description"])


if __name__ == "__main__":

    if "root" not in locals():
        current_path = Path(os.getcwd())
        root = current_path.parent.absolute()
    os.chdir(root)

    main()
