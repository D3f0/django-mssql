def get_table_list(cursor):
    "Returns a list of table names in the current database."
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    return [row[0] for row in cursor.fetchall()]

def get_table_description(cursor, table_name):
    "Returns a description of the table, with the DB-API cursor.description interface."
    cursor.execute("SELECT * FROM %s where 1=0" % (table_name))
    return cursor.description

def _name_to_index(cursor, table_name):
    """
    Returns a dictionary of {field_name: field_index} for the given table.
    Indexes are 0-based.
    """
    return dict([(d[0], i) for i, d in enumerate(get_table_description(cursor, table_name))])

def get_relations(cursor, table_name):
    source_field_dict = _name_to_index(cursor, table_name)
    
    sql = '''SELECT
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
	FK.TABLE_NAME = %s'''
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
    sql = '''
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
'''
    
    cursor.execute(sql,[table_name])
    constraints = cursor.fetchall()
    indexes = dict()
    
    for column_name, unique, primary_key in constraints:
        column_name = column_name.lower()
        indexes[column_name] = {"primary_key":primary_key, "unique":unique}
    
    return indexes
    

    # Copied out of adodbapi for reference:
adArray                       =0x2000     # from enum DataTypeEnum
adBSTR                        =0x8        # from enum DataTypeEnum
adBigInt                      =0x14       # from enum DataTypeEnum
adBinary                      =0x80       # from enum DataTypeEnum
adBoolean                     =0xb        # from enum DataTypeEnum
adChapter                     =0x88       # from enum DataTypeEnum
adChar                        =0x81       # from enum DataTypeEnum
adCurrency                    =0x6        # from enum DataTypeEnum
adDBDate                      =0x85       # from enum DataTypeEnum
adDBTime                      =0x86       # from enum DataTypeEnum
adDBTimeStamp                 =0x87       # from enum DataTypeEnum
adDate                        =0x7        # from enum DataTypeEnum
adDecimal                     =0xe        # from enum DataTypeEnum
adDouble                      =0x5        # from enum DataTypeEnum
adEmpty                       =0x0        # from enum DataTypeEnum
adError                       =0xa        # from enum DataTypeEnum
adFileTime                    =0x40       # from enum DataTypeEnum
adGUID                        =0x48       # from enum DataTypeEnum
adIDispatch                   =0x9        # from enum DataTypeEnum
adIUnknown                    =0xd        # from enum DataTypeEnum
adInteger                     =0x3        # from enum DataTypeEnum
adLongVarBinary               =0xcd       # from enum DataTypeEnum
adLongVarChar                 =0xc9       # from enum DataTypeEnum
adLongVarWChar                =0xcb       # from enum DataTypeEnum
adNumeric                     =0x83       # from enum DataTypeEnum
adPropVariant                 =0x8a       # from enum DataTypeEnum
adSingle                      =0x4        # from enum DataTypeEnum
adSmallInt                    =0x2        # from enum DataTypeEnum
adTinyInt                     =0x10       # from enum DataTypeEnum
adUnsignedBigInt              =0x15       # from enum DataTypeEnum
adUnsignedInt                 =0x13       # from enum DataTypeEnum
adUnsignedSmallInt            =0x12       # from enum DataTypeEnum
adUnsignedTinyInt             =0x11       # from enum DataTypeEnum
adUserDefined                 =0x84       # from enum DataTypeEnum
adVarBinary                   =0xcc       # from enum DataTypeEnum
adVarChar                     =0xc8       # from enum DataTypeEnum
adVarNumeric                  =0x8b       # from enum DataTypeEnum
adVarWChar                    =0xca       # from enum DataTypeEnum
adVariant                     =0xc        # from enum DataTypeEnum
adWChar                       =0x82       # from enum DataTypeEnum


DATA_TYPES_REVERSE = {
    adBoolean: 'BooleanField',
    adChar: 'CharField',
    adWChar: 'CharField',
    adDecimal: 'DecimalField',
    adNumeric: 'DecimalField',
    adDBTimeStamp: 'DateTimeField',
    adDouble: 'FloatField',
    adSingle: 'FloatField',
    adInteger: 'IntegerField',
    adBigInt: 'IntegerField',
    adSmallInt: 'IntegerField',
    adTinyInt: 'IntegerField',
    adVarChar: 'CharField',
    adVarWChar: 'CharField',
    adLongVarWChar: 'TextField',
    adLongVarChar: 'TextField',
}
