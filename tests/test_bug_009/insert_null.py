from myapp.models import *

for klass in all_tables:
    obj = klass(amount=None)
    obj.save()
