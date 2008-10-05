import decimal
from django.db import models
from django.test import TestCase

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
