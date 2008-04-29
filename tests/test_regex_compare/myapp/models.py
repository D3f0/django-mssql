from django.db import models

class Choice(models.Model):
	choice = models.TextField(max_length=200)
	
	def __unicode__(self):
		return u'Choice: %s' % (self.choice)
