# routers/router_auto.py

import inspect
import pkgutil
import importlib
from fastapi import APIRouter, Depends
from sqlmodel import Session
from dbconfig.database import Database
import repositories

# -------------------------------------------------
# HTTP METHOD ORDER (Swagger order)
# -------------------------------------------------
METHOD_ORDER = ["get", "post", "patch", "delete"]

HTTP_METHOD_MAP = {
    "get": "get",
    "post": "post",
    "patch": "patch",
    "delete": "delete",
}

app = APIRouter()


def register_repo_routes():

    for _, module_name, _ in pkgutil.iter_modules(repositories.__path__):
        module = importlib.import_module(f"repositories.{module_name}")

        functions = [
            (name, func)
            for name, func in inspect.getmembers(module, inspect.isfunction)
            if name.startswith("repo_")
        ]

        # -----------------------------
        # Sort by HTTP method order
        # -----------------------------
        def sort_key(item):
            parts = item[0].split("_")
            if len(parts) < 3:
                return 99
            method = parts[2]
            return METHOD_ORDER.index(method) if method in METHOD_ORDER else 99

        functions.sort(key=sort_key)

        # -----------------------------
        # Register routes
        # -----------------------------
        for name, func in functions:
            parts = name.split("_")
            if len(parts) < 3:
                continue

            _, resource, operation = parts[0], parts[1], parts[2]
            http_method = HTTP_METHOD_MAP.get(operation)
            if not http_method:
                continue

            # 🔥 Path logic
            # repo_role_get_by_id → /get_by_id
            action = "_".join(parts[2:])  # get_by_id / post_bulk / etc
            path = f"/{action}"

            router = APIRouter(
                prefix=f"/{resource}",
                tags=[resource],
            )

            def endpoint(
                *args,
                func=func,
                session: Session = Depends(Database.getSession),
            ):
                return func(*args, session=session)

            getattr(router, http_method)(path)(endpoint)
            app.include_router(router)


# MUST run at import time
register_repo_routes()
