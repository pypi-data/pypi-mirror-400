from netbox.api.viewsets import NetBoxModelViewSet

from nb_itsm import models
from nb_itsm import filtersets
from . import serializers

class ConfigurationItemViewSet(NetBoxModelViewSet):
    queryset = models.ConfigurationItem.objects.all()
    serializer_class = serializers.ConfigurationItemSerializer
    filterset_class = filtersets.ConfigurationItemFilter

class ItilServiceViewSet(NetBoxModelViewSet):
    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer

class ApplicationViewSet(NetBoxModelViewSet):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationSerializer

class RelationViewSet(NetBoxModelViewSet):
    queryset = models.Relation.objects.all()
    serializer_class = serializers.RelationSerializer

class PenTestViewSet(NetBoxModelViewSet):
    queryset = models.PenTest.objects.all()
    serializer_class = serializers.PenTestSerializer
