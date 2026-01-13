# Netbox ITSM

[Netbox](https://github.com/netbox-community/netbox) Plugin for IT Service Management.

Forked from https://github.com/renatoalmeidaoliveira/nbservice

## Compatibility

| Plugin Version | NetBox Version | Tested on |
|----------------|----------------|-----------|
| 0.13.1         | >= 4.5.0       | 4.4.5     |


## Installation

Add the following line to /opt/netbox/local_requirements.txt with
```
nb_itsm
```

Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:
```
PLUGINS = ['nb_itsm']
```

Runs /opt/netbox/upgrade.sh

```
sudo /opt/netbox/upgrade.sh
```

## Configuration

```python
PLUGINS_CONFIG = {
    "nb_itsm": {
        "top_level_menu": True # If set to True the plugin will add a top level menu item for the plugin. If set to False the plugin will add a menu item under the Plugins menu item.  Default is set to True.
    },
}
```
