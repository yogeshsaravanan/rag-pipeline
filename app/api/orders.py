"""
CRUD endpoints for the Orders resource.
CDC sync is handled transparently via SQLAlchemy ORM event hooks
(see app/services/cdc_service.py — imported at startup so hooks register).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import OrderCreate
from app.db.database import Order, get_db

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.post("/", status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    order = Order(
        user_id=payload.user_id,
        product_name=payload.product_name,
        details=payload.details,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"status": "Order created", "data": {"id": order.id, "status": order.status}}


@router.patch("/{order_id}")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    return {"status": "Order updated", "new_status": order.status}


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"status": f"Order {order_id} deleted from both SQL and vector store"}
