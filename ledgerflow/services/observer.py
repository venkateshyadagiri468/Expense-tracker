from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: Any) -> None:
        """Called when a subscribed event is published."""
        pass


class EventManager:
    def __init__(self):
        self._listeners: Dict[str, List[Observer]] = {}

    def subscribe(self, event: str, listener: Observer) -> None:
        """Subscribes an observer to an event."""
        if event not in self._listeners:
            self._listeners[event] = []
        if listener not in self._listeners[event]:
            self._listeners[event].append(listener)

    def unsubscribe(self, event: str, listener: Observer) -> None:
        """Unsubscribes an observer from an event."""
        if event in self._listeners:
            self._listeners[event].remove(listener)

    def publish(self, event: str, data: Any) -> None:
        """Publishes an event to all subscribed observers."""
        if event in self._listeners:
            for listener in self._listeners[event]:
                listener.update(event, data)
