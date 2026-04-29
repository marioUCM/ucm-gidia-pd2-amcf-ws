from flask import Blueprint, render_template, request
from ..services.demand_service import predict_trained_model, predict_top_zones, get_zones, generate_demand_map

demand = Blueprint("demand", __name__)

@demand.route("/", methods=["GET", "POST"])
def demand_page():
    trained_result = None
    top_zones_result = None
    selected_max = None
    map_html = None
    selected_map = None

    # obtener zonas
    zones = get_zones()

    # agrupar por borough
    zones_by_borough = {}
    for z in zones:
        b = z["Borough"]
        if b not in zones_by_borough:
            zones_by_borough[b] = []
        zones_by_borough[b].append(z["Zone"])

    if request.method == "POST":

        model_type = request.form.get("model_type")

        date = request.form["date"]
        hour = int(request.form["hour"])
        year, month, day = map(int, date.split("-"))

        zone = request.form.get("zone")
        borough = request.form.get("borough")
        service_type = request.form.get("service_type", "none")

        import json

        previous_trained = request.form.get("previous_trained")
        previous_top = request.form.get("previous_top")
        previous_map = request.form.get("previous_map")

        if previous_trained:
            trained_result = json.loads(previous_trained)

        if previous_top:
            top_zones_result = json.loads(previous_top)

        if previous_map:
            map_html = previous_map

        # --- lógica por tipo de modelo ---
        if model_type == "pretrained":
            if not zone or not borough:
                return render_template(
                    "demand.html",
                    trained_result=trained_result,
                    zones_by_borough=zones_by_borough,
                    top_zones_result=top_zones_result,
                    selected_max=selected_max,
                    map_html=map_html,
                    selected_map=selected_map
                )
            trained_result = predict_trained_model(zone, borough, year, month, day, hour)

        elif model_type == "max_zone":
            selected_max = {
                "date": date,
                "hour": hour,
                "borough": borough if borough else "all",
                "service_type": service_type if service_type else "none"
            }
            top_zones_result = predict_top_zones(year, month, day, hour, borough, service_type)

        elif model_type == "map":
            selected_map = {
                "date": date,
                "hour": hour,
                "service_type": service_type if service_type else "none"
            }
            map_html = generate_demand_map(year, month, day, hour, service_type)

    # PASARLO AL HTML
    return render_template(
        "demand.html",
        trained_result=trained_result,
        zones_by_borough=zones_by_borough,
        top_zones_result=top_zones_result,
        selected_max=selected_max,
        map_html=map_html,
        selected_map=selected_map
    )