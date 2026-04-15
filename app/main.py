from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models.Producto import Producto
from app.models.Orden import Orden
from app.models.OrderItem import OrderItem

from app.routers.productos import router as productos_router
from app.routers.ordenes import router as ordenes_router
from app.db import crear_base_de_datos

@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_base_de_datos()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "API funcionando"}


app.include_router(productos_router)
app.include_router(ordenes_router)