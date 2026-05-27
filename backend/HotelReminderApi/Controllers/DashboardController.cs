using Microsoft.AspNetCore.Mvc;

namespace HotelReminderApi.Controllers;

[ApiController]
[Route("api/dashboard")]
public class DashboardController : ControllerBase
{
    [HttpGet("summary")]
    public IActionResult GetSummary()
    {
        return Ok(new
        {
            totalCustomers = 8,
            totalServices = 5,
            bookedRooms = 4,
            totalRooms = 10,
            totalBookings = 8,
            pendingReminders = 3
        });
    }

    [HttpGet("latest-bookings")]
    public IActionResult GetLatestBookings()
    {
        var bookings = new[]
        {
            new
            {
                id = 8,
                customerName = "Bùi Thị Hà",
                roomNumber = "402",
                checkInDate = "2026-06-03",
                checkOutDate = "2026-06-06",
                status = "Đã xác nhận"
            },
            new
            {
                id = 7,
                customerName = "Vũ Văn Giang",
                roomNumber = "301",
                checkInDate = "2026-06-05",
                checkOutDate = "2026-06-10",
                status = "Chờ xác nhận"
            },
            new
            {
                id = 6,
                customerName = "Đỗ Thị Phương",
                roomNumber = "203",
                checkInDate = "2026-06-02",
                checkOutDate = "2026-06-04",
                status = "Đã xác nhận"
            }
        };

        return Ok(bookings);
    }
}