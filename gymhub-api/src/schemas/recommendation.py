from marshmallow import Schema, fields, pre_load

class RecommendationFormSchema(Schema):
    athlete_experience = fields.String(required=True, description="beginner | intermediate | advanced")
    athlete_goal = fields.String(required=True, description="hypertrophy | strength | endurance")

    exercise_id = fields.Int(required=True)
    sets = fields.Int(required=True)
    reps = fields.Int(required=True)
    load_kg = fields.Float(required=True)

    # opcional; aceita vazio ("") vindo do form e vira None
    rir = fields.Int(allow_none=True, load_default=None)

    @pre_load
    def empty_to_none(self, data, **kwargs):
        # Quando vem de form, campo opcional pode chegar como ""
        if "rir" in data and (data["rir"] is None or str(data["rir"]).strip() == ""):
            data["rir"] = None
        return data
from marshmallow import Schema, fields

class RecommendationFormSchema(Schema):
    athlete_experience = fields.String(required=True, description="beginner | intermediate | advanced")
    athlete_goal = fields.String(required=True, description="hypertrophy | strength | endurance")

    
    exercise_id = fields.Int(required=True)
    sets = fields.Int(required=True)
    reps = fields.Int(required=True)
    load_kg = fields.Float(required=True)
    rir = fields.Int(required=False, allow_none=True)

