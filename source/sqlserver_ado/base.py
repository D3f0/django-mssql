"""Microsoft SQL Server database backend for Django."""
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseValidation, BaseDatabaseClient

from django.core.exceptions import ImproperlyConfigured

import dbapi as Database

from introspection import DatabaseIntrospection
from creation import DatabaseCreation
from operations import DatabaseOperations

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError


class DatabaseFeatures(BaseDatabaseFeatures):
    uses_custom_query_class = True

# IP Address recognizer taken from:
# http://mail.python.org/pipermail/python-list/2006-March/375505.html
def _looks_like_ipaddress(address):
    dots = address.split(".")
    if len(dots) != 4:
        return False
    for item in dots:
        if not 0 <= int(item) <= 255:
            return False
    return True

class DatabaseWrapper(BaseDatabaseWrapper):
    operators = {
        "exact": "= %s",
        "iexact": "LIKE %s ESCAPE '\\'",
        "contains": "LIKE %s ESCAPE '\\'",
        "icontains": "LIKE %s ESCAPE '\\'",
        "gt": "> %s",
        "gte": ">= %s",
        "lt": "< %s",
        "lte": "<= %s",
        "startswith": "LIKE %s ESCAPE '\\'",
        "endswith": "LIKE %s ESCAPE '\\'",
        "istartswith": "LIKE %s ESCAPE '\\'",
        "iendswith": "LIKE %s ESCAPE '\\'",
    }

    def __init__(self, **kwargs):
        super(DatabaseWrapper, self).__init__(**kwargs)
        
        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()
        
        self.client = BaseDatabaseClient()
        self.creation = DatabaseCreation(self) 
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation()
        

    def _cursor(self, settings):
        # Connection strings courtesy of:
        # http://www.connectionstrings.com/?carrier=sqlserver

        if self.connection is None:
            if settings.DATABASE_NAME == '':
                raise ImproperlyConfigured("You need to specify a DATABASE_NAME in your Django settings file.")

            datasource = settings.DATABASE_HOST
            if not datasource:
                datasource = "127.0.0.1"

            # If a port is given, force a TCP/IP connection. The host should be an IP address in this case.
            if settings.DATABASE_PORT != '':
                if not _looks_like_ipaddress(datasource):
                    raise ImproperlyConfigured("When using DATABASE_PORT, DATABASE_HOST must be an IP address.")
                datasource = '%s,%s;Network Library=DBMSSOCN' % (datasource, settings.DATABASE_PORT)

            # If no user is specified, use integrated security.
            if settings.DATABASE_USER != '':
                auth_string = "UID=%s;PWD=%s" % (settings.DATABASE_USER, settings.DATABASE_PASSWORD)
            else:
                auth_string = "Integrated Security=SSPI"

            conn_string = "PROVIDER=SQLOLEDB;DATA SOURCE=%s;Initial Catalog=%s;%s" % \
                (datasource, settings.DATABASE_NAME, auth_string)

            self.connection = Database.connect(conn_string)

        return Database.Cursor(self.connection)
