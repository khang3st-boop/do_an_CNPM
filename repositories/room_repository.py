from models.room import Room


def get_active(db):
    return (
        db.query(Room)
        .filter(Room.is_active == True, Room.status != "inactive")
        .order_by(Room.room_number.asc())
        .all()
    )


def get_all(db):
    return db.query(Room).order_by(Room.room_number.asc()).all()


def get_by_id(db, room_id):
    return db.query(Room).filter(Room.id == room_id).first()


def get_by_room_number(db, room_number):
    return db.query(Room).filter(Room.room_number == room_number).first()


def create(db, room):
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def deactivate(db, room):
    room.status = "inactive"
    room.is_active = False
    db.commit()
    db.refresh(room)
    return room

