from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.Producto import Producto
class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orden.id")
    product_id: int = Field(foreign_key="producto.id")
    quantity: int
    unit_price: float
    
    producto: list["Producto"] = Relationship(back_populates="orderItems")