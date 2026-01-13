#
import re
import uuid

# Django imports
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# Netbox imports
from taggit.managers import TaggableManager
from netbox.models import NetBoxModel
from netbox.models.features import ContactsMixin
from virtualization.models import VirtualMachine
from dcim.models import Device
from ipam.models import Service as IpamService
from tenancy.models import Tenant, TenantGroup

# module imports
from . import choices

SERVICE_PORT_MIN = 1
SERVICE_PORT_MAX = 65535
SHAPE_NAMES = [
    "Round Edges",
    "Stadium Shaped",
    "Subroutine Shape",
    "Cylindrical Shape",
    "Circle Shape",
    "asymmetric shape",
    "rhombus",
    "Hexagon",
    "Parallelogram",
    "Trapezoid",
]

class Service(ContactsMixin, NetBoxModel):
    name = models.CharField(
        "Name",
        max_length=100
    )

    slug = models.CharField(
        verbose_name=_('Slug'),
        max_length=50,
        default=uuid.uuid4,
        unique=True,
        help_text=_('Short name for referencing other applications and services'),
        validators=(
            RegexValidator(
                regex=r'^[a-z0-9_-]+$',
                message=_("Only alphanumeric characters and underscores are allowed."),
                flags=re.IGNORECASE
            ),
            RegexValidator(
                regex=r'__',
                message=_("Double underscores are not permitted in custom field names."),
                flags=re.IGNORECASE,
                inverse_match=True
            ),
        )
    )

    status = models.CharField(
        max_length=100,
        choices=choices.ItilServiceStatusChoices
    )
    def get_status_color(self):
        return choices.ItilServiceStatusChoices.colors.get(self.status)

    type = models.CharField(
        max_length=100,
        choices=choices.ItilServiceTypeChoices
    )
    def get_type_color(self):
        return choices.ItilServiceTypeChoices.colors.get(self.type)

    clients = models.ManyToManyField(
        Tenant,
        related_name="nb_itsm_services",
        verbose_name="Clients"
    )

    client_groups = models.ManyToManyField(
        TenantGroup,
        related_name="nb_itsm_services",
        verbose_name="Client Groups"
    )

    comments = models.TextField(blank=True)

    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="nb_itsm_service_set",
    )

    @property
    def diagram(self):
        mermaid_graph_type: str = "graph TB\n"
        graph = mermaid_graph_type

        open_shape = [
            "(",
            "([",
            "[[",
            "[(",
            "((",
            ">",
            "{",
            "{{",
            "[/",
            "[\\",
        ]

        close_shape = [
            ")",
            "])",
            "]]",
            ")]",
            "))",
            "]",
            "}",
            "}}",
            "/]",
            "\\]",
        ]
        arrow_shape = ["-->", "---", "-.->", "-.-"]
        nodes = {}
        for configuration_item in self.nb_itsm_configuration_items.all():
            node = configuration_item.name.replace(" ", "_")
            graph += f"{node}\n"
            if node not in nodes:
                nodes[node] = configuration_item.get_absolute_url()
        for rel in self.nb_itsm_relationships.all():
            src_node = rel.source.name.replace(" ", "_")
            dest_node = rel.destination.name.replace(" ", "_")
            if src_node not in nodes:
                nodes[src_node] = rel.source.get_absolute_url()
            if dest_node not in nodes:
                nodes[dest_node] = rel.destination.get_absolute_url()

            graph += (
                f"    {src_node}{open_shape[rel.source_shape -1]}"
                + f"{rel.source.name}{close_shape[rel.source_shape -1]}"
                + f" {arrow_shape[rel.connector_shape -1]} "
            )
            if rel.link_text != "":
                graph += f"| {rel.link_text} |"
            graph += (
                f"{dest_node}{open_shape[rel.destination_shape -1]}"
                + f"{rel.destination.name}{close_shape[rel.destination_shape -1]}\n"
            )
        for node in nodes:
            graph += f'click {node} "{nodes[node]}"\n'

        if graph is mermaid_graph_type:
            graph += "empty"

        return graph

    def __str__(self) -> str:
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("plugins:nb_itsm:service", kwargs={"pk": self.pk})


class Application(NetBoxModel):
    name = models.CharField("Name", max_length=100)
    version = models.CharField("Version", max_length=100)
    devices = models.ManyToManyField(
        Device,
        related_name="nb_itsm_uses_apps",
        verbose_name="Devices",
        blank=True,
    )
    vm = models.ManyToManyField(
        VirtualMachine,
        related_name="nb_itsm_uses_apps",
        verbose_name="Virtual Machines",
        blank=True,
    )
    ipam_services = models.ManyToManyField(
        IpamService,
        related_name="nb_itsm_uses_apps",
        verbose_name="IPAM Services",
        blank=True,
    )
    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="nb_itsm_application_set",
    )

    def get_absolute_url(self):
        return reverse(
            "plugins:nb_itsm:application",
            kwargs={
                "pk": self.pk,
            }
        )

    def __str__(self) -> str:
        return f"{self.name} - {self.version}"


class ConfigurationItem(NetBoxModel):
    service = models.ForeignKey(
        to=Service, on_delete=models.CASCADE, related_name="nb_itsm_configuration_items"
    )

    assigned_object_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=choices.OBJECT_ASSIGNMENT_MODELS,
        on_delete=models.CASCADE,
        related_name="nb_itsm_object_models",
        blank=True,
        null=True,
    )
    assigned_object_id = models.PositiveIntegerField(blank=True, null=True)
    assigned_object = GenericForeignKey(
        ct_field="assigned_object_type",
        fk_field="assigned_object_id",
    )

    @property
    def obj_type(self):
        return self.assigned_object_type.name

    @property
    def name(self):
        if self.assigned_object is not None:
            return self.assigned_object.name
        else:
            return ""

    def __str__(self):
        return str(self.assigned_object)

    def get_absolute_url(self):
        url = reverse("plugins:nb_itsm:service", kwargs={"pk": self.service.pk})
        try:
            url = self.assigned_object.get_absolute_url()
        except Exception as e:
            pass
        return url

    def validate_unique(self, exclude=None):
        configuration_items = self.service.nb_itsm_configuration_items.filter(
            assigned_object_type=self.assigned_object_type
        )
        candidate_obj = self.assigned_object
        for obj in configuration_items:
            if candidate_obj == obj.assigned_object:
                raise ValidationError(
                    (f"{self.assigned_object} already in {self.service}")
                )

        super().validate_unique(exclude=exclude)

    class Meta:
        unique_together = [
            ["service", "assigned_object_type", "assigned_object_id"],
        ]


class Relation(NetBoxModel):
    service = models.ForeignKey(
        verbose_name="Service",
        to=Service,
        on_delete=models.CASCADE,
        related_name="nb_itsm_relationships",
    )
    source = models.ForeignKey(
        verbose_name="Source", to=ConfigurationItem, on_delete=models.CASCADE, related_name="nb_itsm_source"
    )
    source_shape = models.IntegerField("Source Shape", choices=choices.ShapeChoices)
    destination = models.ForeignKey(
        verbose_name="Destination", to=ConfigurationItem, on_delete=models.CASCADE, related_name="nb_itsm_destination"
    )
    destination_shape = models.IntegerField(
        "Destination Shape", choices=choices.ShapeChoices
    )
    connector_shape = models.IntegerField(
        "Connector Shape", choices=choices.ConnectorChoices
    )

    link_text = models.CharField("Link Text", max_length=100)

    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="nb_itsm_relation_set",
    )


    @property
    def source_shape_name(self):
        return SHAPE_NAMES[self.source_shape - 1]

    @property
    def destiny_shape_name(self):
        return SHAPE_NAMES[self.destination_shape - 1]

    @property
    def connector(self):
        arrow_shape = ["-->", "---", "-.->", "-.-"]
        return f"{arrow_shape[self.connector_shape -1]}"

    def get_absolute_url(self):
        return reverse("plugins:nb_itsm:relation", kwargs={"pk": self.pk})

    @property
    def diagram(self):
        graph = "graph TB\n"
        open_shape = [
            "(",
            "([",
            "[[",
            "[(",
            "((",
            ">",
            "{",
            "{{",
            "[/",
            "[\\",
        ]

        close_shape = [
            ")",
            "])",
            "]]",
            ")]",
            "))",
            "]",
            "}",
            "}}",
            "/]",
            "\\]",
        ]
        arrow_shape = ["-->", "---", "-.->", "-.-"]
        nodes = {}
        relations = [ self ]
        for rel in relations:
            src_node = rel.source.name.replace(" ", "_")
            dest_node = rel.destination.name.replace(" ", "_")
            if src_node not in nodes:
                nodes[src_node] = rel.source.get_absolute_url()
            if dest_node not in nodes:
                nodes[dest_node] = rel.destination.get_absolute_url()

            graph += (
                f"    {src_node}{open_shape[rel.source_shape -1]}"
                + f"{rel.source.name}{close_shape[rel.source_shape -1]}"
                + f" {arrow_shape[rel.connector_shape -1]} "
            )
            if rel.link_text != "":
                graph += f"| {rel.link_text} |"
            graph += (
                f"{dest_node}{open_shape[rel.destination_shape -1]}"
                + f"{rel.destination.name}{close_shape[rel.destination_shape -1]}\n"
            )
        for node in nodes:
            graph += f'click {node} "{nodes[node]}"\n'
        return graph

    def __str__(self) -> str:
        arrow_shape = ["-->", "---", "-.->", "-.-"]
        src_node = self.source.name.replace(" ", "_")
        dest_node = self.destination.name.replace(" ", "_")

        return f"{src_node} {arrow_shape[self.connector_shape -1]} {dest_node}"


class PenTest(NetBoxModel):
    service = models.ForeignKey(
        to=Service, on_delete=models.CASCADE, related_name="nb_itsm_pentest_reports"
    )
    comments = models.TextField(blank=True)
    status = models.IntegerField(
        "State",
        choices=choices.PenTestChoices,
        help_text="Approved or Reproved",
    )
    date = models.DateField("Execution Date")
    ticket = models.CharField("Ticket", max_length=100)
    report_link = models.CharField("Report link", max_length=100)

    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="nb_itsm_pentest_set",
    )
