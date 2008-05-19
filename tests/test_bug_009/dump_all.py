from myapp.models import *

for klass in all_tables:
	print list(klass.objects.all())
