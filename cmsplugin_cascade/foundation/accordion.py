# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from django.forms import widgets
from cmsplugin_cascade.plugin_base import PartialFormField
from .plugin_base import FoundationPluginBase


class AccordionWrapperPlugin(FoundationPluginBase):
    name = _("Accordion wrapper")
    require_parent = False
    render_template = 'cms/foundation/accordion_wrapper.html'
    generic_child_classes = ('AccordionElementPlugin',)
    partial_fields = [
        PartialFormField('name',
            widgets.TextInput(),
            label="Name for this wrapper",
            help_text="This will be displayed in structure overview to easier find this element. Not displayed on page.",
        ),
    ]

    @classmethod
    def get_identifier(cls, obj):
        if obj.context is not None:
            return obj.context.get('name')
        else:
            return u''



class AccordionElementPlugin(FoundationPluginBase):
    name = _("Accordion element")
    require_parent = True
    parent_classes = ('AccordionWrapperPlugin',)
    partial_fields = [
        PartialFormField('heading',
            widgets.TextInput(),
            label="Heading for this element",
        ),
    ]
    allow_children = True
    render_template = 'cms/foundation/accordion_element.html'

    @classmethod
    def get_identifier(cls, obj):
        if obj.context is not None:
            return obj.context.get('heading')
        else:
            return u''

plugin_pool.register_plugin(AccordionWrapperPlugin)
plugin_pool.register_plugin(AccordionElementPlugin)
