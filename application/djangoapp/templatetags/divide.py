from django import template

register = template.Library()

@register.filter
def div(a, b):
    return a/b

@register.filter
def modulo(a,b):
    return a %b

@register.filter
def to_int(a):
    return a.to_int()
