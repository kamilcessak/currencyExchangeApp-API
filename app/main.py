from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db

from app.routers import auth
from app.routers import wallet
from app.routers import rates
from app.routers import exchange
from app.routers import history

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Kantor Walut API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(wallet.router)
app.include_router(rates.router)
app.include_router(exchange.router)
app.include_router(history.router)

@app.get("/")
async def root():
    return {"message": "Kantor API działa!", "status": "OK"}