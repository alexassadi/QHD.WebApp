from django import template
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='attr')
def attr(field, args):
    attrs = {}
    for arg in args.split(','):
        key, val = arg.split(':')
        attrs[key.strip()] = val.strip()
    return field.as_widget(attrs=attrs)