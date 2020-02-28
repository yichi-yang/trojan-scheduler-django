from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import time


def coursebin_validator(section_list):
    if not isinstance(section_list, list):
        raise ValidationError("coursebin must be a list")

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


def validate_time(time_str, field_name):
    if not time_str:
        raise ValidationError(_('%(field_name)s cannot be empty'),
                              params={'field_name': field_name},)
    try:
        time.fromisoformat(time_str)
    except ValueError:
        raise ValidationError(_('%(value)s is not a valid time string'),
                              params={'value': time_str},)


def check_type(value, field_name, types):
    if not isinstance(value, types):
        raise ValidationError(_("invalid %(field)s %(value)s, expect %(types)s"),
                              params={'field': field_name, 'value': value, 'types': types},)


def preference_validator(preference):
    if not preference:
        raise ValidationError(_("preference cannot be empty"))

    early_time = preference.get("early_time")
    late_time = preference.get("late_time")
    break_time = preference.get("break_time")

    validate_time(early_time, "early_time")
    validate_time(late_time, "late_time")
    validate_time(break_time, "break_time")

    early_weight = preference.get("early_weight")
    late_weight = preference.get("late_weight")
    break_weight = preference.get("break_weight")

    reserved = preference.get("reserved")

    check_type(early_weight, "early_weight", (int, float))
    check_type(late_weight, "late_weight", (int, float))
    check_type(break_weight, "break_weight", (int, float))
    check_type(reserved, "reserved", list)

    for slot in reserved:
        to_time = slot.get("to")
        from_time = slot.get("from")
        weight = slot.get("weight")
        wiggle = slot.get("wiggle")

        check_type(weight, "weight", (int, float))

        validate_time(to_time, "to")
        validate_time(from_time, "from")
        validate_time(wiggle, "wiggle")


def setting_validator(setting):
    course = setting.get("course")
    term = setting.get("term")
    toolsOpen = setting.get("toolsOpen")
    clearedSections = setting.get("clearedSections")
    clearedOnly = setting.get("clearedOnly")
    excludeClosed = setting.get("excludeClosed")
    exemptedSections = setting.get("exemptedSections")

    check_type(course, "course", str)
    check_type(term, "term", str)
    check_type(toolsOpen, "toolsOpen", bool)
    check_type(clearedSections, "clearedSections", str)
    check_type(clearedOnly, "clearedOnly", bool)
    check_type(excludeClosed, "excludeClosed", bool)
    check_type(exemptedSections, "exemptedSections", str)
