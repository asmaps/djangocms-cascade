# -*- coding: utf-8 -*-
import re
import six
import json
from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.html import escape, format_html, format_html_join
from django.utils.translation import ugettext_lazy as _, ugettext


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    def __init__(self, glossary_fields):
        unique_keys = set([field.name for field in glossary_fields])
        if len(glossary_fields) > len(unique_keys):
            raise AttributeError('List of glossary_fields may contain only unique keys')
        self.glossary_fields = glossary_fields[:]
        super(JSONMultiWidget, self).__init__((field.widget for field in glossary_fields))

    def decompress(self, values):
        if not isinstance(values, dict):
            values = json.loads(values or '{}')
        for field in self.glossary_fields:
            if isinstance(field.widget, widgets.MultiWidget):
                values[field.name] = field.widget.decompress(values.get(field.name))
            else:
                values.setdefault(field.name, field.initial)
        return values

    def value_from_datadict(self, data, files, name):
        result = {}
        for field in self.glossary_fields:
            if isinstance(field.widget, widgets.MultiWidget):
                result[field.name] = field.widget.value_from_datadict(data, files, field.name)
            elif getattr(field.widget, 'allow_multiple_selected', False):
                result[field.name] = list(map(escape, data.getlist(field.name)))
            else:
                result[field.name] = escape(data.get(field.name, ''))
        return result

    def render(self, name, values, attrs):
        values = self.decompress(values)
        field_attrs = dict(**attrs)
        render_fields = []
        for field in self.glossary_fields:
            field_attrs['id'] = attrs['id'] + '_' + field.name
            render_fields.append((
                field.name,
                six.text_type(field.label),
                field.widget.render(field.name, values.get(field.name), field_attrs),
                six.text_type(field.help_text)
            ))
        html = format_html_join('\n',
            u'<div class="glossary-widget glossary_{0}"><h1>{1}</h1><div class="glossary-box">{2}</div><small>{3}</small></div>',
            render_fields)
        return html


if DJANGO_VERSION[0] <= 1 and DJANGO_VERSION[1] <= 5:
    input_widget = widgets.TextInput
else:
    input_widget = widgets.NumberInput


class NumberInputWidget(input_widget):
    validation_pattern = re.compile('^\d+$')
    required = True
    required_message = _("In '%(label)s': This field is required.")
    invalid_message = _("In '%(label)s': Value '%(value)s' shall contain a valid number.")

    def validate(self, value):
        if not self.validation_pattern.match(value):
            raise ValidationError(self.validation_message, code='invalid', params={'value': value})


def _compile_validation_pattern(widget, units):
    """
    Assure that passed in units are valid size units.
    Return a tuple with a regular expression to be used for validating and a message if this
    validation failed.
    """
    for u in units:
        if u not in widget.POSSIBLE_UNITS:
            raise ValidationError('{0} is not a valid unit for CascadingSizeField'.format(u))
    endings = (' %s ' % ugettext("or")).join("'%s'" % u.replace('%', '%%') for u in units)
    params = {'label': '%(label)s', 'value': '%(value)s', 'field': '%(field)s', 'endings': endings}
    return re.compile(r'^(\d+)\s*({0})$'.format('|'.join(units))), widget.invalid_message % params


class CascadingSizeWidget(widgets.TextInput):
    """
    Use this field for validating Input Fields containing a value ending in ``px``, ``em`` or ``%``.
    Use it for values representing a margin, padding, width or height.
    """
    POSSIBLE_UNITS = ['px', 'em', '%']
    DEFAULT_ATTRS = {'style': 'width: 5em;'}
    required_message = _("In '%(label)s': This field is required.")
    invalid_message = _("In '%(label)s': Value '%(value)s' shall contain a valid number, ending in %(endings)s.")

    def __init__(self, allowed_units=POSSIBLE_UNITS, attrs=DEFAULT_ATTRS, required=True):
        self.validation_pattern, self.invalid_message = _compile_validation_pattern(self, allowed_units)
        self.required = required
        super(CascadingSizeWidget, self).__init__(attrs=attrs)

    def validate(self, value):
        if not value:
            if self.required:
                raise ValidationError(self.required_message, code='required', params={})
            return
        match = self.validation_pattern.match(value)
        if not (match and match.group(1).isdigit()):
            params = {'value': value}
            raise ValidationError(self.invalid_message, code='invalid', params=params)


class MultipleTextInputWidget(widgets.MultiWidget):
    """
    A widgets accepting multiple input values to be used for rendering CSS inline styles.
    Additionally this widget validates the input data and raises a ValidationError
    """
    required = False

    def __init__(self, labels, required=None, attrs=None):
        text_widgets = [widgets.TextInput({'placeholder': label}) for label in labels]
        super(MultipleTextInputWidget, self).__init__(text_widgets, attrs)
        self.labels = labels[:]
        if required is not None:
            self.required = required
        self.validation_errors = []
        # check if derived classes contain proper error messages
        if hasattr(self, 'validation_pattern') and not hasattr(self, 'invalid_message'):
            raise AttributeError("Multiple...InputWidget class is missing element: 'invalid_message'")
        if self.required and not hasattr(self, 'required_message'):
            raise AttributeError("Multiple...InputWidget class is missing element: 'required_message'")

    def __iter__(self):
        self.validation_errors = []
        for label in self.labels:
            yield label

    def decompress(self, values):
        if not isinstance(values, dict):
            values = {}
        for key in self.labels:
            values.setdefault(key, None)
        return values

    def value_from_datadict(self, data, files, name):
        values = {}
        for key in self.labels:
            values[key] = escape(data.get('{0}-{1}'.format(name, key), ''))
        return values

    def render(self, name, values, attrs):
        widgets = []
        values = values or {}
        for index, key in enumerate(self.labels):
            label = '{0}-{1}'.format(name, key)
            errors = key in self.validation_errors and 'errors' or ''
            widgets.append((self.widgets[index].render(label, values.get(key), attrs), errors))
        return format_html('<div class="clearfix">{0}</div>',
                    format_html_join('\n', '<div class="sibling-field {1}">{0}</div>', widgets))

    def validate(self, value, field_name):
        if hasattr(self, 'validation_pattern'):
            val = value.get(field_name)
            if not val:
                if self.required:
                    raise ValidationError(self.required_message, code='required', params={'field': field_name})
                return
            if val and not self.validation_pattern.match(val):
                self.validation_errors.append(field_name)
                params = {'value': val, 'field': field_name}
                raise ValidationError(self.invalid_message, code='invalid', params=params)


class MultipleCascadingSizeWidget(MultipleTextInputWidget):
    POSSIBLE_UNITS = ['px', 'em', '%']
    DEFAULT_ATTRS = {'style': 'width: 4em;'}
    required_message = _("In '%(label)s': Field '%(field)s' is required.")
    invalid_message = _("In '%(label)s': Value '%(value)s' for field '%(field)s' shall contain a valid number, ending in %(endings)s.")

    def __init__(self, labels, allowed_units=POSSIBLE_UNITS, attrs=DEFAULT_ATTRS, required=True):
        self.validation_pattern, self.invalid_message = _compile_validation_pattern(self, allowed_units)
        self.required = required
        super(MultipleCascadingSizeWidget, self).__init__(labels, attrs=attrs)
