using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HotelManagementAPI.Data;
using HotelManagementAPI.DTOs;

namespace HotelManagementAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class EmployeesController : ControllerBase
    {
        private readonly AppDbContext _context;

        public EmployeesController(AppDbContext context)
        {
            _context = context;
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateEmployee(
            int id,
            UpdateEmployeeDto dto)
        {
            var employee = await _context.Employees
                .FirstOrDefaultAsync(x => x.EmployeeId == id);

            if (employee == null)
            {
                return NotFound(new
                {
                    message = "Không tìm thấy nhân viên"
                });
            }

            employee.FullName = dto.FullName;
            employee.Email = dto.Email;
            employee.Phone = dto.Phone;
            employee.IsActive = dto.IsActive;
            employee.UpdatedAt = DateTime.Now;

            await _context.SaveChangesAsync();

            return Ok(new
            {
                message = "Cập nhật thành công"
            });
        }
    }
}