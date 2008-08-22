/*
This script adds Regex support to SQL Server via the VBScript.RegExp object.
To use this object, OLE Automation needs to be enabled on the server, as 
described here:
    http://msdn2.microsoft.com/en-us/library/ms191188.aspx

with these SQL statements:
*/

sp_configure 'show advanced options', 1;
GO
RECONFIGURE;
GO
sp_configure 'Ole Automation Procedures', 1;
GO
RECONFIGURE;
GO
