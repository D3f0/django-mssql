"""This module provides SQL Server specific fields for Django models."""
from django.db.models import IntegerField

class BigIntegerField(IntegerField):
    """A BigInteger field, until Django ticket #399 lands (if ever.)"""
    def get_internal_type(self):
        return "BigIntegerField"
