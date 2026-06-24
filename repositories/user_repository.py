from models.user import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.query(User).order_by(User.CreatedAt.desc()).all()

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.Username == username).first()

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.UserID == user_id).first()

    def create(self, username: str, password_hash: str, email: str = "", role: str = "staff", department: str = "reception"):
        user = User(
            Username=username,
            PasswordHash=password_hash,
            Email=email,
            Role=role,
            Department=department,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: int, email: str = None, role: str = None,
               password_hash: str = None, department: str = None, status: str = None):
        user = self.get_by_id(user_id)
        if not user:
            return None
        if email is not None:
            user.Email = email
        if role is not None:
            user.Role = role
        if department is not None:
            user.Department = department
        if status is not None:
            user.Status = status
        if password_hash is not None:
            user.PasswordHash = password_hash
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int):
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
        return user

    def exists(self, username: str) -> bool:
        return self.db.query(User).filter(User.Username == username).count() > 0
