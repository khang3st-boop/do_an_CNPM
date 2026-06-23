using HotelManagementAPI.DTOs;
using HotelManagementAPI.Models;
using Microsoft.AspNetCore.Mvc;

namespace HotelManagementAPI.Controllers
{
    [ApiController]
    [Route("api/rooms")]
    public class RoomsController : ControllerBase
    {
        // Fake data để demo
        private static List<Room> rooms = new List<Room>()
        {
            new Room
            {
                RoomId = 1,
                RoomNumber = "A101",
                RoomType = "Standard",
                Price = 500000,
                Status = "Available",
                Description = "Phòng tiêu chuẩn"
            },
            new Room
            {
                RoomId = 2,
                RoomNumber = "B201",
                RoomType = "VIP",
                Price = 1200000,
                Status = "Occupied",
                Description = "Phòng VIP"
            }
        };

        [HttpPut("{id}")]
        public IActionResult UpdateRoom(
            int id,
            UpdateRoomDto dto)
        {
            var room = rooms.FirstOrDefault(
                r => r.RoomId == id);

            if (room == null)
            {
                return NotFound(new
                {
                    message = "Không tìm thấy phòng"
                });
            }

            room.RoomNumber = dto.RoomNumber;
            room.RoomType = dto.RoomType;
            room.Price = dto.Price;
            room.Status = dto.Status;
            room.Description = dto.Description;
            room.UpdatedAt = DateTime.Now;

            return Ok(new
            {
                message = "Cập nhật phòng thành công",
                room
            });
        }
    }
}