from django import template

register = template.Library()

@register.filter
def get_item(obj, key):
    # If it's a form, access fields like a dictionary
    try:
        return obj[key]
    except (KeyError, TypeError, AttributeError):
        return None