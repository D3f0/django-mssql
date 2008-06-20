# To load fixtures:
#  manage.py loaddata data.json
# From the command line, do "manage.py shell" and then "import testing"
# None of these should error out (assuming you've loaded the fixtures.)

from myapp.models import *
p = Products.objects

print p.all()
print p.all()[:3]
print p.all()[2:4]

print p.order_by('name')
print p.order_by('name')[:3]
print p.order_by('name')[2:4]

print "done"
