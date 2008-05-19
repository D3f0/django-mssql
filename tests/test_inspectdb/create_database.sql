IF  EXISTS (SELECT name FROM sys.databases WHERE name = N'django_test_backend')
DROP DATABASE [django_test_backend]
go

create database [django_test_backend]
go

use [django_test_backend]
GO

create table [table has spaces] (
	[Create User] [nvarchar](30) NULL DEFAULT (''),
	[Create Timestamp] [datetime] NOT NULL DEFAULT (getdate())
)
go

use [master]
go
