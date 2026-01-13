from collections.abc import Callable

from simputils.events.components.BasicEvent import BasicEvent


class BasicEventCall:

    _event: BasicEvent = None
    _callback: Callable = None
    _interrupted: bool = False

    def set_interrupted(self, val: bool):
        self._interrupted = val

    @property
    def interrupted(self) -> bool:
        return self._interrupted

    @property
    def event(self) -> BasicEvent:
        return self._event

    @property
    def callback(self) -> Callable:
        return self._callback

    def __init__(self, event: BasicEvent, callback: Callable):
        self._event = event
        self._callback = callback

    def __str__(self):
        interrupted = " INTERRUPTED" if self.interrupted else ""
        return f"<{self.__class__.__name__} {self.event} / {self.callback}{interrupted}>"

    def __call__(self, *args, **kwargs):
        return self._callback(self, *args, **kwargs)
