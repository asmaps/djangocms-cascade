# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import PartialFormField
from cmsplugin_cascade.widgets import MultipleInlineStylesWidget
from .plugin_base import FoundationPluginBase


class HorizontalRulePlugin(FoundationPluginBase):
    name = _("Horizontal Rule")
    allow_children = False
    require_parent = False
    tag_type = 'hr'
    render_template = 'cms/plugins/single.html'
    partial_fields = (
        PartialFormField('inline_styles',
            MultipleInlineStylesWidget(['margin-top', 'margin-bottom']),
            label=_('Inline Styles'),
            help_text=_('Margins for this horizontal rule.')
        ),
    )

plugin_pool.register_plugin(HorizontalRulePlugin)
