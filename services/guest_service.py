from repositories.guest_repository import GuestRepository


class GuestService:
    def __init__(self, db):
        self.repo = GuestRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, guest_id: int):
        return self.repo.get_by_id(guest_id)

    def search(self, keyword: str):
        if not keyword or not keyword.strip():
            return self.repo.get_all()
        return self.repo.search(keyword.strip())

    def create(self, full_name: str, id_card: str, phone: str,
               email: str = "", address: str = "", nationality: str = "Việt Nam"):
        error = self._validate(full_name, id_card, phone)
        if error:
            return None, error
        # Kiểm tra trùng CMND
        if id_card and self.repo.get_by_idcard(id_card):
            return None, f"Số CMND/CCCD '{id_card}' đã tồn tại trong hệ thống"
        g = self.repo.create(full_name.strip(), id_card.strip(), phone.strip(),
                             email.strip(), address.strip(), nationality.strip())
        return g, None

    def update(self, guest_id: int, full_name: str, id_card: str, phone: str,
               email: str = "", address: str = "", nationality: str = ""):
        g = self.repo.get_by_id(guest_id)
        if not g:
            return None, "Không tìm thấy khách hàng"
        error = self._validate(full_name, id_card, phone)
        if error:
            return None, error
        # Kiểm tra trùng CMND với khách khác
        existing = self.repo.get_by_idcard(id_card)
        if existing and existing.GuestID != guest_id:
            return None, f"Số CMND/CCCD '{id_card}' đã tồn tại"
        updated = self.repo.update(
            guest_id,
            FullName=full_name.strip(),
            IDCard=id_card.strip(),
            Phone=phone.strip(),
            Email=email.strip(),
            Address=address.strip(),
            Nationality=nationality.strip() or "Việt Nam"
        )
        return updated, None

    def delete(self, guest_id: int):
        g = self.repo.get_by_id(guest_id)
        if not g:
            return False, "Không tìm thấy khách hàng"
        self.repo.delete(guest_id)
        return True, None

    @staticmethod
    def _validate(full_name: str, id_card: str, phone: str):
        if not full_name or not full_name.strip():
            return "Họ tên không được để trống"
        if not id_card or not id_card.strip():
            return "Số CMND/CCCD không được để trống"
        if not phone or not phone.strip():
            return "Số điện thoại không được để trống"
        return None
