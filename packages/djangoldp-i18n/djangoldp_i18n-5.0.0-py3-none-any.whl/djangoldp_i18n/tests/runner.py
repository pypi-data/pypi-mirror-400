import sys

import django
from django.conf import settings as django_settings
from djangoldp.conf.ldpsettings import LDPSettings

# create a test configuration
config = {
    # add the packages to the reference list
    'ldppackages': ['djangoldp.tests','djangoldp_i18n','djangoldp_i18n.tests'],

    # required values for server
    'server': {
        'AUTH_USER_MODEL': 'tests.User',
        'STORE_ACTIVITIES': 'VERBOSE',
        'REST_FRAMEWORK': {
            'DEFAULT_PAGINATION_CLASS': 'djangoldp.pagination.LDPPagination',
            'PAGE_SIZE': 5
        },
        # map the config of the core settings (avoid asserts to fail)
        'SITE_URL': 'http://happy-dev.fr',
        'BASE_URL': 'http://happy-dev.fr',
        'MODELTRANSLATION_DEFAULT_LANGUAGE': 'en',
        'SEND_BACKLINKS': False,
        'PERMISSIONS_CACHE': False,
        'ANONYMOUS_USER_NAME': None,
        'SERIALIZER_CACHE': False,
        'USE_I18N': True,
        'LANGUAGES': [
            ('en', 'English'),
            ('en-gb', 'English GB'),
            ('en-us', 'English US'),
            ('fr', 'Français'),
        ],
        'MODELTRANSLATION_FALLBACK_LANGUAGES': {
            'default': (),
            'en-gb': ('en','en-us',),
            'en-us': ('en', 'en-gb',),
            'en': ('en-gb', 'en-us')
        }
    }
}

ldpsettings = LDPSettings(config)
django_settings.configure(ldpsettings)

# workaround modeltranslation position
try:
    django_settings.INSTALLED_APPS.remove('modeltranslation')
    django_settings.INSTALLED_APPS.insert(0, 'modeltranslation')
except ValueError:
    pass

django.setup()

from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests([
    'djangoldp.tests.tests_ldp_model',
    'djangoldp.tests.tests_model_serializer',
    'djangoldp.tests.tests_ldp_viewset',
    'djangoldp.tests.tests_post',
    'djangoldp.tests.tests_user_permissions',
    'djangoldp.tests.tests_guardian',
    'djangoldp.tests.tests_anonymous_permissions',
    'djangoldp.tests.tests_update',
    'djangoldp.tests.tests_auto_author',
    'djangoldp.tests.tests_get',
    'djangoldp.tests.tests_delete',
    'djangoldp.tests.tests_sources',
    'djangoldp.tests.tests_pagination',
    'djangoldp.tests.tests_inbox',
    'djangoldp.tests.tests_backlinks_service',
    'djangoldp.tests.tests_cache',
    'djangoldp_i18n.tests.tests_get',
    'djangoldp_i18n.tests.tests_post',
    'djangoldp_i18n.tests.tests_cache'
])
if failures:
    sys.exit(failures)
