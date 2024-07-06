from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self.events: dict[str, list[Callable]] = {}

    def register(self, event: str, callback: Callable):
        if event in self.events:
            self.events.get(event).append(callback)
        else:
            self.events[event] = [callback]

    def emit(self, event: str, *args, **kwargs):
        if event in self.events:
            for callback in self.events[event]:
                return callback(*args, **kwargs)
