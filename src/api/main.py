from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.score_router import router as score_router
from src.api.tokens_router import router as tokens_router

# NEW: Import scheduler starter
from src.scheduler.tasks import start_scheduler

app = FastAPI(
    title="Solana Meme Intel",
    version="1.0.0"
)

# CORS (optional, but good for local UI or frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(score_router)
app.include_router(tokens_router)

# --- SCHEDULER STARTUP ---
@app.on_event("startup")
def launch_scheduler():
    print("🚀 Starting background scheduler...")
    start_scheduler()


@app.get("/")
def root():
    return {"message": "Solana Meme Intel backend is running!"}

