import datetime
import decimal
from django.db import models, IntegrityError
from django.test import TestCase
from django.core.paginator import Paginator
from sqlserver_ado.fields import BigAutoField, BigIntegerField

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


class Bug21Table(models.Model):
    """
    Test adding decimals as actual types or as strings.
    
    >>> Bug21Table(a='decimal as decimal', d=decimal.Decimal('12.34')).save()
    >>> Bug21Table(a='decimal as string', d=u'56.78').save()
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

class Bug23Table(models.Model):
    """
    Test inserting mixed NULL and non-NULL values.

    >>> Bug23Table(mycharfield1=None, mycharfield2="text2", myintfield=1).save()
    >>> Bug23Table(mycharfield1="text1", mycharfield2=None, myintfield=1).save()
    >>> Bug23Table(mycharfield1="text1", mycharfield2="text2", myintfield=None).save()
    >>> Bug23Table(mycharfield1=None, mycharfield2=None, myintfield=1).save()
    >>> Bug23Table(mycharfield1=None, mycharfield2="text2", myintfield=None).save()
    >>> Bug23Table(mycharfield1="text1", mycharfield2=None, myintfield=None).save()
    >>> Bug23Table(mycharfield1=None, mycharfield2=None, myintfield=None).save()
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


# Bug 26 tables, RelatedA and RelatedB
class RelatedB(models.Model):
    a = models.CharField(max_length=50)
    b = models.CharField(max_length=50)
    c = models.CharField(max_length=50)

class RelatedA(models.Model):
    a = models.CharField(max_length=50)
    b = models.ForeignKey(RelatedB)

class Bug26TestCase(TestCase):
    """Test that slicing queries w/ duplicate column names works."""

    def testWithDuplicateColumnNames(self):
        b = RelatedB(a='this is a value', b="valueb", c="valuec")
        b.save()
        
        RelatedA(a="valuea", b=b).save()
        RelatedA(a="valuea", b=b).save()

        items = RelatedA.objects.select_related()[1:2]
        self.assertEqual(len(items), 1)
        
class Bug34DatetimeTable(models.Model):
    """Ensure that __year filters work with datetime fields.
    
    >>> Bug34DatetimeTable(posted=datetime.date(2007,1,1)).save()
    >>> Bug34DatetimeTable(posted=datetime.date(2008,2,2)).save()
    >>> Bug34DatetimeTable(posted=datetime.date(2009,3,3)).save()
    >>> len((Bug34DatetimeTable.objects.filter(posted__day=3)))
    1
    >>> len(list(Bug34DatetimeTable.objects.filter(posted__month=2)))
    1
    >>> len(list(Bug34DatetimeTable.objects.filter(posted__year=2008)))
    1
    >>> len(list(Bug34DatetimeTable.objects.filter(posted__year=2005)))
    0
    """
    posted = models.DateTimeField()
        
class Bug34DateTable(models.Model):
    """Ensure that __year filters work with date fields.
    
    >>> Bug34DateTable(posted=datetime.date(2007,1,1)).save()
    >>> Bug34DateTable(posted=datetime.date(2008,2,2)).save()
    >>> Bug34DateTable(posted=datetime.date(2009,3,3)).save()
    >>> len((Bug34DateTable.objects.filter(posted__day=3)))
    1
    >>> len(list(Bug34DateTable.objects.filter(posted__month=2)))
    1
    >>> len(list(Bug34DateTable.objects.filter(posted__year=2008)))
    1
    >>> len(list(Bug34DateTable.objects.filter(posted__year=2005)))
    0
    """
    posted = models.DateField()

class Bug35ATable(models.Model):
    """Ensure that multiple Postive Integer columns across tables don't 
    create duplicate constraint names.
    """
    int1 = models.PositiveIntegerField()
    int2 = models.PositiveIntegerField()
    int3 = models.PositiveSmallIntegerField()
    int4 = models.PositiveSmallIntegerField()

class Bug35BTable(models.Model):
    """Ensure that multiple Postive Integer columns across tables don't 
    create duplicate constraint names.
    """
    int1 = models.PositiveIntegerField()
    int2 = models.PositiveIntegerField()
    int3 = models.PositiveSmallIntegerField()
    int4 = models.PositiveSmallIntegerField()

class Bug35CModel(models.Model):
    """Ensure that multiple Postive Integer columns across tables don't 
    create duplicate constraint names when using inheritence.
    
    The test for Bug35 is just the creation of the tables; there are no
    other explicit tests.
    """
    age = models.PositiveIntegerField()

    class Meta:
        abstract = True

class Bug35C1Table(Bug35CModel):
    name = models.CharField(max_length=10)
    
class Bug35C2Table(Bug35CModel):
    name = models.CharField(max_length=10)


# Bug 26 tables, RelatedA and RelatedB
class Bug37ATable(models.Model):
    a = models.CharField(max_length=50)
    b = models.CharField(max_length=50)
    c = models.CharField(max_length=50)

class Bug37BTable(models.Model):
    d = models.CharField(max_length=50)
    a = models.ForeignKey(Bug37ATable)

class Bug37TestCase(TestCase):
    """Test that IntegrityErrors are raised when appropriate."""

    def testDuplicateKeysFails(self):
        Bug37ATable(pk=1, a='a', b='b', c='c').save(force_insert=True)
        try:
            Bug37ATable(pk=1, a='a', b='b', c='c').save(force_insert=True)
        except Exception, e:
            self.failUnless(isinstance(e, IntegrityError), 'Expected IntegrityError but got: %s' % type(e))
            
    def testDeleteRelatedRecordFails(self):
        a2 = Bug37ATable(a='a', b='b', c='c')
        a2.save()
        
        Bug37BTable(d='d', a=a2).save()
        try:
            a2.delete()
        except Exception, e:
            self.failUnless(isinstance(e, IntegrityError), 'Expected IntegrityError but got: %s' % type(e))

class Bug38Table(models.Model):
    d = models.DecimalField(max_digits=5, decimal_places=2)


class Bug41Table(models.Model):
    """
    Test that pagination works with extra/select columns.

    >>> Bug41Table(a=100).save()
    >>> Bug41Table(a=101).save()
    >>> Bug41Table(a=102).save()
    >>> len(list(Bug41Table.objects.all()))
    3

    >>> objs = Bug41Table.objects.extra(select={'alias_for_a':'[regressiontests_bug41table].[a]'}).order_by('alias_for_a')
    >>> all_objs = Paginator(objs, 1)
    >>> all_objs.count
    3
    >>> all_objs.num_pages
    3
    >>> page1 = all_objs.page(1)
    >>> page1.object_list[0].alias_for_a
    100
    >>> page2 = all_objs.page(2)
    >>> page2.object_list[0].alias_for_a
    101
    """

    a = models.IntegerField()
    
class Bug62Table(models.Model):
    email = models.CharField(max_length=255, blank=True)

class Bug62TestCase(TestCase):
    def testExclude(self):
        Bug62Table(email='').save()
        Bug62Table(email='abc').save()
        Bug62Table(email='').save()
        Bug62Table(email='def').save()
        
        q = list(Bug62Table.objects.exclude(email='abc'))
        self.assertEqual(len(q), 3)

    def testExcludeEmpty(self):
        Bug62Table(email='').save()
        Bug62Table(email='abc').save()
        Bug62Table(email='').save()
        Bug62Table(email='def').save()

        q = list(Bug62Table.objects.exclude(email=''))
        self.assertEqual(len(q), 2)

    def testExcludeEmptyUnicode(self):
        Bug62Table(email='').save()
        Bug62Table(email='abc').save()
        Bug62Table(email='').save()
        Bug62Table(email='def').save()
        
        q = list(Bug62Table.objects.exclude(email=u''))
        self.assertEqual(len(q), 2)

class Bug63Table(models.Model):
    """
    Test that the BigAutoField and BigIntegerField fields work.

    >>> Bug63Table(number=2147483648L).save()
    >>> len(list(Bug63Table.objects.all()))
    1
    >>> big = Bug63Table.objects.get(number=2147483648L)
    >>> big.number
    2147483648L
    """
    id = BigAutoField(primary_key=True)
    number = BigIntegerField()
