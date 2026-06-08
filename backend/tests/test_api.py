import pytest

# ----------------- CLIENTS TESTS -----------------

def test_create_client_success(client, sales_headers):
    client_data = {
        "company_name": "Test Company",
        "contact_person": "John Doe",
        "phone": "+998901234567",
        "email": "john@test.com",
        "address": "Tashkent",
        "balance": 0.0
    }
    response = client.post("/api/v1/clients", json=client_data, headers=sales_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["company_name"] == "Test Company"
    assert "id" in json_data

def test_create_client_forbidden_for_warehouse(client, warehouse_headers):
    client_data = {
        "company_name": "Test Company 2",
        "contact_person": "Jane Doe",
        "phone": "+998907654321",
        "email": "jane@test.com",
        "address": "Samarkand",
        "balance": 0.0
    }
    response = client.post("/api/v1/clients", json=client_data, headers=warehouse_headers)
    assert response.status_code == 403

def test_get_clients(client, sales_headers):
    response = client.get("/api/v1/clients", headers=sales_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_client(client, sales_headers, db_session):
    from backend.app.models import Client as DBClient
    db_client = DBClient(
        company_name="Old Name",
        contact_person="Old Contact",
        phone="123",
        email="old@email.com",
        address="Old Address",
        balance=100.0
    )
    db_session.add(db_client)
    db_session.commit()
    db_session.refresh(db_client)

    update_data = {
        "company_name": "New Name",
        "contact_person": "New Contact",
        "phone": "321",
        "email": "new@email.com",
        "address": "New Address",
        "balance": 150.0
    }
    response = client.put(f"/api/v1/clients/{db_client.id}", json=update_data, headers=sales_headers)
    assert response.status_code == 200
    assert response.json()["company_name"] == "New Name"
    assert response.json()["balance"] == 150.0


# ----------------- ORDERS TESTS -----------------

def test_create_order_adjusts_client_balance(client, sales_headers, db_session):
    from backend.app.models import Client as DBClient
    db_client = DBClient(
        company_name="Order Client",
        contact_person="Person",
        phone="456",
        email="order@client.com",
        address="Address",
        balance=1000.0
    )
    db_session.add(db_client)
    db_session.commit()
    db_session.refresh(db_client)

    order_data = {
        "client_id": db_client.id,
        "payment_status": "pending",
        "delivery_status": "pending",
        "items": [
            {"product_name": "Shirt", "quantity": 5, "unit_price": 20.0},
            {"product_name": "Pants", "quantity": 2, "unit_price": 50.0}
        ]
    }
    response = client.post("/api/v1/orders", json=order_data, headers=sales_headers)
    assert response.status_code == 200
    order_json = response.json()
    assert order_json["total_amount"] == 200.0 # 5*20 + 2*50 = 200
    
    # Since payment_status is 'pending' (not 'paid'), the client balance should decrease by 200.0
    db_session.refresh(db_client)
    assert db_client.balance == 800.0

def test_update_order_status_updates_balance(client, sales_headers, db_session):
    from backend.app.models import Client as DBClient
    from backend.app.models import Order as DBOrder
    db_client = DBClient(
        company_name="Order Client 2",
        contact_person="Person 2",
        phone="457",
        email="order2@client.com",
        address="Address 2",
        balance=800.0 # Balance after order of 200.0
    )
    db_session.add(db_client)
    db_session.commit()
    
    db_order = DBOrder(
        client_id=db_client.id,
        created_by_id=1, # Mock ID
        total_amount=200.0,
        payment_status="pending",
        delivery_status="pending"
    )
    db_session.add(db_order)
    db_session.commit()
    db_session.refresh(db_order)

    # Change order status to paid, this should add order amount back to client balance (repaying the debt)
    status_data = {"payment_status": "paid", "delivery_status": "processing"}
    response = client.put(f"/api/v1/orders/{db_order.id}/status", json=status_data, headers=sales_headers)
    assert response.status_code == 200
    assert response.json()["payment_status"] == "paid"
    
    db_session.refresh(db_client)
    assert db_client.balance == 1000.0


# ----------------- PAYMENTS TESTS -----------------

def test_create_payment_updates_order_and_balance(client, sales_headers, db_session):
    from backend.app.models import Client as DBClient
    from backend.app.models import Order as DBOrder
    db_client = DBClient(
        company_name="Payment Client",
        contact_person="Person",
        phone="789",
        email="pay@client.com",
        address="Address",
        balance=300.0 # Initial balance
    )
    db_session.add(db_client)
    db_session.commit()

    db_order = DBOrder(
        client_id=db_client.id,
        created_by_id=1,
        total_amount=500.0,
        payment_status="pending",
        delivery_status="pending"
    )
    db_session.add(db_order)
    db_session.commit()
    db_session.refresh(db_order)

    # Make a partial payment of 200.0
    payment_data = {
        "order_id": db_order.id,
        "amount": 200.0,
        "payment_method": "cash",
        "transaction_id": "TXN-TEST-123"
    }
    response = client.post("/api/v1/payments", json=payment_data, headers=sales_headers)
    assert response.status_code == 200
    
    db_session.refresh(db_order)
    db_session.refresh(db_client)
    # Order should be partially paid
    assert db_order.payment_status == "partially_paid"
    # Client balance should increase by 200.0
    assert db_client.balance == 500.0

    # Make another payment of 300.0 to pay off the rest
    payment_data_2 = {
        "order_id": db_order.id,
        "amount": 300.0,
        "payment_method": "bank_transfer",
        "transaction_id": "TXN-TEST-456"
    }
    response2 = client.post("/api/v1/payments", json=payment_data_2, headers=sales_headers)
    assert response2.status_code == 200
    
    db_session.refresh(db_order)
    db_session.refresh(db_client)
    # Order should now be fully paid
    assert db_order.payment_status == "paid"
    # Client balance should increase by 300.0
    assert db_client.balance == 800.0


# ----------------- DELIVERIES TESTS -----------------

def test_get_deliveries_by_warehouse(client, warehouse_headers):
    response = client.get("/api/v1/deliveries", headers=warehouse_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_deliveries_forbidden_for_sales(client, sales_headers):
    response = client.get("/api/v1/deliveries", headers=sales_headers)
    assert response.status_code == 403


# ----------------- REPORTS TESTS -----------------

def test_dashboard_stats_admin_only(client, admin_headers, sales_headers):
    # Admin should access dashboard report
    response = client.get("/api/v1/reports/dashboard", headers=admin_headers)
    assert response.status_code == 200
    assert "total_sales" in response.json()
    assert "pending_payments" in response.json()

    # Sales manager should get forbidden
    response2 = client.get("/api/v1/reports/dashboard", headers=sales_headers)
    assert response2.status_code == 403
