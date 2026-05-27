using Microsoft.AspNetCore.Mvc;

namespace HotelReminderApi.Controllers;

[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        if (request.Email == "admin@gmail.com" && request.Password == "123456")
        {
            return Ok(new
            {
                message = "Đăng nhập thành công",
                user = new
                {
                    id = 1,
                    fullName = "Quản trị viên",
                    email = request.Email,
                    role = "Admin"
                },
                token = "demo-token"
            });
        }

        return Unauthorized(new
        {
            message = "Email hoặc mật khẩu không đúng"
        });
    }

    [HttpPost("logout")]
    public IActionResult Logout()
    {
        return Ok(new
        {
            message = "Đăng xuất thành công"
        });
    }
}

public class LoginRequest
{
    public string Email { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}