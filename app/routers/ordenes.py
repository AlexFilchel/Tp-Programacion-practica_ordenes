from fastapi import APIRouter, Query

from app.schemas.OrdenDTO import OrdenCreate, OrdenRead, OrdenDetalleRead, OrdenPaginadaRead
from app.services.orden_service import OrdenService

router = APIRouter(prefix="/ordenes", tags=["Ordenes"])


@router.post("", response_model=OrdenRead)
def crear_orden(datos_orden: OrdenCreate):
    service = OrdenService()
    return service.crear_orden(datos_orden)

@router.get("/{order_id}", response_model=OrdenDetalleRead)
def obtener_orden(order_id: int):
    service = OrdenService()
    return service.obtener_orden_por_id(order_id)

@router.get("", response_model=OrdenPaginadaRead)
def listar_ordenes(offset: int = Query(0, ge=0), limit: int = Query(10, gt=0)):
    service = OrdenService()
    return service.listar_ordenes(offset=offset, limit=limit)