"""Custom Query class for MS SQL Serever."""
import re

# query_class returns the base class to use for Django queries.
# The custom 'SqlServerQuery' class derives from django.db.models.sql.query.Query
# which is passed in as "QueryClass" by Django itself.
#
# SqlServerQuery overrides:
# ...insert queries to add "SET IDENTITY_INSERT" if needed.
# ...select queries to emulate LIMIT/OFFSET for sliced queries.

_re_order_limit_offset = re.compile(
    r'(?:ORDER BY\s+(.+?))?\s*(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')

def _break(s, find):
    """Break a string s into the part before the substring to find, 
    and the part including and after the substring."""
    i = s.find(find)
    return s[:i], s[i:]

def _get_order_limit_offset(sql):
    return _re_order_limit_offset.search(sql).groups()
    
def _remove_order_limit_offset(sql):
    return _re_order_limit_offset.sub('',sql).split(None, 1)[1]

def query_class(QueryClass):
    """Return a custom Query subclass for SQL Server."""
    class SqlServerQuery(QueryClass):
        def __init__(self, *args, **kwargs):
            super(SqlServerQuery, self).__init__(*args, **kwargs)

            # If we are an insert query, wrap "as_sql"
            # Import here to avoid circular dependency
            from django.db.models.sql.subqueries import InsertQuery
            if isinstance(self, InsertQuery):
                self._parent_as_sql = self.as_sql
                self.as_sql = self._insert_as_sql

        def resolve_columns(self, row, fields=()):
            # If the results are sliced, the resultset will have an initial 
            # "row number" column. Remove this column before the ORM sees it.
            if self._using_row_number:
                return row[1:]
            return row
            
        def as_sql(self, with_limits=True, with_col_aliases=False):
            self._using_row_number = False
            
            # Get out of the way if we're not a select query or there's no limiting involved.
            check_limits = with_limits and (self.low_mark or self.high_mark is not None)
            if not isinstance(self, SqlServerQuery) or not check_limits:
                return super(SqlServerQuery, self).as_sql(with_limits, with_col_aliases)

            raw_sql, fields = super(SqlServerQuery, self).as_sql(False, with_col_aliases)
            
            # Check for high mark only and replace with "TOP"
            if self.high_mark and not self.low_mark:
                sql = re.sub(r'(?i)^SELECT', 'SELECT TOP %s' % self.high_mark, raw_sql, 1)
                return sql, fields
                
            # Else we have limits; rewrite the query using ROW_NUMBER()
            self._using_row_number = True

            order, limit_ignore, offset_ignore = _get_order_limit_offset(raw_sql)
            
            # Using ROW_NUMBER requires an ordering
            if order is None:
                meta = self.get_meta()
                qn = self.connection.ops.quote_name
                order = '%s.%s ASC' % (qn(meta.db_table), qn(meta.pk.attname))
            
            where_row_num = "%s < _row_num" % (self.low_mark)
            if self.high_mark:
                where_row_num += " and _row_num <= %s" % (self.high_mark)
                
            # Lop off ORDER... and the initial "SELECT"
            inner_select = _remove_order_limit_offset(raw_sql)
            outer_fields, inner_select = self._alias_columns(inner_select)
            
            sql = "SELECT _row_num, %s FROM ( SELECT ROW_NUMBER() OVER ( ORDER BY %s) as _row_num, %s) as QQQ where %s"\
                 % (outer_fields, order, inner_select, where_row_num)
            
            return sql, fields
 
        def _alias_columns(self, sql):
            """Return tuple of SELECT and FROM clauses, aliasing duplicate column names."""
            qn = self.connection.ops.quote_name
            
            # Pattern to find the quoted column name at the end of a field specification
            _pat_col = r"\[([^[]+)\]$"  
            #]) Funky comment to get e's syntax highlighting back on track. 
        
            outer = list()
            inner = list()
            names_seen = list()
            
            select_list, from_clause = _break(sql, ' FROM [')
            for col in [x.strip() for x in select_list.split(',')]:
                col_name = re.search(_pat_col, col).group(1)
                
                # If column name was already seen, alias it.
                if col_name in names_seen:
                    alias = qn('%s___%s' % (col_name, names_seen.count(col_name)))
                    outer.append(alias)
                    inner.append("%s as %s" % (col, alias))
                else:
                    outer.append(qn(col_name))
                    inner.append(col)

                names_seen.append(col_name)

            # Add FROM clause back to inner select
            return ', '.join(outer), ', '.join(inner) + from_clause

        def _insert_as_sql(self, *args, **kwargs):
            sql, params = self._parent_as_sql(*args,**kwargs)
            meta = self.get_meta()
            
            if (meta.pk.attname in self.columns) and (meta.pk.__class__.__name__ == "AutoField"):
                quoted_table = self.connection.ops.quote_name(meta.db_table)
                sql = "SET IDENTITY_INSERT %s ON;%s;SET IDENTITY_INSERT %s OFF" %\
                    (quoted_table, sql, quoted_table)

            return sql, params

    return SqlServerQuery
