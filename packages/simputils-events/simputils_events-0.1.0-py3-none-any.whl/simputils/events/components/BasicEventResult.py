from typing import Any

from simputils.events.components.BasicEventCall import BasicEventCall


class BasicEventResult:

    _store: list[tuple[BasicEventCall, Any]] = None
    _pointer: int = 0

    def __init__(self):
        self._store = []

    def append(self, call: BasicEventCall, result: Any):
        self._store.append((call, result))

    def __iter__(self):
        self._pointer = 0
        return self

    def __next__(self) -> tuple[BasicEventCall, Any]:
        try:
            res = self._store[self._pointer]
        except IndexError:
            raise StopIteration

        self._pointer += 1

        return res

    def __len__(self):
        return len(self._store)

    @property
    def results(self) -> list[Any]:
        return [r for c, r in self]
