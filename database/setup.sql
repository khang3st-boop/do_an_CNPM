-- HotelReminderDB setup script
-- Chạy trong SQL Server Management Studio (SSMS).
-- Script này idempotent: chạy lại không bị lỗi trùng bảng/cột/khóa ngoại.

IF DB_ID(N'HotelReminderDB') IS NULL
BEGIN
    CREATE DATABASE HotelReminderDB;
    PRINT N'Database HotelReminderDB đã được tạo.';
END
GO

USE HotelReminderDB;
GO

IF OBJECT_ID(N'dbo.Users', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Users (
        UserID       INT IDENTITY(1,1) PRIMARY KEY,
        Username     NVARCHAR(50)  NOT NULL UNIQUE,
        PasswordHash NVARCHAR(256) NOT NULL,
        Email        NVARCHAR(100) NULL,
        Role         NVARCHAR(20)  NOT NULL DEFAULT N'staff',
        Department   NVARCHAR(50)  NOT NULL DEFAULT N'reception',
        Status       NVARCHAR(20)  NOT NULL DEFAULT N'active',
        CreatedAt    DATETIME2     NOT NULL DEFAULT SYSDATETIME()
    );
    PRINT N'Bảng Users đã được tạo.';
END
GO

IF COL_LENGTH(N'dbo.Users', N'Department') IS NULL
    ALTER TABLE dbo.Users ADD Department NVARCHAR(50) NOT NULL CONSTRAINT DF_Users_Department DEFAULT N'reception';
GO

IF COL_LENGTH(N'dbo.Users', N'Status') IS NULL
    ALTER TABLE dbo.Users ADD Status NVARCHAR(20) NOT NULL CONSTRAINT DF_Users_Status DEFAULT N'active';
GO

UPDATE dbo.Users
SET Department = N'management'
WHERE Role IN (N'admin', N'manager') AND (Department IS NULL OR Department = N'reception');
GO

UPDATE dbo.Users
SET Department = N'housekeeping'
WHERE Role = N'housekeeping' AND (Department IS NULL OR Department = N'reception');
GO

IF OBJECT_ID(N'dbo.Rooms', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Rooms (
        RoomID      INT IDENTITY(1,1) PRIMARY KEY,
        RoomNumber  NVARCHAR(20)  NOT NULL UNIQUE,
        RoomType    NVARCHAR(50)  NULL,
        Status      NVARCHAR(20)  NOT NULL DEFAULT N'available',
        Floor       INT           NULL,
        Description NVARCHAR(500) NULL,
        CreatedAt   DATETIME2     NOT NULL DEFAULT SYSDATETIME()
    );
    PRINT N'Bảng Rooms đã được tạo.';
END
GO

IF OBJECT_ID(N'dbo.Guests', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Guests (
        GuestID     INT IDENTITY(1,1) PRIMARY KEY,
        FullName    NVARCHAR(100) NOT NULL,
        IDCard      NVARCHAR(20)  NULL UNIQUE,
        Phone       NVARCHAR(20)  NULL,
        Email       NVARCHAR(100) NULL,
        Address     NVARCHAR(300) NULL,
        Nationality NVARCHAR(50)  NOT NULL DEFAULT N'Việt Nam',
        CreatedAt   DATETIME2     NOT NULL DEFAULT SYSDATETIME()
    );
    PRINT N'Bảng Guests đã được tạo.';
END
GO

IF OBJECT_ID(N'dbo.Bookings', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Bookings (
        BookingID  INT IDENTITY(1,1) PRIMARY KEY,
        GuestID    INT NOT NULL,
        RoomID     INT NOT NULL,
        CheckIn    DATETIME2 NOT NULL,
        CheckOut   DATETIME2 NOT NULL,
        Status     NVARCHAR(30) NOT NULL DEFAULT N'confirmed',
        Notes      NVARCHAR(500) NULL,
        TotalPrice DECIMAL(12,2) NOT NULL DEFAULT 0,
        CreatedAt  DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_Bookings_Guests FOREIGN KEY (GuestID) REFERENCES dbo.Guests(GuestID),
        CONSTRAINT FK_Bookings_Rooms  FOREIGN KEY (RoomID)  REFERENCES dbo.Rooms(RoomID)
    );
    PRINT N'Bảng Bookings đã được tạo.';
END
GO

IF OBJECT_ID(N'dbo.Reminders', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Reminders (
        ReminderID   INT IDENTITY(1,1) PRIMARY KEY,
        UserID       INT NOT NULL,
        BookingID    INT NULL,
        Title        NVARCHAR(200) NOT NULL,
        Description  NVARCHAR(500) NULL,
        ReminderType NVARCHAR(30)  NOT NULL DEFAULT N'custom',
        ReminderTime DATETIME2     NOT NULL,
        Status       NVARCHAR(50)  NOT NULL DEFAULT N'Chưa đến hạn',
        CreatedAt    DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_Reminders_Users    FOREIGN KEY (UserID)    REFERENCES dbo.Users(UserID) ON DELETE CASCADE,
        CONSTRAINT FK_Reminders_Bookings FOREIGN KEY (BookingID) REFERENCES dbo.Bookings(BookingID)
    );
    PRINT N'Bảng Reminders đã được tạo.';
END
GO

-- Bổ sung cột cho DB cũ nếu đã tạo bằng script bản cũ
IF COL_LENGTH(N'dbo.Reminders', N'BookingID') IS NULL
    ALTER TABLE dbo.Reminders ADD BookingID INT NULL;
GO
IF COL_LENGTH(N'dbo.Reminders', N'ReminderType') IS NULL
    ALTER TABLE dbo.Reminders ADD ReminderType NVARCHAR(30) NOT NULL CONSTRAINT DF_Reminders_ReminderType DEFAULT N'custom';
GO
IF COL_LENGTH(N'dbo.Reminders', N'Status') IS NOT NULL
BEGIN
    -- Giữ nguyên dữ liệu, chỉ bảo đảm độ dài đủ cho các trạng thái tiếng Việt
    IF EXISTS (
        SELECT 1 FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        WHERE c.object_id = OBJECT_ID(N'dbo.Reminders') AND c.name = N'Status' AND c.max_length < 100
    )
    BEGIN
        ALTER TABLE dbo.Reminders ALTER COLUMN Status NVARCHAR(50) NOT NULL;
    END
END
GO

IF OBJECT_ID(N'dbo.FK_Reminders_Bookings', N'F') IS NULL
BEGIN
    ALTER TABLE dbo.Reminders
    ADD CONSTRAINT FK_Reminders_Bookings FOREIGN KEY (BookingID) REFERENCES dbo.Bookings(BookingID);
END
GO

IF OBJECT_ID(N'dbo.Notifications', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Notifications (
        NotificationID INT IDENTITY(1,1) PRIMARY KEY,
        ReminderID     INT NOT NULL,
        SentTime       DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        Status         NVARCHAR(20) NOT NULL DEFAULT N'sent',
        IsRead         INT NOT NULL DEFAULT 0,
        CONSTRAINT FK_Notifications_Reminders FOREIGN KEY (ReminderID) REFERENCES dbo.Reminders(ReminderID) ON DELETE CASCADE
    );
    PRINT N'Bảng Notifications đã được tạo.';
END
GO
IF COL_LENGTH(N'dbo.Notifications', N'IsRead') IS NULL
    ALTER TABLE dbo.Notifications ADD IsRead INT NOT NULL CONSTRAINT DF_Notifications_IsRead DEFAULT 0;
GO

IF OBJECT_ID(N'dbo.InternalNotifications', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.InternalNotifications (
        NotifID    INT IDENTITY(1,1) PRIMARY KEY,
        FromUserID INT NOT NULL,
        ToUserID   INT NULL,
        ToDepartment NVARCHAR(50) NULL,
        Title      NVARCHAR(200)  NOT NULL,
        Content    NVARCHAR(1000) NOT NULL,
        IsRead     BIT NOT NULL DEFAULT 0,
        Priority   NVARCHAR(20) NOT NULL DEFAULT N'normal',
        CreatedAt  DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_InternalNotifications_FromUser FOREIGN KEY (FromUserID) REFERENCES dbo.Users(UserID),
        CONSTRAINT FK_InternalNotifications_ToUser   FOREIGN KEY (ToUserID)   REFERENCES dbo.Users(UserID)
    );
    PRINT N'Bảng InternalNotifications đã được tạo.';
END
GO

IF COL_LENGTH(N'dbo.InternalNotifications', N'ToDepartment') IS NULL
    ALTER TABLE dbo.InternalNotifications ADD ToDepartment NVARCHAR(50) NULL;
GO

IF OBJECT_ID(N'dbo.InternalNotificationReads', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.InternalNotificationReads (
        ReadID INT IDENTITY(1,1) PRIMARY KEY,
        NotifID INT NOT NULL,
        UserID INT NOT NULL,
        ReadAt DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_InternalNotificationReads_Notif FOREIGN KEY (NotifID) REFERENCES dbo.InternalNotifications(NotifID) ON DELETE CASCADE,
        CONSTRAINT FK_InternalNotificationReads_User FOREIGN KEY (UserID) REFERENCES dbo.Users(UserID),
        CONSTRAINT UQ_InternalNotificationReads UNIQUE (NotifID, UserID)
    );
    PRINT N'Bảng InternalNotificationReads đã được tạo.';
END
GO

IF OBJECT_ID(N'dbo.GuestNotifications', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.GuestNotifications (
        GuestNotifID INT IDENTITY(1,1) PRIMARY KEY,
        BookingID    INT NOT NULL,
        Subject      NVARCHAR(200) NOT NULL,
        Content      NVARCHAR(MAX) NOT NULL,
        Channel      NVARCHAR(30) NOT NULL DEFAULT N'system',
        Status       NVARCHAR(20) NOT NULL DEFAULT N'sent',
        SentAt       DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CreatedAt    DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_GuestNotifications_Bookings FOREIGN KEY (BookingID) REFERENCES dbo.Bookings(BookingID)
    );
    PRINT N'Bảng GuestNotifications đã được tạo.';
END
GO

IF OBJECT_ID(N'dbo.HousekeepingTasks', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.HousekeepingTasks (
        TaskID       INT IDENTITY(1,1) PRIMARY KEY,
        RoomID       INT NOT NULL,
        AssignedToID INT NULL,
        TaskType     NVARCHAR(50) NOT NULL,
        Status       NVARCHAR(30) NOT NULL DEFAULT N'pending',
        Priority     NVARCHAR(20) NOT NULL DEFAULT N'normal',
        Description  NVARCHAR(MAX) NULL,
        ResultNote   NVARCHAR(MAX) NULL,
        ScheduledAt  DATETIME2 NOT NULL,
        CompletedAt  DATETIME2 NULL,
        CreatedAt    DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT FK_HousekeepingTasks_Rooms FOREIGN KEY (RoomID) REFERENCES dbo.Rooms(RoomID),
        CONSTRAINT FK_HousekeepingTasks_Users FOREIGN KEY (AssignedToID) REFERENCES dbo.Users(UserID)
    );
    PRINT N'Bảng HousekeepingTasks đã được tạo.';
END
GO

IF COL_LENGTH(N'dbo.HousekeepingTasks', N'ResultNote') IS NULL
    ALTER TABLE dbo.HousekeepingTasks ADD ResultNote NVARCHAR(MAX) NULL;
GO

PRINT N'Setup hoàn tất!';
GO
