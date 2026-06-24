/**
 * Thay cho statusBadge(status) trong app/static/js/api.js
 * (vốn trả về chuỗi HTML `<span class="badge badge-${status}">...`).
 */
export default function Badge({ status }) {
  return <span className={`badge badge-${status}`}>{status}</span>;
}
