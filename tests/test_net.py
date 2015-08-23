# tests/test_net.py

import json
import pytest

from mock import MagicMock
from twisted.test import proto_helpers

from pubsub.net import PubSubFactory, PublisherProtocol, SubscriberProtocol


def make_publish_request(topic, **kwargs):
    return json.dumps({
        'command': 'publish',
        'topic': topic,
        'data': kwargs,
    })


def make_subscribe_request(topic):
    return json.dumps({
        'command': 'subscribe',
        'topic': topic,
    })


class TestPubSubServer:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ps_factory = PubSubFactory()

    def test_dataReceived_subscribe(self):
        sub_proto = self.ps_factory.buildProtocol(('127.0.0.1', 0))
        tr = proto_helpers.StringTransport()
        sub_proto.makeConnection(tr)

        sub_proto.dataReceived(make_subscribe_request('test'))

        assert sub_proto in self.ps_factory.topics['test']

    def test_dataReceived_publish(self):
        # Using a mock here since otherwise StringTransport will complain
        # about being passed unicode when data is being sent to subscribers.

        mock_sub = MagicMock()
        self.ps_factory.topics['test'].add(mock_sub)

        pub_proto = self.ps_factory.buildProtocol(('127.0.0.1', 0))
        pub_tr = proto_helpers.StringTransport()
        pub_proto.makeConnection(pub_tr)

        pub_proto.dataReceived(make_publish_request('test', testdata=5))
        mock_sub.transport.write.assert_called_with(
            json.dumps({'testdata': 5}))

    def test_connectionLost(self):
        sub_proto = self.ps_factory.buildProtocol(('127.0.0.1', 0))
        tr = proto_helpers.StringTransport()
        sub_proto.makeConnection(tr)

        sub_proto.dataReceived(make_subscribe_request('test'))

        assert sub_proto in self.ps_factory.topics['test']

        sub_proto.connectionLost(None)

        assert sub_proto not in self.ps_factory.topics['test']


class TestPubSubClientProtocols:

    def test_publisher(self):
        proto = PublisherProtocol('test', testdata=5)
        proto.makeConnection(MagicMock())

        proto.connectionMade()

        proto.transport.write.assert_called_with(
            make_publish_request('test', testdata=5))

        proto.transport.loseConnection.assert_called_with()

    def test_subscriber_connection(self):
        proto = SubscriberProtocol('test', lambda _: None)
        proto.makeConnection(MagicMock())

        proto.connectionMade()

        proto.transport.write.assert_called_with(
            make_subscribe_request('test'))

    def test_subscriber_received(self):
        callmock = MagicMock()
        proto = SubscriberProtocol('test', callmock)
        proto.makeConnection(MagicMock())

        proto.dataReceived(json.dumps({'testdata': 5}))

        callmock.assert_called_with(testdata=5)
