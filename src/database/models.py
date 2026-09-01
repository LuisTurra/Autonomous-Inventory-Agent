from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    ForeignKey,
    func,
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Product(Base):

    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True)

    product_category_name = Column(String(100))

    unit_price = Column(Numeric(12, 2))


class Inventory(Base):

    __tablename__ = "inventory"

    product_id = Column(String(50), ForeignKey("products.product_id"), primary_key=True)

    quantity = Column(Integer, nullable=False, default=0)

    reserved_quantity = Column(Integer, nullable=False, default=0)

    minimum_stock = Column(Integer, nullable=False, default=10)

    reorder_point = Column(Integer, nullable=False, default=20)

    reorder_quantity = Column(Integer, nullable=False, default=50)

    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class Supplier(Base):

    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, autoincrement=True)

    supplier_name = Column(String(150), nullable=False)

    lead_time_days = Column(Integer, nullable=False)

    reliability = Column(Numeric(5, 2), nullable=False)


class Sale(Base):

    __tablename__ = "sales"

    sale_id = Column(BigInteger, primary_key=True, autoincrement=True)

    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)

    quantity = Column(Integer, nullable=False)

    unit_price = Column(Numeric(12, 2), nullable=False)

    sale_timestamp = Column(DateTime, server_default=func.current_timestamp())


class Purchase(Base):

    __tablename__ = "purchases"

    purchase_id = Column(BigInteger, primary_key=True, autoincrement=True)

    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)

    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)

    quantity = Column(Integer, nullable=False)

    unit_cost = Column(Numeric(12, 2), nullable=False)

    status = Column(String(30), nullable=False, default="ORDERED")

    expected_delivery = Column(DateTime)

    delivered_at = Column(DateTime)


class InventoryMovement(Base):

    __tablename__ = "inventory_movements"

    movement_id = Column(BigInteger, primary_key=True, autoincrement=True)

    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)

    movement_type = Column(String(30), nullable=False)

    quantity = Column(Integer, nullable=False)

    reference_id = Column(BigInteger)

    created_at = Column(DateTime, server_default=func.current_timestamp())


class Event(Base):

    __tablename__ = "events"

    event_id = Column(BigInteger, primary_key=True, autoincrement=True)

    event_type = Column(String(50), nullable=False)

    product_id = Column(String(50))

    quantity = Column(Integer)

    event_data = Column(JSONB)

    event_timestamp = Column(DateTime, server_default=func.current_timestamp())


class Task(Base):

    __tablename__ = "tasks"

    task_id = Column(BigInteger, primary_key=True, autoincrement=True)

    task_type = Column(String(50), nullable=False)

    product_id = Column(String(50), ForeignKey("products.product_id"))

    quantity = Column(Integer)

    priority = Column(String(20))

    status = Column(String(30), default="PENDING")

    created_at = Column(DateTime, server_default=func.current_timestamp())

    completed_at = Column(DateTime)


class Decision(Base):

    __tablename__ = "decisions"

    decision_id = Column(BigInteger, primary_key=True, autoincrement=True)

    agent_name = Column(String(100), nullable=False)

    product_id = Column(String(50))

    decision_type = Column(String(100), nullable=False)

    reasoning = Column(Text)

    decision_data = Column(JSONB)

    created_at = Column(DateTime, server_default=func.current_timestamp())


class AgentMemory(Base):

    __tablename__ = "agent_memory"

    memory_id = Column(BigInteger, primary_key=True, autoincrement=True)

    agent_name = Column(String(100), nullable=False)

    memory_type = Column(String(50))

    context = Column(JSONB)

    created_at = Column(DateTime, server_default=func.current_timestamp())
