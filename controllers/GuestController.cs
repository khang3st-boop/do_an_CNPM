using HotelManagementAPI.Models;
using Microsoft.AspNetCore.Mvc;

namespace HotelManagementAPI.Controllers
{
    [ApiController]
    [Route("api/guests")]
    public class GetGuestsController : ControllerBase
    {
        [HttpGet]
        public IActionResult GetGuests()
        {
            var result = guests
                .Where(x => x.IsActive)
                .ToList();

            return Ok(result);
        }
    }
}