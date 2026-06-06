// ==========================================
// TexStyle CRM - Core Frontend JavaScript Application
// ==========================================

const API_BASE_URL = "/api/v1";

// Global Ilova Holati (State)
let state = {
    token: localStorage.getItem("texstyle_token") || null,
    user: null,
    activeScreen: "dashboard",
    clients: [],
    orders: [],
    tasks: [],
    users: [],
    currentClientIdForComm: null
};

// ----------------- YORDAMCHI FUNKSIYALAR (HELPERS) -----------------

function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    const toastMsg = document.getElementById("toast-message");
    const toastIcon = document.getElementById("toast-icon");
    
    toastMsg.innerText = message;
    toast.className = `toast ${type}`;
    
    // Icon o'zgartirish
    if (type === "success") {
        toastIcon.className = "fa-solid fa-circle-check";
    } else if (type === "danger") {
        toastIcon.className = "fa-solid fa-circle-exclamation";
    } else if (type === "warning") {
        toastIcon.className = "fa-solid fa-triangle-exclamation";
    } else {
        toastIcon.className = "fa-solid fa-circle-info";
    }
    
    toast.classList.remove("hidden");
    
    setTimeout(() => {
        toast.classList.add("hidden");
    }, 4000);
}

function formatCurrency(val) {
    return new Intl.NumberFormat('uz-UZ', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(val);
}

function formatDate(dateStr) {
    if (!dateStr) return "Noma'lum";
    const date = new Date(dateStr);
    return date.toLocaleDateString('uz-UZ', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Global API Fetch funksiyasi
async function apiCall(endpoint, method = "GET", body = null, isUrlEncoded = false) {
    const headers = {};
    
    if (state.token) {
        headers["Authorization"] = `Bearer ${state.token}`;
    }
    
    let requestBody = body;
    if (body && !isUrlEncoded) {
        headers["Content-Type"] = "application/json";
        requestBody = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method,
            headers,
            body: requestBody
        });
        
        if (response.status === 401) {
            // Token eskirgan bo'lsa avtomatik logout
            logout();
            showToast("Sessiya muddati tugadi. Tizimga qayta kiring", "warning");
            throw new Error("Unauthorized");
        }
        
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: "Noma'lum xatolik" }));
            throw new Error(errData.detail || `Server xatoligi: ${response.status}`);
        }
        
        if (response.status === 24) { // No Content
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Call error: ${endpoint}`, error);
        throw error;
    }
}

// ----------------- TIZIMGA KIRISH/CHIQISH (AUTH) -----------------

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const loginBtn = document.getElementById("login-btn");
    
    loginBtn.disabled = true;
    loginBtn.innerHTML = `<span>Kirish...</span> <i class="fa-solid fa-spinner fa-spin"></i>`;
    
    // URLencoded body
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);
    
    try {
        const data = await apiCall("/auth/login", "POST", formData, true);
        state.token = data.access_token;
        localStorage.setItem("texstyle_token", data.access_token);
        
        showToast("Tizimga muvaffaqiyatli kirildi!", "success");
        await checkAuth();
    } catch (error) {
        showToast(error.message || "Email yoki parol noto'g'ri", "danger");
    } finally {
        loginBtn.disabled = false;
        loginBtn.innerHTML = `<span>Kirish</span> <i class="fa-solid fa-arrow-right-to-bracket"></i>`;
    }
});

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem("texstyle_token");
    
    document.getElementById("app-container").classList.add("hidden");
    document.getElementById("login-container").classList.remove("hidden");
}

document.getElementById("logout-btn").addEventListener("click", logout);

async function checkAuth() {
    if (!state.token) {
        logout();
        return;
    }
    
    try {
        const user = await apiCall("/auth/me");
        state.user = user;
        
        // UI sozlamalari
        document.getElementById("user-name").innerText = user.full_name;
        
        let roleUz = "Sotuvchi";
        let badgeClass = "badge-info";
        if (user.role === "admin") {
            roleUz = "Admin";
            badgeClass = "badge-danger";
        } else if (user.role === "warehouse_manager") {
            roleUz = "Omborchi";
            badgeClass = "badge-success";
        }
        
        const roleBadge = document.getElementById("user-role");
        roleBadge.innerText = roleUz;
        roleBadge.className = `badge ${badgeClass}`;
        
        // Login ekranini yopish, dashboardni ochish
        document.getElementById("login-container").classList.add("hidden");
        document.getElementById("app-container").classList.remove("hidden");
        
        applyRoleRestrictions();
        
        // Dastlabki ekran
        switchScreen(state.activeScreen);
        
    } catch (error) {
        logout();
    }
}

function applyRoleRestrictions() {
    const role = state.user.role;
    
    // Admin cheklovlari
    const adminElements = document.querySelectorAll(".admin-only");
    adminElements.forEach(el => {
        if (role === "admin") {
            el.classList.remove("hidden");
        } else {
            el.classList.add("hidden");
        }
    });

    // Sales manager cheklovlari
    const salesOnly = document.querySelectorAll(".sales-manager-only");
    salesOnly.forEach(el => {
        if (role === "sales_manager" || role === "admin") {
            el.classList.remove("hidden");
        } else {
            el.classList.add("hidden");
        }
    });
    
    // Sidebar menyularini moslashtirish
    const warehouseMenuItem = document.querySelector('[data-target="warehouse"]');
    const clientsMenuItem = document.querySelector('[data-target="clients"]');
    const tasksMenuItem = document.querySelector('[data-target="tasks"]');
    const usersMenuItem = document.querySelector('[data-target="users"]');

    warehouseMenuItem.classList.toggle("hidden", !["admin", "warehouse_manager"].includes(role));

    if (role === "warehouse_manager") {
        clientsMenuItem.classList.add("hidden");
        tasksMenuItem.classList.add("hidden");
        usersMenuItem.classList.add("hidden");
        state.activeScreen = "warehouse";
    } else {
        clientsMenuItem.classList.remove("hidden");
        tasksMenuItem.classList.remove("hidden");
    }

    if (role === "sales_manager" && state.activeScreen === "warehouse") {
        state.activeScreen = "dashboard";
    }
}

// ----------------- NAVIGATSIYA -----------------

const menuItems = document.querySelectorAll(".sidebar-menu li");
menuItems.forEach(item => {
    item.addEventListener("click", (e) => {
        e.preventDefault();
        const target = item.getAttribute("data-target");
        
        // Agar rol cheklangan bo'lsa o'tmaslik
        if (state.user.role === "warehouse_manager" && ["clients", "tasks", "users"].includes(target)) {
            return;
        }
        if (state.user.role === "sales_manager" && target === "warehouse") {
            return;
        }
        
        menuItems.forEach(mi => mi.classList.remove("active"));
        item.classList.add("active");
        switchScreen(target);
    });
});

// Mobil qurilmalarda sidebar toggle
const sidebar = document.querySelector(".sidebar");
document.getElementById("sidebar-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("open");
});

function switchScreen(screenName) {
    state.activeScreen = screenName;
    
    // Sarlavhani o'zgartirish
    document.getElementById("page-title").innerText = screenName.toUpperCase();
    
    // Barcha ekranlarni yopish
    document.querySelectorAll(".screen").forEach(screen => {
        screen.classList.add("hidden");
    });
    
    // Kerakli ekranni ochish
    const targetScreen = document.getElementById(`screen-${screenName}`);
    if (targetScreen) {
        targetScreen.classList.remove("hidden");
    }
    
    // Mobilda ekranga o'tganda sidebarni yopish
    sidebar.classList.remove("open");
    
    // Ekran bo'yicha ma'lumotlarni yuklash
    if (screenName === "dashboard") {
        loadDashboard();
    } else if (screenName === "clients") {
        loadClients();
    } else if (screenName === "orders") {
        loadOrders();
    } else if (screenName === "warehouse") {
        loadWarehouse();
    } else if (screenName === "tasks") {
        loadTasks();
    } else if (screenName === "users") {
        loadUsers();
    }
}

// Modallarni boshqarish
function openModal(id) {
    document.getElementById(id).classList.remove("hidden");
}
function closeModal(id) {
    document.getElementById(id).classList.add("hidden");
}

// ----------------- DASHBOARD METRIKALARINI YUKLASH -----------------

async function loadDashboard() {
    try {
        let data;
        
        if (state.user.role === "admin") {
            // Admin bo'lsa serverdan tayyor hisobotni olamiz
            data = await apiCall("/reports/dashboard");
        } else {
            // Managerlar uchun statlar frontendda hisoblanadi (Backendda report/dashboard faqat adminga ruxsat berilgan)
            const orders = await apiCall("/orders");
            const clients = state.user.role === "sales_manager" ? await apiCall("/clients") : [];
            
            const totalSales = orders.filter(o => o.payment_status === "paid").reduce((sum, o) => sum + o.total_amount, 0);
            const pendingPayments = clients.reduce((sum, c) => c.balance < 0 ? sum + Math.abs(c.balance) : sum, 0);
            const completedOrders = orders.filter(o => o.delivery_status === "delivered").length;
            const pendingDeliveries = orders.filter(o => ["pending", "processing", "shipped"].includes(o.delivery_status)).length;
            
            // Oxirgi 5 buyurtma
            const recentOrders = [...orders].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5);
            
            const sales_by_status = {
                paid: orders.filter(o => o.payment_status === "paid").length,
                partially_paid: orders.filter(o => o.payment_status === "partially_paid").length,
                pending: orders.filter(o => o.payment_status === "pending").length
            };
            
            data = {
                total_sales: totalSales,
                pending_payments: pendingPayments,
                completed_orders: completedOrders,
                pending_deliveries: pendingDeliveries,
                recent_orders: recentOrders,
                sales_by_status
            };
        }
        
        // UI ni to'ldirish
        document.getElementById("stat-total-sales").innerText = formatCurrency(data.total_sales);
        document.getElementById("stat-pending-payments").innerText = formatCurrency(data.pending_payments);
        document.getElementById("stat-completed-orders").innerText = `${data.completed_orders} ta`;
        document.getElementById("stat-pending-deliveries").innerText = `${data.pending_deliveries} ta`;
        
        // Grafik / Diagramma qismi
        const total = data.sales_by_status.paid + data.sales_by_status.partially_paid + data.sales_by_status.pending;
        document.getElementById("chart-total-count").innerText = total;
        
        document.getElementById("legend-paid").innerText = data.sales_by_status.paid;
        document.getElementById("legend-partial").innerText = data.sales_by_status.partially_paid;
        document.getElementById("legend-pending").innerText = data.sales_by_status.pending;
        
        // Diagramma konusi rangini dinamik o'rnatish
        const ring = document.getElementById("chart-ring-fill");
        if (total > 0) {
            const p1 = (data.sales_by_status.paid / total) * 100;
            const p2 = (data.sales_by_status.partially_paid / total) * 100;
            const ringEl = document.querySelector(".chart-ring");
            ringEl.style.background = `conic-gradient(var(--success) 0% ${p1}%, var(--warning) ${p1}% ${p1+p2}%, var(--danger) ${p1+p2}% 100%)`;
        }
        
        // Oxirgi buyurtmalar jadvali
        const tbody = document.getElementById("recent-orders-table");
        tbody.innerHTML = "";
        
        if (data.recent_orders.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">Hozircha buyurtmalar yo'q</td></tr>`;
            return;
        }
        
        data.recent_orders.forEach(order => {
            const pBadge = getPaymentBadge(order.payment_status);
            const dBadge = getDeliveryBadge(order.delivery_status);
            
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>#${order.id}</strong></td>
                <td>${order.client.company_name}</td>
                <td>${formatDate(order.created_at)}</td>
                <td>${formatCurrency(order.total_amount)}</td>
                <td>${pBadge}</td>
                <td>${dBadge}</td>
            `;
            tbody.appendChild(tr);
        });
        
    } catch (error) {
        showToast("Dashboard ma'lumotlarini yuklashda xatolik", "danger");
    }
}

function getPaymentBadge(status) {
    if (status === "paid") return `<span class="badge badge-success">To'langan</span>`;
    if (status === "partially_paid") return `<span class="badge badge-warning">Qisman</span>`;
    return `<span class="badge badge-danger">Kutilmoqda</span>`;
}

function getDeliveryBadge(status) {
    if (status === "delivered") return `<span class="badge badge-success">Yetkazildi</span>`;
    if (status === "shipped") return `<span class="badge badge-info">Kuryerda (Yo'lda)</span>`;
    if (status === "processing") return `<span class="badge badge-warning">Tayyorlanmoqda</span>`;
    if (status === "cancelled") return `<span class="badge badge-danger">Bekor bo'ldi</span>`;
    return `<span class="badge badge-outline">Kutilmoqda</span>`;
}

// ----------------- MIJOZLAR SECTION -----------------

async function loadClients() {
    try {
        const clients = await apiCall("/clients");
        state.clients = clients;
        renderClients(clients);
    } catch (error) {
        showToast("Mijozlar ro'yxatini yuklab bo'lmadi", "danger");
    }
}

function renderClients(clients) {
    const tbody = document.getElementById("clients-table-body");
    tbody.innerHTML = "";
    
    if (clients.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Mijozlar topilmadi</td></tr>`;
        return;
    }
    
    clients.forEach(client => {
        const balanceColor = client.balance < 0 ? "text-danger" : (client.balance > 0 ? "text-success" : "");
        const balanceText = client.balance < 0 ? `Qarz: ${formatCurrency(Math.abs(client.balance))}` : formatCurrency(client.balance);
        
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${client.company_name}</strong></td>
            <td>${client.contact_person}</td>
            <td>${client.phone}</td>
            <td>${client.email}</td>
            <td>${client.address}</td>
            <td class="${balanceColor} font-bold">${balanceText}</td>
            <td>
                <div style="display: flex; gap: 8px;">
                    <button onclick="editClient(${client.id})" class="btn btn-secondary btn-sm" title="Tahrirlash"><i class="fa-solid fa-pen-to-square"></i></button>
                    <button onclick="openCommModal(${client.id}, '${client.company_name}')" class="btn btn-secondary btn-sm" title="Muloqotlar tarixi"><i class="fa-solid fa-comments"></i></button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Mijoz qidirish
document.getElementById("client-search").addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = state.clients.filter(c => 
        c.company_name.toLowerCase().includes(query) || 
        c.contact_person.toLowerCase().includes(query) ||
        c.phone.includes(query)
    );
    renderClients(filtered);
});

// Yangi Mijoz yaratish / tahrirlash formasi
document.getElementById("client-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("client-id-field").value;
    const clientData = {
        company_name: document.getElementById("client-company-name").value,
        contact_person: document.getElementById("client-contact").value,
        phone: document.getElementById("client-phone").value,
        email: document.getElementById("client-email").value,
        address: document.getElementById("client-address").value,
        balance: 0.0
    };
    
    try {
        if (id) {
            await apiCall(`/clients/${id}`, "PUT", clientData);
            showToast("Mijoz ma'lumotlari tahrirlandi", "success");
        } else {
            await apiCall("/clients", "POST", clientData);
            showToast("Yangi mijoz muvaffaqiyatli qo'shildi", "success");
        }
        closeModal("client-modal");
        document.getElementById("client-form").reset();
        document.getElementById("client-id-field").value = "";
        loadClients();
    } catch (error) {
        showToast("Mijoz ma'lumotlarini saqlab bo'lmadi", "danger");
    }
});

function editClient(id) {
    const client = state.clients.find(c => c.id === id);
    if (!client) return;
    
    document.getElementById("client-id-field").value = client.id;
    document.getElementById("client-company-name").value = client.company_name;
    document.getElementById("client-contact").value = client.contact_person;
    document.getElementById("client-phone").value = client.phone;
    document.getElementById("client-email").value = client.email;
    document.getElementById("client-address").value = client.address;
    
    document.getElementById("client-modal-title").innerText = "Mijoz ma'lumotlarini o'zgartirish";
    openModal("client-modal");
}

// ----------------- ALOQA LOGLARI (COMMUNICATIONS) -----------------

async function openCommModal(clientId, companyName) {
    state.currentClientIdForComm = clientId;
    document.getElementById("comm-client-id").value = clientId;
    document.getElementById("comm-client-name").innerText = companyName;
    
    // Timeline ro'yxatini tozalash
    document.getElementById("comm-timeline-list").innerHTML = "Yuklanmoqda...";
    
    openModal("client-comm-modal");
    await loadCommunications(clientId);
}

async function loadCommunications(clientId) {
    try {
        const comms = await apiCall("/communications");
        const filtered = comms.filter(c => c.client_id === clientId).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        const list = document.getElementById("comm-timeline-list");
        list.innerHTML = "";
        
        if (filtered.length === 0) {
            list.innerHTML = `<p class="text-muted text-center py-4">Mijoz bilan aloqa tarixi bo'sh</p>`;
            return;
        }
        
        filtered.forEach(c => {
            let icon = "phone";
            if (c.contact_type === "email") icon = "envelope";
            if (c.contact_type === "meeting") icon = "handshake";
            if (c.contact_type === "telegram") icon = "paper-plane";
            
            const div = document.createElement("div");
            div.className = "timeline-item";
            div.innerHTML = `
                <div class="timeline-header">
                    <span><i class="fa-solid fa-${icon}"></i> ${c.contact_type.toUpperCase()}</span>
                    <span>${formatDate(c.created_at)} (Menejer: ${c.user.full_name})</span>
                </div>
                <div class="timeline-content">
                    ${c.summary}
                </div>
            `;
            list.appendChild(div);
        });
    } catch (error) {
        showToast("Aloqalar tarixini yuklashda xatolik", "danger");
    }
}

document.getElementById("comm-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const clientId = state.currentClientIdForComm;
    const commData = {
        client_id: clientId,
        contact_type: document.getElementById("comm-type").value,
        summary: document.getElementById("comm-summary").value
    };
    
    try {
        await apiCall("/communications", "POST", commData);
        showToast("Muloqot logi qo'shildi!", "success");
        document.getElementById("comm-summary").value = "";
        await loadCommunications(clientId);
    } catch (error) {
        showToast("Muloqotni qayd etib bo'lmadi", "danger");
    }
});

// ----------------- BUYURTMALAR SECTION -----------------

async function loadOrders() {
    try {
        const orders = await apiCall("/orders");
        state.orders = orders;
        renderOrders(orders);
    } catch (error) {
        showToast("Buyurtmalarni yuklab bo'lmadi", "danger");
    }
}

function renderOrders(orders) {
    const tbody = document.getElementById("orders-table-body");
    tbody.innerHTML = "";
    
    if (orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">Buyurtmalar topilmadi</td></tr>`;
        return;
    }
    
    orders.forEach(order => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>#${order.id}</strong></td>
            <td>${order.client.company_name}</td>
            <td>${order.created_by.full_name}</td>
            <td>${formatCurrency(order.total_amount)}</td>
            <td>${getPaymentBadge(order.payment_status)}</td>
            <td>${getDeliveryBadge(order.delivery_status)}</td>
            <td>${formatDate(order.created_at)}</td>
            <td>
                <div style="display: flex; gap: 8px;">
                    <button onclick="viewOrderDetails(${order.id})" class="btn btn-secondary btn-sm" title="Tafsilotlar"><i class="fa-solid fa-eye"></i></button>
                    <button onclick="editOrderStatus(${order.id})" class="btn btn-secondary btn-sm" title="Statuslarni o'zgartirish"><i class="fa-solid fa-sliders"></i></button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Buyurtmalarni qidirish
document.getElementById("order-search").addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = state.orders.filter(o => 
        o.id.toString().includes(query) ||
        o.client.company_name.toLowerCase().includes(query) ||
        o.created_by.full_name.toLowerCase().includes(query)
    );
    renderOrders(filtered);
});

// Buyurtma yaratish modali
async function openCreateOrderModal() {
    // Mijozlar ro'yxatini yuklash dropdown uchun
    try {
        const clients = await apiCall("/clients");
        const select = document.getElementById("order-client-id");
        select.innerHTML = `<option value="">-- Mijoz kompaniyani tanlang --</option>`;
        
        clients.forEach(c => {
            select.innerHTML += `<option value="${c.id}">${c.company_name} (Kontakt: ${c.contact_person})</option>`;
        });
        
        // Order items builderini tozalash va birinchi qatorni qo'shish
        document.getElementById("order-items-tbody").innerHTML = "";
        addOrderItemRow();
        calculateOrderTotal();
        
        openModal("order-modal");
    } catch (error) {
        showToast("Mijozlarni yuklashda xatolik", "danger");
    }
}

function addOrderItemRow() {
    const tbody = document.getElementById("order-items-tbody");
    const tr = document.createElement("tr");
    tr.className = "order-item-row";
    tr.innerHTML = `
        <td><input type="text" class="prod-name" placeholder="Masalan: Paxtali Ko'ylak" required></td>
        <td><input type="number" class="prod-qty" value="10" min="1" required onchange="calculateOrderTotal()"></td>
        <td><input type="number" class="prod-price" value="15.00" min="0.1" step="0.01" required onchange="calculateOrderTotal()"></td>
        <td class="prod-total font-bold">$150.00</td>
        <td><button type="button" class="btn-close" onclick="removeOrderItemRow(this)"><i class="fa-solid fa-trash"></i></button></td>
    `;
    tbody.appendChild(tr);
    calculateOrderTotal();
}

function removeOrderItemRow(btn) {
    const row = btn.parentElement.parentElement;
    const tbody = document.getElementById("order-items-tbody");
    if (tbody.children.length > 1) {
        row.remove();
        calculateOrderTotal();
    } else {
        showToast("Kamida bitta mahsulot bo'lishi shart!", "warning");
    }
}

function calculateOrderTotal() {
    const rows = document.querySelectorAll(".order-item-row");
    let grandTotal = 0.0;
    
    rows.forEach(row => {
        const qty = parseFloat(row.querySelector(".prod-qty").value) || 0;
        const price = parseFloat(row.querySelector(".prod-price").value) || 0;
        const total = qty * price;
        row.querySelector(".prod-total").innerText = formatCurrency(total);
        grandTotal += total;
    });
    
    document.getElementById("order-total-display").innerText = formatCurrency(grandTotal);
}

// Buyurtmani yuborish
document.getElementById("order-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const clientId = parseInt(document.getElementById("order-client-id").value);
    const paymentStatus = document.getElementById("order-payment-status").value;
    
    const rows = document.querySelectorAll(".order-item-row");
    const items = [];
    
    rows.forEach(row => {
        items.push({
            product_name: row.querySelector(".prod-name").value,
            quantity: parseInt(row.querySelector(".prod-qty").value),
            unit_price: parseFloat(row.querySelector(".prod-price").value)
        });
    });
    
    const orderData = {
        client_id: clientId,
        payment_status: paymentStatus,
        delivery_status: "pending",
        items: items
    };
    
    try {
        await apiCall("/orders", "POST", orderData);
        showToast("Buyurtma muvaffaqiyatli saqlandi!", "success");
        closeModal("order-modal");
        loadOrders();
    } catch (error) {
        showToast("Buyurtmani saqlab bo'lmadi: " + error.message, "danger");
    }
});

function editOrderStatus(id) {
    const order = state.orders.find(o => o.id === id);
    if (!order) return;
    
    document.getElementById("status-order-id").value = order.id;
    document.getElementById("status-payment").value = order.payment_status;
    document.getElementById("status-delivery").value = order.delivery_status;
    
    openModal("status-modal");
}

document.getElementById("status-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("status-order-id").value;
    const statusData = {
        payment_status: document.getElementById("status-payment").value,
        delivery_status: document.getElementById("status-delivery").value
    };
    
    try {
        await apiCall(`/orders/${id}/status`, "PUT", statusData);
        showToast("Buyurtma statusi yangilandi", "success");
        closeModal("status-modal");
        loadOrders();
    } catch (error) {
        showToast("Statuslarni yangilashda xatolik yuz berdi", "danger");
    }
});

function viewOrderDetails(id) {
    const order = state.orders.find(o => o.id === id);
    if (!order) return;
    
    let itemsText = order.items.map(item => 
        `- ${item.product_name}: ${item.quantity} dona x ${formatCurrency(item.unit_price)} = ${formatCurrency(item.total_price)}`
    ).join("\n");
    
    alert(`Buyurtma Tafsilotlari (ID: #${order.id})
---------------------------------------
Mijoz: ${order.client.company_name}
Yaratgan xodim: ${order.created_by.full_name}
Jami summa: ${formatCurrency(order.total_amount)}
To'lov: ${order.payment_status.toUpperCase()}
Yetkazish: ${order.delivery_status.toUpperCase()}
Sana: ${formatDate(order.created_at)}

Tarkibi:
${itemsText}`);
}

// ----------------- OMBOR & YETKAZIB BERISH (WAREHOUSE) -----------------

async function loadWarehouse() {
    try {
        const deliveries = await apiCall("/deliveries");
        const orders = await apiCall("/orders");
        
        const tbody = document.getElementById("warehouse-table-body");
        tbody.innerHTML = "";
        
        if (deliveries.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Kutilayotgan logistika ishlari yo'q</td></tr>`;
            return;
        }
        
        deliveries.forEach(del => {
            // Tegishli buyurtmani topamiz mijoz nomini olish uchun
            const relatedOrder = orders.find(o => o.id === del.order_id);
            const clientName = relatedOrder ? relatedOrder.client.company_name : "Noma'lum Mijoz";
            
            const estDate = del.estimated_delivery ? formatDate(del.estimated_delivery) : "Belgilanmagan";
            const tracking = del.tracking_number || "Trek-kod yo'q";
            
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>#${del.order_id}</strong></td>
                <td>${clientName}</td>
                <td>${del.carrier_name}</td>
                <td><code class="badge badge-outline">${tracking}</code></td>
                <td>${getDeliveryBadge(del.status)}</td>
                <td>${estDate}</td>
                <td>
                    <button onclick="editDelivery(${del.id})" class="btn btn-primary btn-sm" title="Logistikani tahrirlash">
                        <i class="fa-solid fa-truck-ramp-box"></i> Yangilash
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        showToast("Logistika ro'yxatini yuklashda xatolik yuz berdi", "danger");
    }
}

function editDelivery(id) {
    // Delivery formni ochish
    apiCall("/deliveries").then(deliveries => {
        const del = deliveries.find(d => d.id === id);
        if (!del) return;
        
        document.getElementById("delivery-id-field").value = del.id;
        document.getElementById("delivery-carrier").value = del.carrier_name;
        document.getElementById("delivery-tracking").value = del.tracking_number || "";
        document.getElementById("delivery-status-select").value = del.status;
        
        openModal("delivery-modal");
    });
}

document.getElementById("delivery-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("delivery-id-field").value;
    const deliveryData = {
        status: document.getElementById("delivery-status-select").value,
        carrier_name: document.getElementById("delivery-carrier").value,
        tracking_number: document.getElementById("delivery-tracking").value || null,
        estimated_delivery: new Date(Date.now() + 2*24*60*60*1000).toISOString() // 2 kundan keyingi muddat avtomatik
    };
    
    try {
        await apiCall(`/deliveries/${id}`, "PUT", deliveryData);
        showToast("Logistika ma'lumotlari yangilandi!", "success");
        closeModal("delivery-modal");
        loadWarehouse();
    } catch (error) {
        showToast("Logistikani saqlab bo'lmadi", "danger");
    }
});

// ----------------- VAZIFALAR (TASKS) SECTION -----------------

async function loadTasks() {
    try {
        const tasks = await apiCall("/tasks");
        state.tasks = tasks;
        
        const pendingList = document.getElementById("tasks-pending-list");
        const completedList = document.getElementById("tasks-completed-list");
        
        pendingList.innerHTML = "";
        completedList.innerHTML = "";
        
        const pendingTasks = tasks.filter(t => t.status !== "completed");
        const completedTasks = tasks.filter(t => t.status === "completed");
        
        document.getElementById("count-task-pending").innerText = pendingTasks.length;
        document.getElementById("count-task-completed").innerText = completedTasks.length;
        
        if (pendingTasks.length === 0) {
            pendingList.innerHTML = `<div class="text-muted text-center py-4">Barcha vazifalar bajarilgan!</div>`;
        } else {
            pendingTasks.forEach(task => {
                pendingList.appendChild(createTaskCard(task));
            });
        }
        
        if (completedTasks.length === 0) {
            completedList.innerHTML = `<div class="text-muted text-center py-4">Hozircha bajarilgan vazifalar yo'q.</div>`;
        } else {
            completedTasks.forEach(task => {
                completedList.appendChild(createTaskCard(task));
            });
        }
        
    } catch (error) {
        showToast("Vazifalar ro'yxatini yuklab bo'lmadi", "danger");
    }
}

function createTaskCard(task) {
    const card = document.createElement("div");
    card.className = "task-item-card";
    
    const clientName = task.client ? task.client.company_name : "Mijoz bog'lanmagan";
    const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : "Muddatsiz";
    
    let btnText = `<i class="fa-solid fa-circle-check text-success"></i> Bajarildi qilish`;
    let newStatus = "completed";
    
    if (task.status === "completed") {
        btnText = `<i class="fa-solid fa-rotate-left text-warning"></i> Qayta ochish`;
        newStatus = "pending";
    }
    
    card.innerHTML = `
        <h5>${task.title}</h5>
        <p>${task.description || "Izoh yo'q"}</p>
        <div style="font-size: 0.8rem; margin-bottom: 8px; color: var(--text-secondary)">
            <i class="fa-solid fa-building"></i> ${clientName} | 
            <i class="fa-solid fa-user-tag"></i> Xodim: ${task.assigned_to.full_name}
        </div>
        <div class="task-meta">
            <span class="due"><i class="fa-regular fa-clock"></i> Muddat: ${dueDate}</span>
            <button onclick="toggleTaskStatus(${task.id}, '${newStatus}')" class="btn btn-secondary btn-sm">${btnText}</button>
        </div>
    `;
    
    return card;
}

async function toggleTaskStatus(id, status) {
    try {
        await apiCall(`/tasks/${id}`, "PUT", { status });
        showToast("Vazifa holati o'zgartirildi!", "success");
        loadTasks();
    } catch (error) {
        showToast("Vazifa holatini yangilashda xatolik", "danger");
    }
}

async function openCreateTaskModal() {
    try {
        // Users dropdown to'ldirish
        const users = await apiCall("/users");
        const selectUser = document.getElementById("task-assigned-to");
        selectUser.innerHTML = "";
        users.forEach(u => {
            selectUser.innerHTML += `<option value="${u.id}">${u.full_name} (${u.role.toUpperCase()})</option>`;
        });
        
        // Clients dropdown to'ldirish
        const clients = await apiCall("/clients");
        const selectClient = document.getElementById("task-client-id");
        selectClient.innerHTML = `<option value="">-- Aloqador mijoz yo'q --</option>`;
        clients.forEach(c => {
            selectClient.innerHTML += `<option value="${c.id}">${c.company_name}</option>`;
        });
        
        // Bugungi sanani minimum qilib qo'yish
        document.getElementById("task-due-date").valueAsDate = new Date();
        
        openModal("task-modal");
    } catch (error) {
        showToast("Ma'lumotlarni yuklab bo'lmadi", "danger");
    }
}

document.getElementById("task-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const taskData = {
        title: document.getElementById("task-title").value,
        assigned_to_id: parseInt(document.getElementById("task-assigned-to").value),
        client_id: document.getElementById("task-client-id").value ? parseInt(document.getElementById("task-client-id").value) : null,
        description: document.getElementById("task-description").value,
        due_date: new Date(document.getElementById("task-due-date").value).toISOString(),
        status: "pending"
    };
    
    try {
        await apiCall("/tasks", "POST", taskData);
        showToast("Vazifa muvaffaqiyatli qo'shildi!", "success");
        closeModal("task-modal");
        document.getElementById("task-form").reset();
        loadTasks();
    } catch (error) {
        showToast("Vazifani qo'shishda xatolik", "danger");
    }
});

// ----------------- XODIMLAR SECTION (ADMIN ONLY) -----------------

async function loadUsers() {
    try {
        const users = await apiCall("/users");
        state.users = users;
        
        const tbody = document.getElementById("users-table-body");
        tbody.innerHTML = "";
        
        users.forEach(u => {
            const tr = document.createElement("tr");
            
            let statusBadge = u.is_active ? `<span class="badge badge-success">Faol</span>` : `<span class="badge badge-danger">Nofaol</span>`;
            
            tr.innerHTML = `
                <td><strong>#${u.id}</strong></td>
                <td>${u.full_name}</td>
                <td>${u.email}</td>
                <td><code class="badge badge-outline">${u.role.toUpperCase()}</code></td>
                <td>${statusBadge}</td>
                <td>
                    <button onclick="deleteUser(${u.id}, '${u.email}')" class="btn btn-danger-outline btn-sm" title="O'chirish">
                        <i class="fa-solid fa-trash-can"></i> O'chirish
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        showToast("Xodimlar ro'yxatini yuklashda xatolik", "danger");
    }
}

document.getElementById("user-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const userData = {
        full_name: document.getElementById("user-fullname").value,
        email: document.getElementById("user-email").value,
        password: document.getElementById("user-password").value,
        role: document.getElementById("user-role-select").value,
        is_active: true
    };
    
    try {
        await apiCall("/users", "POST", userData);
        showToast("Yangi xodim muvaffaqiyatli qo'shildi!", "success");
        closeModal("user-modal");
        document.getElementById("user-form").reset();
        loadUsers();
    } catch (error) {
        showToast("Xodimni qo'shib bo'lmadi: " + error.message, "danger");
    }
});

async function deleteUser(id, email) {
    if (confirm(`${email} foydalanuvchisini o'chirishni tasdiqlaysizmi?`)) {
        try {
            await apiCall(`/users/${id}`, "DELETE");
            showToast("Foydalanuvchi tizimdan o'chirildi", "success");
            loadUsers();
        } catch (error) {
            showToast("O'chirishda xatolik: " + error.message, "danger");
        }
    }
}

// ----------------- TIZIMNI BOSHLA SHARTLARI -----------------

window.addEventListener("DOMContentLoaded", () => {
    checkAuth();
});
