pubsub
======

A simple PubSub server implementation in Python. Built with 
`Twisted <https://twistedmatrix.com>`.


Installation
------------

In a virtualenv, run ``python setup.py install``.


Example Usage
-------------


Run the PubSub server with ``pubsubserve`` (by default, the server listens
on ``localhost:3000``).

In an interactive session (I'm using IPython)::

    In [1]: from pubsub import PubSub

    In [2]: def test(**kwargs):
       ...:     print("HELLO %s" % kwargs)
       ...:     

    In [3]: ps = PubSub()

    In [4]: ps.subscribe("hello", test)

    In [5]: ps.run()
        
While this is waiting, in another interactive session::

    In [1]: from pubsub import PubSub

    In [2]: ps = PubSub()

    In [3]: ps.publish("hello", world="WORLD", other="UNIVERSE")

    In [4]: ps.run()

In the listener session, ``HELLO {u'world': u'WORLD', u'other': u'UNIVERSE'}``
should be visible.
