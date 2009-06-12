import datetime
import decimal
from django.db import models
from django.test import TestCase


class BaseModel(models.Model):
    def __unicode__(self):
        return u'id: ' + unicode(self.id) + ' Amount: ' + unicode(self.val)

    class Meta:
        abstract = True

class TableNullTime(BaseModel):
    """
    This test isn't expected to work on SQL Server 2005,
    as there is no bare "time" type.
    
    TableNullTime(val=None).save()
    TableNullTime(val=datetime.time(2,34,2)).save()
    len(list(TableNullTime.objects.all()))
    2
    """
    val = models.TimeField(null=True)


class TableNullChar(BaseModel):
    val = models.CharField(null=True, max_length=100)
    
class TableNullText(BaseModel):
    val = models.TextField(null=True)

class TableNullInteger(BaseModel):
    val = models.IntegerField(null=True)

class TableNullDateTime(BaseModel):
    val = models.DateTimeField(null=True)

class TableNullDate(BaseModel):
    val = models.DateField(null=True)

class TableNullNullBoolean(BaseModel):
    val = models.NullBooleanField(null=True)

class TableNullDecimal(BaseModel):
    val = models.DecimalField(null=True, max_digits=4, decimal_places=2)

class TableNullFloat(BaseModel):
    val = models.FloatField(null=True)


class NullTests(TestCase):
    def _run(self, model, values):
        for v in values:
            model(val=v).save()
            
        self.assertEquals(len(list(model.objects.all())), len(values))

    def testChar(self):
        self._run(TableNullChar, (None, "This is my string value."))
        
    def testText(self):
        self._run(TableNullText, (None, "This is my string value."))
        
    def testInteger(self):
        self._run(TableNullInteger, (None, 32768))
        
    def testDateTime(self):
        self._run(TableNullDateTime,(None, datetime.datetime(2009,1,1,4,3,5)))
     
    def testDate(self):
        self._run(TableNullDate, (None, datetime.date(2009,1,1)))
     
    def testBoolean(self):
        self._run(TableNullNullBoolean, (None, True, False))

    def testFloat(self):
        self._run(TableNullFloat, (None, 34.3))

    def testDecimal(self):
        self._run(TableNullDecimal, (None, decimal.Decimal('99.99')))
