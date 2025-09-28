from flask.views import MethodView
from flask_smorest import Blueprint
from src.ext.db import db
from src.models.exercise import Exercise
from src.schemas.exercises import ExerciseSchema, ExerciseQuerySchema

blp = Blueprint("exercises", __name__, description="CRUD de exercícios")

@blp.route("/exercises")
class ExerciseList(MethodView):
    # GET já tem campos separados (query params)
    @blp.arguments(ExerciseQuerySchema, location="query")
    @blp.response(200, ExerciseSchema(many=True))
    def get(self, args):
        q = (args.get("q") or "").strip()
        page = max(1, int(args.get("page", 1)))
        page_size = min(100, int(args.get("page_size", 10)))

        query = Exercise.query
        if q:
            query = query.filter(
                (Exercise.name.ilike(f"%{q}%")) |
                (Exercise.muscle_group.ilike(f"%{q}%")) |
                (Exercise.equipment.ilike(f"%{q}%"))
            )
        return query.offset((page - 1) * page_size).limit(page_size).all()

    # ⚠️ Aqui muda: FORM em vez de JSON → Swagger mostra 1 campo por propriedade
    @blp.arguments(ExerciseSchema, location="form")
    @blp.response(201, ExerciseSchema)
    def post(self, data):
        obj = Exercise(**data)
        db.session.add(obj)
        db.session.commit()
        return obj

@blp.route("/exercises/<int:obj_id>")
class ExerciseDetail(MethodView):
    @blp.response(200, ExerciseSchema)
    def get(self, obj_id):
        return Exercise.query.get_or_404(obj_id)

    # PUT parcial também via FORM
    @blp.arguments(ExerciseSchema(partial=True), location="form")
    @blp.response(200, ExerciseSchema)
    def put(self, data, obj_id):
        obj = Exercise.query.get_or_404(obj_id)
        for k, v in data.items():
            setattr(obj, k, v)
        db.session.commit()
        return obj

    @blp.response(204)
    def delete(self, obj_id):
        obj = Exercise.query.get_or_404(obj_id)
        db.session.delete(obj)
        db.session.commit()
        return ""
