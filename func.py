from unittest import result
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import st_folium, folium_static
import sqlalchemy
from sqlalchemy import create_engine, text


@st.cache_data
def load_data():
    db = create_engine("sqlite:///data.db")
    return pd.read_sql(con=db, sql="select * from data")


data = load_data()

periodes = [
    "2014S1",
    "2014S2",
    "2015S1",
    "2015S2",
    "2016S1",
    "2016S2",
    "2017S1",
    "2017S2",
    "2018S1",
    "2018S2",
    "2019S1",
    "2019S2",
    "2020S1",
    "2020S2",
    "2021S1",
    "2021S2",
    "2022S1",
    "2022S2",
    "2023S1",
]


@st.cache_data
def load_ref():
    return gpd.read_file("ref_complet.gpkg")


ref = load_ref()


@st.cache_data
def communes():
    return data.nom.unique().tolist()


liste_communes = communes()


def filtre_data(zone, typbien, periode):
    df = data.loc[
        (data["semestre_annee"].isin(periode))
        & (data["zone"].isin(zone))
        & (data["typbien"].isin(typbien))
    ]
    return df


def agreg_data(data_complet=None, groupby_columns=None):
    if groupby_columns is None:
        groupby_columns = []

    df = (
        data_complet.groupby(
            groupby_columns
            + [
                "typbien",
                "zone",
                "semestre_annee",
            ],
            observed=True,
            # as_index=False,
        )
        .agg({"surface": ["sum", "count"], "prix_m2": ["median"]})
        .reset_index()
    )

    df.columns = groupby_columns + [
        "typbien",
        "zone",
        "semestre_annee",
        "surface_somme",
        "surface_compte",
        # "prix_m2_moyenne",
        "prix_m2_mediane",
    ]

    # df_2.columns = groupby_columns + [
    #     "typbien",
    #     "zone",
    #     "semestre_annee",
    #     "surface_somme",
    #     "surface_compte",
    #     # "prix_m2_moyenne",
    #     "prix_m2_mediane",
    # ]

    # df_final = pd.concat([df, df_2])
    df_final = df

    melted_df_final = pd.melt(
        df_final,
        id_vars=groupby_columns + ["typbien", "zone", "semestre_annee"],
        var_name="statistique",
        value_name="valeur",
    )

    melted_df_final["valeur"] = melted_df_final["valeur"].round(0)

    melted_df_final["evolution"] = (
        melted_df_final.groupby(
            groupby_columns + ["typbien", "zone", "statistique"],
            observed=True
            # as_index=False
        )["valeur"].pct_change()
        * 100
    ).round(0)

    melted_df_final.reset_index(inplace=True)

    return melted_df_final


def traitement_donnees_stats(zones, typbien, duree, peri, stat):
    df_filtre = filtre_data(zone=zones, typbien=typbien, periode=duree)
    df_complet = pd.merge(df_filtre, ref, on="codgeo")
    result = agreg_data(df_complet, peri)
    result = result[result["statistique"].isin(stat)]
    #     return a_return
    return result


def traitement_donnees_stats2(zones, typbien, duree, peri, stat):
    df_filtre = filtre_data(zone=zones, typbien=typbien, periode=duree)
    df_complet = pd.merge(df_filtre, ref, on="codgeo")
    result = agreg_data(df_complet, peri)
    result = result[result["statistique"].isin(stat)]
    return result


# @st.cache_data
def pivot_semestre_annee(df_long):
    liste_des_colonnes = df_long.columns.difference(
        ["semestre_annee", "valeur", "evolution"]
    ).tolist()

    df_wide = df_long.pivot_table(
        index=liste_des_colonnes,
        columns="semestre_annee",
        values=["valeur", "evolution"],
    )

    # df_wide.reset_index(inplace=True)

    return df_wide


# @st.cache_data
def traitement_tableau(df, peri):
    pour_dataframe = pivot_semestre_annee(df)  # .drop(columns=["evolution"])
    pour_dataframe = (
        pour_dataframe.groupby(peri + ["statistique", "typbien", "zone"])
        .sum()
        .drop(columns=["evolution"])
        # .reset_index()
        # .droplevel()
        # .rename_axis(index=(None, None), columns=None)
    )
    return pour_dataframe


def graph2(
    st_zone2,
    valeurs_entre_bornes2,
    st_perimetre_col,
    st_perimetre_row,
    st_statistiques2,
    taille,
    regions,
    titre="",
    hauteur=800,
):
    peri = (
        [st_perimetre_col, st_perimetre_row, "taille"]
        if taille
        else [st_perimetre_col, st_perimetre_row]
    )

    df_filtre = filtre_data(
        zone=st_zone2, typbien=["Non bâti"], periode=valeurs_entre_bornes2
    )

    # on filtre sur la taille avant de faire l'analyse
    if taille != []:
        df_filtre = df_filtre.loc[df_filtre["taille"].isin(taille)]

    df_complet = pd.merge(
        df_filtre, pd.DataFrame(ref.drop(columns="geometry")), on="codgeo"
    )

    df_complet = df_complet.loc[df_complet["nom_x"].isin(regions)]

    result = agreg_data(df_complet, peri)

    result = result[result["statistique"].isin(st_statistiques2)]

    # return result  # ICI

    filtered_data_graph2 = result
    # on ne peut pas prendre le traitement_donnees_stats2 car il faut filtrer sur la taille
    # en plus

    # filtered_data_graph2 = traitement_donnees_stats2(
    #     zones=st_zone2,
    #     typbien=["Non bâti"],
    #     duree=valeurs_entre_bornes2,
    #     peri=peri,
    #     stat=st_statistiques2,
    # )

    # ordre=filtered_data_graph2.groupby(
    #    st_perimetre_col).max().sort_values("valeur").reset_index()[st_perimetre_col]

    fig2 = px.bar(
        filtered_data_graph2,
        height=hauteur,
        x="semestre_annee",
        y="valeur",
        color="taille" if taille else None,
        # color_discrete_sequence=px.colors.sequential.Reds,
        color_discrete_sequence=["rgb(103,0,13)", "rgb(203,24,29)", "rgb(252,146,114)"],
        labels={"valeur": "Valeur"},
        facet_row=st_perimetre_row,
        facet_col=st_perimetre_col,
        # category_orders={st_perimetre_col:ordre},
        # line_group="zone"
        barmode="group",
    )
    fig2.update_layout(
        font=dict(size=8),
        title=titre,
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

    fig2.update_yaxes(title_text="", matches="x")
    fig2.update_xaxes(title_text="")

    for a in fig2.layout.annotations:
        a.text = a.text.split("=")[1]

    for annotation in fig2["layout"]["annotations"]:
        annotation["textangle"] = 0

    # pour que chaque axes des y soient indépendants en facet_row mais identique en facet_col
    for row_idx, row_figs in enumerate(fig2._grid_ref):
        for col_idx, col_fig in enumerate(row_figs):
            fig2.update_yaxes(
                row=row_idx + 1,
                col=col_idx + 1,
                matches="y" + str(len(row_figs) * row_idx + 1),
            )

    return fig2


def graph3(
    duree,
    peri,
    zonage,
    stat,
    st_perimetre_col,
    regions,
    titre="",
):
    df_filtre = filtre_data(zone=zonage, typbien=["Non bâti"], periode=duree)

    df_complet = pd.merge(df_filtre, ref, on="codgeo")

    df_complet = df_complet.loc[df_complet["nom_x"].isin(regions)]

    result = agreg_data(df_complet, peri)

    result = result[result["statistique"].isin(stat)]

    filtered_data_graph2 = result

    # filtered_data_graph2 = traitement_donnees_stats2(
    #     zones=zones,
    #     typbien=typbien,
    #     duree=duree,
    #     peri=[peri],
    #     stat=stat,
    # )
    # return filtered_data_graph2

    ordre = (
        filtered_data_graph2.groupby(st_perimetre_col)
        .max()
        .sort_values("valeur")
        .reset_index()[st_perimetre_col]
    )

    fig2 = px.line(
        filtered_data_graph2,
        height=800,
        x="semestre_annee",
        y="valeur",
        color="statistique",
        # color_discrete_sequence=px.colors.sequential.Reds,
        color_discrete_sequence=["rgb(103,0,13)", "rgb(203,24,29)", "rgb(252,146,114)"],
        labels={"valeur": "Valeur"},
        facet_row="statistique",
        facet_col=st_perimetre_col,
        category_orders={st_perimetre_col: ordre}
        # line_group="zone"
        # barmode="group",
    )
    fig2.update_layout(
        font=dict(size=8),
        title=titre,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        legend=dict(
            x=0.5,  # Pour le centrer horizontalement
            y=-0.3,  # Pour le placer en bas
            xanchor="center",
            yanchor="bottom",
            orientation="h",
        ),
        hovermode="x unified",
    )

    fig2.update_yaxes(title_text="", matches="y")
    fig2.update_xaxes(title_text="")

    for a in fig2.layout.annotations:
        a.text = a.text.split("=")[1]

    for annotation in fig2["layout"]["annotations"]:
        annotation["textangle"] = 0

        # pour que chaque axes des y soient indépendants en facet_row mais identique en facet_col
    for row_idx, row_figs in enumerate(fig2._grid_ref):
        for col_idx, col_fig in enumerate(row_figs):
            fig2.update_yaxes(
                row=row_idx + 1,
                col=col_idx + 1,
                matches="y" + str(len(row_figs) * row_idx + 1),
            )

    return fig2


# @st.cache_data
def gen_carto(peri, indic, zones, typbien, statistique, semestre, transac_mini):
    df = data.loc[(data["zone"].isin(zones)) & (data["typbien"].isin(typbien))]
    df_complet = pd.merge(df, ref, on="codgeo")
    result = agreg_data(
        df_complet,
        peri,
    )

    choix_mini_transac = (
        result.loc[
            (result["statistique"] == "surface_compte")
            & (result["valeur"] >= transac_mini)
        ]
    ).drop(columns=["index", "statistique", "valeur", "evolution"])

    result = result.merge(
        choix_mini_transac, on=choix_mini_transac.columns.tolist(), how="inner"
    )
    # return result

    df_agrege = result[
        (result["statistique"].isin(statistique))
        & (result["semestre_annee"] == semestre)
    ]

    # on créer le référentiel

    def agreg_ref(peri):
        gdf = ref.dissolve(
            peri,
            aggfunc={
                "Nb_log_pp_2022": "sum",
                "Nb_logvac_2A_010121": "sum",
            },
        )
        gdf["taux_vac_2a"] = 100 * gdf["Nb_logvac_2A_010121"] / gdf["Nb_log_pp_2022"]

        gdf.reset_index(inplace=True)

        return gdf

    mon_ref = agreg_ref(peri)

    # on fait la jointure
    gdf = pd.merge(mon_ref, df_agrege, how="left", on=peri)

    # on génère la carto
    if indic == "valeur":
        m = gdf.explore(
            # m=m,
            tiles="Cartodb dark_matter",
            column=indic,
            cmap="Reds",
            # scheme="FisherJenks",
            name="Données",
            popup=True,
            tooltip=["valeur"],
            legend_kwds=dict(
                colorbar=True,
                caption=f"{indic} de {statistique} en zone {zones} au semestre : {semestre}",
            ),
        )

    else:
        vmin = gdf["evolution"].min()
        vmax = gdf["evolution"].max()

        m = gdf.explore(
            # m=m,
            tiles="Stamen Toner Lite",
            column=indic,
            cmap="RdYlGn",
            scheme="User_Defined",
            name="Données",
            popup=True,
            tooltip=["valeur"],
            classification_kwds=dict(
                bins=[vmin, -50, -25, -10, -5, 5, 10, 25, 50, vmax]
            ),
            legend_kwds=dict(
                colorbar=True,
                caption=f"{indic} de {statistique} en zone {zones} au semestre : {semestre}",
            ),
        )

    folium.LayerControl().add_to(m)

    folium.plugins.Fullscreen(
        position="topleft",
        title="Plein écran",
        title_cancel="Retour",
        force_separate_button=True,
    ).add_to(m)

    return m
