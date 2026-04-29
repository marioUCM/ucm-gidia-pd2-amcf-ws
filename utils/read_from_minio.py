from minio import Minio
from dotenv import load_dotenv
import os
import pandas as pd
from io import BytesIO
import json

try:
    import geopandas as gpd
except ImportError:
    gpd = None

# ==========================
#   CONFIG MINIO
# ==========================


load_dotenv()

BUCKET = "pd2"

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

client = Minio(
    endpoint="minio.fdi.ucm.es",
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
)


def load_parquet_from_minio(path,columns=None):
    response = client.get_object(BUCKET, path)
    try:
        data = response.read()
        df = pd.read_parquet(BytesIO(data),columns=columns)
    finally:
        response.close()
        response.release_conn()
    return df


def load_geoparquet_from_minio(path,columns=None):
    if gpd is None:
        raise ImportError("geopandas no esta instalado")
    response = client.get_object(BUCKET, path)
    try:
        data = response.read()
        df = gpd.read_parquet(BytesIO(data),columns=columns)
    finally:
        response.close()
        response.release_conn()
    return df

def load_pickle_from_minio(path):
    response = client.get_object(BUCKET, path)
    try:
        data = response.read()
        df = pd.read_pickle(BytesIO(data))
    finally:
        response.close()
        response.release_conn()
    return df

def load_shapefile_from_minio(path):
    if gpd is None:
        raise ImportError("geopandas no esta instalado")
    # Descargar archivo .shp desde MinIO y reconstruirlo en memoria
    # IMPORTANTE: shapefile necesita múltiples archivos (.shp, .shx, .dbf, etc.)
    # Aquí asumimos que están en la misma ruta base

    import tempfile
    import os

    base_path = path.replace(".shp", "")
    extensions = [".shp", ".shx", ".dbf", ".prj", ".cpg"]

    with tempfile.TemporaryDirectory() as tmpdir:
        local_files = {}

        # Descargar cada componente del shapefile
        for ext in extensions:
            try:
                response = client.get_object(BUCKET, base_path + ext)
                data = response.read()
                local_path = os.path.join(tmpdir, os.path.basename(base_path + ext))

                with open(local_path, "wb") as f:
                    f.write(data)

                local_files[ext] = local_path

                response.close()
                response.release_conn()

            except Exception:
                # Algunos archivos como .cpg pueden no existir
                continue

        shp_path = local_files.get(".shp")

        if shp_path is None:
            raise ValueError("No se encontró el archivo .shp en MinIO")

        gdf = gpd.read_file(shp_path)

    return gdf


def load_json_from_minio(path):
    response = client.get_object(BUCKET, path)
    try:
        data = response.read()
        return json.loads(data.decode("utf-8"))
    finally:
        response.close()
        response.release_conn()


def get_minio_object_last_modified(path):
    try:
        result = client.stat_object(BUCKET, path)
    except Exception:
        return None
    return getattr(result, "last_modified", None)
