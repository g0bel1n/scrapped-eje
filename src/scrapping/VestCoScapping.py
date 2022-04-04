import argparse
from ast import arg
from logging import RootLogger
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import numpy as np
import datetime
import os
import time
import logging
from tqdm import tqdm
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def getUnit(text:str, unit:str)->int:
    return int(text[7:9]) if unit in text else 0
    
def getDate(text: str):
    days, minutes, seconds, hours = getUnit(text,'JOURS'),getUnit(text,'MINUTES'),getUnit(text,'SECONDES'),getUnit(text,'HEURES')
    today = datetime.datetime.now()
    return today - datetime.timedelta(
        days=days, minutes=minutes, seconds=seconds, hours=hours
    )

def preprocessing(df):
    df.AJOUTÉ = df.AJOUTÉ.apply(getDate)
    df.prix = df.prix.apply(lambda x : float(x[:-2].replace(',', '.')))
    df['NOMBRE DE VUES'] = df['NOMBRE DE VUES'].astype(int)

def main():
    parser = argparse.ArgumentParser() 
    parser.add_argument('--n', type=int, default=2,help='Number of items to search')
    parser.add_argument('--s', type=str, default='jean',help='Search query')
    parser.add_argument('--fn', type=str, default='vestco',help='name of the output CSV file')
    args = parser.parse_args()
    args.s = args.s.replace(' ', '&')

    start = time.time()
    n = runVintedScrapping(n=args.n, query = args.s, filename= args.fn)
    duration = time.time()-start
    logger.info(f'Scrapped {n} items in {duration} seconds. ({str(duration/n).split(".")[0]} seconds per it)')
    

def runVintedScrapping(n: int, query: str, filename: str):

    driver = webdriver.Chrome()
    pageNumber=1
    url = f'https://fr.vestiairecollective.com/search/p-{pageNumber}/?q={query}'
    driver.get(url)
    driver.implicitly_wait(2)
    colsInDetailsList = ['État', 'Designer','Taille','En ligne depuis le']
    data = {colName : [] for colName in colsInDetailsList+['nom', 'prix']}

    while len(data['Designer'])<n:
        elements = driver.find_elements(by=By.CSS_SELECTOR, value='vc-ref.productSnippet__imageContainer [href]')
        links = [elem.get_attribute('href') for elem in elements]
        for link in links:
            driver.get(link)
            titles = driver.find_elements(by=By.CSS_SELECTOR, value="span.product-description-list_descriptionList__property__21dco")
            values = driver.find_elements(by=By.CSS_SELECTOR, value="span.product-description-list_descriptionList__value__J3Z9l")
            dictVal = {title.get_attribute("textContent") : value.get_attribute("textContent") for title, value in zip(titles, values)}
            
            for col in colsInDetailsList:
                data[col].append(dictVal[col+' :'] if col+' :'  in dictVal else np.nan)

            try :
                prix = driver.find_element(by=By.CLASS_NAME, value="product-price_productPrice__price--promo__Cxs_S").text
            except NoSuchElementException:
                prix = driver.find_element(by=By.CLASS_NAME, value="product-price_productPrice__Uq0dh").text

            data['prix'].append(prix)
            data['nom'].append(driver.find_element(by=By.CLASS_NAME, value="product-seller-description_sellerDescription__SnSkU").get_attribute("textContent"))

            if len(data['Designer'])>n: break
        pageNumber+=1
        driver.get(f'https://fr.vestiairecollective.com/search/p-{pageNumber}/?q={query}')
    driver.close()
    df = pd.DataFrame(data)
    df.to_csv(f'./scrapped/src/data/{filename}.csv')
    return len(data['nom'])

if __name__=='__main__':
    if "root" not in locals():
        current_path = Path(os.getcwd())
        root = current_path.parent.absolute()
    os.chdir(root)

    main()