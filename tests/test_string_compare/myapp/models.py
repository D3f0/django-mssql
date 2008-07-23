from django.db import models

class Choice(models.Model):
    """ A simple model for testing string comparisons.
    
    >>> choices = (
    ...     "no_slashes", "no_slashes_2",
    ...     r"C:\some_folder\somefile.ext", r"\some_folder",
    ...     "some_folder"+'\',
    ...     "[brackets]",
    ...     )
    >>> for c in choices:
    ...     Choice.objects.create(choice=c).save()
    >>> len(Choice.objects.all())
    6    

    >>> len(Choice.objects.filter(choice__contains="shes"))
    2
    
    >>> len(Choice.objects.filter(choice__endswith="shes"))
    1
    
    >>> len(Choice.objects.filter(choice__contains=r"der\som"))
    1
    
    >>> len(Choice.objects.filter(choice__endswith=r"der\somefile.ext"))
    1
    
    >>> len(Choice.objects.filter(choice__contains="["))
    1
    
    """
    choice = models.TextField(max_length=200)
    
    def __unicode__(self):
        return self.choice
