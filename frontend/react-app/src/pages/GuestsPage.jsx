import { useState, useEffect, useCallback, useMemo } from "react";
import Sidebar from "../components/Sidebar";
import Modal from "../components/Modal";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import { useAuth } from "../context/AuthContext";
import { API } from "../api/api";
import { formatDateTime, roleLabel } from "../utils/format";

const EMPTY_FORM = {
  guest_name: "",
  room_id: "",
  reminder_type: "check-in",
  reminder_time: "",
  title: "",
  content: "",
  assigned_user_id: "",
};

/**
 * Trang Thông tin khách hàng - chuyển đổi từ templates/guests.html +
 * static/js/guests.js.
 *
 * Đối chiếu với guests.js gốc:
 * - let allReminders = [] (biến module-scope) -> state `allReminders`.
 * - loadGuestsPage() -> hàm fetchReminders (useCallback).
 * - updateStats(reminders, overdue) -> tính trực tiếp qua useMemo `stats`.
 * - renderGuests() (lọc + render lại tbody) -> useMemo `filteredItems`
 *   tính lại mỗi khi keyword/type/status hoặc allReminders đổi, React tự
 *   render lại bảng - không cần gọi hàm renderGuests() thủ công nữa.
 * - loadFormOptions() -> fetchFormOptions, lưu rooms/staff vào state.
 * - createGuest(event) -> handleCreateSubmit.
 * - completeReminder(reminderId) -> handleCompleteReminder.
 */
export default function GuestsPage() {
  const { user, handleUnauthorized } = useAuth();

  const [allReminders, setAllReminders] = useState([]);
  const [overdueCount, setOverdueCount] = useState(0);
  const [loadingList, setLoadingList] = useState(true);
  const [pageError, setPageError] = useState("");

  // Tương đương 3 input filter: #keyword, #typeFilter, #statusFilter
  const [keyword, setKeyword] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const [rooms, setRooms] = useState([]);
  const [staffList, setStaffList] = useState([]);

  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [createError, setCreateError] = useState("");

  // Tương đương: createBtn.style.display = "none" khi role không đủ quyền tạo
  const canCreate = user && ["admin", "manager", "receptionist"].includes(user.role);

  // Tương đương loadGuestsPage() trong guests.js
  const fetchReminders = useCallback(async () => {
    setPageError("");
    setLoadingList(true);

    try {
      const [remindersRes, overdueRes] = await Promise.all([
        API.getReminders({}, handleUnauthorized).catch(() => ({ data: [] })),
        API.getOverdueReminders(handleUnauthorized).catch(() => ({ data: [] })),
      ]);

      let reminders = remindersRes.data || [];

      // Tương đương: if (!allReminders.length) { const myRes = await API.request("/api/reminders/my"); }
      if (!reminders.length) {
        const myRes = await API.getMyReminders(handleUnauthorized);
        reminders = myRes.data || [];
      }

      setAllReminders(reminders);
      setOverdueCount((overdueRes.data || []).length);
    } catch (err) {
      setPageError(err.message);
    } finally {
      setLoadingList(false);
    }
  }, [handleUnauthorized]);

  // Tương đương loadFormOptions() trong guests.js
  const fetchFormOptions = useCallback(async () => {
    try {
      const roomsRes = await API.getRooms(handleUnauthorized);
      const usersRes = await API.getUsers({}, handleUnauthorized).catch(() => ({ data: [] }));

      setRooms((roomsRes.data || []).filter((room) => room.status !== "inactive"));

      const staff = usersRes.data || [user];
      setStaffList(staff.filter((u) => u.status === "active"));
    } catch {
      // Tương đương catch trong loadFormOptions gốc: fallback về user hiện tại
      if (user) setStaffList([user]);
    }
  }, [handleUnauthorized, user]);

  // Tương đương phần cuối DOMContentLoaded: await loadGuestsPage();
  // và if (createBtn.style.display !== "none") { await loadFormOptions(); }
  useEffect(() => {
    fetchReminders();
    if (canCreate) {
      fetchFormOptions();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Tương đương updateStats(reminders, overdue) trong guests.js
  const stats = useMemo(() => {
    return {
      total: allReminders.length,
      checkin: allReminders.filter((item) => item.reminder_type === "check-in").length,
      checkout: allReminders.filter((item) => item.reminder_type === "check-out").length,
      overdue: overdueCount,
    };
  }, [allReminders, overdueCount]);

  // Tương đương phần lọc trong renderGuests() trong guests.js
  const filteredItems = useMemo(() => {
    let items = [...allReminders];
    const kw = keyword.trim().toLowerCase();

    if (kw) {
      items = items.filter(
        (item) =>
          (item.guest_name || "").toLowerCase().includes(kw) ||
          (item.room_number || "").toLowerCase().includes(kw)
      );
    }
    if (typeFilter) items = items.filter((item) => item.reminder_type === typeFilter);
    if (statusFilter) items = items.filter((item) => item.status === statusFilter);

    return items;
  }, [allReminders, keyword, typeFilter, statusFilter]);

  function handleFormChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  // Tương đương createGuest(event) trong guests.js
  async function handleCreateSubmit(event) {
    event.preventDefault();
    setCreateError("");

    const reminderTime = new Date(form.reminder_time);

    const payload = {
      title: form.title.trim(),
      content: form.content.trim() || null,
      room_id: Number(form.room_id),
      guest_name: form.guest_name.trim(),
      reminder_type: form.reminder_type,
      reminder_time: reminderTime.toISOString(),
      assigned_user_id: Number(form.assigned_user_id),
    };

    try {
      await API.createReminder(payload, handleUnauthorized);
      setForm(EMPTY_FORM);
      setModalOpen(false);
      await fetchReminders();
    } catch (err) {
      setCreateError(err.message);
    }
  }

  // Tương đương completeReminder(reminderId) trong guests.js
  async function handleCompleteReminder(reminderId) {
    try {
      await API.updateReminderStatus(reminderId, "completed", handleUnauthorized);
      await fetchReminders();
    } catch (err) {
      setPageError(err.message);
    }
  }

  function openModal() {
    setModalOpen(true);
    // Đảm bảo danh sách phòng/nhân viên luôn mới khi mở modal
    fetchFormOptions();
  }

  function closeModal() {
    setModalOpen(false);
    setCreateError("");
    setForm(EMPTY_FORM);
  }

  return (
    <div className="app-layout">
      <Sidebar />

      <main className="main-content">
        <header className="page-header">
          <div>
            <h1>Thông tin khách hàng</h1>
            <p className="subtitle">N1-165 — Theo dõi khách check-in / check-out theo lịch nhắc</p>
          </div>
          {/* Tương đương createBtn.style.display = "none" */}
          {canCreate && (
            <button className="btn btn-primary" onClick={openModal}>
              + Thêm lịch nhắc
            </button>
          )}
        </header>

        <section className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Tổng khách</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Check-in</span>
            <span className="stat-value">{stats.checkin}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Check-out</span>
            <span className="stat-value">{stats.checkout}</span>
          </div>
          <div className="stat-card warning">
            <span className="stat-label">Quá hạn</span>
            <span className="stat-value">{stats.overdue}</span>
          </div>
        </section>

        <section className="filters card">
          <input
            type="text"
            placeholder="Tìm theo tên khách, phòng..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="">Tất cả loại</option>
            <option value="check-in">Check-in</option>
            <option value="check-out">Check-out</option>
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">Tất cả trạng thái</option>
            <option value="pending">Chờ xử lý</option>
            <option value="in_progress">Đang xử lý</option>
            <option value="completed">Hoàn thành</option>
            <option value="cancelled">Đã hủy</option>
          </select>
          {/* Việc lọc đã là realtime qua useMemo, nút này giữ lại để đồng bộ UI gốc */}
          <button className="btn btn-secondary" onClick={() => {}}>
            Lọc
          </button>
        </section>

        <section className="card">
          <Alert message={pageError} />
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Khách hàng</th>
                  <th>Phòng</th>
                  <th>Loại</th>
                  <th>Thời gian</th>
                  <th>Nhân viên phụ trách</th>
                  <th>Trạng thái</th>
                  <th>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {loadingList ? (
                  <tr>
                    <td colSpan="7" className="empty">Đang tải...</td>
                  </tr>
                ) : filteredItems.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="empty">Không có dữ liệu</td>
                  </tr>
                ) : (
                  filteredItems.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <strong>{item.guest_name}</strong>
                        <br />
                        <small>{item.title || ""}</small>
                      </td>
                      <td>{item.room_number || item.room_id}</td>
                      <td>
                        <span className={`badge badge-${item.reminder_type}`}>
                          {item.reminder_type}
                        </span>
                      </td>
                      <td>{formatDateTime(item.reminder_time)}</td>
                      <td>{item.assigned_user_name || "-"}</td>
                      <td><Badge status={item.status} /></td>
                      <td>
                        {item.status !== "completed" ? (
                          <button
                            className="btn btn-sm btn-success"
                            onClick={() => handleCompleteReminder(item.id)}
                          >
                            Hoàn thành
                          </button>
                        ) : (
                          "-"
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <Modal open={modalOpen} onClose={closeModal} title="Thêm lịch nhắc khách hàng">
        <form className="form" onSubmit={handleCreateSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Tên khách hàng</label>
              <input
                type="text"
                name="guest_name"
                value={form.guest_name}
                onChange={handleFormChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Phòng</label>
              <select name="room_id" value={form.room_id} onChange={handleFormChange} required>
                <option value="" disabled>Chọn phòng</option>
                {rooms.map((room) => (
                  <option key={room.id} value={room.id}>
                    Phòng {room.room_number} ({room.room_type})
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Loại lịch nhắc</label>
              <select
                name="reminder_type"
                value={form.reminder_type}
                onChange={handleFormChange}
                required
              >
                <option value="check-in">Check-in</option>
                <option value="check-out">Check-out</option>
              </select>
            </div>
            <div className="form-group">
              <label>Thời gian</label>
              <input
                type="datetime-local"
                name="reminder_time"
                value={form.reminder_time}
                onChange={handleFormChange}
                required
              />
            </div>
          </div>
          <div className="form-group">
            <label>Tiêu đề</label>
            <input type="text" name="title" value={form.title} onChange={handleFormChange} required />
          </div>
          <div className="form-group">
            <label>Ghi chú</label>
            <textarea name="content" rows={2} value={form.content} onChange={handleFormChange} />
          </div>
          <div className="form-group">
            <label>Nhân viên phụ trách</label>
            <select
              name="assigned_user_id"
              value={form.assigned_user_id}
              onChange={handleFormChange}
              required
            >
              <option value="" disabled>Chọn nhân viên</option>
              {staffList.map((staff) => (
                <option key={staff.id} value={staff.id}>
                  {staff.name} ({roleLabel(staff.role)})
                </option>
              ))}
            </select>
          </div>
          <Alert message={createError} />
          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={closeModal}>
              Hủy
            </button>
            <button type="submit" className="btn btn-primary">
              Lưu
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
