from models.guest import Guest


def get_all(db):
    return db.query(Guest).order_by(Guest.id.desc()).all()


def get_by_id(db, guest_id):
    return db.query(Guest).filter(Guest.id == guest_id).first()


def create(db, guest):
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest


def update(db, guest, data):
    for field, value in data.items():
        setattr(guest, field, value)
    db.commit()
    db.refresh(guest)
    return guest

