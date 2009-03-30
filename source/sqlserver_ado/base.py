"""Microsoft SQL Server database backend for Django."""
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseValidation, BaseDatabaseClient
from django.db.backends.signals import connection_created
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

def connection_string_from_settings():
    from django.conf import settings
    return make_connection_string(settings)

def make_connection_string(settings):
    class wrap(object):
        def __init__(self, mapping):
            self._dict = mapping
            
        def __getattr__(self, name):
            if hasattr(self._dict, "get"):
                return self._dict.get(name)
            else:
                return getattr(self._dict, name)
            
    settings = wrap(settings) 
    
    if settings.DATABASE_NAME == '':
        raise ImproperlyConfigured("You need to specify a DATABASE_NAME in your Django settings file.")

    # Connection strings courtesy of:
    # http://www.connectionstrings.com/?carrier=sqlserver

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

    parts = [
        "PROVIDER=SQLOLEDB", 
        "DATA SOURCE="+datasource,
        "Initial Catalog="+settings.DATABASE_NAME,
        auth_string
    ]
    
    options = settings.DATABASE_OPTIONS
    if options:
        if 'use_mars' in options and options['use_mars']:
            parts.append("MultipleActiveResultSets=true")
            
        if 'extra_params' in options:
            parts.append(options['extra_params'])
        
    return ";".join(parts)

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

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        
        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()
        
        self.client = BaseDatabaseClient(self)
        self.creation = DatabaseCreation(self) 
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation()
        
    def _cursor(self):
        if self.connection is None:
            self.connection = Database.connect(make_connection_string(self.settings_dict))
            connection_created.send(sender=self.__class__)

        return Database.Cursor(self.connection)
