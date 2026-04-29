from flask import Blueprint, render_template,request,jsonify
from ..services.money_service import grafica1,grafica2,grafica3,grafica4,grafica5,grafica6,generate_economic_map

money = Blueprint("money", __name__)

@money.route("/")
def money_page():

    mapa_coropletico = generate_economic_map()

    topN = 25

    grafica1_html = grafica1()
    grafica2_html = grafica2()
    grafica3_html = grafica3()
    grafica4_html = grafica4()
    grafica5_html = grafica5()
    grafica6_html = grafica6()

    return render_template(
        "money.html",
        mapa_coropletico=mapa_coropletico,
        grafica1=grafica1_html,
        grafica2=grafica2_html,
        grafica3=grafica3_html,
        grafica4=grafica4_html,
        grafica5=grafica5_html,
        grafica6=grafica6_html,
        topN_actual=topN
    )


@money.route("/update-graph", methods=["POST"])
def update_graph():

    data = request.get_json()
    n = int(data.get("top_n", 25))

    update_graph1 = grafica1(n,as_sjon=True)
    update_graph2 = grafica2(n,as_sjon=True)
    update_graph3 = grafica3(n,as_sjon=True)

    return jsonify({
        "updt_g1": update_graph1,
        "updt_g2": update_graph2,
        "updt_g3": update_graph3,
    })