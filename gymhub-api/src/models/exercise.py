from src.ext.db import db


class Exercise(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    muscle_group = db.Column(db.String(80))
    equipment = db.Column(db.String(80))
    is_custom = db.Column(db.Boolean, default=True)