#!/usr/bin/env python
"""
Test runner for djangoldp_edc package.
"""
import sys
import os

# Add the package directory to path
package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, package_dir)

import django
from django.conf import settings, global_settings

if not settings.configured:
    settings.configure(
        default_settings=global_settings,
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'guardian',
            'djangoldp',
            'djangoldp_edc',
        ),
        ROOT_URLCONF='',
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'djangoldp_edc.middleware.EdcNegotiationMiddleware',
        ],
        AUTHENTICATION_BACKENDS=(
            'django.contrib.auth.backends.ModelBackend',
            'guardian.backends.ObjectPermissionBackend',
        ),
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }],
        # DjangoLDP Settings
        DJANGOLDP_PACKAGES=[],
        LDP_RDF_CONTEXT='https://cdn.happy-dev.fr/owl/hdcontext.jsonld',
        ENABLE_SWAGGER_DOCUMENTATION=False,
        SEND_BACKLINKS=False,
        SERIALIZER_CACHE=False,
        # EDC Settings
        SITE_URL='http://localhost:8000',
        BASE_URL='http://localhost:8000',
        EDC_URL='http://localhost:8082',
        EDC_PARTICIPANT_ID='test-participant',
        EDC_API_KEY='test-api-key',
        EDC_AGREEMENT_VALIDATION_ENABLED=True,
        EDC_AUTO_NEGOTIATION_ENABLED=True,
        EDC_POLICY_DISCOVERY_ENABLED=True,
        EDC_ASSET_ID_STRATEGY='slugify',
        EDC_POLICY_OPENNESS_THRESHOLD=0,
        # Required for tests
        SECRET_KEY='test-secret-key-for-testing-only',
        USE_TZ=True,
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )

django.setup()

from django.test.runner import DiscoverRunner

if __name__ == '__main__':
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests([
        'djangoldp_edc.tests.test_permissions',
        'djangoldp_edc.tests.test_permissions_v3',
        'djangoldp_edc.tests.test_utils',
        'djangoldp_edc.tests.test_middleware',
    ])

    if failures:
        sys.exit(failures)
