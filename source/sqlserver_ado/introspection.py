import ado_consts

def get_table_list(cursor):
    "Returns a list of table names in the current database."
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    return [row[0] for row in cursor.fetchall()]

def _is_auto_field(cursor, table_name, column_name):
    """Checks whether column is an identity column, using COLUMNPROPERTY."""
    # COLUMNPROPERTY: http://msdn2.microsoft.com/en-us/library/ms174968.aspx
    sql = "SELECT COLUMNPROPERTY(OBJECT_ID(N'%s'), N'%s', 'IsIdentity')" % \
        (table_name, column_name)

    cursor.execute(sql)      
    return cursor.fetchall()[0][0]

def get_table_description(cursor, table_name, identity_check=True):
    """Returns a description of the table, with DB-API cursor.description interface.

    The 'auto_check' parameter has been added to the function argspec.
    If set to True, the function will check each of the table's fields for the
    IDENTITY property (the IDENTITY property is the MSSQL equivalent to an AutoField).

    When a field is found with an IDENTITY property, it is given a custom field number
    of SQL_AUTOFIELD, which maps to the 'AutoField' value in the DATA_TYPES_REVERSE dict.
    """

    # map pyodbc's cursor.columns to db-api cursor description
    cursor.execute("SELECT * FROM [%s] where 1=0" % (table_name))
    columns = cursor.description

    items = []
    for column in columns:
        column = list(column) # Convert tuple to list
        if identity_check and _is_auto_field(cursor, table_name, column[0]):
            column[1] = ado_consts.AUTO_FIELD_MARKER
        items.append(column)
    return items

    "Returns a description of the table, with the DB-API cursor.description interface."
    # % in the table name because you can't pass table names as parameters (just where values)
    cursor.execute("SELECT * FROM [%s] where 1=0" % (table_name))
    return cursor.description


def _name_to_index(cursor, table_name):
    """
    Returns a dictionary of {field_name: field_index} for the given table.
    Indexes are 0-based.
    """
    return dict([(d[0], i) for i, d in enumerate(get_table_description(cursor, table_name, False))])

def get_relations(cursor, table_name):
    source_field_dict = _name_to_index(cursor, table_name)
    
    sql = """
SELECT
COLUMN_NAME = FK_COLS.COLUMN_NAME,
REFERENCED_TABLE_NAME = PK.TABLE_NAME,
REFERENCED_COLUMN_NAME = PK_COLS.COLUMN_NAME
FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS REF_CONST
JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS FK
	ON REF_CONST.CONSTRAINT_CATALOG = FK.CONSTRAINT_CATALOG
	AND REF_CONST.CONSTRAINT_SCHEMA = FK.CONSTRAINT_SCHEMA
	AND REF_CONST.CONSTRAINT_NAME = FK.CONSTRAINT_NAME
	AND FK.CONSTRAINT_TYPE = 'FOREIGN KEY'

JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS PK 
	ON REF_CONST.UNIQUE_CONSTRAINT_CATALOG = PK.CONSTRAINT_CATALOG
	AND REF_CONST.UNIQUE_CONSTRAINT_SCHEMA = PK.CONSTRAINT_SCHEMA
	AND REF_CONST.UNIQUE_CONSTRAINT_NAME = PK.CONSTRAINT_NAME
	AND PK.CONSTRAINT_TYPE = 'PRIMARY KEY'

JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE FK_COLS 
	ON REF_CONST.CONSTRAINT_NAME = FK_COLS.CONSTRAINT_NAME

JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE PK_COLS 
	ON PK.CONSTRAINT_NAME = PK_COLS.CONSTRAINT_NAME
where
	FK.TABLE_NAME = %s"""
    cursor.execute(sql,[table_name])
    relations = cursor.fetchall()
    relation_map = dict()
    
    for source_column, target_table, target_column in relations:
        target_field_dict = _name_to_index(cursor, target_table)
        target_index = target_field_dict[target_column]
        source_index = source_field_dict[source_column]
        
        relation_map[source_index] = (target_index, target_table)
        
    return relation_map

def get_indexes(cursor, table_name):
#    Returns a dictionary of fieldname -> infodict for the given table,
#    where each infodict is in the format:
#        {'primary_key': boolean representing whether it's the primary key,
#         'unique': boolean representing whether it's a unique index}
    sql = """
select
	C.name as [column_name],
	IX.is_unique as [unique], 
    IX.is_primary_key as [primary_key]
from
	sys.tables T
	join sys.index_columns IC on IC.object_id = T.object_id
	join sys.columns C on C.object_id = T.object_id and C.column_id = IC.column_id
	join sys.indexes Ix on Ix.object_id = T.object_id and Ix.index_id = IC.index_id
where
	T.name = %s
	and (Ix.is_unique=1 or Ix.is_primary_key=1)
    -- Omit multi-column keys
	and not exists (
		select * 
		from sys.index_columns cols
		where
			cols.object_id = T.object_id
			and cols.index_id = IC.index_id
			and cols.key_ordinal > 1
	)
"""
    
    cursor.execute(sql,[table_name])
    constraints = cursor.fetchall()
    indexes = dict()
    
    for column_name, unique, primary_key in constraints:
        column_name = column_name.lower()
        indexes[column_name] = {"primary_key":primary_key, "unique":unique}
    
    return indexes
    

DATA_TYPES_REVERSE = {
    ado_consts.AUTO_FIELD_MARKER: 'AutoField',
    ado_consts.adBoolean: 'BooleanField',
    ado_consts.adChar: 'CharField',
    ado_consts.adWChar: 'CharField',
    ado_consts.adDecimal: 'DecimalField',
    ado_consts.adNumeric: 'DecimalField',
    ado_consts.adDBTimeStamp: 'DateTimeField',
    ado_consts.adDouble: 'FloatField',
    ado_consts.adSingle: 'FloatField',
    ado_consts.adInteger: 'IntegerField',
    ado_consts.adBigInt: 'IntegerField',
    ado_consts.adSmallInt: 'IntegerField',
    ado_consts.adTinyInt: 'IntegerField',
    ado_consts.adVarChar: 'CharField',
    ado_consts.adVarWChar: 'CharField',
    ado_consts.adLongVarWChar: 'TextField',
    ado_consts.adLongVarChar: 'TextField',
}
