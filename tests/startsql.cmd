@echo off
echo Starting SQL Server Express...
net start SQLBrowser
net start MSSQL$SQLEXPRESS
set SQLINSTANCE=SQLEXPRESS
