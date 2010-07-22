This project contains a Django database backend for Microsoft SQL Server 2005/2008.

== TO INSTALL ==

Copy the entire "sqlserver_ado" folder from source/ to somewhere on your Python 
path, visible to both Django and the command-line tools. This could be in 
your lib/site_packages, django/db/backends (if you don't mind mixing in 
external code), or anywhere else on the Python path.

== Django Version ==

This version of Django-mssql requires Django version 1.2+ due to the database 
backend changes made to support django multi-db support.

== References ==

  * Project site: http://code.google.com/p/django-mssql/
  * DB-API 2.0 specification: http://www.python.org/dev/peps/pep-0249/
