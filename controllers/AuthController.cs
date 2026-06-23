using HotelManagementAPI.DTOs;
using HotelManagementAPI.Services;
using Microsoft.AspNetCore.Mvc;

namespace HotelManagementAPI.Controllers
{
    [ApiController]
    [Route("api/auth")]
    public class AuthController : ControllerBase
    {
        private readonly AuthService _authService;

        public AuthController(AuthService authService)
        {
            _authService = authService;
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login(
            LoginRequestDto request)
        {
            var isValid =
                await _authService.ValidateUser(
                    request.Username,
                    request.Password);

            if (!isValid)
            {
                return Unauthorized(new
                {
                    message = "Sai tài khoản hoặc mật khẩu"
                });
            }

            return Ok(new
            {
                message = "Đăng nhập thành công"
            });
        }
    }
}