using System.ComponentModel.DataAnnotations;

namespace HotelManagementAPI.Models
{
    public class Role
    {
        [Key]
        public int RoleId { get; set; }

        public string RoleName { get; set; }
    }
}