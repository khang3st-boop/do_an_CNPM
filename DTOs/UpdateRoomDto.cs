namespace HotelManagementAPI.DTOs
{
    public class UpdateRoomDto
    {
        public string RoomNumber { get; set; }

        public string RoomType { get; set; }

        public decimal Price { get; set; }

        public string Status { get; set; }

        public string Description { get; set; }
    }
}