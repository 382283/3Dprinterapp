from sqlalchemy.orm import Session
from app.models import Order
import datetime


def create_order(
    db: Session, customer_name: str, description: str, status: str = "作成中"
):
    new_order = Order(
        customer_name=customer_name,
        description=description,
        status=status,
        created_at=datetime.datetime.utcnow(),
        updated_at=None,
    )
    db.add(new_order)  # オブジェクトをセションに登録
    db.commit()  # DBに確定（トランザクションコミット）
    db.refresh(new_order)
    return new_order


def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def get_all_orders(db: Session):
    return db.query(Order).all()

def update_order_status(db: Session, order_id: int, new_status: str):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = new_status
        order.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(order)
    return order


def delete_order(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        db.delete(order)
        db.commit()
        return True
    return False
