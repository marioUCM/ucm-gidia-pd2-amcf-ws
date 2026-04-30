import pandas as pd
from plotly import express as px
import os
import folium
from folium.plugins import HeatMap
from utils.read_from_minio import load_parquet_from_minio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

### LOCAL

# data1 = pd.read_parquet(BASE_DIR / "../../data/films/comparativa_taxi.parquet")
# data2 = pd.read_parquet(BASE_DIR / "../../data/films/impacto_taxi.parquet")
# data3 = pd.read_parquet(BASE_DIR / "../../data/films/friccion_taxi.parquet")
# data4 = pd.read_parquet(BASE_DIR / "../../data/events/comparativa_propina.parquet")
# data5 = pd.read_parquet(BASE_DIR / "../../data/events/comparativa_demanda.parquet")
# data6 = pd.read_parquet(BASE_DIR / "../../data/films/df_mapa.parquet")
# data7 = pd.read_parquet(BASE_DIR / "../../data/films/films_location.parquet")


### MINIO

data1 = load_parquet_from_minio("boostmobility/films/comparativa_taxi.parquet")
data2 = load_parquet_from_minio("boostmobility/films/impacto_taxi.parquet")
data3 = load_parquet_from_minio("boostmobility/films/friccion_taxi.parquet")
data4 = load_parquet_from_minio("boostmobility/events/comparativa_propina.parquet")
data5 = load_parquet_from_minio("boostmobility/events/comparativa_demanda.parquet")
data6 = load_parquet_from_minio("boostmobility/films/df_mapa.parquet")
data7 = load_parquet_from_minio("boostmobility/films/films_location.parquet")

def grafica1(topN=25,as_json=False):

    comparativa = data1.copy()

    comparativa["Tipo_Impacto"] = comparativa["impacto_pct"].apply(
        lambda x: "Aumento Tráfico" if x > 0 else "Caída Tráfico")
    
    # Cogemos los 15 peores (caídas) y los 15 mejores (subidas)
    top_caidas = comparativa.head(topN)
    top_subidas = comparativa.tail(topN)
    comparativa_final = pd.concat([top_caidas, top_subidas])

    
    fig = px.bar(
        comparativa_final,
        x="impacto_pct",
        y="zone",
        color="Tipo_Impacto",
        orientation="h",
        title=f"TOP {topN} Impacto del Rodaje en Demanda",
        labels={"Cambio_Pct": "Variación del Tráfico (%)", "Zone": "Zona de Taxi"},
        color_discrete_map={"Aumento Tráfico": "#2ecc71", "Caída Tráfico": "#e74c3c"},
        hover_data=["zone"]
    )

    # Añadimos una línea vertical en el 0% para referencia clara
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="black")

    fig.update_layout(
        xaxis_title="Cambio en el tráfico (%)",
        legend_title_text="Efecto del Rodaje",
        yaxis_showticklabels = False,
    )

    if as_json:
        return fig.to_json()
    
    return fig.to_html(full_html=False, config={'responsive': True})


def grafica2(topN=25,as_json=False):

    impacto_economico = data2.copy()
    
    impacto_economico["Tipo_Impacto"] = impacto_economico["profit_pct"].apply(
        lambda x: "Aumento Ingresos" if x > 0 else "Caida Ingresos")
    
    # Filtramos Top N ganadores y Top N perdedores
    df_viz_money = impacto_economico.sort_values("profit_pct")
    df_viz_money = pd.concat([df_viz_money.head(topN), df_viz_money.tail(topN)])

    fig2 = px.bar(
        df_viz_money,
        x="profit_pct",
        y="zone",
        orientation="h",
        title=f"TOP {topN} Impacto del Rodaje en Ingresos por Hora",
        labels={"profit_pct": "Cambio en Ingresos ($/Hora) %", "zone": "Zona"},
        color="Tipo_Impacto",
        color_discrete_map={"Aumento Ingresos": "#2ecc71", "Caida Ingresos": "#e74c3c"},
        hover_data=["zone"]
    )

    fig2.update_layout(
        xaxis_title="Cambio en Ingresos (%)",
        yaxis={"categoryorder": "total ascending",
               "showticklabels": False},
        legend_title_text="Efecto del Rodaje",
    )

    fig2.add_vline(x=0, line_dash="dash", line_color="black")

    if as_json:
        return fig2.to_json()
    
    return fig2.to_html(full_html=False, config={'responsive': True})


def grafica3(topN=25,as_json=False):

    impacto_velocidad = data3.copy()
    
    impacto_velocidad["Tipo_Velocidad"] = impacto_velocidad["friction_pct"].apply(
        lambda x: "Aumento Velocidad" if x > 0 else "Caida Velocidad")
    
    # Filtramos Top N ganadores y Top N perdedores
    impacto_velocidad.sort_values("friction_pct",inplace=True)
    df_viz = pd.concat([impacto_velocidad.head(topN), impacto_velocidad.tail(topN)])

    fig = px.bar(
        df_viz,
        x="friction_pct",
        y="zone",
        orientation="h",
        title=f"TOP {topN} Impacto de los Rodajes en la Velocidad del Tráfico",
        labels={"friction_pct": "Cambio en Velocidad (%)", "zone": "Zona"},
        color="Tipo_Velocidad",
        color_discrete_map={"Aumento Velocidad": "#2ecc71", "Caida Velocidad": "#e74c3c"},
        hover_data=["zone"]    
    )
    
    fig.update_layout(
        xaxis_title="Cambio en Velocidad (%)",
        yaxis={"categoryorder": "total ascending",
               "showticklabels": False},
        legend_title_text="Efecto del Rodaje",
    )

    fig.add_vline(x=0, line_dash="dash")


    if as_json:
        return fig.to_json()
    
    return fig.to_html(full_html=False, config={'responsive': True})


def grafica4():

    tip_hour = (
    data4.groupby(["hour","has_event"])["tip_amount"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        tip_hour,
        x="hour",
        y="tip_amount",
        color="has_event",
        markers=True,
        title="Propina Media por Hora (Eventos vs No Eventos)"
    )

    fig.update_xaxes(dtick=1)

    return fig.to_html(full_html=False, config={'responsive': True})

def grafica5():

    data5["hour"] = data5["date_hour"].dt.hour

    hourly_effect = (
        data5.groupby(["hour", "has_event"])["trip_count"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        hourly_effect,
        x="hour",
        y="trip_count",
        color="has_event",
        markers=True,
        title="Demanda Media por Hora (Con vs Sin Evento)",
        labels={"trip_count": "Viajes medios"}
    )

    fig.update_xaxes(dtick=1)
    
    return fig.to_html(full_html=False, config={'responsive': True})


def generate_films_taxi_map():
    # Generar el Mapa
    nyc_coords = [40.7128, -74.0060]
    m = folium.Map(location=nyc_coords, zoom_start=12, tiles="CartoDB positron")

    # Capa 1: Calor de Taxis (Usando los centros de las zonas ponderados por 'count')
    # data = [[lat, lon, peso], [lat, lon, peso]...]
    heat_data = data6[["centro_lat", "centro_lon", "count"]].values.tolist()
    HeatMap(heat_data, radius=25, blur=20).add_to(m)

    # Capa 2: Puntos de Rodaje (Exactos)
    for idx, row in data7.iterrows():
        folium.CircleMarker(
            location=[row["Lat"], row["Lon"]],  # Usamos la coordenada exacta del rodaje
            radius=3,
            color="black",
            fill=True,
            popup=f"{int(row['Film_LocationID'])}: {row['zone']}",
        ).add_to(m)

    # Extraer el HTML del mapa folium para inyectarlo en Jinja
    return m._repr_html_()
