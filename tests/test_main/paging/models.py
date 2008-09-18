from django.db import models
from django.core.paginator import Paginator

from django.test import TestCase
#import unittest

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


class PagingTestCase(TestCase):
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
            'extra_column': "select paging_FirstTable.id from paging_FirstTable where paging_FirstTable.id=%s" % (a1_pk,)
        })
        
        for i in (1,2,3):
            self.try_page(i, q)
