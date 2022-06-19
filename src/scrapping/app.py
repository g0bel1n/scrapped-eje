import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image


pd.options.plotting.backend = "plotly"

col1, col2, col3 = st.columns([3,6,3])

with col1:
    st.write("Lucas Saban lucas.saban[at]ensae.fr")

with col2:
    st.markdown("<h1 align = center> Support interactif </h1> ", unsafe_allow_html=True)
    st.markdown("<h2 align = center> EJE x FHCM </h2> ", unsafe_allow_html=True)


with col3:
    logoeje = Image.open('src/logoeje.png')
    st.image(logoeje)



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

categories = category_orders["Segment de marché"]
with st.sidebar:
    logo = Image.open('src/LOGO-ENSAE.png')

    
    option = st.selectbox(
        "Choisissez le produit considéré",
        ("Jean", "Veste de Costume", "Baskets", "Tshirt"),
    )
    website = st.selectbox(
        "Choisissez le site considéré", ("Vinted", "Vestiaire collective")
    )

    with st.expander("Modifier l'estimation du prix neuf"):
        
        st.write("Ajustez le prix neuf estimé selon les segments de marché.")

        st.info("Vers 1, le prix neuf estimé est le prix maximum trouvé en ligne \n. À 0, c'est le prix minimum. Entre 0 et 1, on obtient une pondération entre les deux. La valeur 0.5 correspond à la valeur moyenne")

        x_s = {
            cat: st.slider(
                cat, min_value=0.0, max_value=1.0, value=0.5, step=0.1, key=cat
            )
            for cat in categories
        }

    st.image(logo)


website = "vestco" if website == "Vestiaire collective" else website
df = pd.read_csv(
    f"src/scrapping/{website}/focus/focus_{website}_{option.lower().split(' ')[-1]}.csv"
)
df = df[~(df["max"] == "/")]
df["max"] = df["max"].astype(float)
df["min"] = df["min"].astype(float)

df["prix neuf"] = df.apply(
    lambda x: (
        x_s[x["Segment de marché"]] * x["max"]
        + (1 - x_s[x["Segment de marché"]]) * x["min"]
    ),
    axis=1,
)
df["Valeur résiduelle"] = df["prix"] / df["prix neuf"]

df = df[df["Valeur résiduelle"] < 1.0]
fig = px.histogram(
    data_frame=df,
    y="Valeur résiduelle",
    histfunc="avg",
    x="Segment de marché",
    category_orders=category_orders,
    text_auto=True,
)

img = Image.open(f"src/scrapping/{website}/incidence/incidence_{website}_{option.lower().split(' ')[-1]}.png")
with st.expander("Incidence"):
    st.image(img)


with st.expander("Moyenne des Valeur résiduelle par segment de marché "):
    st.plotly_chart(fig, use_container_width=True)

fig1 = px.scatter(
    data_frame=df,
    x="prix",
    y="Valeur résiduelle",
    color="Segment de marché",
    category_orders=category_orders,
)
with st.expander("Valeur résiduelle en fonction du prix de revente"):
    st.plotly_chart(fig1, use_container_width=True)


