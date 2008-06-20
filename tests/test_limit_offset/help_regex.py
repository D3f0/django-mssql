import re

def _bracketed(s, start, end=None):
    if end is None: 
        end = start
        
    return s[0]==start and s[-1]==end


def slice_limit_offset(original_sql):
    _limit_re = re.compile(r'(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')

    # Look for LIMIT/OFFSET in the SQL
    limit, offset = _limit_re.search(original_sql).groups()
    sql = _limit_re.sub('', original_sql) 
            
    # This backend does not yet support OFFSET
    if offset is not None:
        print 'Offset is not supported by this backend.'
        return
            
    # Convert a LIMIT clause to a TOP clause.
    if limit is not None: 
        limit = int(limit)
        sql = (' TOP %s ' % limit).join(sql.split(None, 1))

    print "Limit:",limit,"Offset:",offset

    print "B:",original_sql
    print "A:",sql


def slice_order_limit_offset(original_sql):
    _limit_re = re.compile(r'(?:ORDER BY\s+(.+?))?\s*(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')

    # Look for LIMIT/OFFSET in the SQL
    order_by, limit, offset = _limit_re.search(original_sql).groups()
    sql = _limit_re.sub('', original_sql) 
            
    # This backend does not yet support OFFSET
    if offset is None:
        slice_limit_offset(original_sql)
        return

    without_select = sql.split(None,1)[1]
    
    row_sql = """SELECT * FROM ( SELECT ROW_NUMBER() OVER ( ORDER BY %(ordering)s) as row_number, %(rest)s) as QQQ where row_number between 2 and 5 order by %(ordering)s""" %\
        {
            'rest': without_select,
            'ordering': order_by,
        }
    

    print "Order by:",order_by
    print "Limit:",limit,"Offset:",offset

    print "B:",original_sql
    print "A:",row_sql


def main():
    sql = "SELECT * FROM Products ORDER BY name LIMIT 4"
    
    slice_limit_offset(sql)
    print
    
    slice_order_limit_offset(sql)
    print

    print
    sql2 = "SELECT * FROM Products ORDER BY name LIMIT 4 OFFSET 2"
    
    slice_limit_offset(sql2)
    print
    
    slice_order_limit_offset(sql2)
    print
    
main()
