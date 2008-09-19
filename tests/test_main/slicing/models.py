from django.db import models
from django.core.paginator import Paginator
from django.test import TestCase


class FirstTable(models.Model):
    b = models.CharField(max_length=100)
    # Add a reserved word column; this will get quoted correctly
    # in queries, but need to make sure paging doesn't break:
    # * Paging should re-quote alias names correctly
    # * The string splitting on 'FROM' shouldn't break either
    c = models.CharField(default=u'test', max_length=10, db_column=u'FROM')
    
    def __repr__(self):
        return '<FirstTable %s: %s, %s>' % (self.pk, self.b, self.c)

class SecondTable(models.Model):
    a = models.ForeignKey(FirstTable)
    b = models.CharField(max_length=100)
    
    def __repr__(self):
        return '<FirstTable %s: %s, %s>' % (self.pk, self.a_id, self.b)

# Test slicing
class Products(models.Model):
    """
    >>> names=['D', 'F', 'B', 'A', 'C', 'E', 'G']
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
    [A, B, C, D, E, F, G]
    >>> list(pn[:3])
    [A, B, C]
    >>> list(pn[2:5])
    [C, D, E]
    >>> list(pn[5:])
    [F, G]
    """

    productid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
        
    def __repr__(self):
        return self.name
        
    def __unicode__(self):
        return "<Product %u: %u>" % (self.productid, self.name)
        
class PagingTestCase(TestCase):
    """The Paginator uses slicing internally."""
    fixtures = ['paging.json']
    
    def get_q(self, a1_pk):
        return SecondTable.objects.filter(a=a1_pk).order_by('b').select_related(depth=1)

    def try_page(self, page_number, q):
        # Use a single item per page, to get multiple pages.
        pager = Paginator(q, 1)
        self.assertEquals(pager.count, 3)

        on_this_page = list(pager.page(page_number).object_list)
        self.assertEquals(len(on_this_page), 1)
        self.assertEquals(on_this_page[0].b, 'B'+str(page_number))
    
    def testWithDuplicateColumnNames(self):
        a1_pk = FirstTable.objects.get(b='A1').pk
        q = self.get_q(a1_pk)
        
        for i in (1,2,3):
            self.try_page(i, q)
            
    def testPerRowSelect(self):
        a1_pk = FirstTable.objects.get(b='A1').pk
        q = SecondTable.objects.filter(a=a1_pk).order_by('b').select_related(depth=1).extra(select=
        {
        'extra_column': 
            "select slicing_FirstTable.id from slicing_FirstTable where slicing_FirstTable.id=%s" % (a1_pk,)
        })
        
        for i in (1,2,3):
            self.try_page(i, q)
