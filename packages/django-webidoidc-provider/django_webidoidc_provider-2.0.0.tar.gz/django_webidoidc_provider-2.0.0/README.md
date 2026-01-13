# Django OpenID Connect Provider

[![Python Versions](https://img.shields.io/pypi/pyversions/django-oidc-provider.svg)](https://pypi.python.org/pypi/django-oidc-provider)
[![PyPI Versions](https://img.shields.io/pypi/v/django-oidc-provider.svg)](https://pypi.python.org/pypi/django-oidc-provider)
[![Documentation Status](https://readthedocs.org/projects/django-oidc-provider/badge/?version=master)](http://django-oidc-provider.readthedocs.io/)
[![Travis](https://travis-ci.org/juanifioren/django-oidc-provider.svg?branch=master)](https://travis-ci.org/juanifioren/django-oidc-provider)

## About OpenID Connect

OpenID Connect is a simple identity layer on top of the OAuth 2.0 protocol, which allows computing clients to verify the identity of an end-user based on the authentication performed by an authorization server, as well as to obtain basic profile information about the end-user in an interoperable and REST-like manner. Like [Google](https://developers.google.com/identity/protocols/OpenIDConnect) for example.

## About Solid OpenID Connect

The primary divergence of django-webid-oidc-provider from its parent package [django-oidc-provider](https://github.com/juanifioren/django-oidc-provider/blob/master/docs/index.rst) is the support of Solid OIDC. Solid OpenID Connect is a draft specification which extends OIDC for use with decentralised applications, in particular applications using [Solid](https://solidproject.org).

* See the specification here: [https://solid.github.io/authentication-panel/solid-oidc/](https://solid.github.io/authentication-panel/solid-oidc/)
* See the Primer which accompanies the specification here: [https://solid.github.io/authentication-panel/solid-oidc-primer/](https://solid.github.io/authentication-panel/solid-oidc-primer/)

### Additional settings

We introduced a new server settings named `OIDC_DPOP_LEEWAY` to prevent issue with server clock desynchronization, with a default value of 1.

## About the package

`django-oidc-provider` can help you providing out of the box all the endpoints, data and logic needed to add OpenID Connect (and OAuth2) capabilities to your Django projects.

Support for Python 3.11 and Django 4.2, improves performance.

[Read documentation for more info.](http://django-oidc-provider.readthedocs.org/)

[Do you want to contribute? Please read this.](http://django-oidc-provider.readthedocs.io/en/latest/sections/contribute.html)
