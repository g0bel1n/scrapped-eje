import itertools
import pandas as pd

conversionEtat = {'Très bon état': 'TRÈS BON ÉTAT', 'Bon état': 'BON ÉTAT', 'Jamais porté':'NEUF SANS ÉTIQUETTE', 'Jamais porté avec étiquette':'NEUF AVEC ÉTIQUETTES', 'Correct':'SATISFAISANT'}

def standardEtat(etat: str)-> str:
    return conversionEtat[etat]

def cleanPrice(price: str)->float:
    return float(price.split('€')[0][:-1].replace(',','.'))

def dropWrongArticles(keywords: list,colsToTest: list, df: pd.DataFrame)-> pd.DataFrame:
    for testWord, col in itertools.product(keywords,colsToTest):
        try :
            df.keep += df[col].str.contains(testWord)
        except AttributeError:
            df['keep'] = df[col].str.contains(testWord)
    return df[df.keep>0].drop(['keep'], axis=1)

def preprocessVesCoDf(df_vesco: pd.DataFrame)->pd.DataFrame:
    df_vesco = df_vesco.drop(['Taille'], axis=1)
    df_vesco.columns = ['État', 'Marque', 'Date', 'Description', 'Prix']
    df_vesco.État = df_vesco.État.apply(standardEtat)
    df_vesco.Prix = df_vesco.Prix.apply(cleanPrice)
    df_vesco.Marque = df_vesco.Marque.str.upper()
    return df_vesco

def preprocessVintedDf(df_vinted: pd.DataFrame)->pd.DataFrame:
    df_vinted.drop(['NOMBRE DE VUES','EMPLACEMENT', 'TAILLE'], inplace=True, axis=1)
    df_vinted.columns = ['État', 'Marque', 'Date', 'nom','Prix', 'Description']
    df_vinted.Date = df_vinted.Date.apply(lambda x: x.split(' ')[0])
    return df_vinted

