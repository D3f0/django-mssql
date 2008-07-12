# Common database settings for all test projects
# plus a path hack to find the backend module.

import os

DATABASE_ENGINE = 'sqlserver_ado'
DATABASE_HOST =  os.environ['COMPUTERNAME'] + '\\' + os.environ.get('SQLINSTANCE', 'ss2005')
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


def make_connection_string():
    # This function duplicates the Django connection string logic, but is meant
    # to be used by non-Django tests that want to share test db settings.
    if DATABASE_NAME == '':
        raise Exception("You need to specify a DATABASE_NAME in your Django settings file.")

    datasource = DATABASE_HOST
    if not datasource:
        datasource = "127.0.0.1"

    # If a port is given, force a TCP/IP connection. The host should be an IP address in this case.
    if DATABASE_PORT != '':
        if not _looks_like_ipaddress(datasource):
            raise Exception("When using DATABASE_PORT, DATABASE_HOST must be an IP address.")
        datasource = '%s,%s;Network Library=DBMSSOCN' % (datasource, DATABASE_PORT)

    # If no user is specified, use integrated security.
    if DATABASE_USER != '':
        auth_string = "UID=%s;PWD=%s" % (DATABASE_USER, DATABASE_PASSWORD)
    else:
        auth_string = "Integrated Security=SSPI"

    return "PROVIDER=SQLOLEDB;DATA SOURCE=%s;Initial Catalog=%s;%s" % \
        (datasource, DATABASE_NAME, auth_string)
