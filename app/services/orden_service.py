from fastapi import HTTPException
from sqlmodel import select

from app.models.Orden import Orden
from app.models.OrderItem import OrderItem
from app.models.Producto import Producto
from app.schemas.OrdenDTO import (
    OrdenCreate,
    OrdenRead,
    OrderItemRead,
    OrdenDetalleRead,
    OrderItemDetalleRead,
    ProductoEnOrdenRead,
    OrdenResumenRead,
    OrdenPaginadaRead,
)
from app.uow.unit_of_work import UnitOfWork


class OrdenService:
    def crear_orden(self, datos_orden: OrdenCreate) -> OrdenRead:
        with UnitOfWork() as uow:
            orden = Orden(
                user_email=datos_orden.user_email,
                total_amount=0
            )
            uow.session.add(orden)
            uow.session.flush()

            items_respuesta = []
            total = 0

            for item in datos_orden.items:
                producto = uow.session.get(Producto, item.product_id)

                if not producto:
                    raise HTTPException(status_code=404, detail="Producto no encontrado")

                subtotal = producto.price * item.quantity
                total += subtotal

                order_item = OrderItem(
                    order_id=orden.id,
                    product_id=producto.id,
                    quantity=item.quantity,
                    unit_price=producto.price
                )
                uow.session.add(order_item)

                items_respuesta.append(
                    OrderItemRead(
                        product_id=producto.id,
                        quantity=item.quantity,
                        unit_price=producto.price
                    )
                )

            orden.total_amount = total

            uow.commit()
            uow.session.refresh(orden)

            return OrdenRead(
                id=orden.id,
                user_email=orden.user_email,
                total_amount=orden.total_amount,
                items=items_respuesta
            )

    def obtener_orden_por_id(self, order_id: int) -> OrdenDetalleRead:
        with UnitOfWork() as uow:
            orden = uow.session.get(Orden, order_id)

            if not orden:
                raise HTTPException(status_code=404, detail="Orden no encontrada")

            statement = (
                select(OrderItem, Producto)
                .join(Producto, OrderItem.product_id == Producto.id)
                .where(OrderItem.order_id == order_id)
            )

            resultados = uow.session.exec(statement).all()

            items = []
            for order_item, producto in resultados:
                items.append(
                    OrderItemDetalleRead(
                        product=ProductoEnOrdenRead(
                            id=producto.id,
                            name=producto.name,
                            price=producto.price
                        ),
                        quantity=order_item.quantity,
                        unit_price=order_item.unit_price
                    )
                )

            return OrdenDetalleRead(
                id=orden.id,
                user_email=orden.user_email,
                total_amount=orden.total_amount,
                items=items
            )

    def listar_ordenes(self, offset: int = 0, limit: int = 10) -> OrdenPaginadaRead:
        with UnitOfWork() as uow:
            total = len(uow.session.exec(select(Orden)).all())

            ordenes = uow.session.exec(
                select(Orden).offset(offset).limit(limit)
            ).all()

            data = [
                OrdenResumenRead(
                    id=orden.id,
                    user_email=orden.user_email,
                    total_amount=orden.total_amount
                )
                for orden in ordenes
            ]

            return OrdenPaginadaRead(
                total=total,
                data=data
            )