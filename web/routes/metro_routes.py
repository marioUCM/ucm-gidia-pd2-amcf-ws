from flask import Blueprint, render_template

from ..services.metro_service import get_metro_dashboard_context


metro = Blueprint("metro", __name__)


@metro.route("/")
def metro_page():
    context = get_metro_dashboard_context()
    return render_template("metro.html", **context)
