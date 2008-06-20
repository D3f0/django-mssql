"""
Custom Query classes for MS SQL Serever.
Derivatives of: django.db.models.sql.query.Query
"""

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
# This seems fragile, but less so than relying on patches against
# Django's guts.
def query_class(QueryClass, Database):
    """
    Returns a custom django.db.models.sql.query.Query subclass that is
    appropriate for MS SQL Server.
    """
    class SqlServerQuery(QueryClass):
        def __init__(self, *args, **kwargs):
            super(SqlServerQuery, self).__init__(*args, **kwargs)
            
            # If we are an insert query, wrap "as_sql"
            if self.__class__.__name__ == "InsertQuery":
                self._parent_as_sql = self.as_sql
                self.as_sql = self._insert_as_sql

                
        def resolve_columns(self, row, fields=()):
            # If we're doing a LIMIT/OFFSET query, the resultset
            # will have an initial "row number" column. We need
            # do ditch this column before the ORM sees it.
            if (len(row) == len(fields)+1):
                return row[1:]
            
            return row
            
        # This doesn't actually work
        def _select_as_sql(self, *args, **kwargs):
            sql = self._parent_as_sql(*args,**kwargs)
            return sql

        def _insert_as_sql(self, *args, **kwargs):
            meta = self.get_meta()
            
            quoted_table = self.connection.ops.quote_name(meta.db_table)
            # Get (sql,params) from original InsertQuery.as_sql
            sql, params = self._parent_as_sql(*args,**kwargs)
            
            if (meta.pk.attname in self.columns) and (meta.pk.__class__.__name__ == "AutoField"):
                sql = "SET IDENTITY_INSERT %s ON;%s;SET IDENTITY_INSERT %s OFF" % \
                    (quoted_table, sql, quoted_table)

            return sql, params

    return SqlServerQuery
