# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from django.forms import widgets
from cmsplugin_cascade.plugin_base import PartialFormField
from .plugin_base import FoundationPluginBase


class MagellanArrivalPlugin(FoundationPluginBase):
    name = _("Magellan Arrival")
    require_parent = False
    render_template = 'cms/foundation/magellan_arrival.html'
    child_classes = ('MagellanArrivalElementPlugin',)

    @classmethod
    def get_identifier(cls, obj):
        return u''


class MagellanArrivalElementPlugin(FoundationPluginBase):
    name = _("Magellan Arrival Element")
    parent_classes = ('MagellanArrivalPlugin',)
    allow_children = False
    render_template = 'cms/foundation/magellan_arrival_element.html'
    partial_fields = [
        PartialFormField(
            'name',
            widgets.TextInput(),
            label="Name",
            help_text="Display name of this element",
        ),
        PartialFormField(
            'destination_name',
            widgets.TextInput(),
            label="Name",
            help_text="Name of the destination where this element will jump to.\
                Needs to be lowercase with only a-z and 0-9",
        ),
    ]

    @classmethod
    def get_identifier(cls, obj):
        if obj.context is not None:
            return obj.context.get('name')
        else:
            return u''


class MagellanDestinationPlugin(FoundationPluginBase):
    name = _("Magellan Destination")
    allow_children = False
    require_parent = False
    partial_fields = [
        PartialFormField(
            'name',
            widgets.TextInput(),
            label="Name",
            help_text="Name of this destination. Needs to be lowercase with only a-z and 0-9",
        ),
    ]
    allow_children = True
    render_template = 'cms/foundation/magellan_destination.html'

    @classmethod
    def get_identifier(cls, obj):
        if obj.context is not None:
            return obj.context.get('name')
        else:
            return u''

plugin_pool.register_plugin(MagellanArrivalPlugin)
plugin_pool.register_plugin(MagellanArrivalElementPlugin)
plugin_pool.register_plugin(MagellanDestinationPlugin)
