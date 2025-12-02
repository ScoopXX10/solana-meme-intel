from fastapi import FastAPI
from src.api.tokens_router import router as tokens_router

app = FastAPI()

app.include_router(tokens_router)

@app.get("/")
def root():
    return {"status": "ok"}
