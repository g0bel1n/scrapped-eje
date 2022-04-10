import argparse
from re import A
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import logging
from tqdm import tqdm
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser() 
    parser.add_argument('--n', type=int, default=2,help='Number of items to search')
    parser.add_argument('--fn', type=str, default='immo_data.csv',help='name of the output CSV file')
    args = parser.parse_args()

    start = time.time()
    n = runImmoDataScrapping(n=args.n, filename= args.fn)
    duration = time.time()-start
    logger.info(f'Scrapped {n} items in {duration/60.} minutes. ({str(duration/n).split(".")[0]} seconds per it)')
    
def runImmoDataScrapping(n: int, filename: str):
    driver = webdriver.Chrome()
    pageNumber=1
    url = 'https://www.immo-data.fr/explorateur/transaction/recherche?minprice=0&maxprice=5000000&minpricesquaremeter=0&maxpricesquaremeter=40000&propertytypes=0%2C1%2C2&minmonthyear=Janvier%202014&maxmonthyear=Juin%202021&nbrooms=1%2C2%2C3%2C4%2C5&minsurface=0&maxsurface=400&minsurfaceland=0&maxsurfaceland=50000&center=2.346997%3B48.85882815&zoom=11.540155719966153'

    driver.get(url)
    driver.implicitly_wait(6)
    colsInDetailsList = ['addresse', 'prix','date_vente','details']
    data = {colName : [] for colName in colsInDetailsList}

    elements = driver.find_elements(by=By.XPATH, value='//div[@class="Card_cardContainer__1xYDO Card_cardContainerList__CL7In"]')
    
    for element in tqdm(elements):
        driver.implicitly_wait(2)            
        addresse = element.find_element(by=By.CSS_SELECTOR, value="div.Card_address__2SfIz").text
        prix = element.find_element(by=By.CSS_SELECTOR, value="div.Card_priceTag__2aA_r").text
        date_vente = element.find_element(by=By.CSS_SELECTOR, value='div.Card_bottomSection__1-tob').text
        details = element.find_element(by=By.CSS_SELECTOR, value='div.Card_middleSection__3sNkm').text
        
        data['addresse'].append(addresse)
        data['prix'].append(prix)
        data['date_vente'].append(date_vente)
        data['details'].append(details)

    driver.close()

    df = pd.DataFrame(data)
    df.to_csv(filename)
    return len(data['addresse'])

if __name__=='__main__':

    main()