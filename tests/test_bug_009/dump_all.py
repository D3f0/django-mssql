from myapp.models import *

print list(TableNullText.objects.all())
print list(TableNullInteger.objects.all())
print list(TableNullDate.objects.all())
