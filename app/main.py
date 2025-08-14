from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app import crud, models
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/orders/")
def create_order(customer_name: str, description: str, db: Session = Depends(get_db)):
    return crud.create_order(db, customer_name, description)


@app.get("/orders/{order_id}")
def read_order(order_id: int, db: Session = Depends(get_db)):
    return crud.get_order(db, order_id)


@app.put("/orders/{order_id}/status")
def update_order(order_id: int, new_status: str, db: Session = Depends(get_db)):
    return crud.update_order_status(db, order_id, new_status)


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    return crud.delete_order(db, order_id)
