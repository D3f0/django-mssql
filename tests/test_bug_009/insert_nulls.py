from myapp.models import *
obj1 = SomeTable(amount=47)
obj1.save()

obj2 = SomeTable(amount=None)
obj2.save()
