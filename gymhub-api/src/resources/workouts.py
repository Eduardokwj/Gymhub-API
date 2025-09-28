from flask.views import MethodView
from flask_smorest import Blueprint
from src.ext.db import db
from src.models.workout import Workout
from src.schemas.workouts import WorkoutSchema, WorkoutQuerySchema

blp = Blueprint("workouts", __name__, description="CRUD de treinos")

@blp.route("/workouts")
class WorkoutList(MethodView):
    @blp.arguments(WorkoutQuerySchema, location="query")
    @blp.response(200, WorkoutSchema(many=True))
    def get(self, args):
        q = (args.get("q") or "").strip()
        page = max(1, int(args.get("page", 1)))
        page_size = min(100, int(args.get("page_size", 10)))
        query = Workout.query
        if q:
            query = query.filter(Workout.title.ilike(f"%{q}%"))
        return query.offset((page - 1) * page_size).limit(page_size).all()

    @blp.arguments(WorkoutSchema, location="form")  # ← form
    @blp.response(201, WorkoutSchema)
    def post(self, data):
        obj = Workout(**data)
        db.session.add(obj)
        db.session.commit()
        return obj

@blp.route("/workouts/<int:obj_id>")
class WorkoutDetail(MethodView):
    @blp.response(200, WorkoutSchema)
    def get(self, obj_id):
        return Workout.query.get_or_404(obj_id)

    @blp.arguments(WorkoutSchema(partial=True), location="form")  # ← form
    @blp.response(200, WorkoutSchema)
    def put(self, data, obj_id):
        obj = Workout.query.get_or_404(obj_id)
        for k, v in data.items():
            setattr(obj, k, v)
        db.session.commit()
        return obj

    @blp.response(204)
    def delete(self, obj_id):
        obj = Workout.query.get_or_404(obj_id)
        db.session.delete(obj)
        db.session.commit()
        return ""
