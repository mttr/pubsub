# pubsub/local.py

"""
A local PubSub_ implementation.

.. _PubSub: https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern

Example usage::

    In [1]: from pubsub.local import PubSub

    In [2]: def subscriber(data=None, **kwargs):
    ...:     print(data)
    ...:

    In [3]: pubsub = PubSub()

    In [4]: pubsub.subscribe("Hello", subscriber)

    In [5]: pubsub.publish("Hello", data="World")
    World
"""

from collections import defaultdict


class PubSub(object):

    def __init__(self):
        self.topics = defaultdict(set)

    def subscribe(self, topic, f):
        """
        Subscribe the function/method ``f`` to ``topic``.
        """
        self.topics[topic].add(f)

    def publish(self, topic, **kwargs):
        """
        Publish ``**kwargs`` to ``topic``, calling all functions/methods
        subscribed to ``topic`` with the arguments specified in ``**kwargs``.
        """
        for f in self.topics[topic]:
            f(**kwargs)
