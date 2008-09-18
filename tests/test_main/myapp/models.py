import datetime
import decimal
from django.db import models

import unittest

class Bug19Table(models.Model):
    """ A simple model for testing string comparisons.
    
    >>> choices = (
    ...     "no_slashes", "no_slashes_2",
    ...     r"C:\some_folder\somefile.ext", r"\some_folder",
    ...     "some_folder"+'\',
    ...     "[brackets]",
    ...     )
    >>> for c in choices:
    ...     Bug19Table.objects.create(choice=c).save()
    >>> len(Bug19Table.objects.all())
    6    

    >>> len(Bug19Table.objects.filter(choice__contains="shes"))
    2
    
    >>> len(Bug19Table.objects.filter(choice__endswith="shes"))
    1
    
    >>> len(Bug19Table.objects.filter(choice__contains=r"der\som"))
    1
    
    >>> len(Bug19Table.objects.filter(choice__endswith=r"der\somefile.ext"))
    1
    
    >>> len(Bug19Table.objects.filter(choice__contains="["))
    1
    
    """
    choice = models.TextField(max_length=200)
    
    def __unicode__(self):
        return self.choice


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


# Test slicing
class Products(models.Model):
    """
    >>> names=['Screws', 'Bolts', 'Nuts', 'SPipe', 'LPipe', 'Item', 'Zebra']
    >>> for n in names: product = Products.objects.create(name=n)
    >>> p = Products.objects
    >>> len(list(p.all()))
    7
    >>> len(list(p.all()[:3]))
    3
    >>> len(list(p.all()[2:5]))
    3
    >>> len(list(p.all()[5:]))
    2
    >>> pn = p.order_by('name')
    >>> list(pn)
    [Bolts, Item, LPipe, Nuts, Screws, SPipe, Zebra]
    >>> list(pn[:3])
    [Bolts, Item, LPipe]
    >>> list(pn[2:5])
    [LPipe, Nuts, Screws]
    >>> list(pn[5:])
    [SPipe, Zebra]
    """

    productid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
        
    def __repr__(self):
        return self.name
        
    def __unicode__(self):
        return "<Product %u: %u>" % (self.productid, self.name)


class RelatedB(models.Model):
    a = models.CharField(max_length=50)
    b = models.CharField(max_length=50)
    c = models.CharField(max_length=50)


class RelatedA(models.Model):
    """
    #>>> b = RelatedB(a='this is a value', b="valueb", c="valuec")
    #>>> b.save()
    #>>> a = RelatedA(a="valuea", b=b)
    #>>> a.save()
    #>>> a = RelatedA(a="valuea", b=b)
    #>>> a.save()
    #>>> items = RelatedA.objects.select_related()[1:2]
    #>>> len(items)
    #1
    """
    a = models.CharField(max_length=50)
    b = models.ForeignKey(RelatedB)
