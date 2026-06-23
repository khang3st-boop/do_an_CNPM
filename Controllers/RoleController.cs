using HotelManagementAPI.Data;
using HotelManagementAPI.DTOs;
using HotelManagementAPI.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace HotelManagementAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class RolesController : ControllerBase
    {
        private readonly AppDbContext _context;

        public RolesController(AppDbContext context)
        {
            _context = context;
        }

        // Gán quyền
        [HttpPost("assign/{employeeId}")]
        public async Task<IActionResult> AssignRole(
            int employeeId,
            AssignRoleDto dto)
        {
            var employee =
                await _context.Employees.FindAsync(employeeId);

            if (employee == null)
                return NotFound("Không tìm thấy nhân viên");

            var role =
                await _context.Roles.FindAsync(dto.RoleId);

            if (role == null)
                return NotFound("Không tìm thấy quyền");

            var userRole = new UserRole
            {
                EmployeeId = employeeId,
                RoleId = dto.RoleId
            };

            _context.UserRoles.Add(userRole);

            await _context.SaveChangesAsync();

            return Ok(new
            {
                message = "Gán quyền thành công"
            });
        }

        // Lấy quyền của nhân viên
        [HttpGet("{employeeId}")]
        public async Task<IActionResult> GetRole(
            int employeeId)
        {
            var role = await _context.UserRoles
                .Include(x => x.Role)
                .FirstOrDefaultAsync(
                    x => x.EmployeeId == employeeId);

            if (role == null)
                return NotFound();

            return Ok(new
            {
                EmployeeId = employeeId,
                Role = role.Role.RoleName
            });
        }
    }
}