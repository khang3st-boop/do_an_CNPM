using Microsoft.AspNetCore.Mvc;

namespace HotelReminderApi.Controllers;

[ApiController]
[Route("api/reminders")]
public class ReminderController : ControllerBase
{
    private static readonly List<Reminder> Reminders = new()
    {
        new Reminder
        {
            Id = 1,
            Title = "Nhắc khách check-out",
            Content = "Phòng 101 cần check-out trước 12h.",
            RoomNumber = "101",
            ReminderTime = DateTime.Now.AddHours(2),
            AssignedTo = "Lễ tân",
            Status = "pending"
        },
        new Reminder
        {
            Id = 2,
            Title = "Nhắc dọn phòng",
            Content = "Phòng 202 cần dọn sau khi khách trả phòng.",
            RoomNumber = "202",
            ReminderTime = DateTime.Now.AddHours(3),
            AssignedTo = "Nhân viên dọn phòng",
            Status = "processing"
        }
    };

    [HttpGet]
    public IActionResult GetAll()
    {
        return Ok(Reminders);
    }

    [HttpGet("{id}")]
    public IActionResult GetById(int id)
    {
        var reminder = Reminders.FirstOrDefault(x => x.Id == id);

        if (reminder == null)
        {
            return NotFound(new
            {
                message = "Không tìm thấy thông báo nhắc lịch"
            });
        }

        return Ok(reminder);
    }

    [HttpPost]
    public IActionResult Create([FromBody] Reminder request)
    {
        request.Id = Reminders.Count + 1;
        request.Status = "pending";

        Reminders.Add(request);

        return Ok(new
        {
            message = "Tạo thông báo nhắc lịch thành công",
            data = request
        });
    }

    [HttpPut("{id}/status")]
    public IActionResult UpdateStatus(int id, [FromBody] UpdateReminderStatusRequest request)
    {
        var reminder = Reminders.FirstOrDefault(x => x.Id == id);

        if (reminder == null)
        {
            return NotFound(new
            {
                message = "Không tìm thấy thông báo nhắc lịch"
            });
        }

        reminder.Status = request.Status;

        return Ok(new
        {
            message = "Cập nhật trạng thái thành công",
            data = reminder
        });
    }

    [HttpGet("filter")]
    public IActionResult Filter([FromQuery] string? roomNumber, [FromQuery] string? status)
    {
        var query = Reminders.AsQueryable();

        if (!string.IsNullOrWhiteSpace(roomNumber))
        {
            query = query.Where(x => x.RoomNumber == roomNumber);
        }

        if (!string.IsNullOrWhiteSpace(status))
        {
            query = query.Where(x => x.Status == status);
        }

        return Ok(query.ToList());
    }
}

public class Reminder
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public string RoomNumber { get; set; } = string.Empty;
    public DateTime ReminderTime { get; set; }
    public string AssignedTo { get; set; } = string.Empty;
    public string Status { get; set; } = "pending";
}

public class UpdateReminderStatusRequest
{
    public string Status { get; set; } = string.Empty;
}