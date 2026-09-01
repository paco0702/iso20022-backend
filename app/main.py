from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.db.cassandra import close_cassandra_connection, get_cassandra_session
from app.core.config import settings
from app.routers import auth

@asynccontextmanager
async def lifespan (app: FastAPI):
    # Startup
    get_cassandra_session()

    yield

    # Shutdown
    close_cassandra_connection()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url,],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

app.include_router(auth.router)

@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} is running"
    }