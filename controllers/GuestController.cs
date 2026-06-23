using HotelManagementAPI.Models;
using Microsoft.AspNetCore.Mvc;

namespace HotelManagementAPI.Controllers
{
    [ApiController]
    [Route("api/guests")]
    public class GuestController : ControllerBase
    {
       
        [HttpDelete("{id}")]
        public IActionResult DeleteGuest(int id)
        {
            var guest = guests.FirstOrDefault(
                x => x.GuestId == id);

            if (guest == null)
            {
                return NotFound(new
                {
                    message = "Không tìm thấy khách lưu trú"
                });
            }

            guest.IsActive = false;

            return Ok(new
            {
                message = "Vô hiệu hóa khách lưu trú thành công"
            });
        }
    }
}