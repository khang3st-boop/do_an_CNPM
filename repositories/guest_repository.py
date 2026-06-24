from models.guest import Guest


class GuestRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.query(Guest).order_by(Guest.CreatedAt.desc()).all()

    def get_by_id(self, guest_id: int):
        return self.db.query(Guest).filter(Guest.GuestID == guest_id).first()

    def get_by_idcard(self, id_card: str):
        return self.db.query(Guest).filter(Guest.IDCard == id_card).first()

    def search(self, keyword: str):
        kw = f"%{keyword}%"
        return (
            self.db.query(Guest)
            .filter(
                Guest.FullName.ilike(kw)
                | Guest.Phone.ilike(kw)
                | Guest.IDCard.ilike(kw)
                | Guest.Email.ilike(kw)
            )
            .all()
        )

    def create(self, full_name: str, id_card: str, phone: str, email: str,
               address: str, nationality: str):
        g = Guest(
            FullName=full_name, IDCard=id_card, Phone=phone,
            Email=email, Address=address, Nationality=nationality
        )
        self.db.add(g)
        self.db.commit()
        self.db.refresh(g)
        return g

    def update(self, guest_id: int, **kwargs):
        g = self.get_by_id(guest_id)
        if not g:
            return None
        for field, value in kwargs.items():
            if value is not None:
                setattr(g, field, value)
        self.db.commit()
        self.db.refresh(g)
        return g

    def delete(self, guest_id: int):
        g = self.get_by_id(guest_id)
        if g:
            self.db.delete(g)
            self.db.commit()
        return g
