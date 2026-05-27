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
            Type = "Check-out",
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
            Type = "Dọn phòng",
            Status = "processing"
        },
        new Reminder
        {
            Id = 3,
            Title = "Nhắc bảo trì phòng",
            Content = "Phòng 305 cần kiểm tra máy lạnh.",
            RoomNumber = "305",
            ReminderTime = DateTime.Now.AddDays(1),
            AssignedTo = "Nhân viên bảo trì",
            Type = "Bảo trì",
            Status = "pending"
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
        request.Id = Reminders.Count == 0 ? 1 : Reminders.Max(x => x.Id) + 1;
        request.Status = string.IsNullOrWhiteSpace(request.Status) ? "pending" : request.Status;

        Reminders.Add(request);

        return Ok(new
        {
            message = "Tạo thông báo nhắc lịch thành công",
            data = request
        });
    }

    [HttpPut("{id}")]
    public IActionResult Update(int id, [FromBody] Reminder request)
    {
        var reminder = Reminders.FirstOrDefault(x => x.Id == id);

        if (reminder == null)
        {
            return NotFound(new
            {
                message = "Không tìm thấy thông báo nhắc lịch"
            });
        }

        reminder.Title = request.Title;
        reminder.Content = request.Content;
        reminder.RoomNumber = request.RoomNumber;
        reminder.ReminderTime = request.ReminderTime;
        reminder.AssignedTo = request.AssignedTo;
        reminder.Type = request.Type;
        reminder.Status = request.Status;

        return Ok(new
        {
            message = "Cập nhật thông báo thành công",
            data = reminder
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

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        var reminder = Reminders.FirstOrDefault(x => x.Id == id);

        if (reminder == null)
        {
            return NotFound(new
            {
                message = "Không tìm thấy thông báo nhắc lịch"
            });
        }

        Reminders.Remove(reminder);

        return Ok(new
        {
            message = "Xóa thông báo nhắc lịch thành công"
        });
    }

    [HttpGet("filter")]
    public IActionResult Filter([FromQuery] string? roomNumber, [FromQuery] string? status, [FromQuery] string? type)
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

        if (!string.IsNullOrWhiteSpace(type))
        {
            query = query.Where(x => x.Type == type);
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
    public string Type { get; set; } = string.Empty;
    public string Status { get; set; } = "pending";
}

public class UpdateReminderStatusRequest
{
    public string Status { get; set; } = string.Empty;
}