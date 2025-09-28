import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_TITLE = "GymHub API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # banco de dados
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_ECHO = False
    PROPAGATE_EXCEPTIONS = True

    # integrações
    COACH_SVC_URL = os.getenv("COACH_SVC_URL", "http://coach-svc:8000")
    WGER_BASE_URL = os.getenv("WGER_BASE_URL", "https://wger.de/api/v2")
    WGER_LANG = os.getenv("WGER_LANG", "pt")

