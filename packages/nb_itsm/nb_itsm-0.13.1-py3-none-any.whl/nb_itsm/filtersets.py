import django_filters
from django.db.models import Q
from tenancy.models import Tenant, TenantGroup
from dcim.models import Device
from virtualization.models import VirtualMachine

from netbox.filtersets import NetBoxModelFilterSet

from . import models

class ConfigurationItemFilter(django_filters.FilterSet):

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    service = django_filters.ModelMultipleChoiceFilter(
        field_name="service__name",
        queryset=models.Service.objects.all(),
        to_field_name="name",
    )
    service_id = django_filters.ModelMultipleChoiceFilter(
        field_name="service__id",
        queryset=models.Service.objects.all(),
        to_field_name="id",
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        ids = []
        for configuration_item in queryset:
            if value in configuration_item.name:
                ids.append(configuration_item.id)
        return queryset.filter(id__in = ids)

    class Meta:
        model = models.ConfigurationItem

        fields = [
            "service",
        ]

class ItilServiceFilterSet(NetBoxModelFilterSet):

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    clients = django_filters.ModelMultipleChoiceFilter(
        field_name="clients__name",
        queryset=Tenant.objects.all(),
        to_field_name="name",
    )
    clients_id = django_filters.ModelMultipleChoiceFilter(
        field_name="clients__id",
        queryset=Tenant.objects.all(),
        to_field_name="id",
    )
    client_groups = django_filters.ModelMultipleChoiceFilter(
        field_name="client_groups__name",
        queryset=TenantGroup.objects.all(),
        to_field_name="name",
    )
    client_groups_id = django_filters.ModelMultipleChoiceFilter(
        field_name="client_groups__id",
        queryset=TenantGroup.objects.all(),
        to_field_name="id",
    )
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(clients__name__icontains=value)
        )
        return queryset.filter(qs_filter)


    class Meta:
        model = models.Service

        fields = [
            "id",
            "name",
            "clients",
        ]

class ApplicationFilterSet(NetBoxModelFilterSet):

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    devices = django_filters.ModelMultipleChoiceFilter(
        field_name="devices__name",
        queryset=Device.objects.all(),
        to_field_name="name",
    )
    devices_id = django_filters.ModelMultipleChoiceFilter(
        field_name="devices__id",
        queryset=Device.objects.all(),
        to_field_name="id",
    )

    virtual_machines = django_filters.ModelMultipleChoiceFilter(
        field_name="vm__name",
        queryset=VirtualMachine.objects.all(),
        to_field_name="name",
    )
    virtual_machines_id = django_filters.ModelMultipleChoiceFilter(
        field_name="vm__id",
        queryset=VirtualMachine.objects.all(),
        to_field_name="id",
    )

    def search(self, queryset, name, value):

        if not value.strip():
            return queryset

        qs_filter = (
            Q(name__icontains=value) |
            Q(devices__name__icontains=value) |
            Q(vm__name__icontains=value)
        )

        return queryset.filter(qs_filter).distinct()

    class Meta:
        model = models.Application

        fields = [
            "id",
            "name",
            "version",
            "devices",
            "virtual_machines",
        ]

class RelationFilter(NetBoxModelFilterSet):

    class Meta:
        model = models.Relation

        fields = [
            "id",
            "service",
        ]
