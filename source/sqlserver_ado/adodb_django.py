"""adodbapi v2.1D -  A (mostly) Python DB API 2.0 interface to Microsoft ADO
	Python's DB-API 2.0:
	http://www.python.org/dev/peps/pep-0249/

    Copyright (C) 2002  Henrik Ekelund
    Email: <http://sourceforge.net/sendmessage.php?touser=618411>

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    Version 2.1 by Vernon Cole
    Version 2.1D by Adam Vandenberg, forked for internal Django backend use
"""

import sys
import time
import datetime
import re

try:
    import decimal
except ImportError: # for Python 2.3
    from django.utils import _decimal as decimal

from win32com.client import Dispatch

# Request Python decimal types
import pythoncom
pythoncom.__future_currency__ = True

from ado_consts import *
from util import MultiMap

apilevel = '2.0' # String constant stating the supported DB API level.

# Level of thread safety this interface supports:
# 1: Threads may share the module, but not connections.
threadsafety = 1

# The underlying ADO library expects parameters as '?', but this wrapper 
# expects '%s' parameters. This wrapper takes care of the conversion.
paramstyle = 'format'

version = __doc__.split('-',2)[0]

# Verbosity of logging code
# 0/False = off
# 1/True = on
# >1 = Additional debugging information
verbose = False

#  Set defaultIsolationLevel on module level before creating the connection.
#   It may be one of "adXact..." consts.
#   if you simply "import adodbapi", you'll say:
#   "adodbapi.adodbapi.defaultIsolationLevel=adodbapi.adodbapi.adXactBrowse", for example
defaultIsolationLevel = adXactReadCommitted

#  Set defaultCursorLocation on module level before creating the connection.
#   It may be one of the "adUse..." consts.
defaultCursorLocation = adUseServer

# Used for COM to Python date conversions.
_ordinal_1899_12_31 = datetime.date(1899,12,31).toordinal()-1
_milliseconds_per_day = 24*60*60*1000

# Used for munging string date times (but see Django issue #7560)
rx_datetime = re.compile(r'^(\d{4}-\d\d?-\d\d? \d\d?:\d\d?:\d\d?.\d{3})\d{3}$')


def standardErrorHandler(connection, cursor, errorclass, errorvalue):
    err = (errorclass, errorvalue)
    connection.messages.append(err)
    if cursor is not None:
        cursor.messages.append(err)
    raise errorclass(errorvalue)


class Error(StandardError): pass
class Warning(StandardError): pass

class InterfaceError(Error):
    def __init__(self, inner_exception=None):
        self.inner_exception = inner_exception

    def __str__(self):
        s = "InterfaceError"
        if self.inner_exception is not None:
            s += "\n" + str(self.inner_exception)
        return s

class DatabaseError(Error): pass
class InternalError(DatabaseError): pass
class OperationalError(DatabaseError): pass
class ProgrammingError(DatabaseError): pass
class IntegrityError(DatabaseError): pass
class DataError(DatabaseError): pass
class NotSupportedError(DatabaseError): pass

class DBAPITypeObject:
    def __init__(self,valuesTuple):
        self.values = valuesTuple

    def __eq__(self, other): return other in self.values
    def __ne__(self, other): return other not in self.values

def _logger(message, log_level=1):
	if verbose and verbose>=log_level: print message

def connect(connection_string, timeout=30):
    "Connection string as in the ADO documentation, SQL timeout in seconds"
    pythoncom.CoInitialize()
    c = Dispatch('ADODB.Connection')
    c.CommandTimeout = timeout
    c.ConnectionString = connection_string

    _logger('%s attempting: "%s"' % (version, connection_string))
    try:
        c.Open()
    except Exception, e:
    	print "Error attempting connection: " + connection_string
        raise DatabaseError(e)
        
    useTransactions = _determineTransactionSupport(c)
    return Connection(c, useTransactions)

def _determineTransactionSupport(adoConn):
    for prop in adoConn.Properties:
        if prop.Name == 'Transaction DDL':
            return (prop.Value > 0)
    return False

def format_parameters(parameters):
	"""Formats a collection of ADO Command Parameters"""
	desc = list()
	for p in parameters:
		desc.append("Name: %s, Type: %s, Size: %s" %\
			(p.Name, adTypeNames.get(p.Type, str(p.Type)+' (unknown type)'), p.Size))
		
	return '[' + ', '.join(desc) + ']'

class Connection(object):
    def __init__(self, adoConn, useTransactions=False):
        self.adoConn = adoConn
        self.errorhandler = None
        self.messages = []
        self.adoConn.CursorLocation = defaultCursorLocation
        self.supportsTransactions = useTransactions
        
        if self.supportsTransactions:
            self.adoConn.IsolationLevel = defaultIsolationLevel
            self.adoConn.BeginTrans() #Disables autocommit

        if verbose:
            print 'adodbapi - New connection at %X' % id(self)
            
    def _raiseConnectionError(self, errorclass, errorvalue):
        eh = self.errorhandler
        if eh is None:
            eh = standardErrorHandler
        eh(self, None, errorclass, errorvalue)

    def _closeAdoConnection(self):
        """close the underlying ADO Connection object,
           rolling it back first if it supports transactions."""
        if self.supportsTransactions:
            self.adoConn.RollbackTrans()
        self.adoConn.Close()
        if verbose:
            print 'adodbapi - Closed connection at %X' % id(self)

    def close(self):
        """Close the connection now (rather than whenever __del__ is called).

        The connection will be unusable from this point forward;
        an Error (or subclass) exception will be raised if any operation is attempted with the connection.
        The same applies to all cursor objects trying to use the connection.
        """
        self.messages = []
        try:
            self._closeAdoConnection()
        except Exception, e:
            self._raiseConnectionError(InternalError,e)
        pythoncom.CoUninitialize()

    def commit(self):
        """Commit any pending transaction to the database.

        Note that if the database supports an auto-commit feature,
        this must be initially off. An interface method may be provided to turn it back on.
        Database modules that do not support transactions should implement this method with void functionality.
        """
        self.messages = []
        if not self.supportsTransactions:
            return
            
        try:
            self.adoConn.CommitTrans()
            if not(self.adoConn.Attributes & adXactCommitRetaining):
                #If attributes has adXactCommitRetaining it performs retaining commits that is,
                #calling CommitTrans automatically starts a new transaction. Not all providers support this.
                #If not, we will have to start a new transaction by this command:
                self.adoConn.BeginTrans()
        except Exception, e:
            self._raiseConnectionError(Error, e)

    def rollback(self):
        """In case a database does provide transactions this method causes the the database to roll back to
        the start of any pending transaction. Closing a connection without committing the changes first will
        cause an implicit rollback to be performed.

        If the database does not support the functionality required by the method, the interface should
        throw an exception in case the method is used.
        The preferred approach is to not implement the method and thus have Python generate
        an AttributeError in case the method is requested. This allows the programmer to check for database
        capabilities using the standard hasattr() function.

        For some dynamically configured interfaces it may not be appropriate to require dynamically making
        the method available. These interfaces should then raise a NotSupportedError to indicate the
        non-ability to perform the roll back when the method is invoked.
        """
        self.messages = []
        if not self.supportsTransactions:
            self._raiseConnectionError(NotSupportedError, None)
            
        self.adoConn.RollbackTrans()
        if not(self.adoConn.Attributes & adXactAbortRetaining):
            #If attributes has adXactAbortRetaining it performs retaining aborts that is,
            #calling RollbackTrans automatically starts a new transaction. Not all providers support this.
            #If not, we will have to start a new transaction by this command:
            self.adoConn.BeginTrans()

    def cursor(self):
        "Returns a new Cursor object using the current connection."
        self.messages = []
        return Cursor(self)

    def printADOerrors(self):
        print 'ADO Errors:(%i)' % self.adoConn.Errors.Count
        for e in self.adoConn.Errors:
            print 'Description: %s' % e.Description
            print 'Error: %s %s ' % (e.Number, adoErrors.get(e.Number, "unknown"))
            if e.Number == ado_error_TIMEOUT:
                print 'Timeout Error: Try using adodbpi.connect(constr,timeout=Nseconds)'
            print 'Source: %s' % e.Source
            print 'NativeError: %s' % e.NativeError
            print 'SQL State: %s' % e.SQLState

    def __del__(self):
        try:
            self._closeAdoConnection()
        except: pass
        self.adoConn = None


def _log_parameters(parameters):
    """Log parameters for debugging queries."""
    for p in parameters:
        print 'adodbapi parameter attributes before=', p.Name, p.Type, p.Direction, p.Size


def _configureParameter(p, value):
    """Configures the given ADO Parameter 'p' with the Python 'value'."""
    if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
        #Known problem with JET Provider. Date can not be specified as a COM date.
        # See for example:
        # http://support.microsoft.com/default.aspx?scid=kb%3ben-us%3b284843
        # One workaround is to provide the date as a string in the format 'YYYY-MM-dd'
        s = value.isoformat()
        # Hack to trim microseconds on iso dates down to 3 decimals
        try: # ... only if parameter is a datetime string
            s = rx_datetime.findall(s)[0]
        except: pass
        p.Value = s
        p.Size = len(s)
                                
    elif isinstance(value, basestring):
        s = value
        # Hack to trim microseconds on iso dates down to 3 decimals
        try: # ... only if parameter is a datetime string
            s = rx_datetime.findall(s)[0]
        except: pass
        p.Value = s
        p.Size = len(s)
    
    elif isinstance(value, buffer):
        p.Size = len(value)
        p.AppendChunk(value)
        
    else: 
        p.Value = value
    
    # Use -1 instead of 0 for empty strings and similar.
    if p.Size == 0: p.Size = -1


class Cursor(object):
    description = None
##    This read-only attribute is a sequence of 7-item sequences.
##    Each of these sequences contains information describing one result column:
##        (name, type_code, display_size, internal_size, precision, scale, null_ok).
##    This attribute will be None for operations that do not return rows or if the
##    cursor has not had an operation invoked via the executeXXX() method yet.
##    The type_code can be interpreted by comparing it to the Type Objects specified in the section below.

    rowcount = -1
##    This read-only attribute specifies the number of rows that the last executeXXX() produced
##    (for DQL statements like select) or affected (for DML statements like update or insert).
##    The attribute is -1 in case no executeXXX() has been performed on the cursor or
##    the rowcount of the last operation is not determinable by the interface.[7]
##    NOTE: -- adodbapi returns "-1" by default for all select statements

    arraysize = 1
##    This read/write attribute specifies the number of rows to fetch at a time with fetchmany().
##    It defaults to 1 meaning to fetch a single row at a time.
##    Implementations must observe this value with respect to the fetchmany() method,
##    but are free to interact with the database a single row at a time.
##    It may also be used in the implementation of executemany().

    def __init__(self, connection):
        self.messages = []
        self.conn = connection
        self.rs = None
        self.description = None
        self.errorhandler = connection.errorhandler
        if verbose:
            print 'adodbapi - New cursor at %X on conn %X' % (id(self),id(self.conn))

    def __iter__(self):
        return iter(self.fetchone, None)

    def _raiseCursorError(self, errorclass, errorvalue):
        eh = self.errorhandler
        if eh is None:
            eh = standardErrorHandler
        eh(self.conn,self,errorclass,errorvalue)

    def callproc(self, procname, parameters=None):
        """Call a stored database procedure with the given name.

            The sequence of parameters must contain one entry for each argument that the procedure expects.
            The result of the call is returned as modified copy of the input sequence.
            Input parameters are left untouched, output and input/output parameters replaced
            with possibly new values.

            The procedure may also provide a result set as output, which is
            then available through the standard fetchXXX() methods.
        """
        self.messages = []
        return self._executeHelper(procname, True, parameters)

    def _returnADOCommandParameters(self, cmd):
        values = list()
        for p in cmd.Parameters:
            if verbose > 2:
                print 'return', p.Name, p.Type, p.Direction, repr(p.Value)

            python_obj = convertVariantToPython(p.Value, p.Type)
            if p.Direction == adParamReturnValue:
                self.returnValue = python_obj
            else:
                values.append(python_obj)

        return values

    def _description_from_recordset(self, recordset):
    	# Abort if closed or no recordset.
        if (recordset is None) or (recordset.State == adStateClosed):
            self.recordset = None
            self.description = None
            return

        # Since we use a forward-only cursor, rowcount will always return -1
        self.rowcount = -1
        self.rs = recordset
        desc = list()
        
        for f in self.rs.Fields:            
            display_size = None            
            if not(self.rs.EOF or self.rs.BOF):
                display_size = f.ActualSize
                
            null_ok = bool(f.Attributes & adFldMayBeNull)
            
            desc.append((f.Name, f.Type, display_size, f.DefinedSize, f.Precision, f.NumericScale, null_ok))
        self.description = desc

    def close(self):
        """Close the cursor now (rather than whenever __del__ is called).
            The cursor will be unusable from this point forward; an Error (or subclass)
            exception will be raised if any operation is attempted with the cursor.
        """
        self.messages = []
        self.conn = None
        if self.rs and self.rs.State != adStateClosed:
            self.rs.Close()
            self.rs = None

    def _new_command(self, isStoredProcedureCall):
        self.cmd = Dispatch("ADODB.Command")
        self.cmd.ActiveConnection = self.conn.adoConn
        self.cmd.CommandTimeout = self.conn.adoConn.CommandTimeout

        if isStoredProcedureCall:
            self.cmd.CommandType = adCmdStoredProc
        else:
            self.cmd.CommandType = adCmdText

    def _executeHelper(self, operation, isStoredProcedureCall, parameters=None):
        if self.conn is None:
            self._raiseCursorError(Error,None)
            return

        if verbose > 1 and parameters:
            print 'adodbapi parameters=',repr(parameters)

        parmIndx = -1
        convertedAllParameters = False

        try:
            self._new_command(isStoredProcedureCall)

            if parameters is not None:
                # This will be a list of (parameter index, python value) tuples.
                input_params = list()
        
                parameter_replacements = list()
                for i,value in enumerate(parameters):
                    if value is None:
                        parameter_replacements.append('NULL')
                    else:
                        parameter_replacements.append('?')
                        p = self.cmd.CreateParameter('p%i' % i, pyTypeToADOType(value))
                        if isStoredProcedureCall:
                            p.Direction = adParamUnknown
                        self.cmd.Parameters.Append(p)
                        
                        # Only process input parameter values
                        if p.Direction in [adParamInput, adParamInputOutput, adParamUnknown]:
                            input_params.append( (i, value) )
                            
                # Substitute literal NULL for None
                operation = operation % tuple(parameter_replacements)
                    
                if verbose > 2:
                   _log_parameters(self.cmd.Parameters)
                   

                for i, value in input_params:
                    parmIndx = i
                    p = self.cmd.Parameters(i)
                    _configureParameter(p, value)

                    if verbose > 2:
                        print 'Parameter %d type %s stored as: %s' %\
                            (i, adTypeNames.get(p.Type, 'unknown'), repr(p.Value))

            convertedAllParameters = True

            self.cmd.CommandText = operation
            recordset = self.cmd.Execute()

        except Exception, e:
            # todo: What if self.cmd is None (hasn't been set yet)?
            # Then this exception handler blows up a little.
            import traceback
            message = u'\n--ADODBAPI\n'
            if not convertedAllParameters and 0 <= parmIndx:
                message += u'-- Trying parameter %d, %s: %s\n' %\
                    (parmIndx, adTypeNames.get(self.cmd.Parameters(parmIndx).Type, 'unknown'), repr(parameters[parmIndx]))
            
            tb = u'\n'.join(traceback.format_exception(*sys.exc_info()))
            
            tracebackhistory = u'%s%s\n-- on command: "%s"\n-- with parameters: %s \n-- supplied values: %s' %\
            	(message, tb, operation, format_parameters(self.cmd.Parameters), parameters)
            self._raiseCursorError(DatabaseError,tracebackhistory)
            return

        self.rowcount=recordset[1]  # May be -1 if NOCOUNT is set.
        self._description_from_recordset(recordset[0])

        if isStoredProcedureCall and parameters != None:
            return self._returnADOCommandParameters(self.cmd)

    def execute(self, operation, parameters=None):
        """Prepare and execute a database operation (query or command)."""
        self.messages = []
        self._executeHelper(operation,False,parameters)

    def executemany(self, operation, seq_of_parameters):
        """Prepare a database operation (query or command) and then execute it against all parameter sequences or mappings found in the sequence seq_of_parameters.

        No return value.
        """
        self.messages = []
        total_recordcount = 0

        for params in seq_of_parameters:
            self.execute(operation, params)
            if self.rowcount == -1:
                total_recordcount = -1
                
            if total_recordcount != -1:
                total_recordcount += self.rowcount

        self.rowcount = total_recordcount

    def _fetch(self, rows=None):
        """ Fetch rows from the recordset.
        rows is None gets all (for fetchall).
        """
        if (self.conn is None) or (self.rs is None):
            self._raiseCursorError(Error,None)
            return
            
        if self.rs.State == adStateClosed or self.rs.BOF or self.rs.EOF:
            if rows == 1: # fetchone can return None
                return None
            else: # fetchall and fetchmany return empty lists
                return list()

        if rows:
            ado_results = self.rs.GetRows(rows)
        else:
            ado_results = self.rs.GetRows()

        returnList = list()
        for i,descTuple in enumerate(self.description):
            # Desctuple =(name, type_code, display_size, internal_size, precision, scale, null_ok).
            type_code = descTuple[1]
            returnList.append([convertVariantToPython(r,type_code) for r in ado_results[i]])

        return tuple(zip(*returnList))

    def fetchone(self):
        """ Fetch the next row of a query result set, returning a single sequence,
            or None when no more data is available.

            An Error (or subclass) exception is raised if the previous call to executeXXX()
            did not produce any result set or no call was issued yet.
        """
        self.messages = []
        result = self._fetch(1)
        if result: # return record (not list of records)
            return result[0]
        return None

    def fetchmany(self, size=None):
        """Fetch the next set of rows of a query result, returning a list of tuples. An empty sequence is returned when no more rows are available.

        The number of rows to fetch per call is specified by the parameter.
        If it is not given, the cursor's arraysize determines the number of rows to be fetched.
        The method should try to fetch as many rows as indicated by the size parameter.
        If this is not possible due to the specified number of rows not being available,
        fewer rows may be returned.

        An Error (or subclass) exception is raised if the previous call to executeXXX()
        did not produce any result set or no call was issued yet.

        Note there are performance considerations involved with the size parameter.
        For optimal performance, it is usually best to use the arraysize attribute.
        If the size parameter is used, then it is best for it to retain the same value from
        one fetchmany() call to the next.
        """
        self.messages = []
        if size is None:
            size = self.arraysize
        return self._fetch(size)

    def fetchall(self):
        """Fetch all (remaining) rows of a query result, returning them as a sequence of sequences (e.g. a list of tuples).

            Note that the cursor's arraysize attribute
            can affect the performance of this operation.
            An Error (or subclass) exception is raised if the previous call to executeXXX()
            did not produce any result set or no call was issued yet.
        """
        self.messages = []
        return self._fetch()

    def nextset(self):
        """Make the cursor skip to the next available set, discarding any remaining rows from the current set.

            If there are no more sets, the method returns None. Otherwise, it returns a true
            value and subsequent calls to the fetch methods will return rows from the next result set.

            An Error (or subclass) exception is raised if the previous call to executeXXX()
            did not produce any result set or no call was issued yet.
        """
        self.messages = []
        if (self.conn is None) or (self.rs is None):
            self._raiseCursorError(Error,None)
            return None

        try:
            recordset = self.rs.NextRecordset()[0]
            if recordset is not None:
                self._description_from_recordset(recordset)
                return True
        except pywintypes.com_error, exc:
            self._raiseCursorError(NotSupportedError, exc.args)


    def setinputsizes(self,sizes): pass
    def setoutputsize(self, size, column=None): pass

# Type specific constructors as required by the DB-API 2 specification.
Date = datetime.date
Time = datetime.time
Timestamp = datetime.datetime
Binary = buffer

def DateFromTicks(ticks):
    """This function constructs an object holding a date value from the given ticks value
    (number of seconds since the epoch; see the documentation of the standard Python time module for details). """
    return datetime.date(*time.localtime(ticks)[:3])

def TimeFromTicks(ticks):
    """This function constructs an object holding a time value from the given ticks value
    (number of seconds since the epoch; see the documentation of the standard Python time module for details). """
    return datetime.time(*time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    """This function constructs an object holding a time stamp value from the given
    ticks value (number of seconds since the epoch;
    see the documentation of the standard Python time module for details). """
    return datetime.datetime(*time.localtime(ticks)[:6])


def pyTypeToADOType(data):
    if isinstance(data, basestring):
        return adBSTR

    return mapPythonTypesToAdoTypes[type(data)]

def cvtCurrency((hi, lo), decimal_places=2):
    if lo < 0:
        lo += (2L ** 32)
    # was: return round((float((long(hi) << 32) + lo))/10000.0, decimal_places)
    return decimal.Decimal((long(hi) << 32) + lo)/decimal.Decimal(1000)

def cvtNumeric(variant):
	return _convertNumberWithCulture(variant, decimal.Decimal)

def cvtFloat(variant):
	converted = _convertNumberWithCulture(variant, float)
    # If the type is float, but there is no decimal part, then return an integer. 
    # --Adam V: Why does Django want this?
	if str(converted)[-2:] == ".0":
	    converted = int(converted)
	return converted
        
def _convertNumberWithCulture(variant, f):
    try:
        return f(variant)
    except (ValueError,TypeError): pass

    try:
        europeVsUS = str(variant).replace(",",".")
        return f(europeVsUS)
    except (ValueError,TypeError): pass


def convertVariantToPython(variant, adType):
    if variant is None: 
        return None
    return variantConversions[adType](variant)

adoIntegerTypes = (adInteger,adSmallInt,adTinyInt,adUnsignedInt,adUnsignedSmallInt,adUnsignedTinyInt,adError)
adoRowIdTypes = (adChapter,)
adoLongTypes = (adBigInt, adUnsignedBigInt, adFileTime)
adoExactNumericTypes = (adDecimal, adNumeric, adVarNumeric, adCurrency)
adoApproximateNumericTypes = (adDouble, adSingle)
adoStringTypes = (adBSTR,adChar,adLongVarChar,adLongVarWChar,adVarChar,adVarWChar,adWChar,adGUID)
adoBinaryTypes = (adBinary, adLongVarBinary, adVarBinary)
adoDateTimeTypes = (adDBTime, adDBTimeStamp, adDate, adDBDate)

"""This type object is used to describe columns in a database that are string-based (e.g. CHAR). """
STRING   = DBAPITypeObject(adoStringTypes)

"""This type object is used to describe (long) binary columns in a database (e.g. LONG, RAW, BLOBs). """
BINARY   = DBAPITypeObject(adoBinaryTypes)

"""This type object is used to describe numeric columns in a database. """
NUMBER   = DBAPITypeObject((adBoolean,) + adoIntegerTypes + adoLongTypes + adoExactNumericTypes + adoApproximateNumericTypes)

"""This type object is used to describe date/time columns in a database. """
DATETIME = DBAPITypeObject(adoDateTimeTypes)

"""This type object is used to describe the "Row ID" column in a database. """
ROWID    = DBAPITypeObject(adoRowIdTypes)


def cvtComDate(comDate):
	date_as_float = float(comDate)
	day_count = int(date_as_float)
	fraction_of_day = abs(date_as_float - day_count)
	
	return (datetime.datetime.fromordinal(day_count + _ordinal_1899_12_31) +
	    datetime.timedelta(milliseconds=fraction_of_day * _milliseconds_per_day))


mapPythonTypesToAdoTypes = {
	buffer: adBinary,
	float: adDouble,
	int: adInteger,
	long: adBigInt,
	bool: adBoolean,
	decimal.Decimal: adNumeric,
	datetime.date: adDate,
	datetime.datetime: adDate,
	datetime.time: adDate,
}

variantConversions = MultiMap({
        adoDateTimeTypes : cvtComDate,
        adoApproximateNumericTypes: cvtFloat,
        (adCurrency,): cvtCurrency,
        (adBoolean,): bool,
        adoLongTypes : long,
        adoIntegerTypes+adoRowIdTypes: int,
        adoBinaryTypes: buffer,
    }, lambda x: x)
