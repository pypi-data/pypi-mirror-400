from . import models
from . import filtersets
from . import forms
from . import tables

from netbox.views import generic
from tenancy.tables import TenantTable, TenantGroupTable
from virtualization.models import VirtualMachine
from dcim.models import Device
from dcim.tables import DeviceTable
from virtualization.tables import VirtualMachineTable
from ipam.tables import ServiceTable as IpamServiceTable
from utilities.views import ViewTab, register_model_view
from netbox.views.generic import ObjectChildrenView
from ipam.models import Service as IpamService

#
# Service Views ###############################################################
#

class ServiceListView(generic.ObjectListView):
    queryset = models.Service.objects.all()
    table = tables.ItilServiceTable
    filterset = filtersets.ItilServiceFilterSet
    filterset_form = forms.ServiceFilterForm

class ServiceView(generic.ObjectView):
    queryset = models.Service.objects.all()

    def get_extra_context(self, request, instance):
        tenants_table = TenantTable(instance.clients.all())
        tenant_groups_table = TenantGroupTable(instance.client_groups.all())

        vuln_table = tables.VulnTable(instance.nb_itsm_pentest_reports.all())

        data = {
                "tenant_table" : tenants_table,
                "tenant_groups_table" : tenant_groups_table,
                "vuln_table" : vuln_table,
            }
        return data

@register_model_view(models.Service, 'contacts')
class ItilServiceContactsView(ObjectChildrenView):
    queryset = models.Service.objects.all()

@register_model_view(models.Service, name='configuration_items')
class ServiceConfigurationItemView(generic.ObjectChildrenView):
    queryset = models.Service.objects.all()
    table = tables.ConfigurationItemsTable
    template_name = "nb_itsm/service-configuration-item-view.html"
    tab = ViewTab(label='Configuration Items', badge=lambda obj: obj.nb_itsm_configuration_items.all().count(), hide_if_empty=True)

    def get_children(self, request, parent):
            children = parent.nb_itsm_configuration_items.all()
            return children


@register_model_view(models.Service, name='relationships')
class ServiceRelationView(generic.ObjectChildrenView):
    queryset = models.Service.objects.all()
    child_model = models.Relation
    table = tables.RelationTable
    template_name = "nb_itsm/service_Relation_view.html"
    tab = ViewTab(
        label='CI Relationships',
        badge=lambda obj: obj.nb_itsm_relationships.all().count(),
        hide_if_empty=True
    )

    def get_children(self, request, parent):
            children = parent.nb_itsm_relationships.all()
            return children

    def get_extra_context(self, request, instance):
        relations = tables.RelationTable(instance.nb_itsm_relationships.all())
        data = {
                "table" : relations,
            }
        return data

@register_model_view(models.Service, name='diagram')
class ServiceDiagramView(generic.ObjectChildrenView):
    queryset = models.Service.objects.all()
    child_model = models.Service
    table = tables.ItilServiceTable
    template_name = "nb_itsm/service_diagram_view.html"
    tab = ViewTab(label='Diagram')

    def get_children(self, request, parent):
            children = parent.nb_itsm_relationships.all()
            return children

class ServiceEditView(generic.ObjectEditView):
    queryset = models.Service.objects.all()
    form  = forms.ItilServiceForm

class ServiceImportView(generic.BulkImportView):
    queryset = models.Service.objects.all()
    model_form = forms.ItilServiceImportForm
    table = tables.ItilServiceTable

class ServiceBulkEditView(generic.BulkEditView):
    queryset = models.Service.objects.all()
    filterset = filtersets.ItilServiceFilterSet
    table = tables.ItilServiceTable
    form = forms.ServiceBulkEditForm

class ServiceBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Service.objects.all()
    table = tables.ItilServiceTable

class ServiceDeleteView(generic.ObjectDeleteView):
    queryset = models.Service.objects.all()


class ICCreateView(generic.ObjectEditView):
    queryset = models.ConfigurationItem.objects.all()
    form = forms.ConfigurationItemForm

    def alter_object(self, obj, request, url_args, url_kwargs):
        if 'device' in request.POST:
            try:
                obj.assigned_object =  Device.objects.get(pk=request.POST['device'])
            except (ValueError, Device.DoesNotExist):
                pass

        if 'virtual_machine' in request.POST:
            try:
                obj.assigned_object =  VirtualMachine.objects.get(pk=request.POST['virtual_machine'])
            except (ValueError, Device.DoesNotExist):
                pass
        if 'application' in request.POST:
            try:
                obj.assigned_object =  models.Application.objects.get(pk=request.POST['application'])
            except (ValueError, Device.DoesNotExist):
                pass

        return obj

#
# Pentest Extra Views ###########################################################
#

class PenTestEditView(generic.ObjectEditView):
    queryset = models.PenTest.objects.all()
    form = forms.PenTestForm

class PenTestDeleteView(generic.ObjectDeleteView):
    queryset = models.PenTest.objects.all()

class RelationDeleteView(generic.ObjectDeleteView):
    queryset = models.Relation.objects.all()

class ICDeleteView(generic.ObjectDeleteView):
    queryset = models.ConfigurationItem.objects.all()

#
# Application Views ###########################################################
#

class ApplicationListView(generic.ObjectListView):
    queryset = models.Application.objects.all()
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet
    filterset_form = forms.ApplicationFilterForm

class ApplicationView(generic.ObjectView):
    queryset = models.Application.objects.all()

@register_model_view(models.Application, name='devices')
class ApplicationDevicesView(generic.ObjectChildrenView):
    queryset = models.Application.objects.all()
    child_model = Device
    table = DeviceTable
    template_name = "nb_itsm/application_objs.html"
    tab = ViewTab(label='Devices', badge=lambda obj: obj.devices.all().count(), hide_if_empty=True)

    def get_children(self, request, parent):
            children = parent.devices.all()
            return children

    def get_extra_context(self, request, instance):
        device_table = DeviceTable(instance.devices.all())
        device_table.exclude = ('actions',)
        data = {
                "table" : device_table,
            }
        return data

@register_model_view(models.Application, name='vms')
class ApplicationVMsView(generic.ObjectChildrenView):
    queryset = models.Application.objects.all()
    child_model = VirtualMachine
    table = VirtualMachineTable
    template_name = "nb_itsm/application_objs.html"
    tab = ViewTab(label='Virtual Machines', badge=lambda obj: obj.vm.all().count(), hide_if_empty=True)

    def get_children(self, request, parent):
            children = parent.vm.all()
            return children

    def get_extra_context(self, request, instance):
        vm_table = VirtualMachineTable(instance.vm.all())
        vm_table.exclude = ('actions',)
        data = {
                "table" : vm_table,
            }
        return data

@register_model_view(models.Application, name='ipam_services')
class ApplicationIpamServicesView(generic.ObjectChildrenView):

    queryset = models.Application.objects.all()
    child_model = IpamService
    table = IpamServiceTable
    template_name = "nb_itsm/application_objs.html"
    tab = ViewTab(label='IPAM Services', badge=lambda obj: obj.ipam_services.all().count(), hide_if_empty=True)

    def get_children(self, request, parent):
            children = parent.ipam_services.all()
            return children
    def get_extra_context(self, request, instance):
        ipam_service_table = IpamServiceTable(instance.ipam_services.all())
        ipam_service_table.exclude = ('actions',)
        data = {
                "table" : ipam_service_table,
            }
        return data

class ApplicationEditView(generic.ObjectEditView):
    queryset = models.Application.objects.all()
    form = forms.ApplicationForm

class ApplicationImportView(generic.BulkImportView):
    queryset = models.Application.objects.all()
    model_form = forms.ApplicationImportForm
    table = tables.ApplicationTable

class ApplicationBulkEditView(generic.BulkEditView):
    queryset = models.Application.objects.all()
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable
    form = forms.ApplicationBulkEditForm

class ApplicationBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Application.objects.all()
    table = tables.ApplicationTable

class ApplicationDeleteView(generic.ObjectDeleteView):
    queryset = models.Application.objects.all()

#
# Relation Views ##############################################################
#

class RelationListView(generic.ObjectListView):
    queryset = models.Relation.objects.all()
    table = tables.RelationTable
    filterset = filtersets.RelationFilter
    filterset_form = forms.RelationFilterForm

class RelationView(generic.ObjectView):
    queryset = models.Relation.objects.all()

class RelationEditView(generic.ObjectEditView):
    queryset = models.Relation.objects.all()
    form = forms.RelationForm
