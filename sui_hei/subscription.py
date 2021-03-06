import json
import pickle
from collections import OrderedDict

import graphene
from graphene import Field
from graphene.types.objecttype import ObjectTypeOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.props import props
from redis import Redis
from rx import Observable, Observer
from six import get_unbound_function

from cindy.settings import REDIS_HOST


class GraphQLObserver(Observer):
    def __init__(self, channel, subscription_id):
        self.subscription_id = subscription_id
        self.channel = channel

    def on_next(self, result):
        self.channel.send({
            'text':
            json.dumps({
                'id': self.subscription_id,
                'type': 'data',
                'payload': {
                    'data': result.data,
                    'errors': result.errors,
                }
            })
        })

    def on_completed(self):
        pass

    def on_error(self, error):
        pass


class SubscriptionOptions(ObjectTypeOptions):
    arguments = None
    output = None
    resolver = None


class Subscription(graphene.ObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls,
                                    resolver=None,
                                    output=None,
                                    arguments=None,
                                    _meta=None,
                                    **options):
        if not _meta:
            _meta = SubscriptionOptions(cls)

        output = output or getattr(cls, 'Output', None)
        fields = {}
        if not output:
            # If output is defined, we don't need to get the fields
            fields = OrderedDict()
            for base in reversed(cls.__mro__):
                fields.update(yank_fields_from_attrs(base.__dict__, _as=Field))
            output = cls

        if not arguments:
            input_class = getattr(cls, 'Arguments', None)

            if input_class:
                arguments = props(input_class)
            else:
                arguments = {}

        if not resolver:
            assert hasattr(
                cls,
                'next'), 'All subscriptions must define a next method in it'
            resolver = get_unbound_function(getattr(cls, 'subscribe'))

        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields

        _meta.output = output
        _meta.resolver = resolver
        _meta.arguments = arguments

        super(Subscription, cls).__init_subclass_with_meta__(
            _meta=_meta, **options)

    @classmethod
    def subscribe(cls, obj, info, **kwargs):
        value = cls.next(info.root_value, info, **kwargs)
        if value:
            result = [value]
        else:
            result = []
        return Observable.from_(result)

    @classmethod
    def Field(cls, *args, **kwargs):
        return Field(
            cls._meta.output,
            args=cls._meta.arguments,
            resolver=cls._meta.resolver)


class GraphQLSubscriptionStore:
    """
    Base for subscription store. Should be replaced with redis or similar when running
    workers in separate processes.
    """

    def __init__(self, key="GraphQLSubscriptionStore"):
        self.key = key
        self.rediscon = Redis(host=REDIS_HOST["host"], port=REDIS_HOST["port"])

        self.rediscon.set(key, b'\x80\x03}q\x00.')  # pickled `{}`

    # Each client has unique channel and each client can have more than one subscription
    # on the same channel.
    def subscribe(self, channel, subscription_id, payload):
        subscriptions = pickle.loads(self.rediscon.get(self.key))

        subscriptions.setdefault(channel, {})
        subscriptions[channel][subscription_id] = {
            'payload': payload,
        }

        self.rediscon.set(self.key, pickle.dumps(subscriptions))

    def unsubscribe(self, channel, subscription_id=None):
        subscriptions = pickle.loads(self.rediscon.get(self.key))
        if channel not in subscriptions:
            return
        if subscription_id:
            if subscription_id not in subscriptions[channel]:
                return
            del subscriptions[channel][subscription_id]
        else:
            del subscriptions[channel]

        self.rediscon.set(self.key, pickle.dumps(subscriptions))

    def get_subscriptions(self, model):
        return pickle.loads(self.rediscon.get(self.key))
