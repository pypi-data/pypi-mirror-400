import json
import logging

from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()
logger = logging.getLogger(__name__)

DJANGOLDP_JSON_BRANDING = getattr(
    settings, "DJANGOLDP_BRANDING_JSON", 'config.json')

from djangoldp_branding.processor import ORBIT_JSON


def validate_path(path):
    current = ORBIT_JSON
    path = path.split(".")
    for part in path:
        if part not in current:
            return False
        current = current[part]
    return True


def read_path(path):
    current = ORBIT_JSON
    path = path.split(".")
    for part in path:
        current = current[part]
    return current


@register.simple_tag(name="orbit")
def render_orbit(path):
    if validate_path(path):
        return read_path(path)
    elif "client" not in ORBIT_JSON and settings.DEBUG and path == "errors":
        return format_html("<div class='segment full'><span class='text-bold text-color-primary'>ERROR</span>: Missing config.json at the root of your server</div>")
    else:
        return ''

@register.simple_tag(name="user")
def render_user(request):
    return request['user']
