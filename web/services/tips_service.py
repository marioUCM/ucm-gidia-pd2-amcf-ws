import pandas as pd
from sklearn.model_selection import train_test_split
from datetime import datetime
from utils.read_from_minio import load_parquet_from_minio, load_pickle_from_minio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

cols_taxi = ['tip_amount' ,'Airport_fee','dia_pickup', 'hora_pickup','mes_pickup','is_airport_binary',
            'Borough','service_zone','Zone', 'temperature_2m (°C)', 'apparent_temperature (°C)',
            'dia_semana', 'num_events', 'VendorID']

### LOCAL
# vtc=pd.read_parquet(BASE_DIR/'../../data/final_models/propinas/vtc_propinas_modelo.parquet')
# taxi=pd.read_parquet(BASE_DIR/'../../data/final_models/propinas/taxi_propinas_modelo.parquet')
# fixed_model_vtc = pd.read_pickle(BASE_DIR/"../../data/final_models/propinas/modelo_vtc_propinas_principal.pkl")
# fixed_model_taxi = pd.read_pickle(BASE_DIR/"../../data/final_models/propinas/modelo_taxi_propinas_principal.pkl")

### MINIO
vtc = load_parquet_from_minio("boostmobility/final_models/propinas/vtc_propinas_modelo.parquet")
taxi = load_parquet_from_minio("boostmobility/final_models/propinas/taxi_propinas_modelo.parquet", columns=cols_taxi)
fixed_model_vtc = load_pickle_from_minio("boostmobility/final_models/propinas/modelo_vtc_propinas_principal.pkl")
fixed_model_taxi = load_pickle_from_minio("boostmobility/final_models/propinas/modelo_taxi_propinas_principal.pkl")


df_pu = vtc[['PULocation_Zone', 'PUservice_zone']].drop_duplicates()
df_do = vtc[['DOLocation_Zone', 'DOservice_zone']].drop_duplicates()
df_pu.columns = ['zona', 'servicio']
df_do.columns = ['zona', 'servicio']
mapeo_servicios = pd.concat([df_pu, df_do]).drop_duplicates().dropna()
mapeo_dict = mapeo_servicios.set_index('zona')['servicio'].to_dict()

#Datos vtc
X_vtc = vtc.drop(columns=['tips', 'hay_propina'])
y_vtc = vtc['tips']

X_train_vtc, X_test_vtc, y_train_vtc, y_test_vtc = train_test_split(
    X_vtc, y_vtc, test_size=0.2, shuffle=False
)

df_test_vtc = X_test_vtc.copy()
df_test_vtc['tips'] = y_test_vtc

X_taxi = taxi.drop(columns=['tip_amount'])
y_taxi = taxi['tip_amount']

X_train_taxi, X_test_taxi, y_train_taxi, y_test_taxi = train_test_split(
    X_taxi, y_taxi, test_size=0.2, shuffle=False
)

df_test_taxi = X_test_taxi.copy()
df_test_taxi['tip_amount'] = y_test_taxi


def predict_trained_model_vtc(PUzone, PUborough, DOzone, DOborough, year, month, day, hour):
    try:
        # Calculamos las variables derivadas que pide el modelo
        fecha_dt = datetime(year, month, day)
        dia_semana = fecha_dt.weekday()
        aeropuertos = ['JFK Airport', 'Newark Airport', 'LaGuardia Airport']

        data_viaje = X_train_vtc[(X_train_vtc['PULocation_Zone'] == PUzone) & (X_train_vtc['DOLocation_Zone'] == DOzone)]

        if not data_viaje.empty:
            avg_miles = data_viaje['trip_miles'].mean()
            avg_fare = data_viaje['base_passenger_fare'].mean()
            avg_time = data_viaje['trip_time'].mean()
        else:
            avg_miles = 3.0
            avg_fare = 15.0
            avg_time = 900
        
        eventos_hist = X_train_vtc[(X_train_vtc['PULocation_Zone'] == PUzone) & 
                                   (X_train_vtc['hora'] == hour)]['num_events_PU']
        
        if not eventos_hist.empty:
            avg_events = eventos_hist.mean()
        else:
            avg_events = X_train_vtc['num_events_PU'].mean() if 'num_events_PU' in X_train_vtc else 0

        data_dict = {
            'base_passenger_fare': avg_fare,
            'PULocation_Zone': PUzone,
            'DOLocation_Zone': DOzone,
            'dispatching_base_num': 'B03404', 
            'PUservice_zone': mapeo_dict.get(PUzone, 'Unknown'),
            'airport_fee': 2.5 if (PUzone in aeropuertos or DOzone in aeropuertos) else 0.0,
            'hora': hour,
            'DOservice_zone': mapeo_dict.get(DOzone, 'Unknown'),
            'num_events_PU': avg_events,
            'trip_miles': avg_miles,
            'trip_time': avg_time,
            'tiempo': avg_time / 60,
            'dia_semana': dia_semana
        }

        DOBorough = DOborough if pd.notna(DOborough) else 'Unknown'

        input_data = pd.DataFrame([data_dict])

        cols_order = [
            'base_passenger_fare', 'PULocation_Zone', 'DOLocation_Zone', 
            'dispatching_base_num', 'PUservice_zone', 'airport_fee', 
            'hora', 'DOservice_zone', 'num_events_PU', 'trip_miles', 
            'trip_time', 'tiempo', 'dia_semana'
        ]
        input_data = input_data[cols_order]


        cat_cols = [
            'PULocation_Zone', 'DOLocation_Zone', 'dispatching_base_num', 
            'PUservice_zone', 'DOservice_zone'
        ]
        
        for col in input_data.columns:
            if col in cat_cols:
                input_data[col] = pd.Categorical(
                    input_data[col], 
                    categories=X_vtc[col].cat.categories
                )
            else:
                input_data[col] = pd.to_numeric(input_data[col], errors='coerce')

        pred = fixed_model_vtc.predict(input_data)[0]
        
        return {
            "prediction": f"{round(max(0, float(pred)), 2)} €",
            "borough": PUborough,
            "zone": PUzone,
            "date": f"{year}-{month:02d}-{day:02d}",
            "hour": hour
        }

    except Exception as e:
        print(f"--- ERROR EN PREDICCIÓN ---")
        print(f"Detalle: {e}")
        return None
    
def predict_trained_model_taxi(PUZone, Borough, year, month, day, hour):
    try:
        fecha_dt = datetime(year, month, day)
        dia_semana = fecha_dt.weekday()
        aeropuertos = ['JFK Airport', 'Newark Airport', 'LaGuardia Airport']

        eventos_hist = X_train_taxi[(X_train_taxi['Zone'] == PUZone) & (X_train_taxi['hora_pickup'] == hour)]['num_events']
        avg_events = float(eventos_hist.mean()) if not eventos_hist.empty else 0.0
        
        temp_mes = X_train_taxi[X_train_taxi['mes_pickup'] == month]['temperature_2m (°C)']
        sensacion_mes = X_train_taxi[X_train_taxi['mes_pickup'] == month]['apparent_temperature (°C)']

        avg_temp = float(temp_mes.mean()) if not temp_mes.empty else 20.0
        avg_sensacion = float(sensacion_mes.mean()) if not sensacion_mes.empty else avg_temp
        
        data_dict = {
            'Airport_fee': 2.5 if PUZone in aeropuertos else 0.0,
            'dia_pickup': int(day),
            'hora_pickup': int(hour),
            'is_airport_binary': int(1 if PUZone in aeropuertos else 0),
            'Borough': Borough,
            'service_zone': 'Airports' if PUZone in aeropuertos else 'Yellow Zone',
            'Zone': PUZone,
            'temperature_2m (°C)': float(avg_temp),
            'apparent_temperature (°C)': float(avg_sensacion),
            'dia_semana': int(dia_semana),
            'num_events': float(avg_events),
            'VendorID': int(2)
        }

        input_data = pd.DataFrame([data_dict])

        cols_order = ['Airport_fee', 'dia_pickup', 'hora_pickup', 'is_airport_binary',
       'Borough', 'service_zone', 'Zone', 'temperature_2m (°C)',
       'apparent_temperature (°C)', 'dia_semana', 'num_events', 'VendorID'
       ]
        
        input_data = input_data[cols_order]

        input_data['Airport_fee'] = input_data['Airport_fee'].astype('float64')
        input_data['dia_pickup'] = input_data['dia_pickup'].astype('int32')
        input_data['hora_pickup'] = input_data['hora_pickup'].astype('int32')
        input_data['is_airport_binary'] = input_data['is_airport_binary'].astype('int64')

        input_data['temperature_2m (°C)'] = input_data['temperature_2m (°C)'].astype('float64')
        input_data['apparent_temperature (°C)'] = input_data['apparent_temperature (°C)'].astype('float64')

        input_data['dia_semana'] = input_data['dia_semana'].astype('int32')
        input_data['num_events'] = input_data['num_events'].astype('float64')
        input_data['VendorID'] = input_data['VendorID'].astype('int32')

        cat_cols = [
            'Borough', 'service_zone', 'Zone'
        ]
        
        for col in input_data.columns:
            if col in cat_cols:
                input_data[col] = pd.Categorical(
                    input_data[col], 
                    categories=X_taxi[col].cat.categories
                )
            else:
                input_data[col] = pd.to_numeric(input_data[col], errors='coerce')
        
        pred = fixed_model_taxi.predict(input_data)[0]
        
        return {
            "prediction": f"{round(max(0, float(pred)), 2)} €",
            "borough": Borough,
            "zone": PUZone,
            "date": f"{year}-{month:02d}-{day:02d}",
            "hour": hour
        }

    except Exception as e:
        print(f"--- ERROR EN PREDICCIÓN TAXI ---")
        print(f"Detalle: {e}")
        return None
    
def get_zones():
    zones = (
        vtc[["PULocation_Zone", "PULocation_Borough"]]
        .dropna()
        .drop_duplicates()
        .sort_values("PULocation_Zone")
    )
    return zones.to_dict(orient="records")