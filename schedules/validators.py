from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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


def preference_validator(preference):
    if not preference:
        raise ValidationError("preference cannot be empty")

    early_time = preference.get("early_time")
    late_time = preference.get("late_time")
    break_time = preference.get("break_time")

    early_weight = preference.get("early_weight")
    late_weight = preference.get("late_weight")
    break_weight = preference.get("break_weight")

    reserved = preference.get("reserved")

    if not early_weight or not (isinstance(early_weight, int) or isinstance(early_weight, float)):
        raise ValidationError("invalid early_weight")

    if not late_weight or not (isinstance(late_weight, int) or isinstance(late_weight, float)):
        raise ValidationError("invalid late_weight")

    if not break_weight or not (isinstance(break_weight, int) or isinstance(break_weight, float)):
        raise ValidationError("invalid break_weight")

    if not isinstance(reserved, list):
        raise ValidationError("invalid reserved")

    for slot in reserved:
        pass
