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
            sql_make_proc = """
"""
            cur.execute(sql_make_proc)
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
   
suite = unittest.makeSuite(test_dbapi, 'test')
testRunner = unittest.TextTestRunner(verbosity=9)
print testRunner.run(suite)
