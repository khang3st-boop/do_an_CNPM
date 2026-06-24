/**
 * Component Modal tái sử dụng - thay cho hàm setupModal() trong
 * app/static/js/api.js (thêm/xóa class "hidden" bằng DOM thủ công).
 * Ở đây trạng thái mở/đóng do component cha quản lý qua prop `open`.
 */
export default function Modal({ open, onClose, title, children }) {
  if (!open) return null;

  return (
    <div className="modal">
      <div className="modal-backdrop" onClick={onClose} />
      <div className="modal-content card">
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="modal-close" type="button" onClick={onClose}>
            &times;
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
