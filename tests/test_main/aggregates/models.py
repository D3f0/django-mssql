from django.db import models
from django.db.models import (
    Avg, Count, Max, Min, StdDev, Sum, Variance)

class AmountTable(models.Model):
    """Test that basic aggregates work.

    >>> AmountTable(amount=100).save()
    >>> AmountTable(amount=101).save()
    >>> AmountTable(amount=102).save()
    >>> len(list(AmountTable.objects.all()))
    3

    >>> AmountTable.objects.aggregate(Avg('amount'))
    {'amount__avg': 101.0}

    >>> AmountTable.objects.aggregate(Max('amount'))
    {'amount__max': 102}

    >>> AmountTable.objects.aggregate(Min('amount'))
    {'amount__min': 100}

    >>> AmountTable.objects.aggregate(Sum('amount'))
    {'amount__sum': 303}
    """
    amount = models.IntegerField()
