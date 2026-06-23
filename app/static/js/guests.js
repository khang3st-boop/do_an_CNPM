let allReminders = [];

document.addEventListener("DOMContentLoaded", async () => {
    if (!API.requireAuth()) return;

    const user = API.getUser();
    const usersNav = document.getElementById("usersNavLink");
    if (usersNav && !["admin", "manager"].includes(user.role)) {
        usersNav.style.display = "none";
    }

    const createBtn = document.getElementById("openCreateModal");
    if (createBtn && !["admin", "manager", "receptionist"].includes(user.role)) {
        createBtn.style.display = "none";
    }

    showCurrentUser();
    setupLogout();
    setupModal("createModal", "openCreateModal");

    document.getElementById("searchBtn").addEventListener("click", renderGuests);
    document.getElementById("createGuestForm").addEventListener("submit", createGuest);

    await loadGuestsPage();
});

async function loadGuestsPage() {
    hideError("guestsError");

    try {
        const [remindersRes, overdueRes] = await Promise.all([
            API.getReminders().catch(() => ({ data: [] })),
            API.getOverdueReminders().catch(() => ({ data: [] })),
        ]);

        allReminders = remindersRes.data || [];

        if (!allReminders.length) {
            const myRes = await API.request("/api/reminders/my");
            allReminders = myRes.data || [];
        }

        updateStats(allReminders, overdueRes.data || []);
        renderGuests();

        if (document.getElementById("openCreateModal").style.display !== "none") {
            await loadFormOptions();
        }
    } catch (error) {
        showError("guestsError", error.message);
    }
}

function updateStats(reminders, overdue) {
    document.getElementById("statTotal").textContent = reminders.length;
    document.getElementById("statCheckin").textContent =
        reminders.filter((item) => item.reminder_type === "check-in").length;
    document.getElementById("statCheckout").textContent =
        reminders.filter((item) => item.reminder_type === "check-out").length;
    document.getElementById("statOverdue").textContent = overdue.length;
}

function renderGuests() {
    const tbody = document.getElementById("guestsTableBody");
    const keyword = document.getElementById("keyword").value.trim().toLowerCase();
    const type = document.getElementById("typeFilter").value;
    const status = document.getElementById("statusFilter").value;

    let items = [...allReminders];

    if (keyword) {
        items = items.filter((item) =>
            (item.guest_name || "").toLowerCase().includes(keyword) ||
            (item.room_number || "").toLowerCase().includes(keyword)
        );
    }
    if (type) items = items.filter((item) => item.reminder_type === type);
    if (status) items = items.filter((item) => item.status === status);

    if (!items.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty">Không có dữ liệu</td></tr>`;
        return;
    }

    tbody.innerHTML = items.map((item) => `
        <tr>
            <td><strong>${item.guest_name}</strong><br><small>${item.title || ""}</small></td>
            <td>${item.room_number || item.room_id}</td>
            <td><span class="badge badge-${item.reminder_type}">${item.reminder_type}</span></td>
            <td>${formatDateTime(item.reminder_time)}</td>
            <td>${item.assigned_user_name || "-"}</td>
            <td>${statusBadge(item.status)}</td>
            <td>
                ${item.status !== "completed" ? `
                    <button class="btn btn-sm btn-success" onclick="completeReminder(${item.id})">Hoàn thành</button>
                ` : "-"}
            </td>
        </tr>
    `).join("");
}

async function loadFormOptions() {
    try {
        const roomsRes = await API.getRooms();
        const usersRes = await API.getUsers().catch(() => ({ data: [] }));

        const roomSelect = document.getElementById("roomSelect");
        roomSelect.innerHTML = (roomsRes.data || [])
            .filter((room) => room.status !== "inactive")
            .map((room) => `<option value="${room.id}">Phòng ${room.room_number} (${room.room_type})</option>`)
            .join("");

        const staffSelect = document.getElementById("staffSelect");
        const staffList = usersRes.data || [API.getUser()];
        staffSelect.innerHTML = staffList
            .filter((user) => user.status === "active")
            .map((user) => `<option value="${user.id}">${user.name} (${roleLabel(user.role)})</option>`)
            .join("");
    } catch (error) {
        const staffSelect = document.getElementById("staffSelect");
        const user = API.getUser();
        if (staffSelect && user) {
            staffSelect.innerHTML = `<option value="${user.id}">${user.name}</option>`;
        }
    }
}

async function createGuest(event) {
    event.preventDefault();
    hideError("createError");

    const form = event.target;
    const user = API.getUser();
    const reminderTime = new Date(form.reminder_time.value);

    const payload = {
        title: form.title.value.trim(),
        content: form.content.value.trim() || null,
        room_id: Number(form.room_id.value),
        guest_name: form.guest_name.value.trim(),
        reminder_type: form.reminder_type.value,
        reminder_time: reminderTime.toISOString(),
        assigned_user_id: Number(form.assigned_user_id.value),
    };

    try {
        await API.createReminder(payload);
        form.reset();
        document.getElementById("createModal").classList.add("hidden");
        await loadGuestsPage();
    } catch (error) {
        showError("createError", error.message);
    }
}

async function completeReminder(reminderId) {
    try {
        await API.updateReminderStatus(reminderId, "completed");
        await loadGuestsPage();
    } catch (error) {
        showError("guestsError", error.message);
    }
}

window.completeReminder = completeReminder;
