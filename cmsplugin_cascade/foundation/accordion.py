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

plugin_pool.register_plugin(AccordionWrapperPlugin)
plugin_pool.register_plugin(AccordionElementPlugin)
