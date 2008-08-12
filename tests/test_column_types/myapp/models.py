from django.db import models
import datetime
from decimal import Decimal as d

# Todo: Investigate what the difference between Boolean and NullBoolean is...

class BaseModel(models.Model):
    def __unicode__(self):
        return u'id: ' + unicode(self.id) + ' Amount: ' + unicode(self.val)

    class Meta:
        abstract = True


class TableNullChar(BaseModel):
    """
    >>> obj = TableNullChar(val=None)
    >>> obj.save()
    >>> obj = TableNullChar(val="This is my stringt value.")
    >>> obj.save()
    >>> len(list(TableNullChar.objects.all()))
    2
    """
    val = models.CharField(null=True, max_length=100)
    
class TableNullText(BaseModel):
    """
    >>> obj = TableNullText(val=None)
    >>> obj.save()
    >>> obj = TableNullText(val="This is my stringt value.")
    >>> obj.save()
    >>> len(list(TableNullText.objects.all()))
    2
    """
    val = models.TextField(null=True)

class TableNullInteger(BaseModel):
    """
    >>> obj = TableNullInteger(val=None)
    >>> obj.save()
    >>> obj = TableNullInteger(val=39482)
    >>> obj.save()
    >>> len(list(TableNullInteger.objects.all()))
    2
    """
    val = models.IntegerField(null=True)

class TableNullDateTime(BaseModel):
    """
    >>> obj = TableNullDateTime(val=None)
    >>> obj.save()
    >>> obj = TableNullDateTime(val=datetime.datetime(2009,1,1,4,3,5))
    >>> obj.save()
    >>> len(list(TableNullDateTime.objects.all()))
    2
    """
    val = models.DateTimeField(null=True)

class TableNullDate(BaseModel):
    """
    >>> obj = TableNullDate(val=None)
    >>> obj.save()
    >>> obj = TableNullDate(val=datetime.date(2009,1,1))
    >>> obj.save()
    >>> len(list(TableNullDate.objects.all()))
    2
    """
    val = models.DateField(null=True)

class TableNullTime(BaseModel):
    """
    This test isn't expected to work on SQL Server 2005,
    as there is no bare "time" type.
    
    obj = TableNullTime(val=None)
    obj.save()
    obj = TableNullTime(val=datetime.time(2,34,2))
    obj.save()
    len(list(TableNullTime.objects.all()))
    2
    """
    val = models.TimeField(null=True)

class TableNullBoolean(BaseModel):
    """
    >>> obj = TableNullBoolean(val=None)
    >>> obj.save()
    >>> obj = TableNullBoolean(val=True)
    >>> obj.save()
    >>> obj = TableNullBoolean(val=False)
    >>> obj.save()
    >>> len(list(TableNullBoolean.objects.all()))
    3
    """
    val = models.BooleanField(null=True)

class TableNullNullBoolean(BaseModel):
    """
    >>> obj = TableNullNullBoolean(val=None)
    >>> obj.save()
    >>> obj = TableNullNullBoolean(val=True)
    >>> obj.save()
    >>> obj = TableNullNullBoolean(val=False)
    >>> obj.save()
    >>> len(list(TableNullNullBoolean.objects.all()))
    3
    """
    val = models.NullBooleanField(null=True)

class TableNullDecimal(BaseModel):
    """
    >>> obj = TableNullDecimal(val=None)
    >>> obj.save()
    >>> obj = TableNullDecimal(val=d('34.2'))
    >>> obj.save()
    >>> len(list(TableNullDecimal.objects.all()))
    2
    """
    val = models.DecimalField(null=True, max_digits=4, decimal_places=2)

class TableNullFloat(BaseModel):
    """
    >>> obj = TableNullFloat(val=None)
    >>> obj.save()
    >>> obj = TableNullFloat(val=34.3)
    >>> obj.save()
    >>> len(list(TableNullFloat.objects.all()))
    2
    """
    val = models.FloatField(null=True)
