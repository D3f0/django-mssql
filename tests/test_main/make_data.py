from paging.models import *

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
