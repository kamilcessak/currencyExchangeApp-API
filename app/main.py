from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db

from app.routers import auth
from app.routers import wallet
from app.routers import rates
from app.routers import exchange

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Kantor Walut API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(wallet.router)
app.include_router(rates.router)
app.include_router(exchange.router)

@app.get("/")
async def root():
    return {"message": "Kantor API działa!", "status": "OK"}