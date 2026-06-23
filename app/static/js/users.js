document.addEventListener("DOMContentLoaded", async () => {
    if (!API.requireAuth()) return;

    const user = API.getUser();
    if (!["admin", "manager"].includes(user.role)) {
        window.location.href = "/ui/guests";
        return;
    }

    showCurrentUser();
    setupLogout();
    const modal = setupModal("createModal", "openCreateModal");

    document.getElementById("searchBtn").addEventListener("click", loadUsers);
    document.getElementById("createUserForm").addEventListener("submit", createUser);

    await loadUsers();
});

async function loadUsers() {
    hideError("usersError");
    const tbody = document.getElementById("usersTableBody");
    tbody.innerHTML = `<tr><td colspan="7" class="empty">Đang tải...</td></tr>`;

    const params = {};
    const keyword = document.getElementById("keyword").value.trim();
    const role = document.getElementById("roleFilter").value;
    const status = document.getElementById("statusFilter").value;

    if (keyword) params.keyword = keyword;
    if (role) params.role = role;
    if (status) params.status_filter = status;

    try {
        const result = await API.getUsers(params);
        const users = result.data || [];

        if (!users.length) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty">Không có dữ liệu</td></tr>`;
            return;
        }

        tbody.innerHTML = users.map((user) => `
            <tr>
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${roleLabel(user.role)}</td>
                <td>${user.department || "-"}</td>
                <td>${statusBadge(user.status)}</td>
                <td>
                    <button class="btn btn-sm ${user.status === "active" ? "btn-danger" : "btn-success"}"
                        onclick="toggleUser(${user.id})">
                        ${user.status === "active" ? "Khóa" : "Mở khóa"}
                    </button>
                </td>
            </tr>
        `).join("");
    } catch (error) {
        showError("usersError", error.message);
        tbody.innerHTML = `<tr><td colspan="7" class="empty">Không tải được dữ liệu</td></tr>`;
    }
}

async function createUser(event) {
    event.preventDefault();
    hideError("createError");

    const form = event.target;
    const payload = {
        name: form.name.value.trim(),
        email: form.email.value.trim(),
        password: form.password.value,
        role: form.role.value,
        department: form.department.value.trim() || null,
        phone: form.phone.value.trim() || null,
    };

    try {
        await API.createUser(payload);
        form.reset();
        document.getElementById("createModal").classList.add("hidden");
        await loadUsers();
    } catch (error) {
        showError("createError", error.message);
    }
}

async function toggleUser(userId) {
    if (!confirm("Bạn có chắc muốn đổi trạng thái tài khoản này?")) return;

    try {
        await API.toggleUserStatus(userId);
        await loadUsers();
    } catch (error) {
        showError("usersError", error.message);
    }
}

window.toggleUser = toggleUser;
