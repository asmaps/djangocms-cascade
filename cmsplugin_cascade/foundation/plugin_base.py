# -*- coding: utf-8 -*-
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.cms_plugins import framework


class FoundationPluginBase(CascadePluginBase):
    module = 'Foundation'
    require_parent = True
    allow_children = True
