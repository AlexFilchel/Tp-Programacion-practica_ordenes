from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db import get_session
from app.models.Producto import Producto
from app.schemas.ProductoDTO import ProductoCreate, ProductoRead

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.post("",response_model=ProductoRead)
def crear_producto(
    datos_producto: ProductoCreate,
    session: Session = Depends(get_session)
):
    producto = Producto(
        name=datos_producto.name,
        price=datos_producto.price
    )
    
    session.add(producto)
    session.commit()
    session.refresh(producto)    #lee el objeto desde la base de  datos (para devolverlo con el id)
    
    return producto