using System.ComponentModel.DataAnnotations;

namespace HotelManagementAPI.Models
{
    public class Room
    {
        [Key]
        public int RoomId { get; set; }

        [Required]
        public string RoomNumber { get; set; }

        public string RoomType { get; set; }

        public decimal Price { get; set; }

        public string Status { get; set; }

        public string Description { get; set; }

        public DateTime UpdatedAt { get; set; } = DateTime.Now;
    }
}