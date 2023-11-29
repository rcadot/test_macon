import streamlit as st
import plotly.express as px
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
from func import *


def _max_width_(prcnt_width: int = 100):
    max_width_str = f"max-width: {prcnt_width}%;"
    st.markdown(
        f""" 
                <style> 
                .reportview-container .main .block-container{{{max_width_str}}}
                </style>    
                """,
        unsafe_allow_html=True,
    )


st.title("Conjoncture foncière")
(cola, colb, colc) = st.columns([1, 1, 1])
with cola:
    st.write(
        """

## Objectif

L'objectif de cet outil en ligne est de pouvoir approfondir plus finement les analyses demandées en matières de conjoncture foncière.

## Méthodologie

### Données

L'ensemble des éléments présentés dans le document proviennent de deux jeux de données :

- Les documents d'urbanisme extraits sur le géoportail de l'urbanisme en octobre 2023 ;
- DVF+ édition octobre 2023.

**🔔 Attention**

_Nous disposons des données sur les mutations depuis 2014, mais les documents d'urbanisme évoluent et les mutations de 2014 d'une commune n'étaient probablement dans le même zonage du PLU actuel. **N'ayant pas d'historique des documents, plus on remonte le temps, plus le biais sera important.** Il est par ailleurs impossible de quantifier cette marge d'erreur._


"""
    )


with colb:
    st.write(
        """

### Hypothèses

Afin d'obtenir des croisements pertinents, il est nécessaire d'effectuer quelques hypothèses et filtres sur les données d'entrée.

##### Documents d'urbanisme

- Les zones constructibles des cartes communales ont été renommées en U afin de faciliter la lecture ;
- On ne conserve pas les zonages AUs (2AU) des documents d'urbanisme car leur réalité physique est très différentes selon les territoires (équipements, etc.)


#### DVF+

On ne conserve que :

- les ventes ;
- supérieures à 100€ ;
- sur une seule commune par transaction ;
- avec une surface de parcelle comprise entre 100 et 2000m² ;
- pour le bâti, on utilise la variable `codtypbien` ;
- les bâtis concernant l'activité ne sont pas distingués par destination (pas disponible pour dvfplus).
"""
    )

with colc:
    st.write(
        """
        
         #### Découpage des parcelles avec les documents d'urbanisme

"""
    )

with colc:
    st.image("010_principes_decoupe.excalidraw.png")

with colc:
    st.write(
        """
### Calculs

Le prix au m² est réalisé en prenant les valeurs suivantes : `valeur foncière / (sbati ou sterr)`
    """
    )

st.subheader("📊 Évolution des prix")
# st.write(
#     """
#          > une représentation de l'évolution des prix de ventes des terrains nus, comparée à l'évolution des prix de vente des maisons, des appartements et des surfaces destinées aux activités commerciales."""
# )
st.markdown("""**Choix les filtres**""")
st.markdown("""_Les filtres sont cumulatifs_""")

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    st_typbien = st.multiselect(
        "Choix des typologies",
        ["Non bâti", "Maison", "Appartement", "Activité"],
        default=["Non bâti", "Maison", "Appartement", "Activité"],
    )

with col2:
    st_zone = st.multiselect(
        "choix des zonages d'urbanisme", ["U", "AUc"], default=["U", "AUc"]
    )

# with col2b:
#     st_perimetre = st.multiselect(
#         "Choix des regroupements",
#         [
#             "region",
#             "dep",
#             "Zone ABC",
#             "LIBDENS",
#             "localisation",
#             "taav",
#             "libaav2020",
#             "cateaav",
#         ],
#         default=None,
#     )


with col3:
    st_statistiques = st.selectbox(
        "Statistiques",
        [
            "surface_compte",
            "surface_somme",
            "prix_m2_mediane",
        ],
        index=2
        # default=["prix_m2_mediane", "surface_compte", "surface_somme"],
    )

periodes_index = {periode: index for index, periode in enumerate(periodes)}

with col4:
    borne_inf, borne_sup = st.select_slider(
        "Période", options=periodes, value=(periodes[0], periodes[-2])
    )

borne_inf_index = periodes_index[borne_inf]
borne_sup_index = periodes_index[borne_sup]
valeurs_entre_bornes = periodes[borne_inf_index : borne_sup_index + 1]


#######################################################

left_column, center_column, right_column = st.columns([2, 4, 2])

#######################################################


########## GRAPH #############

filtered_data_graph1 = traitement_donnees_stats(
    zones=st_zone,
    typbien=st_typbien,
    duree=valeurs_entre_bornes,
    peri=None,
    stat=[st_statistiques],
)

fig = px.bar(
    filtered_data_graph1,
    height=600,
    x="semestre_annee",
    y="valeur",
    color="zone",
    # color_discrete_sequence=px.colors.sequential.Reds,
    color_discrete_sequence=["#3d85c6", "#b1cee8"],
    labels={"valeur": "Valeur"},
    facet_row="typbien",
    # facet_col="statistique",
    # line_group="zone",  # Spécifiez le groupement des lignes par "zone"
    barmode="group",
)

# fig.update_traces(line_shape="linear")  # Ajout de cette ligne

fig.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    showlegend=True,
    legend=dict(
        x=0.5,  # Pour le centrer horizontalement
        y=-0.3,  # Pour le placer en bas
        xanchor="center",
        yanchor="bottom",
        orientation="h",
    ),
    hovermode="x unified",
)


fig.update_yaxes(matches="x", title_text="")
fig.update_xaxes(title_text="")
for a in fig.layout.annotations:
    a.text = a.text.split("=")[1]

# left_column.write(
#     """
# > une représentation de l'évolution des prix de ventes des terrains nus, comparée à l'évolution des prix de vente des maisons, des appartements et des surfaces destinées aux activités commerciales."""
# )
center_column.plotly_chart(fig, use_container_width=True)

#######################################################


# right_column.subheader("🔢 Synthèse")


# pour_dataframe = traitement_tableau(df=filtered_data_graph1, peri=st_perimetre)
# # pour_dataframe = pd.DataFrame(pour_dataframe.to_records()).sort_index()


# right_column.dataframe(
#     pour_dataframe,
#     # hide_index=True,
#     use_container_width=True,  # columns=column_config
# )

# #################################################
st.divider()
# graph 2
st.subheader("📊 Évolution des prix par typologie de territoire")

# st.write(
#     """
# > On ne s'éloignerait pas trop de sur ce quoi nous avions échangé, mais il faudrait avoir à la fois les variations de prix par classe de densité INSEE en fonction de la position de la commune par rapport à l'aire d'attractivité avec 3 type d'agrégation par aire d'attraction, par région et par catégories d'aire d'attraction.
# >
# > Est-ce que vous pensez qu'il est possible de séparer les terrains nus selon leur taille? Il me semble que le choix de départ était d'évaluer les variations de 100m² a 2000m², on pourrait prendre 3 segments pour les terrains, petits, moyens et grands en fonction des terciles des surfaces vendues.
# >
# > Je pense que ça peut valoir le coup d'avoir l'évolution sur la totalité de la plage disponible (2010-2023) quitte à raboter à postériori les résultats.
# """
# )

rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns([1, 1, 1, 1, 2])

with rcol1:
    st_taille = st.multiselect(
        "Taille des parcelles",
        ["petite", "moyenne", "grande"],
        default=["petite", "moyenne", "grande"],
    )

# with rcol1b:


with rcol2:
    st_zone2 = st.selectbox("choix des zonages", ["U", "AUc"])


with rcol3:
    st_perimetre_row = st.selectbox(
        "Lignes",
        [
            "taav",
            # "communes",
            # "region",
            # "dep",
            # "Zone ABC",
            # "LIBDENS",
            "localisation",
            # "libaav2020",
            # "cateaav",
        ],
        index=0,
    )


with rcol4:
    borne_inf2, borne_sup2 = st.select_slider(
        "Période graph", options=periodes, value=(periodes[0], periodes[-2])
    )

with rcol5:
    with st.expander("Choix des communes"):
        st_regions = st.multiselect(
            "communes", liste_communes, liste_communes, label_visibility="hidden"
        )

borne_inf_index2 = periodes_index[borne_inf2]
borne_sup_index2 = periodes_index[borne_sup2]
valeurs_entre_bornes2 = periodes[borne_inf_index2 : borne_sup_index2 + 1]

ma_fig2 = graph2(
    st_zone2=[st_zone2],
    valeurs_entre_bornes2=valeurs_entre_bornes2,
    st_perimetre_col="LIBDENS",
    st_perimetre_row=st_perimetre_row,
    st_statistiques2=["prix_m2_mediane"],
    taille=st_taille,
    regions=st_regions,
    titre=f"Évolution des prix médians en zone {st_zone2} par {st_perimetre_row}",
    hauteur=800,
)

# st.write(ma_fig2)

st.plotly_chart(ma_fig2, use_container_width=True)

st.divider()

# #######################################################
# graph 3
st.subheader("📊 Évolution des flux")

# st.write(
#     """
# > D'autre part, une analyse de l'évolution des flux (monétaires, surfaciques et en nombre) d'échanges sur les terrains pour objectiver les comportements et notamment, s'il existe un effondrement des acquisitions, avec une représentation des évolutions des flux en fonction de la position de la commune rapport à l'aire d'attractivité avec 3 échelles d'agrégations (région, Aire d'attraction et type d'aire d'attraction). On peut partir sur la période 2020-2023.
# """
# )


scol1, scol2, scol3, scol4, scol5 = st.columns([1, 1, 1, 1, 2])

# with scol1:
#     st_zone3 = st.selectbox("choix des zonages d'urbanisme", ["U", "AUc"], key="zone3")

# with rcol1b:


with scol2:
    st_zone3 = st.selectbox("Zonages", ["U", "AUc"])


with scol3:
    st_perimetre_col3 = st.selectbox(
        "Colonnes",
        [
            # "region",
            # "dep",
            # "Zone ABC",
            # "LIBDENS",
            "taav",
            "localisation",
            # "libaav2020",
            # "cateaav",
        ],
        index=1,
    )


with scol4:
    borne_inf3, borne_sup3 = st.select_slider(
        "Période retenue", options=periodes, value=(periodes[-9], periodes[-2])
    )

with scol5:
    with st.expander("Choix des communes"):
        st_regions3 = st.multiselect(
            "Choix des communes",
            liste_communes,
            liste_communes,
            label_visibility="hidden",
        )

borne_inf_index3 = periodes_index[borne_inf3]
borne_sup_index3 = periodes_index[borne_sup3]
valeurs_entre_bornes3 = periodes[borne_inf_index3 : borne_sup_index3 + 1]


ma_fig3 = graph3(
    duree=valeurs_entre_bornes3,
    peri=[st_perimetre_col3],
    zonage=[st_zone3],
    stat=["prix_m2_mediane", "surface_compte", "surface_somme"],
    st_perimetre_col=st_perimetre_col3,
    regions=st_regions3,
    titre=f"Évolution des flux de transactions foncières par {st_perimetre_col3} en zone {st_zone3}",
)

# st.write(ma_fig3)

st.plotly_chart(ma_fig3, use_container_width=True)

# ######################################################

st.divider()

# CARTO

st.subheader("🗺️ Carte pour mieux appréhender les dynamiques spatiales")


ccol1, ccol2 = st.columns([1, 4])

with ccol1:
    c_typbien = st.selectbox(
        "Choix des typologies",
        [
            "Non bâti",
            "Maison",
            "Appartement",
            "Activité",
        ],
    )

with ccol1:
    c_zone = st.selectbox(
        "choix des zonages d'urbanisme",
        ["U", "AUc"],
    )

with ccol1:
    c_perimetre = st.multiselect(
        "Choix des regroupements pour la carto",
        [
            # "region",
            "libgeo",
            "dep",
            "Zone ABC",
            "LIBDENS",
            "localisation",
            "taav",
            "libaav2020",
            "cateaav",
        ],
        default=["libgeo"],
    )

with ccol1:
    c_statistiques = st.selectbox(
        "Statistiques carto",
        [
            "prix_m2_mediane",
            # "prix_m2_moyenne",
            "surface_compte",
            "surface_somme",
        ],
    )

with ccol1:
    c_semestre = st.selectbox("Choix du semestre", periodes, index=17)

with ccol1:
    c_type_ind = st.selectbox("Choix de l'indicateur", ["valeur", "evolution"])

with ccol1:
    c_transac_mini = st.number_input("Nb de transactions minimales", value=1)

# st.write(ref)

ma_carto = gen_carto(
    peri=c_perimetre,
    indic=c_type_ind,
    zones=[c_zone],
    typbien=[c_typbien],
    statistique=[c_statistiques],
    semestre=c_semestre,
    transac_mini=c_transac_mini,
)

# st.write(ma_carto)

# st.write(ma_carto)

# with ccol2:
#     st.write(ma_carto)

with ccol2:
    st_data = folium_static(ma_carto, width=_max_width_())
