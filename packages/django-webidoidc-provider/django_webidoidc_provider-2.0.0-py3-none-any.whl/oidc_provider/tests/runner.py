import sys

import django
from . import settings as settings_default
from django.conf import settings

settings.configure(default_settings=settings_default)

django.setup()
from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests([
    'oidc_provider.tests.cases.test_authorize_endpoint',
    'oidc_provider.tests.cases.test_claims',
    'oidc_provider.tests.cases.test_commands',
    'oidc_provider.tests.cases.test_end_session_endpoint',
    'oidc_provider.tests.cases.test_introspection_endpoint',
    'oidc_provider.tests.cases.test_middleware',
    'oidc_provider.tests.cases.test_provider_info_endpoint',
    'oidc_provider.tests.cases.test_register_endpoint',
    'oidc_provider.tests.cases.test_settings',
    'oidc_provider.tests.cases.test_token_endpoint',
    'oidc_provider.tests.cases.test_userinfo_endpoint',
    'oidc_provider.tests.cases.test_utils',
])
if failures:
    sys.exit(failures)

