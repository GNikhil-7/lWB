from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.db.models.fields.files import FieldFile

from cms.audit import get_current_user
from cms.models import (
    AboutPage,
    AuditLog,
    ContactPage,
    Founder,
    HomeFeature,
    HomePage,
    IndustryCard,
    ResourceItem,
    ServiceCard,
    ServicesPage,
    SiteSettings,
    ValueCard,
)


AUDITED_MODELS = (
    SiteSettings,
    HomePage,
    HomeFeature,
    AboutPage,
    Founder,
    ValueCard,
    ServicesPage,
    ServiceCard,
    IndustryCard,
    ResourceItem,
    ContactPage,
)


def _serialize_value(value):
    if value is None:
        return ""
    if isinstance(value, FieldFile):
        return value.url if value else ""
    return str(value)


def _serialize_instance(instance):
    data = {}
    for field in instance._meta.fields:
        if field.name in {"id", "pk"}:
            continue
        if field.is_relation:
            continue
        data[field.name] = _serialize_value(getattr(instance, field.name))
    return data


def _diff_changes(previous, current):
    changes = {}
    for field_name, current_value in current.items():
        previous_value = previous.get(field_name, "")
        if previous_value != current_value:
            changes[field_name] = {
                "from": previous_value,
                "to": current_value,
            }
    return changes


@receiver(pre_save)
def capture_previous_state(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    if not instance.pk:
        instance._audit_previous_state = {}
        return

    previous = sender.objects.filter(pk=instance.pk).first()
    instance._audit_previous_state = _serialize_instance(previous) if previous else {}


@receiver(post_save)
def create_audit_log_on_save(sender, instance, created, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    previous = getattr(instance, "_audit_previous_state", {})
    current = _serialize_instance(instance)

    if created:
        changes = {field_name: {"from": "", "to": value} for field_name, value in current.items() if value != ""}
        action = "create"
    else:
        changes = _diff_changes(previous, current)
        action = "update"

    if not changes and not created:
        return

    AuditLog.objects.create(
        model_name=sender._meta.verbose_name.title(),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action=action,
        changed_by=get_current_user(),
        changes=changes,
    )

    if hasattr(instance, "_audit_previous_state"):
        delattr(instance, "_audit_previous_state")


@receiver(post_delete)
def create_audit_log_on_delete(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    deleted_values = _serialize_instance(instance)
    changes = {field_name: {"from": value, "to": ""} for field_name, value in deleted_values.items() if value != ""}

    AuditLog.objects.create(
        model_name=sender._meta.verbose_name.title(),
        object_id=str(instance.pk),
        object_repr=str(instance),
        action="delete",
        changed_by=get_current_user(),
        changes=changes,
    )
