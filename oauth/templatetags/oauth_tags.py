from django import template
from django.urls import reverse


register = template.Library()


@register.inclusion_tag('oauth/oauth_applications.html')
def load_oauth_applications(request):
    pass