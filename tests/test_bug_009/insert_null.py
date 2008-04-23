from myapp.models import *

for klass in (TableNullText, TableNullInteger, TableNullDateTime, TableNullDate, TableNullTime, TableNullBoolean, TableNullDecimal):
	obj = klass(amount=None)
	obj.save()
