public async Task<bool> UpdateEmployee(
    int id,
    UpdateEmployeeRequest request)
{
    var employee = await _context.Employees.FindAsync(id);

    if (employee == null)
        return false;

    employee.FullName = request.FullName;
    employee.Email = request.Email;
    employee.Phone = request.Phone;
    employee.IsActive = request.IsActive;
    employee.UpdatedAt = DateTime.Now;

    await _context.SaveChangesAsync();

    return true;
}