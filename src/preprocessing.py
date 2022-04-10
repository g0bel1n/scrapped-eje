import itertools
import pandas as pd

conversionEtat = {'Très bon état': 'TRÈS BON ÉTAT', 'Bon état': 'BON ÉTAT', 'Jamais porté':'NEUF SANS ÉTIQUETTE', 'Jamais porté avec étiquette':'NEUF AVEC ÉTIQUETTE', 'Correct':'SATISFAISANT'}

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
    
    df[df.keep>0].drop(['keep'], axis=1, inplace=True)
    return df

def preprocessVesCoDf(df_vesco: pd.DataFrame)->pd.DataFrame:
    df_vesco = df_vesco.drop(['Taille'], axis=1)
    df_vesco.columns = ['État', 'Marque', 'Date', 'Description', 'Prix']
    df_vesco.Description = df_vesco.Description.str.upper()
    df_vesco.État = df_vesco.État.apply(standardEtat)
    df_vesco.Prix = df_vesco.Prix.apply(cleanPrice)
    df_vesco.Marque = df_vesco.Marque.str.upper()
    return df_vesco

def preprocessVintedDf(df_vinted: pd.DataFrame)->pd.DataFrame:
    df_vinted.drop(['NOMBRE DE VUES','EMPLACEMENT', 'TAILLE'], inplace=True, axis=1)
    df_vinted.columns = ['État', 'Marque', 'Date', 'nom','Prix', 'Description']
    df_vinted.Date = df_vinted.Date.apply(lambda x: x.split(' ')[0])
    df_vinted.Description = df_vinted.Description.str.upper()
    df_vinted.nom = df_vinted.nom.str.upper()


    return df_vinted


UltraFastFashion = ['SHEIN','FASHION NOVA', 'PRETTYLITTLETHING', 'CIDER', 'BOOHOO','ASOS', 'MISSGUIDED', 'ZAFUL', 'KIABI']

FastFashion =['ZARA','VANS','AIRNESS' ,'TOMMY','PUMA','NEW BALANCE','ELLESSE', 'SKETCHERS','VANESSA WU', 'H&M', 'BERSHKA', 'FOREVER21', 'MANGO', 'TOPSHOP', 'UNIQLO', 'URBAN OUTFITTER', 'GAP', 'PEPE JEANS', 'KAPORAL', 'PULL & BEAR', 'PROMOD', 'ARTENGO', 'FILA', 'NIKE', 'CONVERSE', 'ADIDAS','UNIQLO' 'ASICS', 'REEBOK', 'GÉMO', 'SERGIO ROSSI', 'LIBERTO', 'GEOX', 'KAPPA', 'HEELYS', 'NAF NAF', "LEVI'S", 'REEBOK', "TAPE À L'OEIL", 'PIMKIE', 'JENNYFER', 'CAMAÏEU', 'SERGIO TACCHINI']
Fashion=['ACNE', 'SUPERDRY', 'DC', 'JORDAN','SANDRO', 'LACOSTE', 'VEJA', 'CARHART','RALPH LAUREN']
UltraFashion = ['LE TEMPS DES CERISES','PALM','JACQUEMUS','ANINE BING','SUPREME','VIVIENNE WESTWOOD','COMME DES GARÇONS','OFF-WHITE','YEEZY','STONE ISLAND','JEAN PAUL GAULTIER','VERSACE','GIVENCHY','FEAR OF', 'FENDI','PRADA', 'SANTONI','GIUSEPPE ZANOTTI','HOGAN','KARL LAGERFELD', 'STEVE MADDEN', 'BONS BAISERS DE PANAME', 'DIOR','BALENCIAGA', 'VALENTINO', 'DIESEL', 'DOLCE & GABBANA','PHILIPP PLEIN', 'LA PETITE FRANCAISE', 'BURBERRY','YVES SAINT LAURENT','BALMAIN' 'GUESS', 'FEAR OF GOD ESSENTIALS', 'AMIIRI', 'Y/PROJECT', 'TRUE RELIGION','DSQUARED2', 'ISABEL MARANT', 'GUCCI', 'VERSACE', 'D&G', 'PRADA', 'VALENTINO GARAVANI', 'MOLLY BRACKEN', 'LOUIS VUITTON', 'SAINT LAURENT', 'KENZO', 'POLO RALPH LAUREN', 'DR. MARTENS', 'BOUTIQUE PARISIENNE', 'LOEFFLER RANDALL', 'CARVEN', 'MOSCHINO', 'HARRYS OF LONDON', 'PIERRE HARDY', 'LE LISSIER', 'CHANEL']


def categoriseMarque(row: pd.Series)->str:
    if row['Marque'] in UltraFastFashion or any(marqueTest in row['Marque'] for marqueTest in UltraFastFashion) : return 'UltraFastFashion'

    elif row['Marque'] in FastFashion or any(marqueTest in row['Marque'] for marqueTest in FastFashion): return 'FastFashion'

    elif row['Marque'] in Fashion or any(marqueTest in row['Marque'] for marqueTest in Fashion): return 'Fashion'

    elif row['Marque'] in UltraFashion or any(marqueTest in row['Marque'] for marqueTest in UltraFashion): return 'UltraFashion'
    
    else:
        return 'Undefined'
