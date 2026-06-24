from werkzeug.security import generate_password_hash
from repositories.user_repository import UserRepository

VALID_ROLES = ["admin", "manager", "staff", "housekeeping", "receptionist"]
VALID_DEPARTMENTS = ["management", "reception", "housekeeping", "maintenance", "general"]
VALID_STATUSES = ["active", "locked"]


class UserService:
    def __init__(self, db):
        self.repo = UserRepository(db)

    def get_all_users(self):
        return self.repo.get_all()

    def get_user_by_id(self, user_id: int):
        return self.repo.get_by_id(user_id)

    def update_user(self, user_id: int, email: str = None, role: str = None,
                    new_password: str = None, department: str = None,
                    current_user_role: str = "staff"):
        user = self.repo.get_by_id(user_id)
        if not user:
            return None, "Khong tim thay tai khoan"

        if role is not None:
            if current_user_role != "admin":
                return None, "Chi Admin moi co quyen thay doi vai tro"
            if role not in VALID_ROLES:
                return None, f"Vai tro khong hop le. Chon: {', '.join(VALID_ROLES)}"

        if department is not None and department not in VALID_DEPARTMENTS:
            return None, f"Bo phan khong hop le. Chon: {', '.join(VALID_DEPARTMENTS)}"

        password_hash = generate_password_hash(new_password) if new_password else None
        updated = self.repo.update(
            user_id,
            email=email,
            role=role,
            password_hash=password_hash,
            department=department,
        )
        return updated, None

    def delete_user(self, user_id: int, current_user_id: int, current_user_role: str):
        if current_user_role != "admin":
            return False, "Chi Admin moi co quyen xoa tai khoan"
        if user_id == current_user_id:
            return False, "Khong the tu xoa tai khoan cua chinh minh"
        user = self.repo.get_by_id(user_id)
        if not user:
            return False, "Khong tim thay tai khoan"
        self.repo.delete(user_id)
        return True, None

    def toggle_status(self, user_id: int, current_user_id: int, current_user_role: str):
        if current_user_role != "admin":
            return None, "Chi Admin moi co quyen khoa/mo khoa tai khoan"
        if user_id == current_user_id:
            return None, "Khong the khoa tai khoan cua chinh minh"
        user = self.repo.get_by_id(user_id)
        if not user:
            return None, "Khong tim thay tai khoan"
        new_status = "locked" if getattr(user, "Status", "active") == "active" else "active"
        return self.repo.update(user_id, status=new_status), None

    def check_permission(self, user_role: str, required_role: str) -> bool:
        hierarchy = {
            "admin": 4,
            "manager": 3,
            "housekeeping": 2,
            "receptionist": 2,
            "staff": 1,
        }
        return hierarchy.get(user_role, 0) >= hierarchy.get(required_role, 0)
