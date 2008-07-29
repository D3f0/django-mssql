"""
Microsoft SQL Server database backend for Django.

"dbapi.py" is a DB-API 2 interface based on adodbapi 2.1:
    http://adodbapi.sourceforge.net/
"""
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseOperations
from django.core.exceptions import ImproperlyConfigured

import dbapi as Database
import query

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError


class DatabaseFeatures(BaseDatabaseFeatures):
    supports_tablespaces = True
    uses_custom_query_class = True
    allows_unique_and_pk = False

class DatabaseOperations(BaseDatabaseOperations):
    def date_extract_sql(self, lookup_type, field_name):
        return "DATEPART(%s, %s)" % (lookup_type, self.quote_name(field_name))

    def date_trunc_sql(self, lookup_type, field_name):
    	quoted_field_name = self.quote_name(field_name)

        if lookup_type == 'year':
            return "Convert(datetime, Convert(varchar, DATEPART(year, %s)) + '/01/01')" % quoted_field_name
        if lookup_type == 'month':
            return "Convert(datetime, Convert(varchar, DATEPART(year, %s)) + '/' + Convert(varchar, DATEPART(month, %s)) + '/01')" %\
                (quoted_field_name, quoted_field_name)
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
        
    def no_limit_value(self):
        return None

    def value_to_db_datetime(self, value):
        # MS SQL 2005 doesn't support microseconds
        if value is None:
            return None
        return value.replace(microsecond=0)
    
    def value_to_db_time(self, value):
        # MS SQL 2005 doesn't support microseconds
        if value is None:
            return None
        return value.replace(microsecond=0)
	        
    def value_to_db_decimal(self, value, max_digits, decimal_places):
        if value is None:
            return None
        return value # Should be a decimal type.

    def prep_for_like_query(self, x):
        """Prepares a value for use in a LIKE query."""
        
        # Should probably just use a regex to do the replace.
        from django.utils.encoding import smart_unicode
        return (
            smart_unicode(x).\
                replace("\\", "\\\\").\
                replace("%", "\%").\
                replace("_", "\_").\
                replace("[", "\[").\
                replace("]", "\]")
            )

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
