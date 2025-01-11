from fastapi import FastAPI
from src.api.routes import users, papers
from src.utils.logger import setup_logging
from src.utils.config import load_config
import os

def create_app() -> FastAPI:
    config = load_config()

    if "openai_api_key" in config and config["openai_api_key"]:
        os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

    if "database" in config and "url" in config["database"]:
        os.environ["DATABASE_URL"] = config["database"]["url"]

    setup_logging()

    app = FastAPI(title="AI Academic Research Assistant")

    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(papers.router, prefix="/papers", tags=["Papers"])

    @app.get("/")
    def read_root():
        return {"message": "Welcome to the AI Academic Research Assistant API"}

    return app

app = create_app()
