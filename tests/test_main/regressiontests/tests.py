import datetime
import decimal
from django.db import models
from django.test import TestCase

from regressiontests.models import Bug69Table1, Bug69Table2, Bug70Table, Bug93Table

class Bug38Table(models.Model):
    d = models.DecimalField(max_digits=5, decimal_places=2)


class Bug38TestCase(TestCase):
    def testInsertVariousFormats(self):
        """
        Test adding decimals as strings with various formats.
        """
        Bug38Table(d=decimal.Decimal('0')).save()
        Bug38Table(d=decimal.Decimal('0e0')).save()
        Bug38Table(d=decimal.Decimal('0E0')).save()
        Bug38Table(d=decimal.Decimal('450')).save()
        Bug38Table(d=decimal.Decimal('450.0')).save()
        Bug38Table(d=decimal.Decimal('450.00')).save()
        Bug38Table(d=decimal.Decimal('450.000')).save()
        Bug38Table(d=decimal.Decimal('0450')).save()
        Bug38Table(d=decimal.Decimal('0450.0')).save()
        Bug38Table(d=decimal.Decimal('0450.00')).save()
        Bug38Table(d=decimal.Decimal('0450.000')).save()
        Bug38Table(d=decimal.Decimal('4.5e+2')).save()
        Bug38Table(d=decimal.Decimal('4.5E+2')).save()
        self.assertEquals(len(list(Bug38Table.objects.all())),13)

    def testReturnsDecimal(self):
        """
        Test if return value is a python Decimal object 
        when saving the model with a Decimal object as value 
        """
        Bug38Table(d=decimal.Decimal('0')).save()
        d1 = Bug38Table.objects.all()[0]
        self.assertEquals(decimal.Decimal, d1.d.__class__)

    def testReturnsDecimalFromString(self):
        """
        Test if return value is a python Decimal object 
        when saving the model with a unicode object as value.
        """
        Bug38Table(d=u'123').save()
        d1 = Bug38Table.objects.all()[0]
        self.assertEquals(decimal.Decimal, d1.d.__class__)        

    def testSavesAfterDecimal(self):
        """
        Test if value is saved correctly when there are numbers 
        to the right side of the decimal point 
        """
        Bug38Table(d=decimal.Decimal('450.1')).save()
        d1 = Bug38Table.objects.all()[0]
        self.assertEquals(decimal.Decimal('450.1'), d1.d)
    
    def testInsertWithMoreDecimals(self):
        """
        Test if numbers to the right side of the decimal point 
        are saved correctly rounding to a decimal with the correct 
        decimal places.
        """
        Bug38Table(d=decimal.Decimal('450.111')).save()
        d1 = Bug38Table.objects.all()[0]
        self.assertEquals(decimal.Decimal('450.11'), d1.d)    
        
    def testInsertWithLeadingZero(self):
        """
        Test if value is saved correctly with Decimals with a leading zero.
        """
        Bug38Table(d=decimal.Decimal('0450.0')).save()
        d1 = Bug38Table.objects.all()[0]
        self.assertEquals(decimal.Decimal('450.0'), d1.d)


class Bug69TestCase(TestCase):
    def setUp(self):
        for x in xrange(0,5):
            Bug69Table2.objects.create(
                id=x,
                related_obj=Bug69Table1.objects.create(id=x),
            )
        
    def testConflictingFieldNames(self):
        objs = list(Bug69Table2.objects.select_related('related_obj')[2:4])
        self.assertEqual(len(objs), 2)



class Bug70TestCase(TestCase):
    def testInsert(self):
        Bug70Table.objects.create(a=100);
        Bug70Table.objects.create(a=101);
        Bug70Table.objects.create(a=102);
        
        results = Bug70Table.objects.all()
        
        self.assertEquals(results.count(), 3)
        
        self.assertTrue(hasattr(results[0], 'id'))
        self.assertTrue(results[0].id == 1)

class Bug85TestCase(TestCase):
    def testEuropeanDecimalConversion(self):
        from sqlserver_ado.dbapi import _cvtDecimal
        
        val1 = _cvtDecimal('0,05')
        self.assertEqual(decimal.Decimal('0.05'), val1)
        
    def testEuropeanFloatConversion(self):
        from sqlserver_ado.dbapi import _cvtFloat
        
        val1 = _cvtFloat('0,05')
        self.assertEqual(float('0.05'), val1)
        

class Bug93TestCase(TestCase):
    def setUp(self):
        dates = (
            (2009, 1),
            (2009, 2),
            (2009, 3),
            (2010, 1),
            (2010, 2)
        )
            
        for year, month in dates:
            dt = datetime.datetime(year, month, 1)

            Bug93Table.objects.create(
                dt=dt,
                d=dt.date()
            )   
    
    def testDateYear(self):
        dates = Bug93Table.objects.filter(d__year=2009)
        self.assertTrue(dates.count() == 3)

        dates = Bug93Table.objects.filter(d__year='2010')
        self.assertTrue(dates.count() == 2)
        
        
    def testDateTimeYear(self):
        dates = Bug93Table.objects.filter(dt__year=2009)
        self.assertTrue(dates.count() == 3)

        dates = Bug93Table.objects.filter(dt__year='2010')
        self.assertTrue(dates.count() == 2)
