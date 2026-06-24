import { useState, useEffect, useCallback } from "react";
import Sidebar from "../components/Sidebar";
import Modal from "../components/Modal";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import { useAuth } from "../context/AuthContext";
import { API } from "../api/api";
import { roleLabel } from "../utils/format";

const ROLE_OPTIONS = [
  { value: "staff", label: "Nhân viên" },
  { value: "receptionist", label: "Lễ tân" },
  { value: "housekeeping", label: "Buồng phòng" },
  { value: "technician", label: "Kỹ thuật" },
  { value: "manager", label: "Manager" },
  { value: "admin", label: "Admin" },
];

const EMPTY_FORM = {
  name: "",
  email: "",
  password: "",
  role: "staff",
  department: "",
  phone: "",
};

/**
 * Trang Phân quyền tài khoản - chuyển đổi từ templates/users.html +
 * static/js/users.js.
 *
 * Đối chiếu với users.js gốc:
 * - loadUsers() -> hàm fetchUsers (useCallback) gọi API.getUsers().
 * - createUser(event) -> handleCreateSubmit.
 * - toggleUser(userId) -> handleToggleUser.
 * - tbody.innerHTML = users.map(...) -> render <tr> trực tiếp trong JSX.
 */
export default function UsersPage() {
  const { handleUnauthorized } = useAuth();

  const [users, setUsers] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [listError, setListError] = useState("");

  // Tương đương 3 input filter: #keyword, #roleFilter, #statusFilter
  const [keyword, setKeyword] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [createError, setCreateError] = useState("");

  // Tương đương hàm loadUsers() trong users.js
  const fetchUsers = useCallback(async () => {
    setListError("");
    setLoadingList(true);

    const params = {};
    if (keyword.trim()) params.keyword = keyword.trim();
    if (roleFilter) params.role = roleFilter;
    if (statusFilter) params.status_filter = statusFilter;

    try {
      const result = await API.getUsers(params, handleUnauthorized);
      setUsers(result.data || []);
    } catch (err) {
      setListError(err.message);
      setUsers([]);
    } finally {
      setLoadingList(false);
    }
  }, [keyword, roleFilter, statusFilter, handleUnauthorized]);

  // Tương đương `await loadUsers();` trong DOMContentLoaded
  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleFormChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  // Tương đương createUser(event) trong users.js
  async function handleCreateSubmit(event) {
    event.preventDefault();
    setCreateError("");

    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      password: form.password,
      role: form.role,
      department: form.department.trim() || null,
      phone: form.phone.trim() || null,
    };

    try {
      await API.createUser(payload, handleUnauthorized);
      setForm(EMPTY_FORM);
      setModalOpen(false);
      await fetchUsers();
    } catch (err) {
      setCreateError(err.message);
    }
  }

  // Tương đương toggleUser(userId) trong users.js
  async function handleToggleUser(userId) {
    if (!window.confirm("Bạn có chắc muốn đổi trạng thái tài khoản này?")) return;

    try {
      await API.toggleUserStatus(userId, handleUnauthorized);
      await fetchUsers();
    } catch (err) {
      setListError(err.message);
    }
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
            <h1>Phân quyền tài khoản</h1>
            <p className="subtitle">N1-166 — Quản lý nhân viên và vai trò hệ thống</p>
          </div>
          <button className="btn btn-primary" onClick={() => setModalOpen(true)}>
            + Tạo tài khoản
          </button>
        </header>

        <section className="filters card">
          <input
            type="text"
            placeholder="Tìm theo tên, email, SĐT..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
            <option value="">Tất cả vai trò</option>
            {ROLE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">Tất cả trạng thái</option>
            <option value="active">Đang hoạt động</option>
            <option value="locked">Đã khóa</option>
          </select>
          <button className="btn btn-secondary" onClick={fetchUsers}>
            Lọc
          </button>
        </section>

        <section className="card">
          <Alert message={listError} />
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Họ tên</th>
                  <th>Email</th>
                  <th>Vai trò</th>
                  <th>Bộ phận</th>
                  <th>Trạng thái</th>
                  <th>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {loadingList ? (
                  <tr>
                    <td colSpan="7" className="empty">Đang tải...</td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="empty">Không có dữ liệu</td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.name}</td>
                      <td>{user.email}</td>
                      <td>{roleLabel(user.role)}</td>
                      <td>{user.department || "-"}</td>
                      <td><Badge status={user.status} /></td>
                      <td>
                        <button
                          className={`btn btn-sm ${user.status === "active" ? "btn-danger" : "btn-success"}`}
                          onClick={() => handleToggleUser(user.id)}
                        >
                          {user.status === "active" ? "Khóa" : "Mở khóa"}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <Modal open={modalOpen} onClose={closeModal} title="Tạo tài khoản nhân viên">
        <form className="form" onSubmit={handleCreateSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Họ tên</label>
              <input type="text" name="name" value={form.name} onChange={handleFormChange} required />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" name="email" value={form.email} onChange={handleFormChange} required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Mật khẩu</label>
              <input
                type="password"
                name="password"
                minLength={6}
                value={form.password}
                onChange={handleFormChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Vai trò</label>
              <select name="role" value={form.role} onChange={handleFormChange} required>
                {ROLE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Bộ phận</label>
              <input type="text" name="department" value={form.department} onChange={handleFormChange} />
            </div>
            <div className="form-group">
              <label>Số điện thoại</label>
              <input type="text" name="phone" value={form.phone} onChange={handleFormChange} />
            </div>
          </div>
          <Alert message={createError} />
          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={closeModal}>
              Hủy
            </button>
            <button type="submit" className="btn btn-primary">
              Tạo tài khoản
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
