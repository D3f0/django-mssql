"""
ADO MSSQL database backend for Django.
Includes adodb_django, based on  adodbapi 2.1: http://adodbapi.sourceforge.net/
"""
import re

from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseOperations
import adodb_django as Database
import query # local query.py for custom classes

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError


class CursorWrapper(Database.Cursor):
    def __init__(self, connection):
        Database.Cursor.__init__(self,connection)
        self._re_limit_offset = re.compile(r'(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')
        self._re_order_limit_offset = re.compile(r'(?:ORDER BY\s+(.+?))?\s*(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')
        
    def _mangle_order_limit_offset(self, sql, order, limit, offset):
        limit = int(limit)
        offset = int(offset)
        
        # Lop off the ORDER BY ... LIMIT ... OFFSET ...
        sql_without_ORDER = self._re_order_limit_offset.sub('',sql)
        # Lop off the initial "SELECT"
        inner_sql = sql_without_ORDER.split(None, 1)[1]
        
        low = offset + 1
        high = low + limit
        
        final_sql = """SELECT * FROM ( SELECT ROW_NUMBER() OVER ( ORDER BY %(ordering)s) as my_row_number, %(rest)s) as QQQ where my_row_number between %(low)s and %(high)s""" %\
        {
            'rest': inner_sql,
            'ordering': order,
            'low': low,
            'high': high,
        }
        
        return final_sql
        
    def _mangle_limit(self, sql, limit):
        # Turn strings to ints
        limit = int(limit)
        
        # Lop off any LIMIT... from the query
        sql_without_limit = self._re_limit_offset.sub('', sql)
        
        # Cut into ['SELECT', '...rest of query...']
        sql_parts = sql_without_limit.split(None, 1)
        
        return (' TOP %s ' % limit).join(sql_parts)


    def _mangle_sql(self, sql):
        order, limit, offset = self._re_order_limit_offset.search(sql).groups()
        
        if offset is None:
            if limit is not None:
                return self._mangle_limit(sql, limit)
            else:
                return sql
        
        # Otherwise we have an OFFSET
        if order is None:
            order = ""
            #raise Exception("Offset without ORDER BY not supported (need to add the ID internally)")
                
        return self._mangle_order_limit_offset(sql, order, limit, offset)


    def _executeHelper(self, operation, isStoredProcedureCall, parameters=None):
        sql = self._mangle_sql(operation)
        Database.Cursor._executeHelper(self, sql, isStoredProcedureCall, parameters)


class DatabaseFeatures(BaseDatabaseFeatures):
    supports_tablespaces = True
    uses_custom_query_class = True

class DatabaseOperations(BaseDatabaseOperations):
    def date_extract_sql(self, lookup_type, field_name):
        return "DATEPART(%s, %s)" % (lookup_type, self.quote_name(field_name))

    def date_trunc_sql(self, lookup_type, field_name):
    	quoted_field_name = self.quote_name(field_name)
    	
        if lookup_type == 'year':
            return "Convert(datetime, Convert(varchar, DATEPART(year, %s)) + '/01/01')" % quoted_field_name
        if lookup_type == 'month':
            return "Convert(datetime, Convert(varchar, DATEPART(year, %s)) + '/' + Convert(varchar, DATEPART(month, %s)) + '/01')" % (quoted_field_name, quoted_field_name)
        if lookup_type == 'day':
            return "Convert(datetime, Convert(varchar(12), %s))" % quoted_field_name

    def last_insert_id(self, cursor, table_name, pk_name):
        cursor.execute("SELECT CAST(IDENT_CURRENT(%s) as bigint)", [self.quote_name(table_name)]) 
        return cursor.fetchone()[0]

    def query_class(self, DefaultQueryClass):
        return query.query_class(DefaultQueryClass, Database)

    def quote_name(self, name):
        if name.startswith('[') and name.endswith(']'):
            return name # already quoted
        return '[%s]' % name
        
    def random_function_sql(self):
        return 'RAND()'

    def regex_lookup(self, lookup_type):
		# Case sensitivity
		match_option = {'iregex':0, 'regex':1}[lookup_type]
		return "dbo.REGEXP_LIKE(%%s, %%s, %s)=1" % (match_option,)

    def tablespace_sql(self, tablespace, inline=False):
        return "ON %s" % self.quote_name(tablespace)


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
