#!/usr/bin/env python
# pubsub/net.py

"""
A networking implementation of PubSub using Twisted.

=============
PubSub Server
=============

A PubSub server listens for subscription requests and publish commands, and,
when published to, sends data to subscribers. All incoming and outgoing
requests are encoded in JSON.

A Subscribe request looks like this::
    {
        "command": "subscribe",
        "topic": "hello"
    }

A Publish request looks like this::
    {
        "command": "publish",
        "topic": "hello",
        "data": {
            "world": "WORLD"
        }
    }

When the server receive's a Publish request, it will send the ``data`` object
to all subscribers of ``topic``.
"""

import argparse
import json
import logging

from collections import defaultdict

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.protocol import Protocol, Factory, ClientFactory


class PubSubProtocol(Protocol):

    def __init__(self, topics):
        self.topics = topics
        self.subscribed_topic = None

    def connectionLost(self, reason):
        if self.subscribed_topic:
            self.topics[self.subscribed_topic].remove(self)

    def dataReceived(self, data):
        try:
            request = json.loads(data)
        except ValueError:
            # FIXME It would probably be courteous of us to let the sender
            # know that something went wrong.
            logging.debug("ValueError on decoding incoming data. Data: '%s'"
                          % data, exc_info=True)
            self.transport.loseConnection()
            return

        if request['command'] == 'subscribe':
            self.handle_subscribe(request['topic'])
        elif request['command'] == 'publish':
            self.handle_publish(request['topic'], request['data'])

    def handle_subscribe(self, topic):
        self.topics[topic].add(self)
        self.subscribed_topic = topic

    def handle_publish(self, topic, data):
        request = json.dumps(data)

        for protocol in self.topics[topic]:
            protocol.transport.write(request)


class PubSubFactory(Factory):

    def __init__(self):
        self.topics = defaultdict(set)

    def buildProtocol(self, addr):
        return PubSubProtocol(self.topics)


class PublisherProtocol(Protocol):

    def __init__(self, topic, **kwargs):
        self.topic = topic
        self.kwargs = kwargs

    def connectionMade(self):
        request = json.dumps({
            'command': 'publish',
            'topic': self.topic,
            'data': self.kwargs,
        })

        self.transport.write(request)
        self.transport.loseConnection()


class SubscriberProtocol(Protocol):

    def __init__(self, topic, callback):
        self.topic = topic
        self.callback = callback

    def connectionMade(self):
        request = json.dumps({
            'command': 'subscribe',
            'topic': self.topic,
        })

        self.transport.write(request)

    def dataReceived(self, data):
        kwargs = json.loads(data)

        self.callback(**kwargs)


class PubSub(object):

    def __init__(self, host='localhost', port=3000):
        self.host = host
        self.port = port
        self.reactor = reactor

    def _make_connection(self, protocol):
        endpoint = TCP4ClientEndpoint(reactor, self.host, self.port)
        connection = connectProtocol(endpoint, protocol)

    def subscribe(self, topic, callback):
        """
        Subscribe ``callback`` callable to ``topic``.
        """
        sub = SubscriberProtocol(topic, callback)
        self._make_connection(sub)

    def publish(self, topic, **kwargs):
        """
        Publish ``**kwargs`` to ``topic``, calling all callables
        subscribed to ``topic`` with the arguments specified in ``**kwargs``.
        """
        pub = PublisherProtocol(topic, **kwargs)
        self._make_connection(pub)

    def run(self):
        """
        Convenience method to start the Twisted event loop.
        """
        self.reactor.run()


def main():
    parser = argparse.ArgumentParser(description="Run a PubSub server")
    parser.add_argument('address', type=str, nargs='?',
                        default='localhost:3000')
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    host, port = args.address.split(':')
    port = int(port)

    reactor.listenTCP(port, PubSubFactory(), interface=host)
    reactor.run()


if __name__ == '__main__':
    main()
