from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from dcim.models import Device
from virtualization.models import VirtualMachine

from . import models

def handle_configuration_item_assigned_object_delete(sender, instance, *args, **kwargs):
    related_ics = models.ConfigurationItem.objects.filter(
        assigned_object_type=ContentType.objects.get_for_model(instance),
         assigned_object_id=instance.id)
    for configuration_items in related_ics:
        configuration_items.delete()


device_delete = receiver(post_delete, sender=Device)(handle_configuration_item_assigned_object_delete)
vm_delete = receiver(post_delete, sender=VirtualMachine)(handle_configuration_item_assigned_object_delete)
app_delete = receiver(post_delete, sender=models.Application)(handle_configuration_item_assigned_object_delete)
