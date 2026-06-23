import { render, screen } from '@testing-library/react';
import AccountTable from './AccountTable';

test('Kiểm tra bảng có hiển thị tiêu đề danh sách không', () => {
  render(<AccountTable />);
  const linkElement = screen.getByText(/Danh sách tài khoản/i);
  expect(linkElement).toBeInTheDocument();
});