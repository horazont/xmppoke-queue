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

The configuration happens via environment variables:

* ``XMPPOKE_QUEUE_PORT``: the port the queue manager binds to
* ``XMPPOKE_QUEUE_LISTEN``: the address the queue manager binds to
* ``XMPPOKE_DB_HOST``: passed as ``--db-host`` to ``xmppoke``, the host of the PostgreSQL database.
* ``XMPPOKE_DB_PORT``: passed as ``--db-port`` to ``xmppoke``, the port of the PostgreSQL database.
* ``XMPPOKE_DB_PASSWORD``: passed as ``--db-password`` to ``xmppoke``, the password of the PostgreSQL database.
* ``XMPPOKE_VERSION_JID``: passed as ``--version-jid`` to ``xmppoke``, the JID of the account used to query the version of tested servers (optional).
* ``XMPPOKE_VERSION_PASSWORD``: passed as ``--version-password`` to ``xmppoke``, the password of the account used to query the version of tested servers (optional).

Database
--------

XMPPoke uses a database PostgreSQL to store the results (the [schema for the database can be found in the XMPPoke repository](https://bitbucket.org/xnyhps/xmppoke/src/)).

It connects as user ``xmppoke`` to a database called ``xmppoke``. The host, port and password for the database connection can be specified via environment variables.
