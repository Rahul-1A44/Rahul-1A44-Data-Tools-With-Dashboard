# C:\panel\Dashboard\main_app\templatetags\custom_filters.py

from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another substring.
    Usage: {{ value|replace:"old_string|new_string" }}  <-- Note the pipe | as separator
    """
    if isinstance(value, str) and isinstance(arg, str):
        # Split by pipe '|' and ensure we only split on the first occurrence
        parts = arg.split('|', 1)
        if len(parts) == 2:
            old_string, new_string = parts
            return value.replace(old_string, new_string)
        else:
            # If the argument format is incorrect (e.g., missing pipe),
            # return the original value to prevent a template error.
            return value
    return value