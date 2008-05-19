from django.db import models

class BaseModel(models.Model):
    def __unicode__(self):
        return u'id: ' + unicode(self.id) + ' Amount: ' + unicode(self.amount)

    class Meta:
        abstract = True


class TableNullText(BaseModel):
    amount = models.TextField(null=True)

class TableNullInteger(BaseModel):
    amount = models.IntegerField(null=True)

class TableNullDateTime(BaseModel):
    amount = models.DateTimeField(null=True)

class TableNullDate(BaseModel):
    amount = models.DateField(null=True)

class TableNullTime(BaseModel):
    amount = models.TimeField(null=True)

class TableNullBoolean(BaseModel):
    amount = models.BooleanField(null=True)

class TableNullNullBoolean(BaseModel):
    amount = models.NullBooleanField(null=True)

class TableNullDecimal(BaseModel):
    amount = models.DecimalField(null=True, max_digits=4, decimal_places=2)

class TableNullFloat(BaseModel):
    amount = models.FloatField(null=True)

all_tables = (TableNullText, TableNullInteger, TableNullDateTime, TableNullDate, TableNullTime, TableNullBoolean, TableNullNullBoolean, TableNullDecimal, TableNullFloat)
