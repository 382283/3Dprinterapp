from fastapi import FastAPI, Depends, WebSocket
from sqlalchemy.orm import Session
from app import crud, models
from app.database import SessionLocal, engine
from app.websocket import websocket_endpoint, notify_order_update, notify_new_order

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# WebSocketエンドポイント
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """
    WebSocket接続用エンドポイント
    クライアントはws://localhost:8000/ws に接続
    """
    await websocket_endpoint(websocket)


# データベース情報全取得
@app.post("/orders/")
async def create_order(
    customer_name: str, description: str, db: Session = Depends(get_db)
):
    """
    新規依頼作成
    作成後に全クライアントにリアルタイム通知を送信
    """
    order = crud.create_order(db, customer_name, description)

    # 通知用のデータを作成
    order_data = {
        "id": order.id,
        "customer_name": order.customer_name,
        "description": order.description,
        "status": order.status,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }

    # 全クライアントに新規依頼通知を送信
    await notify_new_order(order_data)
    return order


@app.get("/orders/")
def read_order(db: Session = Depends(get_db)):
    return crud.get_all_orders(db)


@app.get("/orders/{order_id}")
def read_order(order_id: int, db: Session = Depends(get_db)):
    return crud.get_order(db, order_id)


@app.put("/orders/{order_id}/status")
async def update_order(order_id: int, new_status: str, db: Session = Depends(get_db)):
    """
    進捗更新
    更新後に全クライアントにリアルタイム通知を送信
    """

    order = crud.update_order_status(db, order_id, new_status)

    if order:
        # 通知用のデータの作成
        order_data = {
            "id": order.id,
            "customer_name": order.customer_name,
            "description": order.description,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        }

        # 全クライアントに進捗更新通知を送信
        await notify_order_update(order_data)

    return order


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    return crud.delete_order(db, order_id)
