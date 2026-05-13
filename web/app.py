from flask import Flask
from flask import send_from_directory
import os
import socket
from .routes.main_routes import main
from .routes.demand_routes import demand
from .routes.metro_routes import metro
from .routes.event_routes import event
from .routes.money_routes import money
from .routes.tips_routes import tips

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.register_blueprint(main)
app.register_blueprint(demand, url_prefix="/demanda")
app.register_blueprint(metro, url_prefix="/metro")
app.register_blueprint(event, url_prefix="/eventos")
app.register_blueprint(money, url_prefix="/economico")
app.register_blueprint(tips, url_prefix="/tips")


# Serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

if __name__ == "__main__":
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_RUN_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")

    def _lan_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.2)
            s.connect(("192.0.2.1", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            return None

    if host == "0.0.0.0":
        lip = _lan_ip()
        if lip:
            print(f"BoostMobility: en este equipo http://127.0.0.1:{port}")
            print(f"  Desde el móvil (misma Wi‑Fi): http://{lip}:{port}")
        else:
            print(f"BoostMobility: http://127.0.0.1:{port} (host {host})")
    else:
        print(f"BoostMobility: http://{host}:{port}")

    app.run(host=host, port=port, debug=debug)