"""This module provides SQL Server specific fields for Django models."""
from django.db.models import AutoField, ForeignKey, IntegerField
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

class BigAutoField(AutoField):
    """A bigint IDENTITY field"""
    def get_internal_type(self):
        return "BigAutoField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise ValidationError(
                _("This value must be a long."))

    def get_db_prep_value(self, value):
        if value is None:
            return None
        return long(value)

class BigForeignKey(ForeignKey):
    """A ForeignKey field that points to a BigAutoField or BigIntegerField"""
    def db_type(self):
        return BigIntegerField().db_type()

class BigIntegerField(IntegerField):
    """A BigInteger field, until Django ticket #399 lands (if ever.)"""
    def get_internal_type(self):
        return "BigIntegerField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise ValidationError(
                _("This value must be a long."))

    def get_db_prep_value(self, value):
        if value is None:
            return None
        return long(value)
