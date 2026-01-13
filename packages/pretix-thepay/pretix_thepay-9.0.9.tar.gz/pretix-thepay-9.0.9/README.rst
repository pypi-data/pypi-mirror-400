pretix-thepay
=============

The Pay payment provider plugin for Pretix. It creates payments via The Pay API,
redirects customers to The Pay, and confirms status by querying The Pay from the
return and notification callbacks.

Features
--------

- The Pay REST API integration (payment creation, status lookup)
- Redirect-based checkout flow
- Server-to-server notifications
- ISO 4217 currency support with correct minor units
- Demo mode via Test Mode setting
- Multi-language gateway support (Czech, Slovak, English)

Requirements
------------

- Pretix >= 2.7.0
- Python >= 3.8
- requests >= 2.25.0

Installation
------------

Install from PyPI::

    pip install pretix-thepay

Or install from source::

    pip install -e /path/to/pretix-thepay

Enable the plugin in ``pretix.cfg``::

    [pretix]
    plugins = pretix_thepay

Restart Pretix after enabling the plugin.

Configuration
-------------

In the Pretix control panel, enable The Pay and configure:

- **Merchant ID**: Your The Pay merchant ID
- **Project ID**: Your The Pay project ID
- **API Password**: Your The Pay API password
- **Language**: Default language for the payment gateway
- **Test Mode**: Enable to use the demo environment

Behavior
--------

1. The customer selects The Pay.
2. Pretix creates a payment at The Pay and redirects the customer.
3. The customer completes payment on The Pay.
4. Pretix confirms the payment by querying The Pay from the return URL and from notifications.

Notes
-----

- Test Mode switches the API base URL to the demo environment.
- The Pay requires a customer name plus email or phone; Pretix order data is used.

Troubleshooting
---------------

Payment not created
^^^^^^^^^^^^^^^^^^^

- Verify Merchant ID, Project ID, and API Password
- Check Pretix logs for The Pay API response details
- Ensure the customer has a name and email or phone

Notification issues
^^^^^^^^^^^^^^^^^^^

- Make sure Pretix is reachable from The Pay (public URL)
- Confirm the notification URL is accessible and responds quickly

Docker
------

For Pretix in Docker::

    FROM pretix/standalone:stable
    USER root
    RUN pip3 install pretix-thepay
    USER pretixuser
    RUN cd /pretix/src && make production

License
-------

Apache Software License 2.0

References
----------

- `Pretix Plugin Development Guide <https://docs.pretix.eu/dev/development/api/index.html>`_
- `The Pay API Documentation <https://docs.thepay.eu/>`_
- `The Pay OpenAPI Spec <https://gate.thepay.cz/openapi.yaml>`_
