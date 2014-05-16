from django import template

register = template.Library()


@register.filter
def can_votar(ocorrencia, user):
    return ocorrencia.can_votar(user)


@register.filter
def can_vetar(ocorrencia, user):
    return ocorrencia.can_vetar(user)
