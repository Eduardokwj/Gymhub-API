from marshmallow import Schema, fields

class RecommendationFormSchema(Schema):
    athlete_experience = fields.String(required=True, description="beginner | intermediate | advanced")
    athlete_goal = fields.String(required=True, description="hypertrophy | strength | endurance")

    
    exercise_id = fields.Int(required=True)
    sets = fields.Int(required=True)
    reps = fields.Int(required=True)
    load_kg = fields.Float(required=True)
    rir = fields.Int(required=False, allow_none=True)
