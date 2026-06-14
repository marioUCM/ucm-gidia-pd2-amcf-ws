import pandas as pd
from plotly import express as px
import os
import folium
from folium.plugins import HeatMap
from utils.read_from_minio import load_parquet_from_minio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

### LOCAL

data1 = pd.read_parquet(BASE_DIR / "../../data/films/comparativa_taxi.parquet")
data2 = pd.read_parquet(BASE_DIR / "../../data/films/impacto_taxi.parquet")
data3 = pd.read_parquet(BASE_DIR / "../../data/films/friccion_taxi.parquet")
data4 = pd.read_parquet(BASE_DIR / "../../data/events/comparativa_propina.parquet")
data5 = pd.read_parquet(BASE_DIR / "../../data/events/comparativa_demanda.parquet")
data6 = pd.read_parquet(BASE_DIR / "../../data/films/df_mapa.parquet")
data7 = pd.read_parquet(BASE_DIR / "../../data/films/films_location.parquet")


### MINIO

# data1 = load_parquet_from_minio("boostmobility/films/comparativa_taxi.parquet")
# data2 = load_parquet_from_minio("boostmobility/films/impacto_taxi.parquet")
# data3 = load_parquet_from_minio("boostmobility/films/friccion_taxi.parquet")
# data4 = load_parquet_from_minio("boostmobility/events/comparativa_propina.parquet")
# data5 = load_parquet_from_minio("boostmobility/events/comparativa_demanda.parquet")
# data6 = load_parquet_from_minio("boostmobility/films/df_mapa.parquet")
# data7 = load_parquet_from_minio("boostmobility/films/films_location.parquet")

_CHART_LAYOUT = {
    "template": "plotly_white",
    "font": dict(family="Inter, system-ui, sans-serif", size=12, color="#14161c"),
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "#f4f5f7",
    "autosize": True,
    "margin": dict(l=44, r=18, t=48, b=42),
}


def _style_figure(fig):
    fig.update_layout(**_CHART_LAYOUT)
    fig.update_layout(
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True),
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
        title=f"TOP {topN} Impacto en Demanda",
        labels={"Cambio_Pct": "Variación del Tráfico (%)", "Zone": "Zona de Taxi"},
        color_discrete_map={"Aumento Tráfico": "#2ecc71", "Caída Tráfico": "#e74c3c"},
        hover_data=["zone"]
    )

    # Añadimos una línea vertical en el 0% para referencia clara
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="#64748b")

    fig.update_layout(
        xaxis_title="Cambio en el tráfico (%)",
        legend_title_text="Efecto del Rodaje",
        yaxis_showticklabels=False,
    )
    _style_figure(fig)

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
        title=f"TOP {topN} Impacto en Ingresos por Hora",
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

    fig2.add_vline(x=0, line_dash="dash", line_color="#64748b")
    _style_figure(fig2)

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
        title=f"TOP {topN} Impacto en la Velocidad del Tráfico",
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

    fig.add_vline(x=0, line_dash="dash", line_color="#64748b")
    _style_figure(fig)

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
        title="Propina Media por Hora (Eventos vs No Eventos)"
    )

    fig.update_xaxes(dtick=1)
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
        title="Demanda Media por Hora (Con vs Sin Evento)",
        labels={"trip_count": "Viajes medios"},
    )

    fig.update_xaxes(dtick=1)
    _style_figure(fig)

    return fig.to_html(full_html=False, config={
        'responsive': True,
        'displayModeBar': False,      # Oculta la barra superior flotante
        'scrollZoom': False,          # Evita hacer zoom con el dedo/rueda
        }
 )

def grafica6():
    """Volumen agregado de viajes según haya o no evento (complementa las series por hora)."""
    df = data5.copy()
    totals = df.groupby("has_event", as_index=False)["trip_count"].sum()

    def _label(v):
        if v is True or v == 1 or str(v).lower() in ("true", "1"):
            return "Con evento"
        return "Sin evento"

    totals["contexto"] = totals["has_event"].map(_label)
    fig = px.bar(
        totals,
        x="contexto",
        y="trip_count",
        color="contexto",
        title="Volumen total de viajes en el periodo (con vs sin evento)",
        labels={"trip_count": "Suma de viajes", "contexto": ""},
        color_discrete_map={"Con evento": "#c9a227", "Sin evento": "#5e6678"},
    )
    fig.update_layout(showlegend=False)
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


def grafica7(as_json=False):
    """Heatmap: Matriz de impactos (demanda, ingresos, velocidad)"""

    # Preparar datos para heatmap
    impact_demand = data1.copy().head(10)[['zone', 'impacto_pct']].rename(columns={'impacto_pct': 'Demanda'})
    impact_income = data2.copy().head(10)[['zone', 'profit_pct']].rename(columns={'profit_pct': 'Ingresos'})
    impact_speed = data3.copy().tail(10)[['zone', 'friction_pct']].rename(columns={'friction_pct': 'Velocidad'})

    # Merge para crear matriz (usar solo zonas comunes)
    heatmap_data = impact_demand.copy()
    heatmap_data = heatmap_data.merge(
        impact_income[['zone', 'Ingresos']],
        on='zone',
        how='left'
    )
    heatmap_data = heatmap_data.merge(
        impact_speed[['zone', 'Velocidad']],
        on='zone',
        how='left'
    )

    # Fillna para zonas sin datos en alguna métrica
    heatmap_data = heatmap_data.fillna(0)

    # Crear heatmap
    fig = px.imshow(
        heatmap_data.set_index('zone')[['Demanda', 'Ingresos', 'Velocidad']].T,
        labels=dict(x="Zona", y="Métrica", color="Cambio %"),
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        title="Matriz de Impactos por Zona",
        aspect="auto",
    )

    fig.update_layout(
        xaxis_title="Zona de Impacto",
        yaxis_title="Métrica",
        coloraxis_colorbar_title="% Cambio",
        height=400,
    )

    _style_figure(fig)

    if as_json:
        return fig.to_json()
    
    return fig.to_html(full_html=False, config={
        'responsive': True,
        'displayModeBar': False,
        'scrollZoom': False
    })


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
