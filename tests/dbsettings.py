# Common database settings for all test projects
# plus a path hack to find the backend module.

import os

DATABASE_ENGINE = 'sqlserver_ado'
DATABASE_MSSQL_REGEX = True

DATABASE_HOST =  os.environ['COMPUTERNAME'] + r'\ss2005'
DATABASE_PORT = ''
DATABASE_NAME = r'django_test_backend'

# Use integrated auth.
DATABASE_USER = ''
DATABASE_PASSWORD = ''

# Adds the relative path for the MS SQL Server backend to Python's import path.
# Note that it pops up two levels because this file is imported from modules another level down,
# not directly.
def _hack_backend_path():
	import os, sys
	backend_path = os.path.join(os.path.abspath(os.path.dirname(".")), "../../source")
	sys.path.append(backend_path)

_hack_backend_path()
