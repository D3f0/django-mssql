This project contains external database backends for Django that support 
Microsoft SQL Server.

The only backend present right now is "sqlserver_ado", which is based on 
the "ado_mssql" backend that ships with Django, and is meant as a replacement.

Copy the entire "sqlserver_ado" folder from src/ to somewhere on your Python 
path, visible to both Django and the command-line tools. This could be in 
your lib/site_packages, django/db/backends (if you don't mind mixing in 
external code), or anywhere else on the Python path.
