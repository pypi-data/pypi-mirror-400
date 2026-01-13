from uuid import UUID, uuid1


class BasicEvent:

	_uid: UUID = None
	_name: str = None

	@property
	def uid(self) -> UUID:
		return self._uid

	@property
	def name(self) -> str:
		return self._name

	def __init__(self, name: str, *, uid: UUID = None):
		self._uid = uid or uuid1()
		self._name = str(name)

	def __str__(self):
		return f"<{self.__class__.__name__} {self._name}>"
