import unittest
from django.db import models
from django.core.paginator import QuerySetPaginator

class FirstTable(models.Model):
    b = models.CharField(max_length=100)
    # Add a reserved word column; this will get quoted correctly
    # in queries, but need to make sure paging doesn't break:
    # * Paging should re-quote alias names correctly
    # * The string splitting on 'FROM' shouldn't break either
    c = models.CharField(default=u'test', max_length=10, db_column=u'FROM')
    
class SecondTable(models.Model):
    a = models.ForeignKey(FirstTable)
    b = models.CharField(max_length=100)


class PagingTestCase(unittest.TestCase):
    def setupPagingData(self):
        a1 = FirstTable(b='A1')
        a1.save()
        
        a2 = FirstTable(b='A2')
        a2.save()
        
        b1 = SecondTable(a=a1, b='B1')
        b1.save()

        b2 = SecondTable(a=a1, b='B2')
        b2.save()

        b3 = SecondTable(a=a1, b='B3')
        b3.save()
        
        return a1.pk
    
    def testPagingWithDuplicateColumnNames(self):
        a1_pk = self.setupPagingData()
        
        # Select related data so we get two 'b' columns per row
        # (and two id columns, too)
        data = SecondTable.objects.filter(a=a1_pk).order_by('b').select_related(depth=1)
        
        # Use a single item per page, to get multiple pages
        paged_data = QuerySetPaginator(data, 1)

        on_this_page = list(paged_data.page(1).object_list)
        self.assertEquals(len(on_this_page), 1, 'Too many results on this page.')
        self.assertEquals(on_this_page[0].b, 'B1')
        
        on_this_page = list(paged_data.page(2).object_list)
        self.assertEquals(len(on_this_page), 1, 'Too many results on this page.')
        self.assertEquals(on_this_page[0].b, 'B2')

        on_this_page = list(paged_data.page(3).object_list)
        self.assertEquals(len(on_this_page), 1, 'Too many results on this page.')
        self.assertEquals(on_this_page[0].b, 'B3')
