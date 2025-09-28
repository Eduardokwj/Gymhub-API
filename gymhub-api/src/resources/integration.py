import requests
from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request, current_app
from marshmallow import Schema, INCLUDE
from src.schemas.recommendation import RecommendationFormSchema

from ..schemas.wger import WgerSearchSchema


# Schema "pass-through": aceita qualquer JSON sem validar campos
class AnySchema(Schema):
    class Meta:
        unknown = INCLUDE  # mantém chaves desconhecidas no payload/resposta


blp = Blueprint("integration", __name__, description="Integrações externas e coach-svc")


@blp.route("/external/wger/exercises")
class WgerSearch(MethodView):
    @blp.arguments(WgerSearchSchema, location="query")
    def get(self, args):
        """
        Proxy para WGER.
        """
        base = current_app.config["WGER_BASE_URL"]
        params = dict(args)  # já vem validado pelo schema

        # Defaults mais "ricos"
        params.setdefault("language", 2)  # 2 = inglês, mais resultados
        params.setdefault("status", 2)    # approved only
        params.setdefault("limit", 20)
        params.setdefault("ordering", "name")

        # modo debug: retorna o JSON cru da WGER
        raw = str(args.get("raw", "")).lower() in ("1", "true", "yes", "y")

        try:
            resp = requests.get(f"{base}/exercise/", params=params, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as exc:
            return {"error": "wger request failed", "detail": str(exc)}, 502

        data = resp.json()
        items = [
            {"id": it.get("id"), "name": it.get("name"), "category": it.get("category")}
            for it in data.get("results", [])
        ]
        return {"count": len(items), "results": items, "params": params}, 200


@blp.route("/external/wger/exerciseinfo")
class WgerInfo(MethodView):
    @blp.arguments(WgerSearchSchema, location="query")
    def get(self, args):
        """
        Proxy para WGER /exerciseinfo/. Retorna nomes legíveis.
        Dicas:
          - language=2 (EN) e limit=20..50 costumam trazer bons resultados
        """
        base = current_app.config["WGER_BASE_URL"]
        params = dict(args)
        params.setdefault("language", 2)
        params.setdefault("limit", 20)

        raw = str(args.get("raw", "")).lower() in ("1", "true", "yes", "y")

        try:
            resp = requests.get(f"{base}/exerciseinfo/", params=params, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as exc:
            return {"error": "wger request failed", "detail": str(exc)}, 502

        data = resp.json()
        if raw:
            return data, 200

        # Resumo com nomes legíveis
        items = []
        for it in data.get("results", []):
            base_info = it.get("exercise_base") or {}
            muscles = it.get("muscles") or []
            equipment = it.get("equipment") or []
            items.append({
                "id": it.get("id"),
                "name": base_info.get("name"),
                "category_name": (it.get("category") or {}).get("name"),
                "muscle_names": [m.get("name") for m in muscles if m.get("name")],
                "equipment_names": [e.get("name") for e in equipment if e.get("name")],
            })
        return {"count": len(items), "results": items}, 200


@blp.route("/recommendations")
class Recommendations(MethodView):
    @blp.arguments(RecommendationFormSchema, location="form")
    def post(self, form):
        """
        Recebe dados por FORM (inputs separados no Swagger),
        monta o payload JSON e chama o coach-svc /plan.
        """
        coach_url = current_app.config["COACH_SVC_URL"].rstrip("/")
        payload = {
            "athlete": {
                "experience": form["athlete_experience"],
                "goal": form["athlete_goal"],
            },
            "session": [{
                "exercise_id": form["exercise_id"],
                "sets": form["sets"],
                "reps": form["reps"],
                "load_kg": form["load_kg"],
                "rir": form.get("rir"),
            }],
        }
        try:
            resp = requests.post(f"{coach_url}/plan", json=payload, timeout=15)
            return resp.json(), resp.status_code
        except requests.RequestException as exc:
            return {"error": "coach-svc unreachable", "detail": str(exc)}, 502

