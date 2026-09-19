from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.restaurants import router as restaurants_router

app = FastAPI(
    title="Restaurant Knowledge OS",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(restaurants_router)


@app.get("/")
def root():
    return {
        "message": "Restaurant Knowledge OS API"
    }