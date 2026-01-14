import importlib
import os
import pkgutil
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from startup.life_cycle import register_startup_event, register_shutdown_event
import routers
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import models  # noqa: F401

load_dotenv()

app = FastAPI(
    title="Venue Hub API Services",
    swagger_ui_parameters={
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": 0,
        "displayRequestDuration": True,
        "persistAuthorization": True,
        "theme": "dark",
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Common"])
def root():
    return RedirectResponse(url="/docs")


@app.get("/test", tags=["Common"])
def roottest():
    return {
        "message": "Welcome to Just Do it Services. Visit /docs for API documentation."
    }


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


register_startup_event(app)
register_shutdown_event(app)

for _, module_name, _ in pkgutil.iter_modules(routers.__path__):
    if not module_name.startswith("router_"):
        continue
    module = importlib.import_module(f"routers.{module_name}")
    router = getattr(module, "app", None)
    if router:
        app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [{"HTTPBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
