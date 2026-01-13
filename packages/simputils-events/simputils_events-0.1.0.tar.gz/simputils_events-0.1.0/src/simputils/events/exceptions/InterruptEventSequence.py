from typing import Any


class InterruptEventSequence(BaseException):
	"""
	Exception used to interrupt silently the event chain.

	Must be explicitly raised in the callback that suppose to interrupt the event-chain.

	Optionally `result` can be specified as a first argument of the constructor.

	Additionally, `EventCall` instance during which this happens will have `interrupted` field set to True
	"""

	_result: Any | None = None

	@property
	def result(self) -> Any | None:
		return self._result

	def __init__(self, result: Any | None = None):
		self._result = result
		super().__init__()
