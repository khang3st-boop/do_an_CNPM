using System.ComponentModel.DataAnnotations;

namespace HotelManagementAPI.Models
{
    public class UserRole
    {
        [Key]
        public int UserRoleId { get; set; }

        public int EmployeeId { get; set; }

        public int RoleId { get; set; }

        public Employee Employee { get; set; }

        public Role Role { get; set; }
    }
}