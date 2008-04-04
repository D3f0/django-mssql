from django.db import models

class Choice(models.Model):
	choice = models.TextField(max_length=200)
	longchoice =  models.TextField()
	votes = models.IntegerField()
