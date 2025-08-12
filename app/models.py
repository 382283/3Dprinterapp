from sqlalchemy import Column, Integer, String, DateTime, TEXT
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    description = Column(TEXT, nullable=False)
    status = Column(String, nullable=False, default="作成中")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return (
            f"<Order(id={self.id}, customer_name={self.customer_name},"
            f"description={self.description},  status={self.status},"
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )
