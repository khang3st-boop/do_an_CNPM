using System.ComponentModel.DataAnnotations;

namespace HotelManagementAPI.Models
{
    public class Employee
    {
        [Key]
        public int EmployeeId { get; set; }

        [Required]
        public string FullName { get; set; }

        [Required]
        public string Username { get; set; }

        [Required]
        public string Password { get; set; }

        public string Email { get; set; }

        public string Phone { get; set; }

        public bool IsActive { get; set; } = true;

        public DateTime UpdatedAt { get; set; } = DateTime.Now;
    }
}