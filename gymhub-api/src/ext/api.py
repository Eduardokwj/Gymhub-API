from flask_smorest import Api
from src.resources.exercises import blp as ExercisesBP
from src.resources.workouts import blp as WorkoutsBP
from src.resources.sessions import blp as SessionsBP
from src.resources.integration import blp as IntegrationBP


def init_api(app):
    api = Api(app)
    api.register_blueprint(ExercisesBP)
    api.register_blueprint(WorkoutsBP)
    api.register_blueprint(SessionsBP)
    api.register_blueprint(IntegrationBP)