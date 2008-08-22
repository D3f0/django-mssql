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
    >>> obj = TableNullChar(val=None)
    >>> obj.save()
    >>> obj = TableNullChar(val="This is my string value.")
    >>> obj.save()
    >>> len(list(TableNullChar.objects.all()))
    2
    """
    val = models.CharField(null=True, max_length=100)
    
class TableNullText(BaseModel):
    """
    >>> obj = TableNullText(val=None)
    >>> obj.save()
    >>> obj = TableNullText(val="This is my string value.")
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
    
    Try a value at the top end of the specified precision/scale
    >>> obj = TableNullDecimal(val=decimal.Decimal('99.99'))
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
    
class Bug23Table(models.Model):
    """
    Test inserting mixed NULL and non-NULL values.
    
    >>> obj = Bug23Table(mycharfield1=None, mycharfield2="text2", myintfield=1)
    >>> obj.save()
    >>> obj = Bug23Table(mycharfield1="text1", mycharfield2=None, myintfield=1)
    >>> obj.save()
    >>> obj = Bug23Table(mycharfield1="text1", mycharfield2="text2", myintfield=None)
    >>> obj.save()
    >>> obj = Bug23Table(mycharfield1=None, mycharfield2=None, myintfield=1)
    >>> obj.save()
    >>> obj = Bug23Table(mycharfield1=None, mycharfield2="text2", myintfield=None)
    >>> obj.save()
    >>> obj = Bug23Table(mycharfield1="text1", mycharfield2=None, myintfield=None)
    >>> obj.save()
    >>> obj = Bug23Table(mycharfield1=None, mycharfield2=None, myintfield=None)
    >>> obj.save()
    >>> objs = list(Bug23Table.objects.all())
    >>> len(objs)
    7
    >>> len([obj for obj in objs if obj.mycharfield1=="text1"])
    3
    >>> len([obj for obj in objs if obj.mycharfield2=="text2"])
    3
    >>> len([obj for obj in objs if obj.myintfield==1])
    3
    """
    mycharfield1 = models.CharField(max_length=100, null=True)
    mycharfield2 = models.CharField(max_length=50, null=True)
    myintfield = models.IntegerField(null=True)

class Bug21Table(models.Model):
    """
    Test adding decimals as actual types or as strings.
    
    >>> obj = Bug21Table(a='decimal as decimal', d=decimal.Decimal('12.34'))
    >>> obj.save()
    >>> obj = Bug21Table(a='decimal as string', d=u'56.78')
    >>> obj.save()
    >>> len(list(Bug21Table.objects.all()))
    2
    """
    a = models.CharField(max_length=50)
    d = models.DecimalField(max_digits=5, decimal_places=2)

class Bug27Table(models.Model):
    """
    Test that extra/select works, and doesn't interfere with the 
    limit/offset implementation.
    
    >>> Bug27Table(a=100).save()
    >>> Bug27Table(a=101).save()
    >>> len(list(Bug27Table.objects.all()))
    2
    
    >>> objs = list(Bug27Table.objects.extra(select={'alias_for_a':'a'}).order_by('a'))
    >>> objs[0].alias_for_a
    100

    >>> objs[1].alias_for_a
    101
    """
    
    a = models.IntegerField()
