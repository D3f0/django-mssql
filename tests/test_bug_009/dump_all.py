from myapp.models import *

for klass in (TableNullText, TableNullInteger, TableNullDateTime, TableNullDate, TableNullTime, TableNullBoolean, TableNullDecimal):
	print list(klass.objects.all())
