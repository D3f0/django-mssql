-- Enable CLR in this database
sp_configure 'show advanced options', 1;
GO
RECONFIGURE;
GO
sp_configure 'clr enabled', 1;
GO
RECONFIGURE;
GO

-- Create the assembly in the database from the path can this be done via a file path?
-- CREATE ASSEMBLY regex_clr from 'c:\Projects\django-mssql\sqlserver\regex_clr\bin\Debug\regex_clr.dll' WITH PERMISSION_SET = SAFE

-- Pull in the User Defined Function from the assembly
create function REGEXP_LIKE
(
	@input nvarchar(4000),
	@pattern nvarchar(4000),
	@caseSensitive int
) 
RETURNS INT  AS 
EXTERNAL NAME regex_clr.UserDefinedFunctions.REGEXP_LIKE
