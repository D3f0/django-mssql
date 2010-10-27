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

create table [Software] (
	SoftwareID	bigint identity(1,1) not null,
	
	[PublicationID] [bigint] NOT NULL,
	[Version] [nvarchar](20)   NOT NULL,
	[VersionDate] [datetime] NOT NULL,
    [NewFeatures] [nvarchar](1024) NULL,
    
	CONSTRAINT [PK_Software] PRIMARY KEY (SoftwareID ASC)
)
go
