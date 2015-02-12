from django import template
from django.template import Context
from django.template.loader import get_template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def as_material(field, col='s6'):

    return get_template("materialize/field.html").render(
        Context({
            'field': field,
            'col': col,
        })
    )


@register.filter
def html_attrs(attrs):
    pairs = []
    for name, value in attrs.items():
        pairs.append(u'%s="%s"' % (escape(name), escape(value)))
    return mark_safe(u' '.join(pairs))
