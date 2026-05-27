using Microsoft.AspNetCore.Mvc;

namespace HotelReminderAPI.Controllers
{
    [Route("api/reminders")]
    [ApiController]
    public class ReminderController : ControllerBase
    {
        private static List<Reminder> reminders = new List<Reminder>
        {
            new Reminder
            {
                Id = 1,
                Title = "Nhắc khách check-out",
                Content = "Phòng 101 cần check-out trước 12h",
                RoomNumber = "101",
                ReminderTime = DateTime.Now.AddHours(2),
                AssignedTo = "Lễ tân",
                Status = "pending"
            },
            new Reminder
            {
                Id = 2,
                Title = "Nhắc dọn phòng",
                Content = "Phòng 202 cần được dọn sau khi khách trả phòng",
                RoomNumber = "202",
                ReminderTime = DateTime.Now.AddHours(3),
                AssignedTo = "Nhân viên dọn phòng",
                Status = "processing"
            }
        };

        [HttpGet]
        public IActionResult GetAllReminders()
        {
            return Ok(reminders);
        }

        [HttpGet("{id}")]
        public IActionResult GetReminderById(int id)
        {
            var reminder = reminders.FirstOrDefault(r => r.Id == id);

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
        public IActionResult CreateReminder([FromBody] Reminder reminder)
        {
            reminder.Id = reminders.Count + 1;
            reminder.Status = "pending";

            reminders.Add(reminder);

            return Ok(new
            {
                message = "Tạo thông báo nhắc lịch thành công",
                data = reminder
            });
        }

        [HttpPut("{id}/status")]
        public IActionResult UpdateReminderStatus(int id, [FromBody] ReminderStatusUpdate request)
        {
            var reminder = reminders.FirstOrDefault(r => r.Id == id);

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
        public IActionResult FilterReminders([FromQuery] string? roomNumber, [FromQuery] string? status)
        {
            var result = reminders.AsQueryable();

            if (!string.IsNullOrEmpty(roomNumber))
            {
                result = result.Where(r => r.RoomNumber == roomNumber);
            }

            if (!string.IsNullOrEmpty(status))
            {
                result = result.Where(r => r.Status == status);
            }

            return Ok(result.ToList());
        }
    }

    public class Reminder
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Content { get; set; }
        public string RoomNumber { get; set; }
        public DateTime ReminderTime { get; set; }
        public string AssignedTo { get; set; }
        public string Status { get; set; }
    }

    public class ReminderStatusUpdate
    {
        public string Status { get; set; }
    }
}