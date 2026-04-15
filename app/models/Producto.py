from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from app.models.OrderItem import OrderItem
    
class Producto(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float

    orderItems: list["OrderItem"] = Relationship(back_populates="producto")