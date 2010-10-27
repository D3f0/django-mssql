# Common database settings for all test projects
# plus a path hack to find the backend module.

import os

# use old style settings for non-django dbapi tests
DATABASE_NAME = 'django_test_backend'
DATABASE_HOST = os.environ['COMPUTERNAME'] + '\\' + os.environ.get('SQLINSTANCE', 'ss2008')
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_COMMAND_TIMEOUT = 30
DATABASE_ENGINE = 'sqlserver_ado'

# django required database settings
DATABASES = {
    'default': {
        'NAME': DATABASE_NAME,
        'ENGINE': 'sqlserver_ado',
        'HOST': DATABASE_HOST,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'COMMAND_TIMEOUT': DATABASE_COMMAND_TIMEOUT,
        'OPTIONS' : {
            #'provider': 'SQLNCLI10',
            #'extra_params': 'DataTypeCompatibility=80;MARS Connection=True;',
        },
    }
}

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
    
    settings = DATABASES.get('default', {})
    
    db_host = settings.get('HOST', '127.0.0.1')
    db_port = settings.get('PORT', '')
    db_name = settings.get('NAME', '')
    db_user = settings.get('USER', '')
    db_pass = settings.get('PASSWORD', '')
    
    if db_name == '':
        raise Exception("You need to specify a DATABASE_NAME in your Django settings file.")

    # If a port is given, force a TCP/IP connection. The host should be an IP address in this case.
    if db_port != '':
        if not _looks_like_ipaddress(db_host):
            raise Exception("When using DATABASE_PORT, DATABASE_HOST must be an IP address.")
        datasource = '%s,%s;Network Library=DBMSSOCN' % (db_host, db_port)

    # If no user is specified, use integrated security.
    if db_user != '':
        auth_string = "UID=%s;PWD=%s" % (db_user, db_pass)
    else:
        auth_string = "Integrated Security=SSPI"

    return "PROVIDER=SQLOLEDB;DATA SOURCE=%s;Initial Catalog=%s;%s" % \
        (db_host, db_name, auth_string)
