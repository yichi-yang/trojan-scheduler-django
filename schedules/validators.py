from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Create your models here.


def coursebin_validator(section_list):
    if not section_list:
        raise ValidationError("coursebin cannot be an empty list")

    for node in section_list:
        node_type = node.get("type")
        node_id = node.get("node_id")
        node_parent = node.get("parent")
        node_group = node.get("group")

        if node_type not in ["course", "part", "component", "section"]:
            raise ValidationError(
                _('%(value)s does not have a valid type'),
                params={'value': node},
            )
        if not node_id:
            raise ValidationError(
                _('%(value)s does not have a valid node_id'),
                params={'value': node},
            )

        if node_type != "course":
            if not node_parent:
                raise ValidationError(
                    _('%(value)s does not have a valid parent'),
                    params={'value': node},
                )
        else:
            if not node_group:
                raise ValidationError(
                    _('%(value)s does not have a valid group'),
                    params={'value': node},
                )
