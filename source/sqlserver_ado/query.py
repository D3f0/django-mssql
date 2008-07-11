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
#
# Seems fragile, but less so than monkeypatching Django's guts.

_re_order_limit_offset = \
    re.compile(r'(?:ORDER BY\s+(.+?))?\s*(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')

def _remove_limit_offset(sql):
    return re.sub(r'(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$', '', sql)


def query_class(QueryClass, Database):
    """
    Return a custom django.db.models.sql.query.Query subclass appropriate 
    for SQL Server.
    """
    class SqlServerQuery(QueryClass):
        def __init__(self, *args, **kwargs):
            super(SqlServerQuery, self).__init__(*args, **kwargs)

            # If we are an insert query, wrap "as_sql"
            if self.__class__.__name__ == "InsertQuery":
                self._parent_as_sql = self.as_sql
                self.as_sql = self._insert_as_sql


        def _rewrite_limit_offset(self, sql, order, limit, offset):
            # Lop off the ORDER BY ... LIMIT ... OFFSET ...
            sql_without_ORDER = _re_order_limit_offset.sub('',sql)
            # Lop off the initial "SELECT"
            inner_sql = sql_without_ORDER.split(None, 1)[1]
            
            low = offset + 1
            high = low + limit - 1
            
            final_sql = "SELECT * FROM ( SELECT ROW_NUMBER() OVER ( ORDER BY %s) as my_row_number, %s) as QQQ where my_row_number between %s and %s" % ( order, inner_sql, low, high)
            
            return final_sql
            
        def _replace_limit_with_top(self, sql, limit):
            # Lop off any LIMIT... from the query
            sql_without_limit = _remove_limit_offset(sql)
            
            # Cut into ['SELECT', '...rest of query...']
            sql_parts = sql_without_limit.split(None, 1)
            return (' TOP %s ' % limit).join(sql_parts)

        def _mangle_sql(self, sql):
            order, limit, offset = _re_order_limit_offset.search(sql).groups()
            
            # Hack around an issue in [7885], extraneous "OFFSET 0":
            if limit is None and offset == '0':
                return _remove_limit_offset(sql)
            
            # If we have no OFFSET, look for LIMIT and replace with TOP
            if offset is None:
                if limit is None:
                    return sql
                return self._replace_limit_with_top(sql, int(limit))
            
            # Otherwise we have an OFFSET, synthesize an ordering if needed
            if order is None:
                meta = self.get_meta()
                order = meta.pk.attname+" ASC"
                    
            return self._rewrite_limit_offset(sql, order, int(limit), int(offset))
    
        def resolve_columns(self, row, fields=()):
            # If we're doing a LIMIT/OFFSET query, the resultset will have an
            # initial "row number" column. We need do ditch this column 
            # before the ORM sees it.
            if (len(row) == len(fields)+1):
                return row[1:]
            return row
            
        def as_sql(self, with_limits=True, with_col_aliases=False):
            # Get out of the way if we're not a select query
            if self.__class__.__name__ != 'SqlServerQuery':
                return super(SqlServerQuery, self).as_sql(with_limits, with_col_aliases)

            raw_sql, fields = super(SqlServerQuery, self).as_sql(with_limits, with_col_aliases)
            return self._mangle_sql(raw_sql), fields

        def _insert_as_sql(self, *args, **kwargs):
            meta = self.get_meta()
            
            quoted_table = self.connection.ops.quote_name(meta.db_table)
            # Get (sql,params) from original InsertQuery.as_sql
            sql, params = self._parent_as_sql(*args,**kwargs)
            
            if (meta.pk.attname in self.columns) and (meta.pk.__class__.__name__ == "AutoField"):
                sql = "SET IDENTITY_INSERT %s ON;%s;SET IDENTITY_INSERT %s OFF" %\
                    (quoted_table, sql, quoted_table)

            return sql, params

    return SqlServerQuery
