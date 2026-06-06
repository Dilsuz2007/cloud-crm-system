import datetime
from .database import SessionLocal, engine, Base
from .models import User, Client, Order, OrderItem, Payment, Delivery, Task, Communication
from .auth import get_password_hash

def init_db():
    # Jadvallarni o'chirish va qayta yaratish
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Dastlabki foydalanuvchilarni yaratish...")
        # Foydalanuvchilar (Rollar bilan)
        users = [
            User(
                email="admin@texstyle.uz",
                password_hash=get_password_hash("admin123"),
                full_name="Akrom Aliyev (Tizim Admini)",
                role="admin",
                is_active=True
            ),
            User(
                email="sales@texstyle.uz",
                password_hash=get_password_hash("sales123"),
                full_name="Bobur Karimov (Sotuv Menejeri)",
                role="sales_manager",
                is_active=True
            ),
            User(
                email="warehouse@texstyle.uz",
                password_hash=get_password_hash("warehouse123"),
                full_name="Dilshod Umarov (Ombor Menejeri)",
                role="warehouse_manager",
                is_active=True
            )
        ]
        db.add_all(users)
        db.commit()
        
        # Olingan user ID larni saqlaymiz
        admin_user = db.query(User).filter(User.role == "admin").first()
        sales_user = db.query(User).filter(User.role == "sales_manager").first()
        
        print("Namunaviy mijozlarni (B2B) yaratish...")
        # Mijozlar
        clients = [
            Client(
                company_name="Elegant Style Boutique",
                contact_person="Zilola Karimova",
                phone="+998901234567",
                email="info@elegantstyle.uz",
                address="Toshkent sh., Chilonzor 4-daha, 12-uy",
                balance=-1250.0  # Namunaviy qarz balansi
            ),
            Client(
                company_name="MegaWear Wholesale LLC",
                contact_person="Rustam Qosimov",
                phone="+998935557788",
                email="rustam@megawear.uz",
                address="Samarqand sh., Registon ko'chasi, 89-uy",
                balance=0.0
            ),
            Client(
                company_name="Trendy Kids & Youth",
                contact_person="Madina Oripova",
                phone="+998971112233",
                email="trendy.kids@gmail.com",
                address="Farg'ona sh., Mustaqillik ko'chasi, 14-uy",
                balance=0.0
            )
        ]
        db.add_all(clients)
        db.commit()
        
        c1 = db.query(Client).filter(Client.company_name == "Elegant Style Boutique").first()
        c2 = db.query(Client).filter(Client.company_name == "MegaWear Wholesale LLC").first()
        
        print("Namunaviy buyurtmalarni yaratish...")
        # Buyurtma 1
        order1 = Order(
            client_id=c1.id,
            created_by_id=sales_user.id,
            total_amount=2500.0,
            payment_status="partially_paid",
            delivery_status="processing",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
        )
        order1.items = [
            OrderItem(product_name="Klassik Kostyum-Shim (Erkaklar)", quantity=20, unit_price=80.0, total_price=1600.0),
            OrderItem(product_name="Oq Paxtali Ko'ylak (Premium)", quantity=30, unit_price=30.0, total_price=900.0)
        ]
        
        # Buyurtma 2
        order2 = Order(
            client_id=c2.id,
            created_by_id=sales_user.id,
            total_amount=1500.0,
            payment_status="paid",
            delivery_status="delivered",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=10)
        )
        order2.items = [
            OrderItem(product_name="Kuzgi Kurtka (Ayollar uchun)", quantity=15, unit_price=100.0, total_price=1500.0)
        ]
        
        db.add_all([order1, order2])
        db.commit()
        
        print("Namunaviy kuryerlar va to'lovlarni yaratish...")
        # To'lovlar
        payment1 = Payment(
            order_id=order1.id,
            amount=1250.0,
            payment_method="bank_transfer",
            payment_date=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            transaction_id="TXN-9988776655"
        )
        payment2 = Payment(
            order_id=order2.id,
            amount=1500.0,
            payment_method="cash",
            payment_date=datetime.datetime.utcnow() - datetime.timedelta(days=10),
            transaction_id="TXN-5544332211"
        )
        db.add_all([payment1, payment2])
        
        # Yetkazib berish (Deliveries)
        delivery1 = Delivery(
            order_id=order1.id,
            carrier_name="BTS Express",
            tracking_number="BTS-TRK-7711",
            status="processing",
            estimated_delivery=datetime.datetime.utcnow() + datetime.timedelta(days=2)
        )
        delivery2 = Delivery(
            order_id=order2.id,
            carrier_name="Fargo",
            tracking_number="FRG-TRK-8822",
            status="delivered",
            shipped_at=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            delivered_at=datetime.datetime.utcnow() - datetime.timedelta(days=8)
        )
        db.add_all([delivery1, delivery2])
        db.commit()
        
        print("Namunaviy vazifalar (Tasks) yaratish...")
        # Vazifalar
        tasks = [
            Task(
                assigned_to_id=sales_user.id,
                client_id=c1.id,
                title="Elegant Style Boutique bilan qolgan to'lovni gaplashish",
                description="Mijoz 1250.0$ qarzini shu haftada yopishini va'da qilgan edi.",
                status="pending",
                due_date=datetime.datetime.utcnow() + datetime.timedelta(days=1)
            ),
            Task(
                assigned_to_id=sales_user.id,
                client_id=c2.id,
                title="Yangi yozgi kolleksiyani taklif qilish",
                description="E-mail orqali yangi katalog yuborilsin.",
                status="completed",
                due_date=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            )
        ]
        db.add_all(tasks)
        
        print("Namunaviy aloqalar tarixi yaratish...")
        # Aloqalar
        comms = [
            Communication(
                client_id=c1.id,
                user_id=sales_user.id,
                contact_type="phone",
                summary="Zilola bilan bog'lanildi. Kostyum-shimlar sifati juda yoqibdi, tez kunlarda qo'shimcha zakaz qilmoqchi."
            ),
            Communication(
                client_id=c2.id,
                user_id=sales_user.id,
                contact_type="meeting",
                summary="Rustam Qosimov bilan ofisimizda ko'rishildi. Yangi hamkorlik shartnomasi imzolanib, birinchi buyurtma to'lovi joyida to'landi."
            )
        ]
        db.add_all(comms)
        db.commit()
        
        print("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi!")
        
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
