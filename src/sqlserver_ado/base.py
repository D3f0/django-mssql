"""
ADO MSSQL database backend for Django.

Includes adodb_django, based on  adodbapi 2.1: http://adodbapi.sourceforge.net/
"""

from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseOperations
import adodb_django as Database

import re
    
DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

# We need to use a special Cursor class because adodbapi expects question-mark
# param style, but Django expects "%s". This cursor converts question marks to
# format-string style.
class CursorWrapper(Database.Cursor):
    def __init__(self, connection):
        Database.Cursor.__init__(self,connection)
        self._limit_re = re.compile(r'(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')
        
    def _executeHelper(self, operation, isStoredProcedureCall, parameters=None):
        sql = operation # So we can see the original and modified SQL in a traceback

        # Convert parameter style
        # Todo: Make this less naive; as it stands it would kill a wildcard prefix search.
        if parameters is not None and "%s" in sql:
            sql = sql.replace("%s", "?")
            
        # Look for LIMIT/OFFSET in the SQL
        limit, offset = self._limit_re.search(sql).groups()
        sql = self._limit_re.sub('', sql) 
        
        # This backend does not yet support OFFSET
        if offset is not None:
            raise Database.NotSupportedError('Offset is not supported by this backend.')
        
        # Convert a LIMIT clause to a TOP clause.
        if limit is not None: 
            limit = int(limit)
            sql = (' TOP %s ' % limit).join(sql.split(None, 1))

        Database.Cursor._executeHelper(self, sql, isStoredProcedureCall, parameters)

class DatabaseFeatures(BaseDatabaseFeatures):
    supports_tablespaces = True


class DatabaseOperations(BaseDatabaseOperations):
    def date_extract_sql(self, lookup_type, field_name):
        return "DATEPART(%s, %s)" % (lookup_type, field_name)

    def date_trunc_sql(self, lookup_type, field_name):
        if lookup_type == 'year':
            return "Convert(datetime, Convert(varchar, DATEPART(year, %s)) + '/01/01')" % field_name
        if lookup_type == 'month':
            return "Convert(datetime, Convert(varchar, DATEPART(year, %s)) + '/' + Convert(varchar, DATEPART(month, %s)) + '/01')" % (field_name, field_name)
        if lookup_type == 'day':
            return "Convert(datetime, Convert(varchar(12), %s))" % field_name

    def last_insert_id(self, cursor, table_name, pk_name):
        cursor.execute("SELECT %s FROM %s WHERE %s = @@IDENTITY" % (pk_name, table_name, pk_name))
        return cursor.fetchone()[0]

    def quote_name(self, name):
        if name.startswith('[') and name.endswith(']'):
            return name # Quoting once is enough.
        return '[%s]' % name

    def random_function_sql(self):
        return 'RAND()'

    def tablespace_sql(self, tablespace, inline=False):
        return "ON %s" % self.quote_name(tablespace)
        
    def regex_lookup(self, lookup_type):
		if settings.DATABASE_ENGINE == 'sqlserver_ado' and \
				hasattr(settings, 'DATABASE_MSSQL_REGEX') and \
				settings.DATABASE_MSSQL_REGEX:
			# Case sensitivity
			match_option = {'iregex':0, 'regex':1}[lookup_type]
				
			return "dbo.REGEXP_LIKE(%s, %s, %s)=1" % (field_sql, cast_sql, match_option)
		else:
			raise NotImplementedError


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
    features = DatabaseFeatures()
    ops = DatabaseOperations()
    operators = {
        'exact': '= %s',
        'iexact': 'LIKE %s',
        'contains': 'LIKE %s',
        'icontains': 'LIKE %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s',
        'endswith': 'LIKE %s',
        'istartswith': 'LIKE %s',
        'iendswith': 'LIKE %s',
    }

    def _cursor(self, settings):
        if self.connection is None:
            if settings.DATABASE_NAME == '':
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured("You need to specify a DATABASE_NAME in your Django settings file.")
                    
            datasource = settings.DATABASE_HOST
            if not datasource:
                datasource = "127.0.0.1"
            
            # If a port is given, force a TCP/IP connection. The host should be an IP address in this case.
            # Connection string courtesy of:
            # http://www.connectionstrings.com/?carrier=sqlserver
            if settings.DATABASE_PORT != '':
                if not _looks_like_ipaddress(datasource):
                    from django.core.exceptions import ImproperlyConfigured
                    raise ImproperlyConfigured("When using DATABASE_PORT, DATABASE_HOST must be an IP address.")
                datasource += "," + settings.DATABASE_PORT + ";Network Library=DBMSSOCN"
                
            # If no user is specified, default to integrated security.
            if settings.DATABASE_USER != '':
                auth_string = "UID=%s;PWD=%s" % (settings.DATABASE_USER, settings.DATABASE_PASSWORD)
            else:
                auth_string = "Integrated Security=SSPI"
            
            conn_string = "PROVIDER=SQLOLEDB;DATA SOURCE=%s;Initial Catalog=%s;%s" % \
                (datasource, settings.DATABASE_NAME, auth_string)
                
            self.connection = Database.connect(conn_string)
        return CursorWrapper(self.connection)
