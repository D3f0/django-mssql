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

class Player(models.Model):
    name = models.CharField(max_length=40)
    
class GamerCard(models.Model):
    player = models.ForeignKey(Player)
    name = models.CharField(max_length=40, default="default_card")
    avatar = models.CharField(max_length=40)
    
class Bet(models.Model):
    """Test cross-table aggregates
    
    >>> p1 = Player(name="Adam Vandenberg")
    >>> p1.save()
    
    >>> p2 = Player(name="Joe Betsalot")
    >>> p2.save()
    
    >>> GamerCard(player=p1).save()
    >>> GamerCard(player=p2).save()
    
    >>> Bet(player=p1, amount="100.00").save()
    >>> Bet(player=p1, amount="200.00").save()
    >>> Bet(player=p1, amount="300.00").save()
    >>> Bet(player=p1, amount="400.00").save()
    >>> Bet(player=p1, amount="500.00").save()
    
    >>> Bet(player=p2, amount="1000.00").save()
    >>> Bet(player=p2, amount="2000.00").save()
    >>> Bet(player=p2, amount="3000.00").save()
    >>> Bet(player=p2, amount="4000.00").save()
    >>> Bet(player=p2, amount="5000.00").save()
    
    >>> p = Player.objects.annotate(Count('bet'), avg_bet=Avg('bet__amount')).order_by('name')
    
    >>> p[0].name
    u'Adam Vandenberg'
    >>> p[0].bet__count
    5
    >>> p[0].avg_bet
    300
    
    >>> p[1].name
    u'Joe Betsalot'
    >>> p[1].bet__count
    5
    >>> p[1].avg_bet
    3000
    
    >>> p = Player.objects.annotate(bets=Count('bet'), avg_bet=Avg('bet__amount')).values()
    """
    player = models.ForeignKey(Player)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
