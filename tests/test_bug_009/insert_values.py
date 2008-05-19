from myapp.models import *
import datetime
import decimal

# (TableNullText, TableNullInteger, TableNullDateTime, TableNullDate, TableNullTime, TableNullBoolean, TableNullNullBoolean, TableNullDecimal, TableNullFloat)

t1 = TableNullText(amount="this is some text")
t1.save()

t2 = TableNullInteger(amount=23423)
t2.save()

t3 = TableNullDateTime(amount=datetime.datetime.now())
t3.save()

t4 = TableNullDate(amount=datetime.date.today())
t4.save()

# Time fields not currently handled
# t5 = TableNullTime(amount=datetime.datetime.now().time())
# t5.save()

t6 = TableNullBoolean(amount=True)
t6.save()

t7 = TableNullNullBoolean(amount=True)
t7.save()

# Decimal fields are being sent back as string values.
# This causes problems for MS SQL, so we'll need a workaround
# before enabling this.
#t8 = TableNullDecimal(amount=decimal.Decimal("34232.27"))
#t8.save()

t9 = TableNullFloat(amount=34232.27)
t9.save()
