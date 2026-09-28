from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from .database import init_db

from .routes import router as page_router

from .api import router as api_router


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    init_db()

    yield


app = FastAPI(
    title="FitBuddy API",
    description=(
        "AI-powered personalized "
        "fitness and wellness plan generator."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static",
)


app.include_router(
    page_router
)

app.include_router(
    api_router
)