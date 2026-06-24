from werkzeug.security import generate_password_hash, check_password_hash
from repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db):
        self.repo = UserRepository(db)

    def login(self, username: str, password: str):
        """Kiểm tra thông tin đăng nhập. Trả về User nếu hợp lệ, None nếu sai."""
        user = self.repo.get_by_username(username)
        if user and check_password_hash(user.PasswordHash, password):
            return user
        return None

    def create_user(self, username: str, password: str, email: str = "", role: str = "staff"):
        """Tạo tài khoản mới với password đã hash."""
        if self.repo.exists(username):
            return None, "Tên đăng nhập đã tồn tại"
        hashed = generate_password_hash(password)
        user = self.repo.create(username, hashed, email, role)
        return user, None

    def get_user_by_id(self, user_id: int):
        return self.repo.get_by_id(user_id)
