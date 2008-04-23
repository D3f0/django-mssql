from myapp.models import *
obj1 = TableNullText(amount=None)
obj1.save()

obj2 = TableNullInteger(amount=None)
obj2.save()

obj3 = TableNullDate(amount=None)
obj3.save()
