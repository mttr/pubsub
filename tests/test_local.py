# tests/test_pubsub.py

from pubsub.local import PubSub


def test_local_pubsub():
    """Verify simple usage of local PubSub."""
    pubsub = PubSub()
    results = {'a': 0, 'b': 0}
    expected = {'a', 'b'}

    def sub_func_a(add=0, **kwargs):
        results['a'] += add

    def sub_func_b(add=0, **kwargs):
        results['b'] += add

    pubsub.subscribe("test", sub_func_a)
    pubsub.publish("test", add=3)

    assert results == {'a': 3, 'b': 0}

    pubsub.subscribe("test", sub_func_b)
    pubsub.publish("test", add=2)

    assert results == {'a': 5, 'b': 2}
