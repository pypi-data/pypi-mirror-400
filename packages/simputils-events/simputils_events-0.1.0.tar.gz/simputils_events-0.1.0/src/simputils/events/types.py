from collections.abc import Callable
from enum import Enum
from typing import Any, Concatenate

from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.components.BasicEventCall import BasicEventCall

EventType = str | Enum | BasicEvent
EventCallType = Callable[Concatenate[BasicEventCall, ...], Any | None]
