using System.ComponentModel.DataAnnotations;

namespace HotelManagementAPI.Models
{
    public class Guest
    {
        [Key]
        public int GuestId { get; set; }

        public string FullName { get; set; }

        public string IdentityNumber { get; set; }

        public string Phone { get; set; }

        public string Email { get; set; }

        public string Address { get; set; }

        public bool IsActive { get; set; } = true;
    }
}