from django.db import models

class TableNullText(models.Model):
	amount = models.TextField(null=True)
	
	def __unicode__(self):
		return u'Amount: ' + unicode(self.amount)
		
class TableNullInteger(models.Model):
	amount = models.IntegerField(null=True)
	
	def __unicode__(self):
		return u'Amount: ' + unicode(self.amount)

class TableNullDate(models.Model):
	amount = models.DateTimeField(null=True)
	
	def __unicode__(self):
		return u'Amount: ' + unicode(self.amount)
