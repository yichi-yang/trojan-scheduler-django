from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Create your models here.


def validate_termcode(value):
    if not (value > 20000 and value <= 30000 and value % 10 >= 1 and value % 10 <= 3):
        raise ValidationError(
            _('%(value)s is not a valid term code'),
            params={'value': value},
        )


def validate_days_array(days):
    for day in days:
        if not (day >= 0 and day <= 6):
            raise ValidationError(
                _('%(value)s contains invlaid day code'),
                params={'value': days},
            )

    if len(set(days)) != len(days):
        raise ValidationError(
            _('%(value)s contains duplicates'),
            params={'value': days},
        )
