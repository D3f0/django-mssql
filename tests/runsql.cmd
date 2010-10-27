@echo off
REM USAGE:
REM runsql.cmd sql-script-file [local-sqlserver-instance]
REM SQLINSTANCE can be set to the instance to use as an
REM   environmental variable as well

pushd & setlocal

if {%SQLINSTANCE%}=={} set SQLINSTANCE=%2
if {%SQLINSTANCE%}=={} set SQLINSTANCE=ss2005
sqlcmd.exe -S localhost\%SQLINSTANCE% -E -V11 -i %1

endlocal & popd

:END
exit /b %ERRORLEVEL%
