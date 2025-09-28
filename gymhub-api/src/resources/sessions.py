from flask.views import MethodView
from flask_smorest import Blueprint
from src.ext.db import db
from src.models.session import Session
from src.schemas.sessions import SessionSchema, SessionQuerySchema

blp = Blueprint("sessions", __name__, description="CRUD de sessões")

@blp.route("/sessions")
class SessionList(MethodView):
    @blp.arguments(SessionQuerySchema, location="query")
    @blp.response(200, SessionSchema(many=True))
    def get(self, args):
        page = max(1, int(args.get("page", 1)))
        page_size = min(100, int(args.get("page_size", 10)))
        query = Session.query
        w = args.get("workout_id")
        e = args.get("exercise_id")
        if w:
            query = query.filter(Session.workout_id == int(w))
        if e:
            query = query.filter(Session.exercise_id == int(e))
        return query.offset((page - 1) * page_size).limit(page_size).all()

    @blp.arguments(SessionSchema, location="form")  # ← form
    @blp.response(201, SessionSchema)
    def post(self, data):
        obj = Session(**data)
        db.session.add(obj)
        db.session.commit()
        return obj

@blp.route("/sessions/<int:obj_id>")
class SessionDetail(MethodView):
    @blp.response(200, SessionSchema)
    def get(self, obj_id):
        return Session.query.get_or_404(obj_id)

    @blp.arguments(SessionSchema(partial=True), location="form")  # ← form
    @blp.response(200, SessionSchema)
    def put(self, data, obj_id):
        obj = Session.query.get_or_404(obj_id)
        for k, v in data.items():
            setattr(obj, k, v)
        db.session.commit()
        return obj

    @blp.response(204)
    def delete(self, obj_id):
        obj = Session.query.get_or_404(obj_id)
        db.session.delete(obj)
        db.session.commit()
        return ""
