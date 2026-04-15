from pydantic import BaseModel, Field
from typing import List


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrdenCreate(BaseModel):
    user_email: str
    items: List[OrderItemCreate]


class OrderItemRead(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrdenRead(BaseModel):
    id: int
    user_email: str
    total_amount: float
    items: List[OrderItemRead]
    
class ProductoEnOrdenRead(BaseModel):
    id: int
    name: str
    price: float


class OrderItemDetalleRead(BaseModel):
    product: ProductoEnOrdenRead
    quantity: int
    unit_price: float


class OrdenDetalleRead(BaseModel):
    id: int
    user_email: str
    total_amount: float
    items: List[OrderItemDetalleRead]
    
class OrdenResumenRead(BaseModel):
    id: int
    user_email: str
    total_amount: float


class OrdenPaginadaRead(BaseModel):
    total: int
    data: List[OrdenResumenRead]