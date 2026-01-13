import django_tables2 as tables

from netbox.tables import NetBoxTable, ToggleColumn , columns

from . import models


class ItilServiceTable(NetBoxTable):

    name = tables.LinkColumn(verbose_name="Service")
    slug = tables.LinkColumn(verbose_name="Slug")
    id = ToggleColumn()
    type = tables.Column(verbose_name="Type")
    status = tables.Column(verbose_name="Status")

    class Meta(NetBoxTable.Meta):
        model = models.Service
        fields = (
            "name",
            "slug",
            "type",
            "status",
        )

class ConfigurationItemsTable(NetBoxTable):
    id = ToggleColumn()
    assigned_object = tables.LinkColumn(verbose_name="Configuration Item")
    obj_type = tables.Column(verbose_name="Type")
    actions = columns.ActionsColumn(actions=("delete",))

    class Meta(NetBoxTable.Meta):
        model = models.ConfigurationItem
        fields = (
            "id",
            "assigned_object",
            "obj_type"
        )

class VulnTable(NetBoxTable):
    id = ToggleColumn()

    class Meta(NetBoxTable.Meta):
        model = models.PenTest
        fields = (
            "id",
            "ticket",
            "date",
            "status",
        )

class ApplicationTable(NetBoxTable):

    name = tables.LinkColumn(verbose_name="Application")
    id = ToggleColumn()

    class Meta(NetBoxTable.Meta):
        model = models.Application
        fields = [
            "name",
            "version",
         ]

class RelationTable(NetBoxTable):
    id = ToggleColumn()

    service = tables.LinkColumn(verbose_name="Service")
    source = tables.LinkColumn(verbose_name="Source")
    destination = tables.LinkColumn(verbose_name="Destination")

    class Meta(NetBoxTable.Meta):
        model = models.Relation
        fields = [
            "service",
            "source",
            "source_shape",
            "destination",
            "destination_shape",
            "connector_shape",
            "link_text",
        ]