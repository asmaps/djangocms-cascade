# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from .plugin_base import FoundationPluginBase


class ButtonWrapperPlugin(FoundationPluginBase):
    name = _("Button wrapper")
    require_parent = False
    render_template = 'cms/plugins/naked.html'
    generic_child_classes = ('LinkPlugin',)
    tag_type = None
    default_css_class = 'button'

plugin_pool.register_plugin(ButtonWrapperPlugin)
