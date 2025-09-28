# src/blueprints/integration.py

import re
import unicodedata
import requests
from flask.views import MethodView
from flask_smorest import Blueprint
from flask import current_app
from marshmallow import Schema, INCLUDE

from src.schemas.recommendation import RecommendationFormSchema
from ..schemas.wger import WgerSearchSchema


# Schema "pass-through": aceita qualquer JSON sem validar campos
class AnySchema(Schema):
    class Meta:
        unknown = INCLUDE


blp = Blueprint("integration", __name__, description="Integrações externas e coach-svc")


# -------- Helpers --------

def _norm(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s.casefold())
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def _match_contains(name: str, query: str) -> bool:
    n = _norm(name)
    tokens = [t for t in re.split(r"\s+", _norm(query)) if t]
    return all(tok in n for tok in tokens)

def pick_name(item: dict, lang_id: int = 2):
    """
    Retorna o nome do exercício a partir de 'translations'.
    Prioriza o idioma solicitado (lang_id), depois EN(2), depois qualquer um.
    """
    translations = item.get("translations") or []
    for t in translations:
        if t.get("language") == lang_id and t.get("name"):
            return t["name"]
    for t in translations:
        if t.get("language") == 2 and t.get("name"):
            return t["name"]
    for t in translations:
        if t.get("name"):
            return t["name"]
    return None

def clamp_limit(params: dict, key: str = "limit", default: int = 20, max_limit: int = 100):
    try:
        lim = int(params.get(key, default))
    except (TypeError, ValueError):
        lim = default
    params[key] = max(1, min(max_limit, lim))

def fetch_exerciseinfo_pages(base_url: str, params: dict, timeout: int = 20, max_pages: int = 5):
    """
    Itera as páginas do /exerciseinfo/ e rende 'results' já decodados.
    Respeita 'next' do payload da WGER.
    """
    url = f"{base_url}/exerciseinfo/"
    page = 0
    while url and page < max_pages:
        resp = requests.get(url, params=params if page == 0 else None, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", []) or []
        for r in results:
            yield r
        url = data.get("next")
        page += 1


# -------- Endpoints --------

@blp.route("/external/wger/exercises")
class WgerSearch(MethodView):
    @blp.arguments(WgerSearchSchema, location="query")
    def get(self, args):
        """
        Lista básica de exercícios com nome.
        Agora suporta filtro 'contains' no servidor.
        """
        base = current_app.config["WGER_BASE_URL"].rstrip("/")
        params = dict(args)

        # Defaults
        params.setdefault("language", 2)  # 2 = EN
        params.setdefault("status", 2)    # approved only (se suportado)
        params.setdefault("limit", 20)
        params.pop("ordering", None)      # evitar 400 em /exerciseinfo/

        clamp_limit(params)
        try:
            lang_id = int(params.get("language", 2))
        except (TypeError, ValueError):
            lang_id = 2

        contains = (args.get("contains") or "").strip()
        raw = str(args.get("raw", "")).lower() in ("1", "true", "yes", "y")

        try:
            if contains:
                # Busca paginada até coletar 'limit' itens que batam o contains
                wanted = params["limit"]
                collected = []
                for it in fetch_exerciseinfo_pages(base, params, timeout=20, max_pages=5):
                    name = pick_name(it, lang_id)
                    if name and _match_contains(name, contains):
                        collected.append({
                            "id": it.get("id"),
                            "name": name,
                            "category": (it.get("category") or {}).get("id"),
                            "category_name": (it.get("category") or {}).get("name"),
                        })
                        if len(collected) >= wanted:
                            break
                items = collected
            else:
                # Sem filtro: só 1 requisição
                resp = requests.get(f"{base}/exerciseinfo/", params=params, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                if raw:
                    return data, 200
                items = [{
                    "id": it.get("id"),
                    "name": pick_name(it, lang_id),
                    "category": (it.get("category") or {}).get("id"),
                    "category_name": (it.get("category") or {}).get("name"),
                } for it in data.get("results", [])]
        except requests.RequestException as exc:
            return {"error": "wger request failed", "detail": str(exc)}, 502

        return {"count": len(items), "results": items, "params": params}, 200


@blp.route("/external/wger/exerciseinfo")
class WgerInfo(MethodView):
    @blp.arguments(WgerSearchSchema, location="query")
    def get(self, args):
        """
        Detalhes dos exercícios com nomes legíveis + músculos/equipamentos.
        Suporta 'contains' (servidor) igual ao endpoint básico.
        """
        base = current_app.config["WGER_BASE_URL"].rstrip("/")
        params = dict(args)
        params.setdefault("language", 2)
        params.setdefault("limit", 20)
        params.pop("ordering", None)

        clamp_limit(params)
        try:
            lang_id = int(params.get("language", 2))
        except (TypeError, ValueError):
            lang_id = 2

        contains = (args.get("contains") or "").strip()
        raw = str(args.get("raw", "")).lower() in ("1", "true", "yes", "y")

        try:
            if contains:
                wanted = params["limit"]
                collected = []
                for it in fetch_exerciseinfo_pages(base, params, timeout=20, max_pages=5):
                    name = pick_name(it, lang_id)
                    if not (name and _match_contains(name, contains)):
                        continue
                    muscles = it.get("muscles") or []
                    equipment = it.get("equipment") or []
                    collected.append({
                        "id": it.get("id"),
                        "name": name,
                        "category_id": (it.get("category") or {}).get("id"),
                        "category_name": (it.get("category") or {}).get("name"),
                        "muscle_names": [m.get("name_en") or m.get("name") for m in muscles if (m.get("name_en") or m.get("name"))],
                        "equipment_names": [e.get("name") for e in equipment if e.get("name")],
                    })
                    if len(collected) >= wanted:
                        break
                items = collected
            else:
                resp = requests.get(f"{base}/exerciseinfo/", params=params, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                if raw:
                    return data, 200
                items = []
                for it in data.get("results", []):
                    muscles = it.get("muscles") or []
                    equipment = it.get("equipment") or []
                    items.append({
                        "id": it.get("id"),
                        "name": pick_name(it, lang_id),
                        "category_id": (it.get("category") or {}).get("id"),
                        "category_name": (it.get("category") or {}).get("name"),
                        "muscle_names": [m.get("name_en") or m.get("name") for m in muscles if (m.get("name_en") or m.get("name"))],
                        "equipment_names": [e.get("name") for e in equipment if e.get("name")],
                    })
        except requests.RequestException as exc:
            return {"error": "wger request failed", "detail": str(exc)}, 502

        return {"count": len(items), "results": items, "params": params}, 200


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
            try:
                body = resp.json()
            except ValueError:
                body = {"error": "invalid coach-svc response", "text": resp.text}
            return body, resp.status_code
        except requests.RequestException as exc:
            return {"error": "coach-svc unreachable", "detail": str(exc)}, 502
