from fastapi import FastAPI
from src.api.tokens_router import router as tokens_router
from src.api.score_router import router as score_router

app = FastAPI()

app.include_router(tokens_router)
app.include_router(score_router)


@app.get("/")
def root():
    return {"status": "ok"}
