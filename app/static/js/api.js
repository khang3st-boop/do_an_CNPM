const API = {
    getToken() {
        return localStorage.getItem("token");
    },

    getUser() {
        const raw = localStorage.getItem("user");
        return raw ? JSON.parse(raw) : null;
    },

    setSession(token, user) {
        localStorage.setItem("token", token);
        localStorage.setItem("user", JSON.stringify(user));
    },

    clearSession() {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    },

    requireAuth(redirectTo = "/ui/login") {
        if (!this.getToken()) {
            window.location.href = redirectTo;
            return false;
        }
        return true;
    },

    async request(path, options = {}) {
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        };

        const token = this.getToken();
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }

        const response = await fetch(path, { ...options, headers });
        const data = await response.json().catch(() => ({}));

        if (response.status === 401) {
            this.clearSession();
            window.location.href = "/ui/login";
            throw new Error(data.message || "Phiên đăng nhập hết hạn");
        }

        if (!response.ok) {
            throw new Error(data.message || "Có lỗi xảy ra");
        }

        return data;
    },

    async login(email, password) {
        return this.request("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        });
    },

    async me() {
        return this.request("/api/auth/me");
    },

    async getUsers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/users${query ? `?${query}` : ""}`);
    },

    async createUser(payload) {
        return this.request("/api/users", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    },

    async toggleUserStatus(userId) {
        return this.request(`/api/users/${userId}/toggle-status`, {
            method: "PATCH",
        });
    },

    async getReminders(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/reminders${query ? `?${query}` : ""}`);
    },

    async getOverdueReminders() {
        return this.request("/api/reminders/overdue");
    },

    async createReminder(payload) {
        return this.request("/api/reminders", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    },

    async updateReminderStatus(reminderId, status) {
        return this.request(`/api/reminders/${reminderId}/status`, {
            method: "PATCH",
            body: JSON.stringify({ status }),
        });
    },

    async getRooms() {
        return this.request("/api/rooms");
    },
};

function formatDateTime(value) {
    if (!value) return "-";
    const date = new Date(value);
    return date.toLocaleString("vi-VN");
}

function roleLabel(role) {
    const labels = {
        admin: "Admin",
        manager: "Manager",
        receptionist: "Lễ tân",
        housekeeping: "Buồng phòng",
        technician: "Kỹ thuật",
        staff: "Nhân viên",
    };
    return labels[role] || role;
}

function statusBadge(status) {
    return `<span class="badge badge-${status}">${status}</span>`;
}

function setupLogout() {
    const btn = document.getElementById("logoutBtn");
    if (btn) {
        btn.addEventListener("click", () => {
            API.clearSession();
            window.location.href = "/ui/login";
        });
    }
}

function showCurrentUser() {
    const el = document.getElementById("currentUser");
    const user = API.getUser();
    if (el && user) {
        el.textContent = `${user.name} (${roleLabel(user.role)})`;
    }
}

function setupModal(modalId, openBtnId) {
    const modal = document.getElementById(modalId);
    const openBtn = document.getElementById(openBtnId);
    if (!modal) return;

    const close = () => modal.classList.add("hidden");
    const open = () => modal.classList.remove("hidden");

    if (openBtn) openBtn.addEventListener("click", open);
    modal.querySelectorAll(".modal-close, .modal-backdrop").forEach((el) => {
        el.addEventListener("click", close);
    });

    return { close, open };
}

function showError(elementId, message) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.classList.remove("hidden");
}

function hideError(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.classList.add("hidden");
}
