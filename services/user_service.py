from werkzeug.security import generate_password_hash
from repositories.user_repository import UserRepository

# Danh sách role hợp lệ (N1-13: phân quyền)
VALID_ROLES = ["admin", "manager", "staff"]


class UserService:
    def __init__(self, db):
        self.repo = UserRepository(db)

    # ── N1-12: Quản lý tài khoản nhân viên ──────────────────────────

    def get_all_users(self):
        return self.repo.get_all()

    def get_user_by_id(self, user_id: int):
        return self.repo.get_by_id(user_id)

    def update_user(self, user_id: int, email: str = None, role: str = None, new_password: str = None, current_user_role: str = "staff"):
        """Cập nhật thông tin nhân viên. Chỉ admin/manager mới được đổi role."""
        user = self.repo.get_by_id(user_id)
        if not user:
            return None, "Không tìm thấy tài khoản"

        # N1-13: Chỉ admin mới được đổi role
        if role is not None:
            if current_user_role != "admin":
                return None, "Chỉ Admin mới có quyền thay đổi vai trò"
            if role not in VALID_ROLES:
                return None, f"Vai trò không hợp lệ. Chọn: {', '.join(VALID_ROLES)}"

        password_hash = generate_password_hash(new_password) if new_password else None
        updated = self.repo.update(user_id, email=email, role=role, password_hash=password_hash)
        return updated, None

    def delete_user(self, user_id: int, current_user_id: int, current_user_role: str):
        """Xóa tài khoản. Chỉ admin mới được xóa, không được tự xóa chính mình."""
        if current_user_role != "admin":
            return False, "Chỉ Admin mới có quyền xóa tài khoản"
        if user_id == current_user_id:
            return False, "Không thể tự xóa tài khoản của chính mình"
        user = self.repo.get_by_id(user_id)
        if not user:
            return False, "Không tìm thấy tài khoản"
        self.repo.delete(user_id)
        return True, None

    # ── N1-13: Phân quyền ────────────────────────────────────────────

    def check_permission(self, user_role: str, required_role: str) -> bool:
        """Kiểm tra quyền theo thứ tự: admin > manager > staff."""
        hierarchy = {"admin": 3, "manager": 2, "staff": 1}
        return hierarchy.get(user_role, 0) >= hierarchy.get(required_role, 0)
