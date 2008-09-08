import unittest

# Django settings for testbackend project.
def hack_path():
    import os, sys
    common_path = os.path.join(os.path.abspath(os.path.dirname(".")), "..")
    sys.path.append(common_path)

hack_path()
from dbsettings import *

from sqlserver_ado import dbapi
import dbapi20

class test_dbapi(dbapi20.DatabaseAPI20Test):
    driver = dbapi
    connect_args = [ make_connection_string() ]
    
    def setUp(self):
        # This should create the "lower" sproc.
        con = self._connect()
        cur = None
        try:
            cur = con.cursor()
            cur.execute("""IF OBJECT_ID(N'[dbo].[to_lower]', N'P') IS NOT NULL DROP PROCEDURE [dbo].[to_lower]""")
            cur.execute("""
CREATE PROCEDURE to_lower
    @input nvarchar(max)
AS
BEGIN
    select LOWER(@input)
END
""")
        finally:
            try:
                if cur is not None:
                    cur.close()
            except: pass
            con.close()
    
    # Don't need exceptions mirrored on connections.
    def test_ExceptionsAsConnectionAttributes(self): 
        pass
        
    # Don't need setoutputsize tests.
    def test_setoutputsize(self): 
        pass
        
    def test_nextset(self):
        print "Multiple recordset test skipped."
   
suite = unittest.makeSuite(test_dbapi, 'test')
testRunner = unittest.TextTestRunner(verbosity=9)
print testRunner.run(suite)
