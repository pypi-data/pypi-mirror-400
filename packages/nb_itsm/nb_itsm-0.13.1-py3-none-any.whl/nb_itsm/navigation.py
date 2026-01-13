from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


from django.conf import settings

plugin_settings = settings.PLUGINS_CONFIG["nb_itsm"]

menu_buttons = (
    PluginMenuItem(
        permissions=["nb_itsm.view_service"],
        link="plugins:nb_itsm:service_list",
        link_text="Service Catalog",
    ),
    PluginMenuItem(
        permissions=["nb_itsm.view_application"],
        link="plugins:nb_itsm:application_list",
        link_text="Applications",
    ),
)

if plugin_settings.get("top_level_menu"):
    menu = PluginMenu(
        label="IT Service management",
        groups=(("ITSM", menu_buttons),),
        icon_class="mdi mdi-cog-outline",
    )
else:
    menu_items = menu_buttons