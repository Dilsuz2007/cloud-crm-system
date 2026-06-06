import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="sales_manager")  # admin, sales_manager, warehouse_manager
    is_active = Column(Boolean, default=True)

    # Relationships
    orders = relationship("Order", back_populates="created_by")
    tasks = relationship("Task", back_populates="assigned_to")
    communications = relationship("Communication", back_populates="user")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    contact_person = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    balance = Column(Float, default=0.0)

    # Relationships
    orders = relationship("Order", back_populates="client")
    tasks = relationship("Task", back_populates="client")
    communications = relationship("Communication", back_populates="client")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, default=0.0)
    payment_status = Column(String, default="pending")  # pending, partially_paid, paid
    delivery_status = Column(String, default="pending")  # pending, processing, shipped, delivered, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="orders")
    created_by = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    deliveries = relationship("Delivery", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # cash, bank_transfer, card, click, payme
    payment_date = Column(DateTime, default=datetime.datetime.utcnow)
    transaction_id = Column(String, unique=True, index=True, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="payments")


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    carrier_name = Column(String, nullable=False)  # e.g., Fargo, BTS, Custom Driver
    tracking_number = Column(String, unique=True, index=True, nullable=True)
    status = Column(String, default="pending")  # pending, processing, shipped, delivered
    estimated_delivery = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="deliveries")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, cancelled
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    assigned_to = relationship("User", back_populates="tasks")
    client = relationship("Client", back_populates="tasks")


class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_type = Column(String, nullable=False)  # phone, email, meeting, telegram
    summary = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="communications")
    user = relationship("User", back_populates="communications")
