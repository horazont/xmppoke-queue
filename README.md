XMPPoke Queue Manager
=====================

What is XMPPoke?
----------------

[XMPPoke](https://bitbucket.org/xnyhps/xmppoke) is a tool which is used to probe
XMPP servers for their security and connectivity settings.
Think [testssl.sh](https://testssl.sh/), but for XMPP and with different features.

It focuses on cipher suites, certificate validity, authentication options, SRV
record setup and DANE.

Configuration
------------

See the example config for hints.

Database
--------

XMPPoke uses a database PostgreSQL to store the results (the [schema for the database can be found in the XMPPoke repository](https://bitbucket.org/xnyhps/xmppoke/src/)).

It connects as user ``xmppoke`` to a database called ``xmppoke``. The host, port and password for the database connection can be specified in the configuration file.
