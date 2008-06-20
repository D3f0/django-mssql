# To load fixtures:
#  manage.py loaddata data.json
# From the command line, do "manage.py shell" and then "import testing"
# None of these should error out (assuming you've loaded the fixtures.)

from myapp.models import *

def run_test(query, expected_count, message, messages):
    items = list(query)
#    print "%s items (%s expected)" % (len(items), expected_count)
#    print items
    
    if len(items)!=expected_count: 
        messages.append("Expected %s items in %s" % (expected_count, message))

p = Products.objects
messages = list()

run_test(p.all(), 7, ".all()", messages)
run_test(p.all()[:3], 3, ".all()[:3]", messages)
run_test(p.all()[2:4], 2, ".all()[2:4]", messages)

run_test(p.order_by('name'), 7, ".order_by('name')", messages)
run_test(p.order_by('name')[:3], 3, ".order_by('name')[:3]", messages)
run_test(p.order_by('name')[2:4], 2, ".order_by('name')[2:4]", messages)

if not messages:
    messages.append("No messages.")

print
print "\n".join(messages)
print "done"
