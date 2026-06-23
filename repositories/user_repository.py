from models.user import User


def get_all(db):
    return db.query(User).order_by(User.id.desc()).all()


def get_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db, email):
    return db.query(User).filter(User.email == email.lower()).first()


def create(db, user):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def toggle_status(db, user):
    user.status = "locked" if user.status == "active" else "active"
    db.commit()
    db.refresh(user)
    return user

