# Pour chaque marque du sheet, récupérer l'url.
# Si 500+ aller en page 100 si n'existe pas, aller en page 50 sinon 150
# Récupérer le nombre de vêtements:
# si la marque n'existe pas direct, la mettre dans une liste
# Vinted prend les marques en minuscule

#%%
import contextlib
from time import sleep
from webbrowser import Chrome
from gsheets import Sheets
import yaml
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

#%%
def get_brands_list():

    sheets = Sheets.from_files("../client_secrets.json")

    with open("../../config.yml", "r") as yml_file:
        config = yaml.safe_load(yml_file)

    s = sheets[config["gsheet_id"]]
    mySheet = s.sheets[0]  # type: ignore
    df = mySheet.to_frame()
    return df["N°Obs"].str.upper().str.replace("&", "").str.replace(" ", "%20").unique(), df


# %%
brands_name, sheet_df = get_brands_list()
# %%
easy_brands, hard_brands = sheet_df[~sheet_df['N°Obs'].str.contains(' ')],sheet_df[sheet_df['N°Obs'].str.contains(' ')]
# %%
hard_brands
n_page = 1
#%%
def recurr_find(default_url: str, driver: Chrome, page_min: int, page_max: int):

    mid = int((page_max+page_min)/2)

    if page_max-page_min <= 1:
        return page_min

    driver.get(default_url+str(mid))

    try :
        el = driver.find_element(by=By.CSS_SELECTOR, value='h1.Text_text__QBn4-.Text_heading__gV4um.Text_center__1au2s')
        return recurr_find(default_url, driver, page_min=page_min, page_max=mid)

    except NoSuchElementException :
        return recurr_find(default_url, driver, page_min = mid, page_max=page_max)


#%%
def get_incidence(brand: str, driver: Chrome):
    
    #default_url = f'https://www.vinted.fr/brand/{brand}?catalog[]=1806&catalog[]=1807&catalog[]=1808&page='


    try :
        nb = driver.find_element(by=By.CSS_SELECTOR, value='h3.Text_text__QBn4-')

        if nb.text.split(' ')[0] == '500+':
            return recurr_find(default_url, driver, 20, 500)*24,True

        return nb.text.split(' ')[0], False
    except NoSuchElementException:
        return 0, False
# %%
driver = webdriver.Chrome()
l = []
url = 'https://www.vinted.fr/vetements?search_text=t%20shirt&catalog[]=221&catalog[]=1806&catalog[]=1807&catalog[]=1808'
driver.get(url)
sleep(2)
for brand in easy_brands['N°Obs']:
    incidence, need_reset = get_incidence(brand, driver)
    l.append(incidence)
    if need_reset : 
driver.close()

#%%

easy_brands['incidence'] = l








     
# %%
easy_brands[easy_brands.incidence==3000].count()
# %%
hard_brands['N°Obs'] = hard_brands['N°Obs'].str.replace(' ', '-')
# %%
hard_brands
# %%
driver = webdriver.Chrome()
l = []
for brand in hard_brands['N°Obs']:
    l.append(get_incidence(brand, driver))
driver.close()

#%%
hard_brands['incidence'] = l

# %%

hard_brands[hard_brands.incidence == 'NaN']
# %%
easy_brands[easy_brands.incidence == 'NaN'].count()

# %%
easy_brands
# %%

df = pd.concat((easy_brands, hard_brands), axis=0)
# %%
df.to_csv('incidence_vinted.csv')
# %%
df = df[~(df.incidence=='NaN')]
# %%
df[df.incidence==3000].groupby(by='Segment de marché').count()
# %%
df.incidence = df.incidence.astype(int)
#%%
df.groupby(by='Segment de marché').incidence.hist(legend=True)

# %%
df.incidence.astype(int)
# %%
df = pd.read_csv('incidence_vinted.csv')
# %%
df[df.incidence.isna()].to_clipboard()
# %%

et_brands = sheet_df[sheet_df['N°Obs'].str.contains('&')]

# %%
et_brands['N°Obs'] = et_brands['N°Obs'].str.replace('&', '')
# %%
et_brands['N°Obs'] = et_brands['N°Obs'].str.replace(' ', '-')

# %%
et_brands['N°Obs'] = et_brands['N°Obs'].str.replace('--', '-')

#%%
driver = webdriver.Chrome()
l = []
for brand in et_brands['N°Obs']:
    l.append(get_incidence(brand, driver))
driver.close()
# %%
df[df['N°Obs'].str.contains('&')].incidence = l
# %%
l
# %%
df[df.incidence.isna()]
# %%
df.iloc[df[df['N°Obs'].str.contains('&')].index, 10] = l
# %%
df
df[df['N°Obs'].str.contains('&')].index
# %%
df
# %%
df[df.incidence.isna()]

# %%
df.to_csv('incidence_vinted.csv')

# %%
df = pd.read_csv('incidence_vinted.csv')

df=df[~df.incidence.isna()]
df=df[df.incidence != 'NaN']
#%%
df = df[['N°Obs','Niveau de prix', 'Segment de marché', 'incidence']]
#%%
df['rank'] = df.groupby(by='Segment de marché').rank('max', False).iloc[:,2]
# %%
df.sort_values(by='rank', inplace=True)
#%%

df.groupby(by='Segment de marché').sum()

#%%

df[df.incidence==3000].groupby(by='Segment de marché').count()


#%%
import pandas as pd
import plotly.express as px

category_orders = {"Niveau de prix" : ['Discount','Bas', 'Moyen-Bas', 'Moyen', 'Moyen-Haut', 'Haut', 'Premium Luxury', 'Luxe'], "Segment de marché" : [
        "ultra fast fashion / discount",
        "entrée de gamme / mass market",
        "milieu de gamme",
        "premium / luxe abordable",
        "luxe & création",
    ], "État" :[
        "BON ÉTAT",
        "NEUF AVEC ÉTIQUETTE",
        "NEUF SANS ÉTIQUETTE",
        "SATISFAISANT",
        "TRÈS BON ÉTAT",
    ] }
pd.options.plotting.backend = "plotly"
fig = px.histogram(df, x='Segment de marché', y='incidence',histfunc='sum', category_orders=category_orders, text_auto=True)
fig.show()
fig.write_image('incidence_vinted.png')
# %%

df[df['rank']<=10.].groupby(by='Segment de marché').head()

#%%

upper_df = df[df.incidence==3000]
# %%
upper_df['brand'] = upper_df['N°Obs'].str.replace('-', ' ')
# %%
upper_df['fletter'] = upper_df.brand.str[:1]
# %%
driver = webdriver.Chrome(executable_path='/Users/g0bel1n/scrapped/src/scrapping/chromedriver')
default_url  = 'https://www.vinted.fr/brands/by_letter/'
for el in upper_df.groupby(by='fletter'):
    fletter, df = el[0], el[1]
    if fletter!='&':
        driver.get(default_url+fletter)
        for brand in el[1].itertuples():
            pp  =driver.find_elements(by=By.CSS_SELECTOR, value ='div.follo')

            try :
                nb = driver.find_element_by_xpath(f'//a[contains(@href,{brand[1].lower()})]')
                print(nb.text)
            except NoSuchElementException:
                print('NaN')
driver.close()    
# %%
driver = webdriver.Chrome(executable_path='/Users/g0bel1n/scrapped/src/scrapping/chromedriver')
default_url  = 'https://www.vinted.fr/brands/by_letter/'
data4df= {'brand':[], 'incidence':[]}
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    driver.get(default_url+letter)
    elements = driver.find_elements(by=By.CLASS_NAME, value ='follow__body')
    for element in elements :
        data4df['brand'].append(element.find_element(by=By.CLASS_NAME, value ='follow__name').text.split('/')[-1])
        data4df['incidence'].append(int(element.find_element(by=By.CLASS_NAME, value ='follow__details' ).text.split(' ')[0]))
driver.close()
df = pd.DataFrame(data4df)
df.to_csv('global_incidence_vinted.csv')
# %%

df_glob_incidence = pd.read_csv('global_incidence_vinted.csv')
# %%
df = pd.read_csv('incidence_vinted.csv')

df=df[~df.incidence.isna()]
df=df[df.incidence != 'NaN']
#%%
df = df[['N°Obs','Niveau de prix', 'Segment de marché', 'incidence']]
# %%
df['N°Obs'] = df['N°Obs'].str.lower()
# %%
df['global_incidence'] = 
# %%
df_glob_incidence.brand = df_glob_incidence.brand.str.replace(' ', '-').str.lower()
# %%
df_glob_incidence = df_glob_incidence.set_index('brand')
# %%
df_glob_incidence = df_glob_incidence['incidence']

# %%
df_glob_incidence.loc[df[df.incidence==3000]['N°Obs']]
# %%
df_glob_incidence = df_glob_incidence.append(pd.Series(5201537, index=['levis']))
# %%
#%%
df = df.set_index('N°Obs').drop(['courir', '&-other-stories'])
# %%
df[df.incidence==3000].index
#%%


df[df.incidence==3000]['incidence_glob'] = df_glob_incidence.loc[df[df.incidence==3000].index]

# %%
df['incidence_glob']=[0]*311
# %%
df.loc['adidas']
# %%
df
# %%
df.loc[df.incidence==3000,'incidence_glob'] = df_glob_incidence.loc[df[df.incidence==3000].index]
# %%
brands_2_scrap_from = df.sort_values(by=['incidence','incidence_glob']).groupby(by='Segment de marché').tail(5).index.tocsv()
#%%
import contextlib
def get_brand(brand: str, driver: Chrome):
    data = {'brand':[], 'prix':[]}
    page = 1
    default_url = f'https://www.vinted.fr/brand/{brand}?catalog[]=1806&catalog[]=1807&catalog[]=1808&page='
    driver.get(default_url + str(page))
    while True: 
        articles = driver.find_elements(by=By.CSS_SELECTOR, value='h3.Text_text__QBn4-.Text_subtitle__1I9iB.Text_left__3s3CR.Text_amplified__2ccjx.Text_bold__1scEZ')
        for article in articles:
            data['brand'].append(brand)
            data['prix'].append(article.text.split(',')[0])
        page+=1
        driver.get(default_url + str(page))
        with contextlib.suppress(NoSuchElementException):
            driver.find_element(by=By.CSS_SELECTOR, value='h1.Text_text__QBn4-.Text_heading__gV4um.Text_center__1au2s')
            break
    pd.DataFrame(data).to_csv(f'brands/{brand}.csv')
    
# %%
driver = webdriver.Chrome(executable_path='/Users/g0bel1n/scrapped/src/scrapping/chromedriver')
for brand in brands_2_scrap_from:
    get_brand(brand=brand, driver=driver)
# %%
brands_2_scrap_from
# %%
driver = webdriver.Chrome(executable_path='/Users/g0bel1n/scrapped/src/scrapping/chromedriver')
get_brand(brand='hm', driver=driver)
# %%
import os
files = [el for el in os.listdir('brands') if el.endswith('.csv')]
df = pd.read_csv(f'brands/{files[0]}')
for file in files[1:]:
    df = pd.concat([pd.read_csv(f'brands/{file}'), df])
#%%

df
# %%
brands_2_scrap_from.to_csv(
)
# %%
df1  = pd.read_csv('../tshirt_selection_prices.csv', delimiter=';')
# %%
df1['middle_price'] = (df1['prix min'].str.replace(',', '.').astype(float) + df1['prix max'].str.replace(',', '.').astype(float))/2
# %%
dict_translator = df1[['middle_price','name']].set_index('name').to_dict()['middle_price']
dict_translator['hm'] = dict_translator['h&m']
# %%
df['prix neuf'] = df.brand.apply(lambda x : dict_translator[x])
#%%
df['rabais'] =  df['prix']/df['prix neuf']
# %%
df['rabais']
# %%
sheet_df['N°Obs'] = sheet_df['N°Obs'].str.replace(' ', '-').str.lower()
# %%
sheet_df = sheet_df.set_index('N°Obs')
# %%
sheet_df=sheet_df[['Segment de marché', 'Niveau de prix']]

# %%
abc = sheet_df.to_dict()
# %%
df['Segment'] = df['brand'].apply(lambda x : abc['Segment de marché']['h&m' if x=='hm' else x])
# %%
df['Niveau'] = df['brand'].apply(lambda x : abc['Niveau de prix']['h&m' if x=='hm' else x])

# %%
import plotly.express as px
category_orders = {"Niveau" : ['Discount','Bas', 'Moyen-Bas', 'Moyen', 'Moyen-Haut', 'Haut', 'Premium Luxury', 'Luxe'], "Segment" : [
        "ultra fast fashion / discount",
        "entrée de gamme / mass market",
        "milieu de gamme",
        "premium / luxe abordable",
        "luxe & création",
    ], "État" :[
        "BON ÉTAT",
        "NEUF AVEC ÉTIQUETTE",
        "NEUF SANS ÉTIQUETTE",
        "SATISFAISANT",
        "TRÈS BON ÉTAT",
    ] }
pd.options.plotting.backend = "plotly"

fig = px.histogram(df[df['rabais']<1.], x='Segment', y='rabais',histfunc='avg', category_orders=category_orders)
fig.show()
# %%
df[df['rabais']<1.].groupby(by='Segment')['prix neuf'].mean(

)# %%

# %%
