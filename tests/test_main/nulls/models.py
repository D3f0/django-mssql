import datetime
import decimal
from django.db import models

class BaseModel(models.Model):
    def __unicode__(self):
        return u'id: ' + unicode(self.id) + ' Amount: ' + unicode(self.val)

    class Meta:
        abstract = True


class TableNullChar(BaseModel):
    """
    >>> for val in (None, "This is my string value."):
    ...     TableNullChar(val=val).save()
    >>> len(list(TableNullChar.objects.all()))
    2
    """
    val = models.CharField(null=True, max_length=100)
    
class TableNullText(BaseModel):
    """
    >>> for val in (None, "This is my string value."):
    ...     TableNullText(val=val).save()
    >>> len(list(TableNullText.objects.all()))
    2
    """
    val = models.TextField(null=True)

class TableNullInteger(BaseModel):
    """
    >>> for val in (None, 32768):
    ...     TableNullInteger(val=val).save()
    >>> len(list(TableNullInteger.objects.all()))
    2
    """
    val = models.IntegerField(null=True)

class TableNullDateTime(BaseModel):
    """
    >>> for val in (None, datetime.datetime(2009,1,1,4,3,5)):
    ...     TableNullDateTime(val=val).save()
    >>> len(list(TableNullDateTime.objects.all()))
    2
    """
    val = models.DateTimeField(null=True)

class TableNullDate(BaseModel):
    """
    >>> for val in (None, datetime.date(2009,1,1)):
    ...     TableNullDate(val=val).save()
    >>> len(list(TableNullDate.objects.all()))
    2
    """
    val = models.DateField(null=True)

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

class TableNullBoolean(BaseModel):
    """
    >>> for val in (None, True, False):
    ...     TableNullBoolean(val=val).save()
    >>> len(list(TableNullBoolean.objects.all()))
    3
    """
    val = models.BooleanField(null=True)

class TableNullNullBoolean(BaseModel):
    """
    >>> for val in (None, True, False):
    ...     TableNullNullBoolean(val=val).save()
    >>> len(list(TableNullNullBoolean.objects.all()))
    3
    """
    val = models.NullBooleanField(null=True)

class TableNullDecimal(BaseModel):
    """
    Try a value at the top end of the specified precision/scale.
    >>> for val in (None, decimal.Decimal('99.99')):
    ...     TableNullDecimal(val=val).save()
    >>> len(list(TableNullDecimal.objects.all()))
    2
    """
    val = models.DecimalField(null=True, max_digits=4, decimal_places=2)

class TableNullFloat(BaseModel):
    """
    >>> for val in (None, 34.3):
    ...     TableNullFloat(val=val).save()
    >>> len(list(TableNullFloat.objects.all()))
    2
    """
    val = models.FloatField(null=True)
