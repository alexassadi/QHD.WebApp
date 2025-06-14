from django import template

register = template.Library()

@register.simple_tag
def form_field(form, prefix, index):
    key = f"{prefix}{index}"
    return form[key]

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)