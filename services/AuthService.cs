using HotelManagementAPI.Data;
using Microsoft.EntityFrameworkCore;

namespace HotelManagementAPI.Services
{
    public class AuthService
    {
        private readonly AppDbContext _context;

        public AuthService(AppDbContext context)
        {
            _context = context;
        }

        public async Task<bool> ValidateUser(
            string username,
            string password)
        {
            var user = await _context.Employees
                .FirstOrDefaultAsync(x =>
                    x.Username == username &&
                    x.Password == password);

            return user != null;
        }
    }
}