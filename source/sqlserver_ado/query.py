"""
Custom Query classes for MS SQL Serever.
Derivatives of: django.db.models.sql.query.Query
"""
import re

# Gets the /base class/ for all Django queryies.
# This custom class derives from: django.db.models.sql.query.Query
# which is passed in as "QueryClass".
# Django's subquery times (InsertQuery, DeleteQuery, etc.) will then inherit
# from this custom class.
#
# This means that we can override the basic "Query" behavior, but not
# derived behavior, unless we do more work.
#
# The goal here is to be able to override some "InsertQuery" behavior,
# so we check the most-derived type name and replace a method if it is
# "InsertQuery".

_re_order_limit_offset = re.compile(
    r'(?:ORDER BY\s+(.+?))?\s*(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')

def _get_order_limit_offset(sql):
    return _re_order_limit_offset.search(sql).groups()
    
def _remove_order_limit_offset(sql):
    return _re_order_limit_offset.sub('',sql)

def query_class(QueryClass, Database):
    """
    Return a custom django.db.models.sql.query.Query subclass appropriate 
    for SQL Server.
    """
    class SqlServerQuery(QueryClass):
        def __init__(self, *args, **kwargs):
            super(SqlServerQuery, self).__init__(*args, **kwargs)
            self._using_row_number = False

            # If we are an insert query, wrap "as_sql"
            if self.__class__.__name__ == "InsertQuery":
                self._parent_as_sql = self.as_sql
                self.as_sql = self._insert_as_sql

        def resolve_columns(self, row, fields=()):
            # If the results are sliced, the resultset will have an initial 
            # "row number" column. Remove this column before the ORM sees it.
            if self._using_row_number:
                return row[1:]
            return row
            
        def as_sql(self, with_limits=True, with_col_aliases=False):
            # Get out of the way if we're not a select query
            # or there's no limiting involved.
            check_limits = with_limits and (self.low_mark > 0 or self.high_mark is not None)
            if self.__class__.__name__ != 'SqlServerQuery' or not check_limits:
                return super(SqlServerQuery, self).as_sql(with_limits, with_col_aliases)

            raw_sql, fields = super(SqlServerQuery, self).as_sql(False, with_col_aliases)
            
            # Check for high mark only, replace with "TOP"
            if self.high_mark and not self.low_mark:
                sql_parts = raw_sql.split(None, 1)
                raw_sql = (' TOP %s ' % self.high_mark).join(sql_parts)
                return raw_sql, fields
                
            # Else we have limits; rewrite the query using ROW_NUMBER()
            self._using_row_number = True

            order, limit, offset = _get_order_limit_offset(raw_sql)
            
            # Lop off ORDER... and the initial "SELECT"
            sql = _remove_order_limit_offset(raw_sql).split(None, 1)[1]

            # Using ROW_NUMBER requires an ordering
            if order is None:
                meta = self.get_meta()
                qn = self.connection.ops.quote_name
                order = '%s.%s ASC' % (qn(meta.db_table), qn(meta.pk.attname))
                
            where = "%s <= my_row_number" % (self.low_mark)
            if self.high_mark:
                where += " and my_row_number < %s" % (self.high_mark)

            sql = "SELECT * FROM ( SELECT ROW_NUMBER() OVER ( ORDER BY %s) as my_row_number, %s) as QQQ where %s" % (order, sql, where)
            
            return sql, fields

        def _insert_as_sql(self, *args, **kwargs):
            meta = self.get_meta()
            quoted_table = self.connection.ops.quote_name(meta.db_table)
            
            sql, params = self._parent_as_sql(*args,**kwargs)
            
            if (meta.pk.attname in self.columns) and (meta.pk.__class__.__name__ == "AutoField"):
                sql = "SET IDENTITY_INSERT %s ON;%s;SET IDENTITY_INSERT %s OFF" %\
                    (quoted_table, sql, quoted_table)

            return sql, params

    return SqlServerQuery
