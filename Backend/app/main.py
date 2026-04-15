from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import init_db
from app.api.v1.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="SpeakSmart Backend",
    description="Backend API for the SpeakSmart language learning app.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow your React frontend (Vite runs on port 5173) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SpeakSmart Backend is running! 🚀"}

@app.get("/health")
async def health():
    return {"status": "healthy"}