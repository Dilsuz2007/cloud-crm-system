import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add workspace and backend paths to sys.path to ensure absolute imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import User
from backend.app.auth import get_password_hash, create_access_token

TEST_DATABASE_URL = "sqlite:///./test_texstyle_crm.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if os.path.exists("./test_texstyle_crm.db"):
        try:
            os.remove("./test_texstyle_crm.db")
        except Exception:
            pass
            
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    
    if os.path.exists("./test_texstyle_crm.db"):
        try:
            os.remove("./test_texstyle_crm.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_users(db_session):
    users = [
        User(
            email="test_admin@texstyle.uz",
            password_hash=get_password_hash("admin123"),
            full_name="Test Admin",
            role="admin",
            is_active=True
        ),
        User(
            email="test_sales@texstyle.uz",
            password_hash=get_password_hash("sales123"),
            full_name="Test Sales",
            role="sales_manager",
            is_active=True
        ),
        User(
            email="test_warehouse@texstyle.uz",
            password_hash=get_password_hash("warehouse123"),
            full_name="Test Warehouse",
            role="warehouse_manager",
            is_active=True
        )
    ]
    db_session.add_all(users)
    db_session.commit()
    
    return {
        "admin": db_session.query(User).filter(User.role == "admin").first(),
        "sales": db_session.query(User).filter(User.role == "sales_manager").first(),
        "warehouse": db_session.query(User).filter(User.role == "warehouse_manager").first()
    }

@pytest.fixture
def admin_headers(test_users):
    token = create_access_token(data={"sub": test_users["admin"].email, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sales_headers(test_users):
    token = create_access_token(data={"sub": test_users["sales"].email, "role": "sales_manager"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def warehouse_headers(test_users):
    token = create_access_token(data={"sub": test_users["warehouse"].email, "role": "warehouse_manager"})
    return {"Authorization": f"Bearer {token}"}
