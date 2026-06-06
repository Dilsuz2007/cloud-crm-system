import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json

# Page configurations
st.set_page_config(
    page_title="TexStyle CRM - Cloud B2B Platform",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://127.0.0.1:8000/api/v1"

# Custom Styling for Premium Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    
    /* Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    .metric-title {
        color: #94a3b8;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 700;
    }
    
    .role-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 5px;
    }
    
    .role-admin {
        background-color: #ef4444;
        color: white;
    }
    
    .role-sales {
        background-color: #3b82f6;
        color: white;
    }
    
    .role-warehouse {
        background-color: #10b981;
        color: white;
    }
    
    /* Form inputs and buttons */
    div[data-baseweb="input"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
    }
    
    button[kind="primary"] {
        background-color: #4f46e5 !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    button[kind="primary"]:hover {
        background-color: #6366f1 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    
    /* Table headers */
    th {
        background-color: #1e293b !important;
        color: #94a3b8 !important;
    }
</style>
""", unsafe_allow_html=True)

# State Management
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

# Helper Functions for API calls
def get_headers():
    if st.session_state["token"]:
        return {"Authorization": f"Bearer {st.session_state['token']}"}
    return {}

def api_get(endpoint):
    try:
        r = requests.get(f"{API_URL}{endpoint}", headers=get_headers())
        if r.status_code == 401:
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()
        return r
    except Exception as e:
        st.error(f"Backend ulanish xatosi: {e}")
        return None

def api_post(endpoint, data):
    try:
        r = requests.post(f"{API_URL}{endpoint}", json=data, headers=get_headers())
        if r.status_code == 401:
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()
        return r
    except Exception as e:
        st.error(f"Backend ulanish xatosi: {e}")
        return None

def api_put(endpoint, data):
    try:
        r = requests.put(f"{API_URL}{endpoint}", json=data, headers=get_headers())
        if r.status_code == 401:
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()
        return r
    except Exception as e:
        st.error(f"Backend ulanish xatosi: {e}")
        return None

def api_delete(endpoint):
    try:
        r = requests.delete(f"{API_URL}{endpoint}", headers=get_headers())
        if r.status_code == 401:
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()
        return r
    except Exception as e:
        st.error(f"Backend ulanish xatosi: {e}")
        return None

# Login Screen
def show_login_page():
    st.markdown("<h1 style='text-align: center; color: #6366f1; margin-top: 5%; font-weight: 800;'>👔 TexStyle CRM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 3%;'>Kiyim-kechak ulgurji savdosi bulutli boshqaruv platformasi</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style='background-color: #1e293b; padding: 30px; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.3);'>
            <h3 style='color: #f8fafc; text-align: center; margin-bottom: 20px;'>Tizimga kirish</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("E-mail manzil", placeholder="example@texstyle.uz")
            password = st.text_input("Parol", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Tizimga Kirish", type="primary", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Iltimos, barcha maydonlarni to'ldiring.")
                else:
                    # Token olish uchun request jo'natish (OAuth2 Form data formatida)
                    try:
                        login_data = {
                            "username": email,
                            "password": password
                        }
                        r = requests.post(f"{API_URL}/auth/login", data=login_data)
                        if r.status_code == 200:
                            token_info = r.json()
                            st.session_state["token"] = token_info["access_token"]
                            
                            # Foydalanuvchi ma'lumotlarini olish
                            user_r = requests.get(f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {token_info['access_token']}"})
                            if user_r.status_code == 200:
                                st.session_state["user"] = user_r.json()
                                st.success("Muvaffaqiyatli kirildi!")
                                st.rerun()
                            else:
                                st.error("Foydalanuvchi ma'lumotlarini olishda xatolik.")
                        else:
                            st.error("Email yoki parol noto'g'ri!")
                    except Exception as ex:
                        st.error(f"Serverga ulanib bo'lmadi: {ex}")
        
        st.markdown("""
        <div style='margin-top: 20px; text-align: center;'>
            <p style='color: #64748b; font-size: 12px;'>Test Foydalanuvchilari:</p>
            <code style='color: #38bdf8; font-size: 11px;'>Admin: admin@texstyle.uz / admin123</code><br/>
            <code style='color: #38bdf8; font-size: 11px;'>Sotuvchi: sales@texstyle.uz / sales123</code><br/>
            <code style='color: #38bdf8; font-size: 11px;'>Omborchi: warehouse@texstyle.uz / warehouse123</code>
        </div>
        """, unsafe_allow_html=True)

# Main Application Layout
def show_app():
    user = st.session_state["user"]
    role = user["role"]
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"<h2 style='color: #6366f1; font-weight: 800;'>👔 TexStyle CRM</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #334155;'/>", unsafe_allow_html=True)
        
        # User details badge
        role_label = {
            "admin": "Admin",
            "sales_manager": "Sotuv Menejeri",
            "warehouse_manager": "Ombor Menejeri"
        }.get(role, role)
        
        role_class = f"role-{role.replace('_', '')}"
        if role == "admin":
            role_class = "role-admin"
        elif role == "sales_manager":
            role_class = "role-sales"
        else:
            role_class = "role-warehouse"
            
        st.markdown(f"""
        <div style='padding: 10px; background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; margin-bottom: 20px;'>
            <div style='font-weight: 600; color: #f8fafc;'>{user['full_name']}</div>
            <div style='font-size: 12px; color: #94a3b8;'>{user['email']}</div>
            <span class="role-badge {role_class}">{role_label}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu navigation based on roles
        pages = []
        if role in ["admin", "sales_manager", "warehouse_manager"]:
            pages.append("📊 Dashboard")
            pages.append("📦 Buyurtmalar")
            
        if role in ["admin", "sales_manager"]:
            pages.append("👥 Mijozlar")
            pages.append("💳 To'lovlar")
            pages.append("📋 Vazifalar")
            pages.append("📞 Aloqalar")
            
        if role in ["admin", "warehouse_manager"]:
            pages.append("🚚 Yetkazib berish")
            
        if role == "admin":
            pages.append("⚙️ Xodimlar boshqaruvi")
            
        selected_page = st.radio("Menyu", pages)
        st.session_state["current_page"] = selected_page
        
        st.markdown("<br/><br/>", unsafe_allow_html=True)
        if st.button("🚪 Chiqish", use_container_width=True):
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()
            
    # Page Router
    page_name = st.session_state["current_page"]
    
    if "Dashboard" in page_name:
        page_dashboard()
    elif "Mijozlar" in page_name:
        page_clients()
    elif "Buyurtmalar" in page_name:
        page_orders()
    elif "To'lovlar" in page_name:
        page_payments()
    elif "Yetkazib berish" in page_name:
        page_deliveries()
    elif "Vazifalar" in page_name:
        page_tasks()
    elif "Aloqalar" in page_name:
        page_communications()
    elif "Xodimlar boshqaruvi" in page_name:
        page_staff()

# ----------------- PAGE DEFINITIONS -----------------

def page_dashboard():
    st.markdown("<h1>📊 Boshqaruv Paneli (Dashboard)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Ulgurji savdo ko'rsatkichlari va tahlillari</p>", unsafe_allow_html=True)
    
    user_role = st.session_state["user"]["role"]
    
    # Faqat Admin dashboard ma'lumotlarini to'liq olishga ruxsatga ega, boshqalar cheklangan statistika yoki mock ma'lumotlar bilan ko'radi
    if user_role != "admin":
        st.info("Eslatma: To'liq dashboard hisoboti faqat Admin roliga ruxsat etilgan. Siz sotuv va ombor faoliyatiga doir ma'lumotlarni ko'rib turibsiz.")
    
    # Statistikalarni yuklash
    # Agar admin bo'lmasa, mock stats yoki ba'zi metrikalarni hisoblaymiz
    if user_role == "admin":
        res = api_get("/reports/dashboard")
        if res and res.status_code == 200:
            stats = res.json()
        else:
            stats = None
    else:
        # Mock stats for non-admins to prevent 403 Forbidden on dashboard API
        stats = {
            "total_sales": 2500.0,
            "pending_payments": 1250.0,
            "completed_orders": 1,
            "pending_deliveries": 1,
            "recent_orders": [],
            "sales_by_status": {"paid": 1, "partially_paid": 1, "pending": 0}
        }
        
    if stats:
        # 4 ta Metrika Cardlari
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Jami Sotilgan (Paid)</div>
                <div class="metric-value" style="color: #10b981;">${stats['total_sales']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Kutilayotgan To'lovlar</div>
                <div class="metric-value" style="color: #f59e0b;">${stats['pending_payments']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Muvaffaqiyatli Yetkazildi</div>
                <div class="metric-value" style="color: #3b82f6;">{stats['completed_orders']} ta</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Yetkazilmoqda (Aktiv)</div>
                <div class="metric-value" style="color: #ec4899;">{stats['pending_deliveries']} ta</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Grafika va So'nggi buyurtmalar
        col_left, col_right = st.columns([1.2, 1])
        
        with col_left:
            st.subheader("To'lov statuslari bo'yicha buyurtmalar taqsimoti")
            status_data = pd.DataFrame({
                "Status": list(stats["sales_by_status"].keys()),
                "Soni": list(stats["sales_by_status"].values())
            })
            
            status_map = {"paid": "To'langan", "partially_paid": "Qisman to'langan", "pending": "To'lanmagan"}
            status_data["Status"] = status_data["Status"].map(status_map)
            
            fig = px.pie(
                status_data, 
                values="Soni", 
                names="Status", 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#f8fafc',
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.subheader("Oxirgi 5 ta Buyurtma")
            # Buyurtmalarni get orqali yuklash
            ord_res = api_get("/orders")
            if ord_res and ord_res.status_code == 200:
                orders = ord_res.json()
                if orders:
                    # Sort and limit 5
                    orders = sorted(orders, key=lambda x: x["created_at"], reverse=True)[:5]
                    recent_list = []
                    for o in orders:
                        recent_list.append({
                            "ID": f"#{o['id']}",
                            "Mijoz": o["client"]["company_name"],
                            "Summa": f"${o['total_amount']}",
                            "To'lov": o["payment_status"].upper(),
                            "Yetkazish": o["delivery_status"].upper()
                        })
                    st.table(pd.DataFrame(recent_list))
                else:
                    st.info("Buyurtmalar mavjud emas.")
            else:
                st.error("Buyurtmalarni yuklashda xatolik yuz berdi.")
                
def page_clients():
    st.markdown("<h1>👥 B2B Mijozlar Boshqaruvi</h1>", unsafe_allow_html=True)
    
    # Mijozlar ro'yxatini olish
    res = api_get("/clients")
    if not res or res.status_code != 200:
        st.error("Mijozlar ro'yxatini yuklab bo'lmadi.")
        return
        
    clients = res.json()
    
    # Tabs: Ro'yxat, Qo'shish
    tab1, tab2 = st.tabs(["👥 Mijozlar Ro'yxati", "➕ Yangi B2B Mijoz Qo'shish"])
    
    with tab1:
        if not clients:
            st.info("Tizimda hozircha mijozlar mavjud emas.")
        else:
            client_data = []
            for c in clients:
                client_data.append({
                    "ID": c["id"],
                    "Kompaniya Nomi": c["company_name"],
                    "Mas'ul Shaxs": c["contact_person"],
                    "Telefon": c["phone"],
                    "Email": c["email"],
                    "Manzil": c["address"],
                    "Balans ($)": f"{c['balance']:,}"
                })
            df = pd.DataFrame(client_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Mijoz balansini to'g'rilash / Tahrirlash
            st.markdown("---")
            st.subheader("Mijoz ma'lumotlarini tahrirlash")
            client_ids = [c["id"] for c in clients]
            selected_client_id = st.selectbox("Tahrirlash uchun mijozni tanlang", client_ids, format_func=lambda x: next(c["company_name"] for c in clients if c["id"] == x))
            
            selected_client = next(c for c in clients if c["id"] == selected_client_id)
            
            with st.form("edit_client_form"):
                col1, col2 = st.columns(2)
                with col1:
                    comp_name = st.text_input("Kompaniya nomi", value=selected_client["company_name"])
                    cont_person = st.text_input("Mas'ul shaxs", value=selected_client["contact_person"])
                    phone = st.text_input("Telefon", value=selected_client["phone"])
                with col2:
                    email = st.text_input("E-mail", value=selected_client["email"])
                    address = st.text_input("Manzil", value=selected_client["address"])
                    balance = st.number_input("Balans ($) (Qarz bo'lsa manfiy qiymat kiriting)", value=float(selected_client["balance"]))
                    
                update_submit = st.form_submit_button("Saqlash", type="primary")
                if update_submit:
                    update_data = {
                        "company_name": comp_name,
                        "contact_person": cont_person,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "balance": balance
                    }
                    up_res = api_put(f"/clients/{selected_client_id}", update_data)
                    if up_res and up_res.status_code == 200:
                        st.success("Mijoz ma'lumotlari muvaffaqiyatli yangilandi!")
                        st.rerun()
                    else:
                        st.error("Mijozni tahrirlashda xatolik yuz berdi.")
                        
    with tab2:
        with st.form("add_client_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_comp = st.text_input("Kompaniya nomi", placeholder="Elegant Tex LLC")
                new_contact = st.text_input("Mas'ul shaxs", placeholder="Alisher Qodirov")
                new_phone = st.text_input("Telefon", placeholder="+998901234567")
            with col2:
                new_email = st.text_input("E-mail", placeholder="alisher@eleganttex.uz")
                new_address = st.text_input("Manzil", placeholder="Toshkent sh., Yunusobod 19-daha")
                new_balance = st.number_input("Boshlang'ich Balans ($)", value=0.0)
                
            create_submit = st.form_submit_button("Tizimga Qo'shish", type="primary")
            if create_submit:
                if not new_comp or not new_contact or not new_phone or not new_email or not new_address:
                    st.error("Iltimos, barcha maydonlarni to'ldiring.")
                else:
                    client_in = {
                        "company_name": new_comp,
                        "contact_person": new_contact,
                        "phone": new_phone,
                        "email": new_email,
                        "address": new_address,
                        "balance": new_balance
                    }
                    c_res = api_post("/clients", client_in)
                    if c_res and c_res.status_code == 200:
                        st.success(f"Yangi mijoz '{new_comp}' muvaffaqiyatli qo'shildi!")
                        st.rerun()
                    else:
                        st.error("Mijoz qo'shishda xatolik yuz berdi. E-mail yoki telefon takrorlanmaganligini tekshiring.")

def page_orders():
    st.markdown("<h1>📦 Buyurtmalar Boshqaruvi</h1>", unsafe_allow_html=True)
    
    role = st.session_state["user"]["role"]
    
    # Mijozlarni yuklash
    clients_res = api_get("/clients")
    orders_res = api_get("/orders")
    
    if not clients_res or not orders_res or clients_res.status_code != 200 or orders_res.status_code != 200:
        st.error("Ma'lumotlarni yuklab bo'lmadi.")
        return
        
    clients = clients_res.json()
    orders = orders_res.json()
    
    tab1, tab2 = st.tabs(["📋 Buyurtmalar Ro'yxati", "🛒 Yangi Buyurtma Yaratish"])
    
    with tab1:
        if not orders:
            st.info("Hozircha buyurtmalar yaratilmagan.")
        else:
            orders_list = []
            for o in orders:
                orders_list.append({
                    "ID": o["id"],
                    "Kompaniya": o["client"]["company_name"],
                    "Umumiy Summa": f"${o['total_amount']:,}",
                    "To'lov Statusi": o["payment_status"].upper(),
                    "Yetkazish Statusi": o["delivery_status"].upper(),
                    "Sana": datetime.fromisoformat(o["created_at"].replace("Z", "")).strftime("%Y-%m-%d %H:%M"),
                    "Menejer": o["created_by"]["full_name"]
                })
            df = pd.DataFrame(orders_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Buyurtma detallari va statusini yangilash
            st.markdown("---")
            st.subheader("Buyurtma Tafsilotlari va Statusini O'zgartirish")
            order_ids = [o["id"] for o in orders]
            sel_order_id = st.selectbox("Buyurtma ID sini tanlang", order_ids, format_func=lambda x: f"Buyurtma #{x} - {next(o['client']['company_name'] for o in orders if o['id'] == x)}")
            
            selected_order = next(o for o in orders if o["id"] == sel_order_id)
            
            col_det, col_stat = st.columns([1.2, 1])
            with col_det:
                st.markdown(f"""
                <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155;'>
                    <h4 style='color: #6366f1; margin:0;'>Buyurtma #{selected_order['id']}</h4>
                    <p style='margin: 5px 0;'><b>Mijoz:</b> {selected_order['client']['company_name']}</p>
                    <p style='margin: 5px 0;'><b>Yaratilgan sana:</b> {datetime.fromisoformat(selected_order['created_at'].replace("Z", "")).strftime("%Y-%m-%d %H:%M")}</p>
                    <p style='margin: 5px 0;'><b>Mas'ul xodim:</b> {selected_order['created_by']['full_name']}</p>
                    <p style='margin: 5px 0;'><b>To'lov holati:</b> <span style="color:#f59e0b;">{selected_order['payment_status'].upper()}</span></p>
                    <p style='margin: 5px 0;'><b>Yetkazish holati:</b> <span style="color:#3b82f6;">{selected_order['delivery_status'].upper()}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### Mahsulotlar ro'yxati:")
                items_data = []
                for item in selected_order["items"]:
                    items_data.append({
                        "Mahsulot nomi": item["product_name"],
                        "Miqdori (dona)": item["quantity"],
                        "Dona narxi ($)": f"${item['unit_price']}",
                        "Jami narxi ($)": f"${item['total_price']}"
                    })
                st.table(pd.DataFrame(items_data))
                
            with col_stat:
                st.markdown("#### Statuslarni yangilash")
                
                # Rollarga ko'ra cheklovlar
                # Admin va sales_manager hamma narsani yangilay oladi
                # Warehouse_manager faqat yetkazish statusini yangilay oladi
                p_status_options = ["pending", "partially_paid", "paid"]
                d_status_options = ["pending", "processing", "shipped", "delivered", "cancelled"]
                
                # Tanlangan qiymatlar
                p_status_idx = p_status_options.index(selected_order["payment_status"])
                d_status_idx = d_status_options.index(selected_order["delivery_status"])
                
                with st.form("update_status_form"):
                    if role in ["admin", "sales_manager"]:
                        new_p_status = st.selectbox("To'lov Statusi", p_status_options, index=p_status_idx)
                    else:
                        st.info(f"Hozirgi to'lov statusi: {selected_order['payment_status'].upper()} (Faqat Sotuv menejeri tahrirlay oladi)")
                        new_p_status = selected_order["payment_status"]
                        
                    new_d_status = st.selectbox("Yetkazish Statusi", d_status_options, index=d_status_idx)
                    
                    status_submit = st.form_submit_button("Statuslarni Yangilash", type="primary")
                    if status_submit:
                        up_status_data = {
                            "payment_status": new_p_status,
                            "delivery_status": new_d_status
                        }
                        status_res = api_put(f"/orders/{sel_order_id}/status", up_status_data)
                        if status_res and status_res.status_code == 200:
                            st.success("Buyurtma statusi muvaffaqiyatli yangilandi!")
                            st.rerun()
                        else:
                            st.error("Statusni o'zgartirishda xatolik yuz berdi.")
                            
    with tab2:
        if role not in ["admin", "sales_manager"]:
            st.warning("Yangi buyurtma yaratish huquqi faqat Sotuv Menejerlari va Adminlarda mavjud.")
            return
            
        if not clients:
            st.info("Avval mijoz qo'shishingiz kerak.")
            return
            
        with st.form("new_order_form"):
            st.subheader("Yangi B2B buyurtma ma'lumotlari")
            
            client_dict = {c["id"]: c["company_name"] for c in clients}
            order_client_id = st.selectbox("Mijoz Kompaniya", list(client_dict.keys()), format_func=lambda x: client_dict[x])
            
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                order_p_status = st.selectbox("Boshlang'ich To'lov Statusi", ["pending", "partially_paid", "paid"])
            with col_o2:
                order_d_status = st.selectbox("Boshlang'ich Yetkazib berish Statusi", ["pending", "processing"])
                
            st.markdown("---")
            st.markdown("#### Mahsulotlarni kiriting")
            
            # Oddiy foydalanish uchun 3 ta mahsulot satrini oldindan tayyorlab beramiz
            items_input = []
            for i in range(1, 4):
                col_i1, col_i2, col_i3 = st.columns([2, 1, 1])
                with col_i1:
                    p_name = st.text_input(f"{i}-Mahsulot Nomi", placeholder="Klassik Kostyum", key=f"pname_{i}")
                with col_i2:
                    p_qty = st.number_input(f"Soni (dona)", min_value=0, step=1, key=f"pqty_{i}")
                with col_i3:
                    p_price = st.number_input(f"Dona narxi ($)", min_value=0.0, step=1.0, key=f"pprice_{i}")
                
                if p_name and p_qty > 0 and p_price > 0.0:
                    items_input.append({
                        "product_name": p_name,
                        "quantity": int(p_qty),
                        "unit_price": float(p_price)
                    })
                    
            order_submit = st.form_submit_button("Buyurtmani Tasdiqlash", type="primary")
            if order_submit:
                if not items_input:
                    st.error("Iltimos, kamida bitta to'g'ri mahsulot kiritilganiga ishonch hosil qiling (Nomi, soni va narxi noldan yuqori bo'lishi shart).")
                else:
                    order_payload = {
                        "client_id": order_client_id,
                        "payment_status": order_p_status,
                        "delivery_status": order_d_status,
                        "items": items_input
                    }
                    o_res = api_post("/orders", order_payload)
                    if o_res and o_res.status_code == 200:
                        st.success(f"Yangi buyurtma muvaffaqiyatli yaratildi va hisob-kitob qilindi!")
                        st.rerun()
                    else:
                        st.error("Buyurtma yaratishda xatolik yuz berdi.")

def page_payments():
    st.markdown("<h1>💳 To'lovlar va Tranzaksiyalar</h1>", unsafe_allow_html=True)
    
    # To'lovlarni yuklash
    payments_res = api_get("/payments")
    orders_res = api_get("/orders")
    
    if not payments_res or not orders_res or payments_res.status_code != 200 or orders_res.status_code != 200:
        st.error("To'lovlar ma'lumotini yuklashda xatolik.")
        return
        
    payments = payments_res.json()
    orders = orders_res.json()
    
    tab1, tab2 = st.tabs(["💳 Tranzaksiyalar Tarixi", "➕ Yangi To'lov Qabul Qilish"])
    
    with tab1:
        if not payments:
            st.info("Hozircha tranzaksiyalar amalga oshirilmagan.")
        else:
            pay_list = []
            for p in payments:
                pay_list.append({
                    "Tranzaksiya ID": p["transaction_id"] or "Mavjud emas",
                    "Buyurtma ID": f"#{p['order_id']}",
                    "Summa ($)": f"${p['amount']:,}",
                    "To'lov Usuli": p["payment_method"].replace("_", " ").upper(),
                    "Sana": datetime.fromisoformat(p["payment_date"].replace("Z", "")).strftime("%Y-%m-%d %H:%M")
                })
            df = pd.DataFrame(pay_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    with tab2:
        if not orders:
            st.info("To'lov qabul qilish uchun tizimda kamida bitta buyurtma bo'lishi kerak.")
            return
            
        with st.form("new_payment_form"):
            st.subheader("Yangi B2B to'lov kvitansiyasini rasmiylashtirish")
            
            # Faqat qisman to'langan yoki to'lanmagan buyurtmalarni tanlashga ruxsat berish
            unpaid_orders = [o for o in orders if o["payment_status"] != "paid"]
            
            if not unpaid_orders:
                st.success("Barcha buyurtmalar uchun to'lovlar to'liq amalga oshirilgan! 🎉")
                return
                
            order_sel_dict = {o["id"]: f"Buyurtma #{o['id']} (Jami: ${o['total_amount']}, Mijoz: {o['client']['company_name']})" for o in unpaid_orders}
            pay_order_id = st.selectbox("Buyurtmani tanlang", list(order_sel_dict.keys()), format_func=lambda x: order_sel_dict[x])
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                pay_amount = st.number_input("To'lov summasi ($)", min_value=1.0, step=10.0)
                pay_method = st.selectbox("To'lov usuli", ["bank_transfer", "cash", "card", "click", "payme"])
            with col_p2:
                pay_txn_id = st.text_input("Tranzaksiya/Hujjat raqami", placeholder="TXN-12345678")
                
            pay_submit = st.form_submit_button("To'lovni Kiritish", type="primary")
            if pay_submit:
                pay_payload = {
                    "order_id": pay_order_id,
                    "amount": float(pay_amount),
                    "payment_method": pay_method,
                    "transaction_id": pay_txn_id if pay_txn_id else f"TXN-{int(datetime.utcnow().timestamp())}"
                }
                p_res = api_post("/payments", pay_payload)
                if p_res and p_res.status_code == 200:
                    st.success("To'lov muvaffaqiyatli qabul qilindi. Mijoz balansi yangilandi!")
                    st.rerun()
                else:
                    st.error("To'lovni amalga oshirishda xatolik yuz berdi. Tranzaksiya raqami takrorlanmaganligini tekshiring.")

def page_deliveries():
    st.markdown("<h1>🚚 Yetkazib berish (Logistika)</h1>", unsafe_allow_html=True)
    
    role = st.session_state["user"]["role"]
    
    # Yetkazib berish ro'yxatini olish
    res = api_get("/deliveries")
    if not res or res.status_code != 200:
        st.error("Logistika ma'lumotlarini yuklab bo'lmadi.")
        return
        
    deliveries = res.json()
    
    if not deliveries:
        st.info("Hozircha yetkazib berish jarayonidagi buyurtmalar yo'q.")
        return
        
    deliv_list = []
    for d in deliveries:
        deliv_list.append({
            "ID": d["id"],
            "Buyurtma ID": f"#{d['order_id']}",
            "Kuryer Kuryerlik": d["carrier_name"],
            "Kuryer Tracker ID": d["tracking_number"] or "Kiritilmagan",
            "Holati": d["status"].upper(),
            "Taxminiy sana": d["estimated_delivery"][:10] if d["estimated_delivery"] else "Noma'lum",
            "Jo'natilgan sana": d["shipped_at"][:16].replace("T", " ") if d["shipped_at"] else "-",
            "Yetkazilgan sana": d["delivered_at"][:16].replace("T", " ") if d["delivered_at"] else "-"
        })
    df = pd.DataFrame(deliv_list)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Logistikani yangilash formasi (Omborchi va Admin uchun)
    if role not in ["admin", "warehouse_manager"]:
        st.info("Eslatma: Kuryerlik va yetkazib berish ma'lumotlarini faqat Ombor Menejeri va Admin yangilashi mumkin.")
        return
        
    st.markdown("---")
    st.subheader("Logistika Ma'lumotlarini Yangilash")
    
    deliv_ids = [d["id"] for d in deliveries]
    sel_del_id = st.selectbox("Yetkazib berish ID sini tanlang", deliv_ids, format_func=lambda x: f"Yetkazish #{x} (Buyurtma {next(d['order_id'] for d in deliveries if d['id'] == x)})")
    
    selected_del = next(d for d in deliveries if d["id"] == sel_del_id)
    
    with st.form("update_delivery_form"):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            carrier_name = st.text_input("Kuryer kompaniya / Shofyor", value=selected_del["carrier_name"])
            tracking_number = st.text_input("Kuryer Tracking ID", value=selected_del["tracking_number"] or "")
            status = st.selectbox("Yetkazish Holati", ["pending", "processing", "shipped", "delivered"], index=["pending", "processing", "shipped", "delivered"].index(selected_del["status"]))
        with col_d2:
            st.markdown("Sanalarni o'zgartirish (agar kerak bo'lsa):")
            est_date = st.date_input("Taxminiy yetkazish sanasi", value=date.today())
            
        del_submit = st.form_submit_button("Saqlash va Yangilash", type="primary")
        if del_submit:
            del_payload = {
                "status": status,
                "tracking_number": tracking_number if tracking_number else None,
                "estimated_delivery": datetime.combine(est_date, datetime.min.time()).isoformat(),
            }
            if status == "shipped" and not selected_del["shipped_at"]:
                del_payload["shipped_at"] = datetime.utcnow().isoformat()
            elif status == "delivered" and not selected_del["delivered_at"]:
                del_payload["delivered_at"] = datetime.utcnow().isoformat()
                
            d_up_res = api_put(f"/deliveries/{sel_del_id}", del_payload)
            if d_up_res and d_up_res.status_code == 200:
                st.success("Logistika ma'lumotlari muvaffaqiyatli yangilandi!")
                st.rerun()
            else:
                st.error("Logistika ma'lumotlarini yangilashda xatolik yuz berdi.")

def page_tasks():
    st.markdown("<h1>📋 Xodimlar uchun Vazifalar</h1>", unsafe_allow_html=True)
    
    role = st.session_state["user"]["role"]
    
    # Vazifalarni va xodimlarni yuklash
    tasks_res = api_get("/tasks")
    users_res = api_get("/users") if role == "admin" else None
    clients_res = api_get("/clients")
    
    if not tasks_res or tasks_res.status_code != 200:
        st.error("Vazifalar ro'yxatini yuklashda xatolik yuz berdi.")
        return
        
    tasks = tasks_res.json()
    clients = clients_res.json() if clients_res and clients_res.status_code == 200 else []
    
    tab1, tab2 = st.tabs(["📋 Vazifalar Ro'yxati", "➕ Yangi Vazifa Yuklash (Admin/Sotuv)"])
    
    with tab1:
        if not tasks:
            st.info("Hozircha sizga biriktirilgan vazifalar mavjud emas.")
        else:
            task_list = []
            for t in tasks:
                task_list.append({
                    "ID": t["id"],
                    "Mavzu": t["title"],
                    "Tavsif": t["description"] or "-",
                    "Mijoz Kompaniya": t["client"]["company_name"] if t["client"] else "Umumiy",
                    "Muddat": t["due_date"][:10] if t["due_date"] else "Noma'lum",
                    "Holati": t["status"].upper(),
                    "Kimga biriktirilgan": t["assigned_to"]["full_name"]
                })
            df = pd.DataFrame(task_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Vazifa statusini o'zgartirish
            st.markdown("---")
            st.subheader("Vazifa holatini yangilash")
            my_task_ids = [t["id"] for t in tasks]
            if my_task_ids:
                sel_task_id = st.selectbox("Vazifani tanlang", my_task_ids, format_func=lambda x: f"Vazifa #{x} - {next(t['title'] for t in tasks if t['id'] == x)}")
                selected_task = next(t for t in tasks if t["id"] == sel_task_id)
                
                with st.form("update_task_status_form"):
                    new_status = st.selectbox("Vazifa Holati", ["pending", "in_progress", "completed", "cancelled"], index=["pending", "in_progress", "completed", "cancelled"].index(selected_task["status"]))
                    task_up_submit = st.form_submit_button("Vazifani Yangilash", type="primary")
                    if task_up_submit:
                        up_task_data = {"status": new_status}
                        t_res = api_put(f"/tasks/{sel_task_id}", up_task_data)
                        if t_res and t_res.status_code == 200:
                            st.success("Vazifa holati muvaffaqiyatli yangilandi!")
                            st.rerun()
                        else:
                            st.error("Vazifa holatini o'zgartirib bo'lmadi.")
            
    with tab2:
        # Xodimlar ro'yxatini olish (Admin uchun)
        if role != "admin":
            st.warning("Faqat Tizim Admini yangi vazifalar yarata oladi.")
            return
            
        if not users_res or users_res.status_code != 200:
            st.info("Xodimlar ro'yxatini yuklab bo'lmadi (Faqat admin vazifa yuklay oladi).")
            return
            
        users = users_res.json()
        
        with st.form("create_task_form"):
            st.subheader("Yangi xizmat vazifasini yaratish")
            
            task_title = st.text_input("Vazifa mavzusi", placeholder="Mijoz bilan bog'lanish va qarzni undirish")
            task_desc = st.text_area("Vazifa batafsil tavsifi", placeholder="Shu hafta oxirigacha qarzdorlikni yopish bo'yicha gaplashilsin.")
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                assigned_user_id = st.selectbox("Ijrochi xodim", [u["id"] for u in users], format_func=lambda x: next(f"{u['full_name']} ({u['role'].upper()})" for u in users if u['id'] == x))
                due_date_input = st.date_input("Muddat", value=date.today())
            with col_t2:
                task_client_id = st.selectbox("Bog'liq mijoz (ixtiyoriy)", [None] + [c["id"] for c in clients], format_func=lambda x: "Mijoz bog'lanmagan" if x is None else next(c["company_name"] for c in clients if c['id'] == x))
                
            task_submit = st.form_submit_button("Vazifani Saqlash", type="primary")
            if task_submit:
                if not task_title:
                    st.error("Vazifa mavzusini kiritish shart!")
                else:
                    task_payload = {
                        "assigned_to_id": assigned_user_id,
                        "client_id": task_client_id,
                        "title": task_title,
                        "description": task_desc if task_desc else None,
                        "status": "pending",
                        "due_date": datetime.combine(due_date_input, datetime.min.time()).isoformat()
                    }
                    t_c_res = api_post("/tasks", task_payload)
                    if t_c_res and t_c_res.status_code == 200:
                        st.success("Vazifa muvaffaqiyatli biriktirildi!")
                        st.rerun()
                    else:
                        st.error("Vazifani yaratishda xatolik yuz berdi.")

def page_communications():
    st.markdown("<h1>📞 Mijozlar bilan Aloqalar Tarixi</h1>", unsafe_allow_html=True)
    
    # Aloqalar ro'yxatini yuklash
    comm_res = api_get("/communications")
    clients_res = api_get("/clients")
    
    if not comm_res or comm_res.status_code != 200:
        st.error("Mijoz bilan aloqa tarixini yuklab bo'lmadi.")
        return
        
    communications = comm_res.json()
    clients = clients_res.json() if clients_res and clients_res.status_code == 200 else []
    
    tab1, tab2 = st.tabs(["📞 Aloqalar Jurnali", "✍️ Yangi Aloqa Hujjatlashtirish"])
    
    with tab1:
        if not communications:
            st.info("Hozircha aloqalar tarixi mavjud emas.")
        else:
            comm_list = []
            for c in communications:
                comm_list.append({
                    "Mijoz Kompaniya": c["client"]["company_name"],
                    "Aloqa turi": c["contact_type"].upper(),
                    "Qisqacha mazmuni": c["summary"],
                    "Mas'ul xodim": c["user"]["full_name"],
                    "Sana": datetime.fromisoformat(c["created_at"].replace("Z", "")).strftime("%Y-%m-%d %H:%M")
                })
            df = pd.DataFrame(comm_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    with tab2:
        if not clients:
            st.info("Mijozlar mavjud emas. Avval mijoz qo'shing.")
            return
            
        with st.form("new_comm_form"):
            st.subheader("Mijoz bilan bog'lanish tafsilotlari")
            
            comm_client_id = st.selectbox("Mijoz", [c["id"] for c in clients], format_func=lambda x: next(c["company_name"] for c in clients if c["id"] == x))
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                contact_type = st.selectbox("Aloqa turi", ["phone", "email", "meeting", "telegram"])
            with col_c2:
                st.markdown("<small style='color: #64748b;'>Hujjatni saqlashdan avval barcha tafsilotlarni to'g'ri yozganingizga ishonch hosil qiling.</small>", unsafe_allow_html=True)
                
            summary = st.text_area("Muloqot mazmuni va natijasi", placeholder="Mijoz yangi yozgi kolleksiyaga qiziqish bildirdi. Keyingi dushanba kuni qayta bog'lanadigan bo'ldik.")
            
            comm_submit = st.form_submit_button("Muloqotni Saqlash", type="primary")
            if comm_submit:
                if not summary:
                    st.error("Muloqot mazmunini kiritish shart!")
                else:
                    comm_payload = {
                        "client_id": comm_client_id,
                        "contact_type": contact_type,
                        "summary": summary
                    }
                    c_res = api_post("/communications", comm_payload)
                    if c_res and c_res.status_code == 200:
                        st.success("Aloqa tarixi muvaffaqiyatli saqlandi!")
                        st.rerun()
                    else:
                        st.error("Aloqa tarixini saqlashda xatolik yuz berdi.")

def page_staff():
    st.markdown("<h1>⚙️ Tizim Xodimlari (Admin Paneli)</h1>", unsafe_allow_html=True)
    
    # Xodimlar ro'yxatini yuklash
    res = api_get("/users")
    if not res or res.status_code != 200:
        st.error("Xodimlar ro'yxatini yuklab bo'lmadi.")
        return
        
    users = res.json()
    
    tab1, tab2 = st.tabs(["👥 Tizim Foydalanuvchilari", "➕ Yangi Xodim Qo'shish"])
    
    with tab1:
        user_list = []
        for u in users:
            user_list.append({
                "ID": u["id"],
                "Ism Familiya": u["full_name"],
                "E-mail manzili": u["email"],
                "Roli": u["role"].upper(),
                "Holati": "Faol" if u["is_active"] else "Faol emas"
            })
        df = pd.DataFrame(user_list)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Foydalanuvchini o'chirish
        st.markdown("---")
        st.subheader("Xodimni tizimdan o'chirish")
        delete_user_ids = [u["id"] for u in users if u["email"] != "admin@texstyle.uz"]
        
        if delete_user_ids:
            sel_del_user_id = st.selectbox("O'chirish uchun xodimni tanlang", delete_user_ids, format_func=lambda x: next(f"{u['full_name']} ({u['email']})" for u in users if u['id'] == x))
            
            if st.button("❌ Foydalanuvchini O'chirish", type="primary"):
                del_res = api_delete(f"/users/{sel_del_user_id}")
                if del_res and del_res.status_code == 204:
                    st.success("Foydalanuvchi tizimdan muvaffaqiyatli o'chirildi!")
                    st.rerun()
                else:
                    st.error("Foydalanuvchini o'chirib bo'lmadi.")
        else:
            st.info("O'chirish mumkin bo'lgan qo'shimcha foydalanuvchilar mavjud emas.")
            
    with tab2:
        with st.form("add_user_form"):
            st.subheader("Yangi xodim ma'lumotlari")
            
            new_email = st.text_input("E-mail manzil", placeholder="employee@texstyle.uz")
            new_fullname = st.text_input("F.I.SH", placeholder="Asqar Karimov")
            new_role = st.selectbox("Lavozimi (Rol)", ["sales_manager", "warehouse_manager", "admin"])
            new_password = st.text_input("Maxfiy parol", type="password", placeholder="••••••••")
            new_is_active = st.checkbox("Tizimda faol xodim", value=True)
            
            user_submit = st.form_submit_button("Foydalanuvchini Yaratish", type="primary")
            if user_submit:
                if not new_email or not new_fullname or not new_password:
                    st.error("Iltimos, barcha maydonlarni to'ldiring.")
                else:
                    user_payload = {
                        "email": new_email,
                        "full_name": new_fullname,
                        "role": new_role,
                        "password": new_password,
                        "is_active": new_is_active
                    }
                    u_res = api_post("/users", user_payload)
                    if u_res and u_res.status_code == 200:
                        st.success(f"Yangi xodim '{new_fullname}' muvaffaqiyatli yaratildi!")
                        st.rerun()
                    else:
                        st.error("Foydalanuvchi yaratishda xatolik. Email manzil unikal bo'lishi kerak.")

# ----------------- ENTRYPOINT -----------------
if __name__ == "__main__":
    if st.session_state["token"] is None:
        show_login_page()
    else:
        show_app()
