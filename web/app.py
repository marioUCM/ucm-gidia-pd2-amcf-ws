from flask import Flask
from flask import send_from_directory
import os
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
    app.run(debug=True,use_reloader=False)              #Minio
    # app.run(host="0.0.0.0", port=5000, debug=False)     #Docker