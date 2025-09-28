from flask import Flask
from config import Config
from src.ext.db import init_db
from src.ext.api import init_api
from flask import redirect 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    init_api(app)
    return app


app = create_app()

@app.route("/")
def home():
    # abre direto o Swagger do GymHub
    return redirect("/docs", code=302)

@app.route("/coach-docs")
def coach_docs():
    # atalho para o Swagger do coach-svc
    coach = app.config.get("COACH_SVC_URL", "http://coach-svc:8000").rstrip("/")
    return redirect(f"{coach}/docs", code=302)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

