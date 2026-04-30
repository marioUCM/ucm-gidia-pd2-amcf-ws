import pandas as pd
import folium
import geopandas as gpd
from utils.read_from_minio import load_pickle_from_minio, load_parquet_from_minio, load_geoparquet_from_minio
from pathlib import Path

### LOCAL
BASE_DIR = Path(__file__).resolve().parent
df_test = pd.read_parquet(BASE_DIR/"../../data/final_models/demanda/modelo_demanda_test.parquet")
df_service_test = pd.read_parquet(BASE_DIR/"../../data/final_models/demanda/modelo_demanda_service_type_test.parquet")
fixed_model = pd.read_pickle(BASE_DIR/"../../data/final_models/demanda/modelo_demanda_fijo.pkl")
service_model = pd.read_pickle(BASE_DIR/"../../data/final_models/demanda/modelo_demanda_service_type.pkl")
taxi_zones = gpd.read_parquet(BASE_DIR/"../../data/utils/taxi_zones.parquet")

### MINIO
# df_test = load_parquet_from_minio("boostmobility/final_models/demanda/modelo_demanda_test.parquet")
# df_service_test = load_parquet_from_minio("boostmobility/final_models/demanda/modelo_demanda_service_type_test.parquet")
# fixed_model = load_pickle_from_minio("boostmobility/final_models/demanda/modelo_demanda_fijo.pkl")
# service_model = load_pickle_from_minio("boostmobility/final_models/demanda/modelo_demanda_service_type.pkl")
# taxi_zones = load_geoparquet_from_minio("boostmobility/utils/taxi_zones.parquet")

def get_zones():

    # usar solo df_test (modelo fijo) para zonas
    zones = (
        df_test[["Zone", "Borough"]]
        .drop_duplicates()
        .sort_values("Zone")
    )

    return zones.to_dict(orient="records")


def predict_trained_model(zone, borough, year, month, day, hour):

    row = df_test[
        (df_test["Zone"] == zone) &
        (df_test["Borough"] == borough) &
        (df_test["year"] == year) &
        (df_test["month"] == month) &
        (df_test["day"] == day) &
        (df_test["hour"] == hour)
    ]

    if row.empty:
        return None

    X_pred = row.drop(columns=["demand"]).copy()

    # alinear features EXACTAS del modelo
    model_features = fixed_model.feature_name_
    X_pred = X_pred[model_features]

    # reconstruir categorías globales (aprox. del entrenamiento)
    zone_cats = pd.Index(sorted(pd.concat([df_test["Zone"], df_service_test["Zone"]]).astype(str).unique()))
    borough_cats = pd.Index(sorted(pd.concat([df_test["Borough"], df_service_test["Borough"]]).astype(str).unique()))

    if "Zone" in X_pred.columns:
        X_pred["Zone"] = pd.Categorical(X_pred["Zone"].astype(str), categories=zone_cats)

    if "Borough" in X_pred.columns:
        X_pred["Borough"] = pd.Categorical(X_pred["Borough"].astype(str), categories=borough_cats)

    pred = fixed_model.predict(X_pred)[0]
    real = row["demand"].values[0]

    pred_rounded = int(round(pred))

    return {
        "prediction": pred_rounded,
        "zone": zone,
        "borough": borough,
        "date": f"{year}-{month:02d}-{day:02d}",
        "hour": hour
    }

def predict_top_zones(year, month, day, hour, borough="all", service_type="none", top_n=3):

    source_df = df_service_test if service_type != "none" else df_test

    rows = source_df[
        (source_df["year"] == year) &
        (source_df["month"] == month) &
        (source_df["day"] == day) &
        (source_df["hour"] == hour)
    ].copy()

    # filtro borough (robusto a mayúsculas/espacios)
    if borough != "all":
        rows = rows[
            rows["Borough"].astype(str).str.strip().str.lower()
            == str(borough).strip().lower()
        ]

    # filtro service_type
    if service_type != "none" and "service_type" in rows.columns:
        rows = rows[
            rows["service_type"].astype(str).str.strip()
            == str(service_type).strip()
        ]

    if rows.empty:
        return None

    X_pred = rows.drop(columns=["demand"]).copy()

    if service_type != "none":
        X_pred["service_type"] = service_type

    # elegir modelo
    model = service_model if service_type != "none" else fixed_model

    # ajustar columnas según modelo
    if service_type == "none" and "service_type" in X_pred.columns:
        X_pred = X_pred.drop(columns=["service_type"])

    # alinear features EXACTAS del modelo
    model_features = model.feature_name_
    X_pred = X_pred[model_features]

    # asegurar mismas categorías que en entrenamiento
    if service_type != "none":
        base_df = df_service_test
    else:
        base_df = df_test

    cat_cols = ["Zone", "Borough"]
    if "service_type" in X_pred.columns:
        cat_cols.append("service_type")

    for col in cat_cols:
        if col in X_pred.columns and col in base_df.columns:
            train_col = base_df[col].astype("category")
            X_pred[col] = pd.Categorical(
                X_pred[col].astype(str),
                categories=train_col.cat.categories,
                ordered=train_col.cat.ordered
            )

    for col in X_pred.select_dtypes(include="category").columns:
        X_pred[col] = X_pred[col].astype("category")

    rows["prediction"] = model.predict(X_pred).round().astype(int)

    top_rows = (
        rows[["Zone", "Borough", "prediction"]]
        .sort_values("prediction", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    return top_rows.to_dict(orient="records")

def predict_all_zones(year, month, day, hour, service_type="none"):

    source_df = df_service_test if service_type != "none" else df_test

    rows = source_df[
        (source_df["year"] == year) &
        (source_df["month"] == month) &
        (source_df["day"] == day) &
        (source_df["hour"] == hour)
    ].copy()

    if service_type != "none" and "service_type" in rows.columns:
        rows = rows[
            rows["service_type"].astype(str).str.strip()
            == str(service_type).strip()
        ]

    if rows.empty:
        return None

    X_pred = rows.drop(columns=["demand"]).copy()

    # añadir service_type si corresponde
    if service_type != "none":
        X_pred["service_type"] = service_type

    # elegir modelo
    model = service_model if service_type != "none" else fixed_model

    # ajustar columnas según modelo
    if service_type == "none" and "service_type" in X_pred.columns:
        X_pred = X_pred.drop(columns=["service_type"])

    # alinear features EXACTAS del modelo
    model_features = model.feature_name_
    X_pred = X_pred[model_features]

    # asegurar mismas categorías que en entrenamiento
    if service_type != "none":
        base_df = df_service_test
    else:
        base_df = df_test

    cat_cols = ["Zone", "Borough"]
    if "service_type" in X_pred.columns:
        cat_cols.append("service_type")

    for col in cat_cols:
        if col in X_pred.columns and col in base_df.columns:
            train_col = base_df[col].astype("category")
            X_pred[col] = pd.Categorical(
                X_pred[col].astype(str),
                categories=train_col.cat.categories,
                ordered=train_col.cat.ordered
            )

    for col in X_pred.select_dtypes(include="category").columns:
        X_pred[col] = X_pred[col].astype("category")

    # predecir
    preds = model.predict(X_pred)

    rows["prediction"] = preds.round().astype(int)

    # clasificación basada en percentiles (más robusto)
    q33 = rows["prediction"].quantile(0.33)
    q66 = rows["prediction"].quantile(0.66)

    def classify(val):
        if val <= q33:
            return "low"
        elif val <= q66:
            return "medium"
        else:
            return "high"

    rows["level"] = rows["prediction"].apply(classify)

    return rows[["Zone", "Borough", "prediction", "level"]].to_dict(orient="records")



def generate_demand_map(year, month, day, hour, service_type="none"):

    data = predict_all_zones(year, month, day, hour, service_type)

    if data is None:
        return None

    df_pred = pd.DataFrame(data)

    # cargar geojson
    gdf = taxi_zones

    # normalizar nombres
    gdf["zone"] = gdf["zone"].astype(str).str.strip()
    df_pred["Zone"] = df_pred["Zone"].astype(str).str.strip()

    # merge
    gdf = gdf.merge(df_pred, left_on="zone", right_on="Zone", how="left")

    # marcar zonas sin datos
    gdf["no_data"] = gdf["prediction"].isna()

    # SOLO rellenar prediction (NO tocar level)
    gdf["prediction"] = gdf["prediction"].fillna(0)

    # quitar level en zonas sin datos
    gdf.loc[gdf["no_data"], "level"] = None

    # texto de nivel para mostrar correctamente
    gdf["level_text"] = gdf.apply(
        lambda row: "Sin demanda" if row["no_data"] else row["level"],
        axis=1
    )

    # colores
    def get_color(row):
        if row["no_data"]:
            return "#555555"  # gris oscuro sin demanda
        if row["level"] == "high":
            return "#ff0033"
        elif row["level"] == "medium":
            return "#ffff00"
        elif row["level"] == "low":
            return "#00ff00"
        else:
            return "#00ff00"

    gdf["color"] = gdf.apply(get_color, axis=1)

    # mapa base
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            "fillColor": feature["properties"]["color"],
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["zone", "prediction", "level_text"],
            aliases=["Zona", "Demanda", "Nivel"],
        ),
    ).add_to(m)

    return m._repr_html_()