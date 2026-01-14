from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any, DefaultDict

import dataclasses
import uuid
from collections import defaultdict
import fnmatch

if TYPE_CHECKING:
    from .session import Session

EventCallbackType = Callable[["Broker.Event"], None]


class BrokerImplementation:

    def __init__(self, broker: Broker):
        self._broker = broker

    def publish(self, topic: str, event: Broker.Event) -> None: ...
    def subscribe(
        self, topic_pattern: str, callback: EventCallbackType
    ) -> Broker.Subscription: ...
    def unsubscribe(self, subscription: Broker.Subscription) -> bool: ...


class TestBroker(BrokerImplementation):
    def __init__(self, broker: Broker):
        super().__init__(broker=broker)
        self._subscriptions: DefaultDict[str, list[Broker.Subscription]] = defaultdict(
            list
        )

    def topic_match(self, topic: str, topic_pattern: str):
        # TODO: implement it like nats or zenoh
        return fnmatch.fnmatch(topic, topic_pattern)

    def publish(self, topic: str, event: Broker.Event) -> None:
        print("Publish", repr(topic), event)
        for topic_pattern, subscriptions in self._subscriptions.items():
            # print("?? topic match?", topic_pattern)
            if self.topic_match(topic, topic_pattern):
                for subscription in subscriptions:
                    print(
                        f"  --push--> event to {subscription.topic_pattern!r}: {subscription.callback}"
                    )
                    subscription.callback(event)

    def subscribe(
        self, topic_pattern: str, callback: EventCallbackType
    ) -> Broker.Subscription:
        subscription = self._broker.Subscription(
            topic_pattern=topic_pattern,
            callback=callback,
        )
        self._subscriptions[topic_pattern].append(subscription)
        return subscription

    def unsubscribe(
        self, subscription: Broker.Subscription, raise_if_unknown: bool = True
    ) -> bool:
        topic_pattern = subscription.topic_pattern
        subscriptions = self._subscriptions[topic_pattern]
        try:
            subscriptions.remove(subscription)
        except ValueError:
            if not raise_if_unknown:
                return False
            raise ValueError(f"This subscription is not registerd here: {subscription}")
        return True


class Broker:

    class Event:
        def __init__(self, **data: Any):
            self._data = data

        def __str__(self) -> str:
            kwargs = ", ".join([f"{k}={v!r}" for k, v in self._data.items()])
            return f"{self.__class__.__name__}({kwargs})"

        def unpack(self, *args):
            data = self._data.copy()
            ret = []
            for name in args:
                try:
                    ret.append(data.pop(name))
                except KeyError:
                    raise KeyError(
                        f"Cannot unpack {args} from {self._data}, missing {name!r}."
                    )
            ret.append(data)
            return ret

    @dataclasses.dataclass
    class Subscription:
        topic_pattern: str
        callback: Callable[[Broker.Event], None]
        uuid: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)

    def __init__(self, session: Session):
        self._session = session
        self._broker_implementation = self._create_broker_implementation()

    def _create_broker_implementation(self) -> BrokerImplementation:
        # TODO: select the Broker class from self.session.config
        broker_implementation = TestBroker(self)
        return broker_implementation

    def publish(self, topic: str, **data: Any) -> None:
        self._broker_implementation.publish(topic, self.Event(**data))

    def cmd(self, cmd_name: str, **kwargs) -> None:
        topic = "$CMD." + cmd_name
        event = self.Event(**kwargs)
        self._broker_implementation.publish(topic, event=event)

    def subscribe(
        self, topic_pattern: str, callback: EventCallbackType
    ) -> Broker.Subscription:
        return self._broker_implementation.subscribe(
            topic_pattern=topic_pattern, callback=callback
        )

    def unsubscribe(self, subscription: Broker.Subscription) -> bool:
        return self._broker_implementation.unsubscribe(subscription=subscription)
