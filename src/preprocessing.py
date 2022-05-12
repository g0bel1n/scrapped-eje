import itertools
import pandas as pd

conversionEtat = {
    "Très bon état": "TRÈS BON ÉTAT",
    "Bon état": "BON ÉTAT",
    "Jamais porté": "NEUF SANS ÉTIQUETTE",
    "Jamais porté avec étiquette": "NEUF AVEC ÉTIQUETTE",
    "Correct": "SATISFAISANT",
}


def standardEtat(etat: str) -> str:
    return conversionEtat[etat]


def cleanPrice(price: str) -> float:
    return float(price.split("€")[0][:-1].replace(",", "."))


def dropWrongArticles(
    keywords: list, colsToTest: list, df: pd.DataFrame, reject_kw: list
):

    for testWord, col in itertools.product(keywords, colsToTest):
        try:
            df.keep += df[col].str.contains(testWord)
        except AttributeError:
            df["keep"] = df[col].str.contains(testWord)

    for rejectWord, col in itertools.product(reject_kw, colsToTest):
        df.keep &= ~df[col].str.contains(rejectWord)

    if "TAILLE" in df.columns:
        df.keep &= ~df["TAILLE"].str.contains("ANS")

    df = df[df.keep > 0]
    return df.drop(["keep"], axis=1)


def preprocessVesCoDf(df_vesco: pd.DataFrame) -> pd.DataFrame:
    df_vesco = df_vesco.drop(["Taille"], axis=1)
    df_vesco.columns = ["État", "Marque", "Date", "Description", "Prix"]
    df_vesco.Description = df_vesco.Description.str.upper()
    df_vesco.État = df_vesco.État.apply(standardEtat)
    df_vesco.Prix = df_vesco.Prix.apply(cleanPrice)
    df_vesco.Marque = df_vesco.Marque.str.upper().str.lstrip().str.rstrip()
    return df_vesco


def preprocessVintedDf(df_vinted: pd.DataFrame) -> pd.DataFrame:
    df_vinted.drop(["NOMBRE DE VUES", "EMPLACEMENT"], inplace=True, axis=1)
    df_vinted.columns = [
        "État",
        "Marque",
        "TAILLE",
        "Date",
        "nom",
        "Prix",
        "Description",
    ]
    df_vinted.Date = df_vinted.Date.apply(lambda x: x.split(" ")[0])
    df_vinted.Description = df_vinted.Description.str.upper().str.lstrip().str.rstrip()
    df_vinted.nom = df_vinted.nom.str.upper().str.lstrip().str.rstrip()
    df_vinted.Marque = df_vinted.Marque.str.upper().str.lstrip().str.rstrip()
    df_vinted.TAILLE = df_vinted.TAILLE.apply(lambda x: str(x).upper())

    return df_vinted


UltraFastFashion = [
    "SHEIN",
    "FASHION NOVA",
    "PRETTYLITTLETHING",
    "CIDER",
    "BOOHOO",
    "ASOS",
    "MISSGUIDED",
    "ZAFUL",
    "KIABI",
]
# Prix Max<20

FastFashion = [
    "ZARA",
    "VANS",
    "AIRNESS",
    "TOMMY",
    "PUMA",
    "NEW BALANCE",
    "ELLESSE",
    "LE TEMPS DES CERISES",
    "SKETCHERS",
    "VANESSA WU",
    "H&M",
    "BERSHKA",
    "FOREVER21",
    "MANGO",
    "TOPSHOP",
    "UNIQLO",
    "URBAN OUTFITTER",
    "GAP",
    "PEPE JEANS",
    "BONS BAISERS DE PANAME",
    "KAPORAL",
    "GUESS",
    "LA PETITE FRANCAISE",
    "PULL & BEAR",
    "PROMOD",
    "ARTENGO",
    "FILA",
    "NIKE",
    "CONVERSE",
    "ADIDAS",
    "UNIQLO" "ASICS",
    "REEBOK",
    "GÉMO",
    "SERGIO ROSSI",
    "LIBERTO",
    "GEOX",
    "KAPPA",
    "HEELYS",
    "NAF NAF",
    "LEVI'S",
    "REEBOK",
    "TAPE À L'OEIL",
    "PIMKIE",
    "JENNYFER",
    "CAMAÏEU",
    "SERGIO TACCHINI",
]
# Prix Max < 50

Fashion = [
    "ACNE",
    "SUPERDRY",
    "DC",
    "JORDAN",
    "SANDRO",
    "LACOSTE",
    "VEJA",
    "CARHART",
    "RALPH LAUREN",
    "KENZO",
    "COMME DES GARÇONS",
]
# Prix Max < 100

UltraFashion = [
    "PALM",
    "ANINE BING",
    "SUPREME",
    "VIVIENNE WESTWOOD",
    "OFF-WHITE",
    "YEEZY",
    "STONE ISLAND",
    "JEAN PAUL GAULTIER",
    "FEAR OF",
    "SANTONI",
    "GIUSEPPE ZANOTTI",
    "HOGAN",
    "KARL LAGERFELD",
    "STEVE MADDEN",
    "VALENTINO",
    "DIESEL",
    "FEAR OF GOD ESSENTIALS",
    "TRUE RELIGION",
    "ISABEL MARANT",
    "VALENTINO GARAVANI",
    "LOUIS VUITTON",
    "SAINT LAURENT",
    "POLO RALPH LAUREN",
    "DR. MARTENS",
    "LOEFFLER RANDALL",
    "CARVEN",
    "MOSCHINO",
    "HARRYS OF LONDON",
    "PIERRE HARDY",
    "LE LISSIER",
]
# Prix Max > 300

Luxe = [
    "JACQUEMUS",
    "VERSACE",
    "GIVENCHY",
    "FENDI",
    "PRADA",
    "DIOR",
    "BALENCIAGA",
    "DOLCE & GABBANA",
    "PHILIPP PLEIN",
    "BURBERRY",
    "GUCCI",
    "VERSACE",
    "D&G",
    "PRADA",
    "CHANEL",
    "YVES SAINT LAURENT",
    "BALMAIN",
    "DSQUARED2",
    "AMIIRI",
    "Y/PROJECT",
]
# Prix Min > 300


def categoriseMarque(row: pd.Series) -> str:
    if row["Marque"] in UltraFastFashion or any(
        marqueTest in row["Marque"] for marqueTest in UltraFastFashion
    ):
        return "UltraFastFashion"

    elif row["Marque"] in FastFashion or any(
        marqueTest in row["Marque"] for marqueTest in FastFashion
    ):
        return "FastFashion"

    elif row["Marque"] in Fashion or any(
        marqueTest in row["Marque"] for marqueTest in Fashion
    ):
        return "Fashion"

    elif row["Marque"] in Luxe or any(
        marqueTest in row["Marque"] for marqueTest in Luxe
    ):
        return "Luxe"

    elif row["Marque"] in UltraFashion or any(
        marqueTest in row["Marque"] for marqueTest in UltraFashion
    ):
        return "UltraFashion"

    else:
        return "Undefined"
