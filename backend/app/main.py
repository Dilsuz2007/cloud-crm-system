import logging
import time
import uuid
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import datetime

from .config import settings
from .database import get_db, engine, Base
from .models import User, Client, Order, OrderItem, Payment, Delivery, Task, Communication
from .schemas import (
    UserResponse, UserCreate, Token, ClientResponse, ClientCreate,
    OrderResponse, OrderCreate, OrderStatusUpdate, PaymentResponse, PaymentCreate,
    DeliveryResponse, DeliveryUpdate, TaskResponse, TaskCreate, TaskStatusUpdate,
    CommunicationResponse, CommunicationCreate, DashboardStats
)
from .auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, RoleChecker
)

# Ma'lumotlar bazasi jadvallarini avtomatik yaratish
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")
logger = logging.getLogger("texstyle.api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request_id=%s method=%s path=%s unhandled_error",
            request_id,
            request.method,
            request.url.path,
        )
        raise

    duration_ms = (time.perf_counter() - started_at) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.1f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
    logger.warning(
        "request_id=%s method=%s path=%s status=%s detail=%s",
        request_id,
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_id": request_id,
            "path": request.url.path,
        },
        headers={**(exc.headers or {}), "X-Request-ID": request_id},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
    errors = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        errors.append(f"{location}: {error['msg']}")
    detail = "; ".join(errors)
    logger.warning(
        "request_id=%s method=%s path=%s status=422 detail=%s",
        request_id,
        request.method,
        request.url.path,
        detail,
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": detail,
            "error_id": request_id,
            "path": request.url.path,
        },
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
    logger.exception(
        "request_id=%s method=%s path=%s status=500 detail=%s",
        request_id,
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ichki server xatosi yuz berdi",
            "error_id": request_id,
            "path": request.url.path,
        },
        headers={"X-Request-ID": request_id},
    )

# CORS sozlamalari (Frontend ulanishi uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Real ishlab chiqarishda cheklash kerak
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- AUTH ENDPOINTS -----------------

@app.post(f"{settings.API_V1_STR}/auth/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Foydalanuvchi faol emas")
        
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get(f"{settings.API_V1_STR}/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ----------------- USERS ENDPOINTS (ADMIN ONLY) -----------------

@app.get(
    f"{settings.API_V1_STR}/users", 
    response_model=List[UserResponse],
    dependencies=[Depends(RoleChecker(["admin"]))]
)
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post(
    f"{settings.API_V1_STR}/users", 
    response_model=UserResponse,
    dependencies=[Depends(RoleChecker(["admin"]))]
)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu email manziliga ega foydalanuvchi allaqachon mavjud")
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        password_hash=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=user_in.is_active
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.delete(
    f"{settings.API_V1_STR}/users/{{id}}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(["admin"]))]
)
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.email == "admin@texstyle.uz":
        raise HTTPException(status_code=400, detail="Tizim asosiy adminini o'chirib bo'lmaydi")
    db.delete(user)
    db.commit()
    return None


# ----------------- CLIENTS ENDPOINTS -----------------

@app.get(
    f"{settings.API_V1_STR}/clients", 
    response_model=List[ClientResponse],
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()

@app.post(
    f"{settings.API_V1_STR}/clients", 
    response_model=ClientResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def create_client(client_in: ClientCreate, db: Session = Depends(get_db)):
    client = Client(**client_in.dict())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@app.put(
    f"{settings.API_V1_STR}/clients/{{id}}", 
    response_model=ClientResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def update_client(id: int, client_in: ClientCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    
    for field, value in client_in.dict().items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    return client


# ----------------- ORDERS ENDPOINTS -----------------

@app.get(
    f"{settings.API_V1_STR}/orders", 
    response_model=List[OrderResponse],
    dependencies=[Depends(RoleChecker(["admin", "sales_manager", "warehouse_manager"]))]
)
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@app.get(
    f"{settings.API_V1_STR}/orders/{{id}}", 
    response_model=OrderResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager", "warehouse_manager"]))]
)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return order

@app.post(
    f"{settings.API_V1_STR}/orders", 
    response_model=OrderResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def create_order(
    order_in: OrderCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == order_in.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
        
    total_amount = 0.0
    order_items = []
    
    for item in order_in.items:
        item_total = item.quantity * item.unit_price
        total_amount += item_total
        order_items.append(
            OrderItem(
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item_total
            )
        )
        
    order = Order(
        client_id=order_in.client_id,
        created_by_id=current_user.id,
        total_amount=total_amount,
        payment_status=order_in.payment_status,
        delivery_status=order_in.delivery_status,
        items=order_items
    )
    
    # B2B Mijoz balansiga qarz yoziladi
    if order_in.payment_status != "paid":
        client.balance -= total_amount
        
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Avtomatik ravishda yetkazib berish (delivery) va boshlang'ich kuryer yaratish
    delivery = Delivery(
        order_id=order.id,
        carrier_name="BTS Express (Standart)",
        status="pending"
    )
    db.add(delivery)
    db.commit()
    
    return order

@app.put(
    f"{settings.API_V1_STR}/orders/{{id}}/status", 
    response_model=OrderResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager", "warehouse_manager"]))]
)
def update_order_status(id: int, status_in: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
        
    client = db.query(Client).filter(Client.id == order.client_id).first()
    
    # To'lov holati yangilanganda mijoz balansini to'g'irlash
    if status_in.payment_status and status_in.payment_status != order.payment_status:
        if status_in.payment_status == "paid" and order.payment_status != "paid":
            # Agar to'lansa, balansga qaytariladi
            client.balance += order.total_amount
        elif status_in.payment_status != "paid" and order.payment_status == "paid":
            client.balance -= order.total_amount
        order.payment_status = status_in.payment_status
        
    if status_in.delivery_status and status_in.delivery_status != order.delivery_status:
        order.delivery_status = status_in.delivery_status
        
        # Delivery status o'zgarganda deliveries jadvalini ham yangilaymiz
        delivery = db.query(Delivery).filter(Delivery.order_id == order.id).first()
        if delivery:
            delivery.status = status_in.delivery_status
            if status_in.delivery_status == "shipped":
                delivery.shipped_at = datetime.datetime.utcnow()
            elif status_in.delivery_status == "delivered":
                delivery.delivered_at = datetime.datetime.utcnow()
            db.add(delivery)
            
    db.commit()
    db.refresh(order)
    return order


# ----------------- PAYMENTS ENDPOINTS -----------------

@app.get(
    f"{settings.API_V1_STR}/payments", 
    response_model=List[PaymentResponse],
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()

@app.post(
    f"{settings.API_V1_STR}/payments", 
    response_model=PaymentResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def create_payment(payment_in: PaymentCreate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == payment_in.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
        
    payment = Payment(**payment_in.dict())
    db.add(payment)
    
    # To'lov summasiga asosan buyurtma statusini yangilash
    total_paid = sum([p.amount for p in order.payments]) + payment_in.amount
    client = db.query(Client).filter(Client.id == order.client_id).first()
    
    # Qarz balansini to'ldirish
    client.balance += payment_in.amount
    
    if total_paid >= order.total_amount:
        order.payment_status = "paid"
    else:
        order.payment_status = "partially_paid"
        
    db.commit()
    db.refresh(payment)
    return payment


# ----------------- DELIVERIES ENDPOINTS -----------------

@app.get(
    f"{settings.API_V1_STR}/deliveries", 
    response_model=List[DeliveryResponse],
    dependencies=[Depends(RoleChecker(["admin", "warehouse_manager"]))]
)
def get_deliveries(db: Session = Depends(get_db)):
    return db.query(Delivery).all()

@app.put(
    f"{settings.API_V1_STR}/deliveries/{{id}}", 
    response_model=DeliveryResponse,
    dependencies=[Depends(RoleChecker(["admin", "warehouse_manager"]))]
)
def update_delivery(id: int, delivery_in: DeliveryUpdate, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Kuryerlik ma'lumoti topilmadi")
        
    for field, value in delivery_in.dict(exclude_unset=True).items():
        setattr(delivery, field, value)
        
    # Shuningdek, bog'langan order statusini ham yangilaymiz
    order = db.query(Order).filter(Order.id == delivery.order_id).first()
    if order:
        order.delivery_status = delivery.status
        
    db.commit()
    db.refresh(delivery)
    return delivery


# ----------------- TASKS ENDPOINTS -----------------

@app.get(
    f"{settings.API_V1_STR}/tasks", 
    response_model=List[TaskResponse],
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Admin barcha vazifalarni, sales manager esa faqat o'ziga tegishlilarini ko'radi
    if current_user.role == "admin":
        return db.query(Task).all()
    return db.query(Task).filter(Task.assigned_to_id == current_user.id).all()

@app.post(
    f"{settings.API_V1_STR}/tasks", 
    response_model=TaskResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**task_in.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.put(
    f"{settings.API_V1_STR}/tasks/{{id}}", 
    response_model=TaskResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def update_task_status(id: int, status_in: TaskStatusUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")
    task.status = status_in.status
    db.commit()
    db.refresh(task)
    return task


# ----------------- COMMUNICATIONS ENDPOINTS -----------------

@app.get(
    f"{settings.API_V1_STR}/communications", 
    response_model=List[CommunicationResponse],
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def get_communications(db: Session = Depends(get_db)):
    return db.query(Communication).all()

@app.post(
    f"{settings.API_V1_STR}/communications", 
    response_model=CommunicationResponse,
    dependencies=[Depends(RoleChecker(["admin", "sales_manager"]))]
)
def create_communication(
    comm_in: CommunicationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comm = Communication(
        client_id=comm_in.client_id,
        user_id=current_user.id,
        contact_type=comm_in.contact_type,
        summary=comm_in.summary
    )
    db.add(comm)
    db.commit()
    db.refresh(comm)
    return comm


# ----------------- REPORTS ENDPOINTS -----------------

@app.get(
    f"{settings.API_V1_STR}/reports/dashboard", 
    response_model=DashboardStats,
    dependencies=[Depends(RoleChecker(["admin"]))]
)
def get_dashboard_reports(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    clients = db.query(Client).all()
    
    total_sales = sum([o.total_amount for o in orders if o.payment_status == "paid"])
    
    # Qarzlar summasi (balansi manfiy bo'lgan mijozlar balansi yig'indisi modullari)
    pending_payments = sum([abs(c.balance) for c in clients if c.balance < 0])
    
    completed_orders = len([o for o in orders if o.delivery_status == "delivered"])
    pending_deliveries = len([o for o in orders if o.delivery_status in ["pending", "processing", "shipped"]])
    
    # Grafik uchun status bo'yicha buyurtmalar soni
    sales_by_status = {
        "paid": len([o for o in orders if o.payment_status == "paid"]),
        "partially_paid": len([o for o in orders if o.payment_status == "partially_paid"]),
        "pending": len([o for o in orders if o.payment_status == "pending"])
    }
    
    # Oxirgi 5 ta buyurtma
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
    
    return {
        "total_sales": total_sales,
        "pending_payments": pending_payments,
        "completed_orders": completed_orders,
        "pending_deliveries": pending_deliveries,
        "recent_orders": recent_orders,
        "sales_by_status": sales_by_status
    }
