from models.room import Room


class RoomRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.query(Room).order_by(Room.Floor.asc(), Room.RoomNumber.asc()).all()

    def get_by_id(self, room_id: int):
        return self.db.query(Room).filter(Room.RoomID == room_id).first()

    def get_by_number(self, room_number: str):
        return self.db.query(Room).filter(Room.RoomNumber == room_number).first()

    def get_by_status(self, status: str):
        return self.db.query(Room).filter(Room.Status == status).all()

    def create(self, room_number: str, room_type: str, floor: int, description: str = ""):
        room = Room(RoomNumber=room_number, RoomType=room_type, Floor=floor, Description=description)
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def update(self, room_id: int, room_type: str = None, status: str = None,
               floor: int = None, description: str = None):
        room = self.get_by_id(room_id)
        if not room:
            return None
        if room_type  is not None: room.RoomType    = room_type
        if status     is not None: room.Status      = status
        if floor      is not None: room.Floor       = floor
        if description is not None: room.Description = description
        self.db.commit()
        self.db.refresh(room)
        return room

    def delete(self, room_id: int):
        room = self.get_by_id(room_id)
        if room:
            self.db.delete(room)
            self.db.commit()
        return room
