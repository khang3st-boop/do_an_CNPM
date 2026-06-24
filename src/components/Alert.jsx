/**
 * Thay cho showError(elementId, message) / hideError(elementId) trong
 * app/static/js/api.js. Component chỉ render khi có message (tương đương
 * việc gỡ bỏ class "hidden").
 */
export default function Alert({ message }) {
  if (!message) return null;
  return <div className="alert alert-error">{message}</div>;
}
