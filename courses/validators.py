from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Create your models here.
def validate_termcode(value):
    if not (value > 0 and value % 10 >= 1 and value % 10 <= 3):
        raise ValidationError(
            _('%(value)s is not a valid term code'),
            params={'value': value},
        )
