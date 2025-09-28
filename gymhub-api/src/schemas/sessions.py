from marshmallow import Schema, fields, validates, ValidationError

class SessionSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True, description="ID do treino associado")
    exercise_id = fields.Int(required=True, description="ID do exercício associado")
    sets = fields.Int(required=True, description="Número de séries")
    reps = fields.Int(required=True, description="Número de repetições")
    load_kg = fields.Float(required=True, description="Carga em kg")
    rir = fields.Int(required=False, description="Reps in reserve")

    @validates("sets")
    def _v_sets(self, v): 
        if v <= 0 or v > 20: raise ValidationError("sets deve estar entre 1 e 20")

    @validates("reps")
    def _v_reps(self, v):
        if v <= 0 or v > 50: raise ValidationError("reps deve estar entre 1 e 50")

    @validates("load_kg")
    def _v_load(self, v):
        if v < 0 or v > 1000: raise ValidationError("load_kg deve ser >= 0 e <= 1000")


class SessionQuerySchema(Schema):
    workout_id = fields.Int(required=False, description="Filtrar por treino")
    exercise_id = fields.Int(required=False, description="Filtrar por exercício")
    page = fields.Int(required=False, missing=1, description="Página (>=1)")
    page_size = fields.Int(required=False, missing=10, description="Itens por página (<=100)")