from django import forms

from dcim.models import Device
from tenancy.models import Tenant, TenantGroup
from virtualization.models import VirtualMachine
from ipam.models import Service as IpamService
from utilities.forms.fields import (
    DynamicModelMultipleChoiceField,
    DynamicModelChoiceField,
    CSVModelMultipleChoiceField,
)
from utilities.forms.widgets import DatePicker

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelFilterSetForm,
    NetBoxModelBulkEditForm,
    NetBoxModelImportForm,
)

from . import models

class ItilServiceForm(NetBoxModelForm):

    clients = DynamicModelMultipleChoiceField(label="Clients",
        queryset=Tenant.objects.all(),
        required=False,
    )

    client_groups = DynamicModelMultipleChoiceField(label="Client Groups",
        queryset=TenantGroup.objects.all(),
        required=False,
    )

    class Meta:
        model = models.Service
        fields = [
            "name",
            "slug",
            "status",
            "type",
            "clients",
            "client_groups",
            "comments",
        ]

class ApplicationForm(NetBoxModelForm):

    devices = DynamicModelMultipleChoiceField(label="Devices",
        queryset=Device.objects.all(),
        required=False,
    )
    vm = DynamicModelMultipleChoiceField(label="Virtual Machines",
        queryset=VirtualMachine.objects.all(),
        required=False,
    )
    ipam_services = DynamicModelMultipleChoiceField(label="IPAM Services",
        queryset=IpamService.objects.all(),
        required=False,
    )

    class Meta:
        model = models.Application
        fields = [
            "name",
            "version",
            "devices",
            "vm",
            "ipam_services",
        ]

class ConfigurationItemForm(NetBoxModelForm):

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
    )

    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
    )

    class Meta:
        model = models.ConfigurationItem
        fields = [
            'service',
        ]


class PenTestForm(NetBoxModelForm):

    class Meta:
        model = models.PenTest
        fields = [
            'service',
            'comments',
            'status',
            'date',
            'ticket',
            "report_link",
        ]

        widgets = {
            'date': DatePicker(),
        }

class RelationForm(NetBoxModelForm):

    source = DynamicModelChoiceField(
        queryset=models.ConfigurationItem.objects.all(),
        required=True,
        label='Source',
        query_params={
            'service_id': '$service',
        },
    )

    destination = DynamicModelChoiceField(
        queryset=models.ConfigurationItem.objects.all(),
        required=True,
        label='Destination',
        query_params={
            'service_id': '$service',
        },
    )

    link_text = forms.CharField(required=False)

    class Meta:
        model = models.Relation
        fields = [
            'service',
            'source',
            'source_shape',
            'destination',
            'destination_shape',
            "connector_shape",
            "link_text",
        ]

class RelationFilterForm(NetBoxModelFilterSetForm):
    model = models.Relation

    class Meta:
        fields = [
            'service',
            'source',
            'source_shape',
            'destination',
            'destination_shape',
            "connector_shape",
            "link_text",
        ]


class ServiceFilterForm(forms.ModelForm):

    q = forms.CharField(
        required=False,
        label='Search'
    )
    clients = DynamicModelMultipleChoiceField(
        label="Clients",
        queryset=Tenant.objects.all(),
        required=False,
    )

    class Meta:
        model = models.Service
        fields = [
            'q',
            'clients',
        ]

class ServiceBulkEditForm(NetBoxModelBulkEditForm):
    model = models.Service

    clients = DynamicModelMultipleChoiceField(
        label="Clients",
        queryset=Tenant.objects.all(),
        required=False,
    )
    comments = forms.Textarea(
        attrs={'class': 'font-monospace'}
    )

    class Meta:
        nullable_fields = (
            "clients",
            "comments",
        )

class ItilServiceImportForm(NetBoxModelImportForm):
    clients = CSVModelMultipleChoiceField(
        label="Clients",
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        error_messages={
            "invalid_choice": "Client name not found",
        }
    )

    class Meta:
        model = models.Service
        fields = ["name",
                  "clients",
                  "comments",
          ]


class ApplicationFilterForm(forms.ModelForm):

    q = forms.CharField(
        required=False,
        label='Search'
    )
    devices = DynamicModelMultipleChoiceField(label="Devices",
        queryset=Device.objects.all(),
        required=False,
    )

    vm = DynamicModelMultipleChoiceField(label="Virtual Machines",
        queryset=VirtualMachine.objects.all(),
        required=False,
    )

    ipam_services = DynamicModelMultipleChoiceField(label="IPAM Services",
        queryset=IpamService.objects.all(),
        required=False,
    )

    class Meta:
        model = models.Service
        fields = [
            'q',
            'devices',
            'vm',
            'ipam_services',
        ]

class ApplicationImportForm(NetBoxModelImportForm):

    devices = CSVModelMultipleChoiceField(
        label="Devices",
        queryset=Device.objects.all(),
        required=False,
        to_field_name="name",
        error_messages={
            "invalid_choice": "Device name not found",
        }
    )
    vm = CSVModelMultipleChoiceField(
        label="Virtual Machines",
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name="name",
        error_messages={
            "invalid_choice": "Virtual machine name not found",
        }
    )

    class Meta:
        model = models.Application
        fields = ["name", "version", "devices", "vm"]

class ApplicationBulkEditForm(NetBoxModelBulkEditForm):
    model = models.Application

    devices = DynamicModelMultipleChoiceField(
        label="Devices",
        queryset=Device.objects.all(),
        required=False,
    )
    vm = DynamicModelMultipleChoiceField(
        label="Virtual Machines",
        queryset=VirtualMachine.objects.all(),
        required=False,
    )

    class Meta:
        fields = ["version", "devices", "vm"]
        nullable_fields = ("devices", "vm")
