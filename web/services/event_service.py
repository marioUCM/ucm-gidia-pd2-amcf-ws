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


def _style_figure(fig):
    fig.update_layout(
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True),
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        margin=dict(l=10, r=20, t=50, b=20),
        xaxis_dtick=6,
        xaxis_tickangle=0,
    )


def grafica1(topN=25, as_json=False):

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
        labels={"Tipo_Impacto": "Efecto", "impacto_pct": "Demanda (%)", "Zone": "Zona"},
        color_discrete_map={"Aumento Tráfico": "#2ecc71", "Caída Tráfico": "#e74c3c"},
        hover_data=["zone"]
    )

    # Añadimos una línea vertical en el 0% para referencia clara
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="#64748b")

    _style_figure(fig)

    fig.update_layout(
        title={'text': 'Demanda', 'x': 0.5, 'xanchor': 'center'},
        yaxis_showticklabels=False,
        margin=dict(l=10, r=20, t=50, b=20),
        xaxis_dtick=15,
    )

    if as_json:
        return fig.to_json()
    
    return fig.to_html(full_html=False, config={
        'responsive': True,
        'displayModeBar': False,      # Oculta la barra superior flotante
        'scrollZoom': False,          # Evita hacer zoom con el dedo/rueda
        }

    )

def grafica2(topN=25, as_json=False):

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
        labels={"Tipo_Impacto": "Efecto", "profit_pct": "Ingresos (%) %", "zone": "Zona"},
        color="Tipo_Impacto",
        color_discrete_map={"Aumento Ingresos": "#2ecc71", "Caida Ingresos": "#e74c3c"},
        hover_data=["zone"]
    )
    _style_figure(fig2)

    fig2.update_layout(
        title={'text': 'Ingresos', 'x': 0.5, 'xanchor': 'center'},
        yaxis={"categoryorder": "total ascending",
               "showticklabels": False},
        margin=dict(l=10, r=20, t=50, b=20),
        xaxis_dtick=5,
    )

    fig2.add_vline(x=0, line_dash="dash", line_color="#64748b")

    if as_json:
        return fig2.to_json()
    
    return fig2.to_html(full_html=False, config={
        'responsive': True,
        'displayModeBar': False,      # Oculta la barra superior flotante
        'scrollZoom': False,          # Evita hacer zoom con el dedo/rueda
        }
 )

def grafica3(topN=25, as_json=False):

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
        labels={"Tipo_Velocidad": "Efecto", "friction_pct": "Velocidad (%)", "zone": "Zona"},
        color="Tipo_Velocidad",
        color_discrete_map={"Aumento Velocidad": "#2ecc71", "Caida Velocidad": "#e74c3c"},
        hover_data=["zone"]    
    )

    _style_figure(fig)

    fig.update_layout(
        title={'text': 'Velocidad', 'x': 0.5, 'xanchor': 'center'},
        yaxis={"categoryorder": "total ascending",
               "showticklabels": False},
        margin=dict(l=10, r=20, t=50, b=20),
        xaxis_dtick=5,
    )

    fig.add_vline(x=0, line_dash="dash", line_color="#64748b")

    if as_json:
        return fig.to_json()
    
    return fig.to_html(full_html=False, config={
        'responsive': True,
        'displayModeBar': False,      # Oculta la barra superior flotante
        'scrollZoom': False,          # Evita hacer zoom con el dedo/rueda
        }
 )

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
        labels={"tip_amount": "Propina promedio", "hour": "Hora", "has_event": "Evento"},
        color_discrete_map={
            True: "#3b82f6",   # Con evento -> Azul
            False: "#ef4444",  # Sin evento -> Rojo
            }
    )

    fig.update_layout(
        title={'text': 'Propina Promedia', 'x': 0.5, 'xanchor': 'center'},
    )

    _style_figure(fig)

    return fig.to_html(full_html=False, config={
        'responsive': True,
        'displayModeBar': False,
        'scrollZoom': False
    })  


def grafica5():
    df = data5.copy()
    df["hour"] = df["date_hour"].dt.hour

    hourly_effect = (
        df.groupby(["hour", "has_event"])["trip_count"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        hourly_effect,
        x="hour",
        y="trip_count",
        color="has_event",
        markers=True,
        labels={"trip_count": "Viajes medios", "hour": "Hora", "has_event": "Evento"},
        color_discrete_map={
            True: "#3b82f6",   # Con evento -> Azul
            False: "#ef4444",  # Sin evento -> Rojo
            }
    )

    fig.update_layout(
        title={'text': 'Demanda Promedia', 'x': 0.5, 'xanchor': 'center'},
    )

    _style_figure(fig)

    return fig.to_html(full_html=False, config={
        'responsive': True,
        'displayModeBar': False,      # Oculta la barra superior flotante
        'scrollZoom': False,          # Evita hacer zoom con el dedo/rueda
        }
 )

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

def extract_impact_summary():
    """Extract impact summary for dashboard indicators"""

    # Max demand impact
    max_demand_impact = data1['impacto_pct'].max()
    min_demand_impact = data1['impacto_pct'].min()

    # Max income impact
    max_income_impact = data2['profit_pct'].max()
    min_income_impact = data2['profit_pct'].min()

    # Max speed impact
    max_speed_impact = data3['friction_pct'].max()
    min_speed_impact = data3['friction_pct'].min()

    return {
        'demand_impact': round(max_demand_impact, 1),
        'demand_direction': 'positive' if max_demand_impact > 0 else 'negative',
        'income_impact': round(max_income_impact, 1),
        'income_direction': 'positive' if max_income_impact > 0 else 'negative',
        'speed_impact': round(max_speed_impact, 1),
        'speed_direction': 'positive' if max_speed_impact > 0 else 'negative',
    }
