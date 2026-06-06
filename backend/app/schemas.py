from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Client Schemas
class ClientBase(BaseModel):
    company_name: str
    contact_person: str
    phone: str
    email: str
    address: str
    balance: Optional[float] = 0.0

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int

    class Config:
        from_attributes = True

# Order Item Schemas
class OrderItemBase(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    total_price: float

    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    client_id: int
    payment_status: Optional[str] = "pending"
    delivery_status: Optional[str] = "pending"

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    id: int
    created_by_id: int
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]
    client: ClientResponse
    created_by: UserResponse

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    payment_status: Optional[str] = None
    delivery_status: Optional[str] = None

# Payment Schemas
class PaymentBase(BaseModel):
    order_id: int
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime

    class Config:
        from_attributes = True

# Delivery Schemas
class DeliveryBase(BaseModel):
    order_id: int
    carrier_name: str
    tracking_number: Optional[str] = None
    status: Optional[str] = "pending"
    estimated_delivery: Optional[datetime] = None

class DeliveryCreate(DeliveryBase):
    pass

class DeliveryResponse(DeliveryBase):
    id: int
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeliveryUpdate(BaseModel):
    status: str
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

# Task Schemas
class TaskBase(BaseModel):
    assigned_to_id: int
    client_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    assigned_to: UserResponse
    client: Optional[ClientResponse] = None

    class Config:
        from_attributes = True

class TaskStatusUpdate(BaseModel):
    status: str

# Communication Schemas
class CommunicationBase(BaseModel):
    client_id: int
    contact_type: str
    summary: str

class CommunicationCreate(CommunicationBase):
    pass

class CommunicationResponse(CommunicationBase):
    id: int
    user_id: int
    created_at: datetime
    user: UserResponse
    client: ClientResponse

    class Config:
        from_attributes = True

# Dashboard Stats Schema
class DashboardStats(BaseModel):
    total_sales: float
    pending_payments: float
    completed_orders: int
    pending_deliveries: int
    recent_orders: List[OrderResponse]
    sales_by_status: dict
