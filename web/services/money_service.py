import pandas as pd
from plotly import express as px
import os
import geopandas as gpd 
import folium
import numpy as np
from utils.read_from_minio import load_geoparquet_from_minio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

### LOCAL

data = gpd.read_parquet(BASE_DIR/"../../data/money/df_mapa.parquet")

### MINIO

# data = load_geoparquet_from_minio("boostmobility/money/df_mapa.parquet")


data['ZIP_CODE'] = data['ZIP_CODE'].astype(str)


def grafica1(topN=25,as_sjon=False):


     # Ordenamos el dataframe por propina de mayor a menor
    df_ordenado = data.sort_values('volumen_viajes', ascending=False)

    top = df_ordenado.head(topN)
    bottom = df_ordenado.tail(topN)
    df_extremos = pd.concat([top, bottom])

    fig = px.bar(
        data_frame=df_extremos, 
        x='volumen_viajes', 
        y='ZIP_CODE',    
        orientation="h",
        color="volumen_viajes",
    )

    fig.update_layout(
        title=f'TOP {topN} Códigos Postales más y menos demandados de NYC',
        xaxis_title='Numero de Viajes',
        yaxis_title='ZIP Code',
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False,
    )

    if as_sjon:
        return fig.to_json()
    return fig.to_html(full_html=False, config={'responsive': True})


def grafica2(topN=25,as_sjon=False):

    # Ordenamos el dataframe por propina de mayor a menor
    df_ordenado = data.sort_values('propina_media', ascending=False)

    top = df_ordenado.head(topN)
    bottom = df_ordenado.tail(topN)
    df_extremos = pd.concat([top, bottom])

    fig = px.bar(
        data_frame=df_extremos, 
        x='propina_media', 
        y='ZIP_CODE',    
        orientation="h",
        color="propina_media",
    )

    fig.update_layout(
        title=f'TOP {topN} Códigos Postales más y menos generosos de NYC',
        xaxis_title='Propina Media ($)',
        yaxis_title='ZIP Code',
        yaxis={'categoryorder': 'total ascending'}, # Ordena correctamente de mayor a menor
        coloraxis_showscale=False,
    )

    if as_sjon:
        return fig.to_json()
    return fig.to_html(full_html=False, config={'responsive': True})



def grafica3(topN=25,as_sjon=False):

    # Ordenamos el dataframe por propina de mayor a menor
    df_ordenado = data.sort_values('ingreso_medio', ascending=False)

    top = df_ordenado.head(topN)
    bottom = df_ordenado.tail(topN)
    df_extremos = pd.concat([top, bottom])

    fig = px.bar(
        data_frame=df_extremos, 
        x='ingreso_medio', 
        y='ZIP_CODE',    
        orientation="h",
        color="ingreso_medio",
    )

    fig.update_layout(
        title=f'TOP {topN} Códigos Postales más y menos generosos de NYC',
        xaxis_title='Ingreso Medio ($)',
        yaxis_title='ZIP Code',
        yaxis={'categoryorder': 'total ascending'}, # Ordena correctamente de mayor a menor
        coloraxis_showscale=False,
    )

    if as_sjon:
        return fig.to_json()
    return fig.to_html(full_html=False, config={'responsive': True})
    

def grafica4():

    fig = px.box(
    data_frame=data,
    y='volumen_viajes',        # Los valores numéricos en el eje vertical
    )

    fig.update_layout(
        title='Distribución de Viajes: Boxplot',
        xaxis_title='',
        yaxis_title='Total Viajes',
    )

    return fig.to_html(full_html=False, config={'responsive': True})


def grafica5():
    fig = px.box(
    data_frame=data,
    y='propina_media',        # Los valores numéricos en el eje vertical
    )

    fig.update_layout(
        title='Distribución de Propinas: Boxplot',
        xaxis_title='',
        yaxis_title='Propina Media ($)',
    )

    return fig.to_html(full_html=False, config={'responsive': True})


def grafica6():
    fig = px.box(
    data_frame=data,
    y='ingreso_medio',        # Los valores numéricos en el eje vertical
    )

    fig.update_layout(
        title='Distribución de Ingresos: Boxplot',
        xaxis_title='',
        yaxis_title='Ingreso Medio ($)',
    )

    return fig.to_html(full_html=False, config={'responsive': True})




def generate_economic_map():
    
    # PREPARACIÓN VISUAL Y TRATAMIENTO DE TIPOS
    df_vis = data.copy()

    # Formateamos los números como moneda para el Tooltip
    df_vis['propina_fmt'] = df_vis['propina_media'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "Sin datos")
    df_vis['alquiler_fmt'] = df_vis['valor_alquiler'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "Sin datos")
    df_vis['propiedad_fmt'] = df_vis['valor_propiedad'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "Sin datos")
    df_vis['ingreso_fmt'] = df_vis['ingreso_medio'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "Sin datos")
    df_vis['viajes_fmt'] = df_vis['volumen_viajes'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "Sin datos")

    # Convertimos a float para que Folium y NumPy calculen los colores sin rechistar
    df_vis['propina_media'] = df_vis['propina_media'].astype(float)
    df_vis['valor_alquiler'] = df_vis['valor_alquiler'].astype(float)
    df_vis['valor_propiedad'] = df_vis['valor_propiedad'].astype(float)
    df_vis['ingreso_medio'] = df_vis['ingreso_medio'].astype(float)
    df_vis['volumen_viajes'] = df_vis['volumen_viajes'].astype(float)

    # Calculamos los cortes óptimos para los mapas
    bins_propina = list(np.unique(df_vis['propina_media'].dropna().quantile([0, 0.2, 0.4, 0.6, 0.8, 1.0])))
    bins_ingreso = list(np.unique(df_vis['ingreso_medio'].dropna().quantile([0, 0.2, 0.4, 0.6, 0.8, 1.0])))
    bins_viajes = list(np.unique(df_vis['volumen_viajes'].dropna().quantile([0, 0.2, 0.4, 0.6, 0.8, 1.0])))
    bins_alquiler = list(np.unique(df_vis['valor_alquiler'].dropna().quantile([0, 0.2, 0.4, 0.6, 0.8, 1.0])))
    bins_propiedad = list(np.unique(df_vis['valor_propiedad'].dropna().quantile([0, 0.2, 0.4, 0.6, 0.8, 1.0])))

    # INICIALIZAR EL MAPA
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=11, tiles=None)

    folium.TileLayer('CartoDB positron', overlay=True, control=False).add_to(m)
    
    folium.map.CustomPane('panel_interactivo', z_index=650, pointer_events=True).add_to(m)
    
    def quitar_leyenda(capa):
        for key in list(capa._children.keys()):
            if key.startswith('color_map'):
                del(capa._children[key])
        return capa
    
    # CAPA  MAPA DE PROPINAS
    capa_propinas=folium.Choropleth(
        geo_data=df_vis, 
        name='🚕 Mapa de Propinas',
        data=df_vis,                 
        columns=['ZIP_CODE', 'propina_media'], 
        key_on='feature.properties.ZIP_CODE',
        fill_color='YlGnBu',        
        fill_opacity=0.85,          
        line_opacity=0.5,
        line_color='#888888',
        line_weight=1,         
        legend_name='Propina Media por Viaje ($)',
        bins=bins_propina,          
        nan_fill_color='#f0f0f0',   
        smooth_factor=0,
        show=True,
        overlay=False,
    )
    quitar_leyenda(capa_propinas).add_to(m)

    # CAPA MAPA DE INGRESO
    capa_ingreso=folium.Choropleth(
        geo_data=df_vis, 
        name='🚕 Mapa de Ingreso',
        data=df_vis,                 
        columns=['ZIP_CODE', 'ingreso_medio'], 
        key_on='feature.properties.ZIP_CODE',
        fill_color='YlGn',        
        fill_opacity=0.85,          
        line_opacity=0.5,
        line_color='#888888',
        line_weight=1, 
        legend_name='Ingreso Medio por Viaje ($)',
        bins=bins_ingreso,          
        nan_fill_color='#f0f0f0',   
        smooth_factor=0,
        show=False,
        overlay=False
    )
    quitar_leyenda(capa_ingreso).add_to(m)


    # CAPA MAPA DE VIAJES
    capa_viajes=folium.Choropleth(
        geo_data=df_vis, 
        name='🚕 Mapa de Viajes',
        data=df_vis,                 
        columns=['ZIP_CODE', 'volumen_viajes'], 
        key_on='feature.properties.ZIP_CODE',
        fill_color='YlOrRd',        
        fill_opacity=0.85,          
        line_opacity=0.5,         
        line_color='#888888',
        line_weight=1,          
        legend_name='Volumen de Viajes',
        bins=bins_viajes,          
        nan_fill_color='#f0f0f0',   
        smooth_factor=0,
        show=False,
        overlay=False
    )
    quitar_leyenda(capa_viajes).add_to(m)

    # CAPA MAPA DE ALQUILERES
    capa_alquiler=folium.Choropleth(
        geo_data=df_vis, 
        name='🏢 Mapa de Coste de Alquiler',
        data=df_vis,                 
        columns=['ZIP_CODE', 'valor_alquiler'], 
        key_on='feature.properties.ZIP_CODE',
        fill_color='PuBuGn',
        fill_opacity=0.85,          
        line_opacity=0.5,
        line_color='#888888',
        line_weight=1,        
        legend_name='Precio Medio del Alquiler ($)',
        bins=bins_alquiler,          
        nan_fill_color='#f0f0f0',   
        smooth_factor=0,
        show=False,
        overlay=False
    )
    quitar_leyenda(capa_alquiler).add_to(m)

    # CAPA MAPA DE PROPIEDADES
    capa_propiedades=folium.Choropleth(
        geo_data=df_vis, 
        name='🏡 Mapa de Valor de Propiedad',
        data=df_vis,                 
        columns=['ZIP_CODE', 'valor_propiedad'], 
        key_on='feature.properties.ZIP_CODE',
        fill_color='YlOrBr',
        fill_opacity=0.85,          
        line_opacity=0.5,
        line_color='#888888',
        line_weight=1,        
        legend_name='Valor Medio de Propiedad ($)',
        bins=bins_propiedad,          
        nan_fill_color='#f0f0f0',   
        smooth_factor=0,
        show=False,
        overlay=False
    )
    quitar_leyenda(capa_propiedades).add_to(m)

    # CAPA INTERACTIVA: EL TOOLTIP PARA TODOS LOS MAPAS
    folium.GeoJson(
        df_vis,
        name="Datos detallados",
        # ---> AÑADE ESTAS DOS PROPIEDADES <---
        pane='panel_interactivo', # Atamos esta capa al panel invencible
        control=False,            # La ocultamos del menú lateral (así el usuario no la puede apagar por error y siempre funciona)
        
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent', 'weight': 0},
        highlight_function=lambda x: {'weight': 3, 'color': '#ff7f50', 'fillOpacity': 0.1},
        tooltip=folium.GeoJsonTooltip(
            fields=['ZIP_CODE', 'propina_fmt','ingreso_fmt','viajes_fmt', 'alquiler_fmt', 'propiedad_fmt'],
            aliases=['📍 Código Postal:', '🚕 Propina Media:','🚕 Ingreso Medio:','🚕 Volumen Viajes:', '🏢 Alquiler:', '🏡 Valor Propiedad:'],
            style=("background-color: white; color: #333333; font-family: Arial, sans-serif; "
                   "font-size: 13px; padding: 10px; border-radius: 8px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);")
        )
    ).add_to(m)

    # CONTROL DE CAPAS
    folium.LayerControl(collapsed=False).add_to(m)

    # Extraer el HTML del mapa folium para inyectarlo en Jinja
    return m._repr_html_()