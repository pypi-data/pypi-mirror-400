from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from netbox.api.fields import ContentTypeField
from utilities.api import get_serializer_for_model
from tenancy.api.serializers import TenantSerializer, TenantGroupSerializer
from dcim.api.serializers import DeviceSerializer
from virtualization.api.serializers import VirtualMachineSerializer
from ipam.api.serializers import ServiceSerializer as IpamServiceSerializer

from netbox.api.serializers import NetBoxModelSerializer

from nb_itsm import models
from nb_itsm import choices


class ApplicationSerializer(NetBoxModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    display = serializers.SerializerMethodField("get_display")
    version = serializers.CharField()
    devices = DeviceSerializer(many=True, required=False, allow_null=True, nested=True)
    vm = VirtualMachineSerializer(many=True, required=False, allow_null=True, nested=True)
    ipam_services = IpamServiceSerializer(many=True, required=False, allow_null=True, nested=True)

    def get_display(self, obj):
        return f"{obj}"

    class Meta:
        model = models.Application
        fields = [
            "id",
            "display",
            "name",
            "version",
            "devices",
            "vm",
            "ipam_services",
        ]

    def create(self, validated_data):
        devices = validated_data.pop("devices", None)
        virtual_machines = validated_data.pop("vm", None)
        ipam_services = validated_data.pop("ipam_services", None)

        application = super().create(validated_data)

        if devices is not None:
            application.devices.set(devices)
        if virtual_machines is not None:
            application.vm.set(virtual_machines)
        if ipam_services is not None:
            application.ipam_services.set(ipam_services)

        return application

    def update(self, instance, validated_data):
        devices = validated_data.pop("devices", None)
        virtual_machines = validated_data.pop("vm", None)
        ipam_services = validated_data.pop("ipam_services", None)

        application = super().update(instance, validated_data)

        if devices is not None:
            application.devices.set(devices)
        if virtual_machines is not None:
            application.vm.set(virtual_machines)
        if ipam_services is not None:
            application.ipam_services.set(ipam_services)

        return application


class ConfigurationItemSerializer(serializers.Serializer):

    name = serializers.CharField(read_only=True)
    display = serializers.SerializerMethodField("get_display")
    service = serializers.CharField(source="service.name", required=False)

    id = serializers.IntegerField(read_only=True)
    service_id = serializers.IntegerField(
        source="service.id",
        required=True,
    )

    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(choices.OBJECT_ASSIGNMENT_MODELS),
        required=True,
        allow_null=True,
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    assigned_object_id = serializers.IntegerField(source="assigned_object.id", write_only=True)

    def get_display(self, obj):
        return obj.name

    def get_assigned_object(self, obj):
        if obj.assigned_object is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_object)
        context = {"request": self.context["request"]}
        return serializer(obj.assigned_object, nested=True, context=context).data

    class Meta:
        model = models.ConfigurationItem
        fields = [
            "id",
            "display",
            "name",
            "service",
            "assigned_object_type",
            "assigned_object",
            "assigned_object_id",
        ]


class ServiceSerializer(NetBoxModelSerializer):

    name = serializers.CharField()
    slug = serializers.CharField()
    type = serializers.CharField()
    status = serializers.CharField()
    display = serializers.SerializerMethodField("get_display")
    clients = TenantSerializer(many=True, required=False, allow_null=True, nested=True)
    client_groups = TenantGroupSerializer(many=True, required=False, allow_null=True, nested=True)
    comments = serializers.CharField()

    def get_display(self, obj):
        return obj.name

    def create(self, validated_data):
        clients = validated_data.pop("clients", None)
        client_groups = validated_data.pop("client_groups", None)

        service = super().create(validated_data)

        if clients is not None:
            service.clients.set(clients)
        if client_groups is not None:
            service.client_groups.set(client_groups)

        return service

    def update(self, instance, validated_data):
        clients = validated_data.pop("clients", None)
        client_groups = validated_data.pop("client_groups", None)

        service = super().update(instance, validated_data)

        if clients is not None:
            service.clients.set(clients)
        if client_groups is not None:
            service.client_groups.set(client_groups)

        return service

    class Meta:
        model = models.Service
        fields = [
            "id",
            "display",
            "name",
            "slug",
            "type",
            "status",
            "clients",
            "client_groups",
            "comments"
        ]


class RelationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    service = serializers.SlugRelatedField(
        slug_field="name", queryset=models.Service.objects.all()
    )

    def get_display(self, obj):
        return obj.name

    class Meta:
        model = models.Relation
        fields = [
            "id",
            "display",
            "name",
            "service",
            "source",
            "source_shape",
            "destination",
            "destination_shape",
            "connector_shape",
            "link_text",
        ]

class PenTestSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    service = serializers.SlugRelatedField(
        slug_field="name", queryset=models.Service.objects.all()
    )


    class Meta:
        model = models.PenTest
        fields = [
            "id",
            "service",
            "status",
            "comments",
            "date",
            "ticket",
            "report_link"
        ]
