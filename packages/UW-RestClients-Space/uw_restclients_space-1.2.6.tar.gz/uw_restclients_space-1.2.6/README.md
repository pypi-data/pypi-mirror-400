# uw-restclients-space
Restclient for Attestations Service

[![Build Status](https://github.com/uw-it-aca/uw-restclients-space/workflows/tests/badge.svg)](https://github.com/uw-it-aca/uw-restclients-space/actions)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/uw-restclients-space/badge.svg?branch=main)](https://coveralls.io/github/uw-it-aca/uw-restclients-space?branch=main)
[![PyPi Version](https://img.shields.io/pypi/v/uw-restclients-space.svg)](https://pypi.python.org/pypi/uw-restclients-space)
![Python versions](https://img.shields.io/badge/python-3.12-blue.svg)

Installation:

    pip install UW-RestClients-Attest

To use this client, you'll need these settings in your application or script:

    # Specifies whether requests should use live or mocked resources,
    # acceptable values are 'Live' or 'Mock' (default)
    RESTCLIENTS_SPACE_DAO_CLASS='Live'

# Paths to UWCA cert and key files
RESTCLIENTS_SPACE_CERT_FILE='/path/to/cert'
RESTCLIENTS_SPACE_KEY_FILE='/path/to/key'

Settings:
    RESTCLIENTS_SPACE_HOST=''
    RESTCLIENTS_SPACE_TIMEOUT=
    RESTCLIENTS_SPACE_POOL_SIZE=
