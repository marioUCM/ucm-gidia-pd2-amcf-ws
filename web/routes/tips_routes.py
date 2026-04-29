from flask import Blueprint, render_template, request
from ..services.tips_service import predict_trained_model_vtc, predict_trained_model_taxi, get_zones
import pandas as pd

tips = Blueprint("tips", __name__)

@tips.route("/", methods=["GET", "POST"])
def tips_page():

    result = None

    zones = get_zones()

    zones_by_borough = {}
    for z in zones:
        distrito = z["PULocation_Borough"]
        barrio = z["PULocation_Zone"]
        
        if pd.notna(distrito) and distrito != 'Unknown':
            if distrito not in zones_by_borough:
                zones_by_borough[distrito] = []
            zones_by_borough[distrito].append(barrio)

    for distrito in zones_by_borough:
        zones_by_borough[distrito].sort()

    zones_by_borough = {k: sorted(v) for k, v in zones_by_borough.items() if pd.notna(k)}

    if request.method == "POST":

        model_type = request.form.get("model_type")
        
        if not model_type:
            return render_template(
                "tips.html",
                result="Error: No se seleccionó un modelo",
                zones_by_borough=zones_by_borough
            )

        PUzone = request.form.get("PUzone")
        PUborough = request.form.get("PUborough")
        date = request.form.get("date")
        hour = request.form.get("hour")
        
        if not all([PUzone, PUborough, date, hour]):
            return render_template(
                "tips.html",
                result="Error: Faltan campos obligatorios",
                zones_by_borough=zones_by_borough
            )
        
        hour = int(hour)
        year, month, day = map(int, date.split("-"))

        if model_type == "pretrained":
            DOzone = request.form.get("DOzone")
            DOborough = request.form.get("DOborough")
            
            if not DOzone or not DOborough:
                return render_template(
                    "tips.html",
                    result="Error: Para el modelo pre-entrenado se necesitan la zona y distrito de destino",
                    zones_by_borough=zones_by_borough
                )
                
            result = predict_trained_model_vtc(PUzone, PUborough, DOzone, DOborough, year, month, day, hour)
        elif model_type == "taxi":
            result = predict_trained_model_taxi(PUzone, PUborough, year, month, day, hour)
                       
    return render_template(
        "tips.html",
        result=result,
        zones_by_borough=zones_by_borough
    )