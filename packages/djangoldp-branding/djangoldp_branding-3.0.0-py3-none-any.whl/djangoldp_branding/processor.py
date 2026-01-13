import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

DJANGOLDP_JSON_BRANDING = getattr(
    settings, "DJANGOLDP_BRANDING_JSON", 'config.json')

ORBIT_JSON = {}

if DJANGOLDP_JSON_BRANDING:
    try:
        with open(DJANGOLDP_JSON_BRANDING, 'r') as f:
            ORBIT_JSON = json.load(f)
    except:
        logger.info('Error while loading config.json from the root of your server')

ORBIT_JSON['debug_flag'] = settings.DEBUG
ORBIT_JSON['default_client'] = settings.INSTANCE_DEFAULT_CLIENT
ORBIT_JSON['base_url'] = settings.BASE_URL
ORBIT_JSON['site_url'] = settings.SITE_URL
ORBIT_JSON['client_settings'] = ORBIT_JSON['client']


def branding_context(request):
    return ORBIT_JSON
