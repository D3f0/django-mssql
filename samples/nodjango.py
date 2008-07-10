"""An example of using the internal DB-API module without any Django."""

# Adds the relative path for the MS SQL Server backend to Python's import path.
# We do this so we can run this module from a checkout for demo purposes
# without having to install it.
def _hack_backend_path():
	import os, sys
	backend_path = os.path.join(os.path.abspath(os.path.dirname(".")), "../source")
	sys.path.append(backend_path)

# Import the dbapi module, after hacking the import path.
_hack_backend_path()
import sqlserver_ado.dbapi as db

def _print_names(results):
    for item in results:
        print item[1]

def sproc_1(connection):
    "Calls a sproc using execute with explicit parameter markers."
    c = connection.cursor()
    c.execute('uspAppUser_GetAll %s', ['current_user'])
    _print_names(c.fetchall())
    c.close()

def sproc_1b(connection):
    "Calls a sproc using execute with explicit parameter markers."
    c = connection.cursor()
    c.execute('uspAppUser_GetAll %s', [None])
    _print_names(c.fetchall())
    c.close()

def sproc_2(connection):
    "Calls a sproc using 'callproc'."
    c = connection.cursor()
    c.callproc('uspAppUser_GetAll', ['current_user'])
    _print_names(c.fetchall())
    c.close()

def sproc_2b(connection):
    "Calls a sproc using 'callproc'; None isn't supported as a parameter yet."
    c = connection.cursor()
    c.callproc('uspAppUser_GetAll', [''])
    _print_names(c.fetchall())
    c.close()


def main():
    connection = db.connect("PROVIDER=SQLOLEDB;DATA SOURCE=localhost\\ss2005;Initial Catalog=Ted;Integrated Security=SSPI")
    sproc_1b(connection)
    connection.close()

main()
