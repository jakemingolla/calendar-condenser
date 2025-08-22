from fastapi import FastAPI

from src.api.routes.graphs import router as graphs_router
from src.api.routes.users import router as users_router

app = FastAPI()

app.include_router(users_router, prefix="/api/v1")
app.include_router(graphs_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
