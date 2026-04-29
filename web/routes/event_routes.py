from flask import Blueprint, render_template,request,jsonify
from ..services.event_service import grafica1,grafica2,grafica3,grafica4,grafica5,generate_films_taxi_map

event = Blueprint("event", __name__)


@event.route("/")
def event_page():

    mapa_pelis = generate_films_taxi_map()

    topN = 25

    grafica1_html = grafica1(topN,as_json=False)
    grafica2_html = grafica2(topN,as_json=False)
    grafica3_html = grafica3(topN,as_json=False)
    grafica4_html = grafica4()
    grafica5_html = grafica5()

    return render_template("event.html",
                            mapa_pelis=mapa_pelis,
                            grafica1=grafica1_html,
                            grafica2=grafica2_html,
                            grafica3=grafica3_html,
                            grafica4=grafica4_html,
                            grafica5=grafica5_html,
                            topN_actual=topN
                            )

@event.route("/update-graph", methods=["POST"])
def update_graph():
    data = request.get_json()
    n = int(data.get("top_n", 25))
    
    update_graph1 = grafica1(topN=n,as_json=True)
    update_graph2 = grafica2(topN=n,as_json=True)
    update_graph3 = grafica3(topN=n,as_json=True)

    return jsonify({
        "updt_g1": update_graph1,
        "updt_g2": update_graph2,
        "updt_g3": update_graph3
    })