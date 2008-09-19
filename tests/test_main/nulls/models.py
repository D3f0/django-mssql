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
    >>> TableNullChar(val=None).save()
    >>> TableNullChar(val="This is my string value.").save()
    >>> len(list(TableNullChar.objects.all()))
    2
    """
    val = models.CharField(null=True, max_length=100)
    
class TableNullText(BaseModel):
    """
    >>> TableNullText(val=None).save()
    >>> TableNullText(val="This is my string value.").save()
    >>> len(list(TableNullText.objects.all()))
    2
    """
    val = models.TextField(null=True)

class TableNullInteger(BaseModel):
    """
    >>> TableNullInteger(val=None).save()
    >>> TableNullInteger(val=39482).save()
    >>> len(list(TableNullInteger.objects.all()))
    2
    """
    val = models.IntegerField(null=True)

class TableNullDateTime(BaseModel):
    """
    >>> TableNullDateTime(val=None).save()
    >>> TableNullDateTime(val=datetime.datetime(2009,1,1,4,3,5)).save()
    >>> len(list(TableNullDateTime.objects.all()))
    2
    """
    val = models.DateTimeField(null=True)

class TableNullDate(BaseModel):
    """
    >>> TableNullDate(val=None).save()
    >>> TableNullDate(val=datetime.date(2009,1,1)).save()
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
    >>> TableNullBoolean(val=None).save()
    >>> TableNullBoolean(val=True).save()
    >>> TableNullBoolean(val=False).save()
    >>> len(list(TableNullBoolean.objects.all()))
    3
    """
    val = models.BooleanField(null=True)

class TableNullNullBoolean(BaseModel):
    """
    >>> TableNullNullBoolean(val=None).save()
    >>> TableNullNullBoolean(val=True).save()
    >>> TableNullNullBoolean(val=False).save()
    >>> len(list(TableNullNullBoolean.objects.all()))
    3
    """
    val = models.NullBooleanField(null=True)

class TableNullDecimal(BaseModel):
    """
    >>> TableNullDecimal(val=None).save()
   
    Try a value at the top end of the specified precision/scale
    >>> TableNullDecimal(val=decimal.Decimal('99.99')).save()
    
    >>> len(list(TableNullDecimal.objects.all()))
    2
    """
    val = models.DecimalField(null=True, max_digits=4, decimal_places=2)

class TableNullFloat(BaseModel):
    """
    >>> TableNullFloat(val=None).save()
    >>> TableNullFloat(val=34.3).save()
    >>> len(list(TableNullFloat.objects.all()))
    2
    """
    val = models.FloatField(null=True)
