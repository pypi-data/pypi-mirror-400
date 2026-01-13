from abc import ABCMeta
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.exceptions.InterruptEventSequence import InterruptEventSequence
from simputils.events.types import EventType, EventCallType

if TYPE_CHECKING:
	from simputils.events.components.BasicEventCall import BasicEventCall
	from simputils.events.components.BasicEventResult import BasicEventResult


class Eventful(metaclass=ABCMeta):
	"""
	Parent class for utilizing simputils-events infrastructure
	"""

	_event_callbacks: dict[str, dict[UUID, tuple[EventCallType, dict]]] = None
	_events_cache_uid: dict[UUID, "BasicEvent"] = None
	_events_cache_name: dict[str, "BasicEvent"] = None

	def __init__(self):
		self._event_callbacks = {}
		self._events_cache_uid = {}
		self._events_cache_name = {}

	@classmethod
	def __get_str_event(cls, event: EventType) -> str:
		"""
		Primitive to translate event-type into a string-name

		:param event: EventType (string, enum, BasicEvent)
		:return: Event stringified name
		"""
		if isinstance(event, Enum):
			return event.value
		return f"{event}"

	def on_event(self, event: EventType, callback: EventCallType, **kwargs: object) -> "BasicEvent":
		"""
		Registering a callback on an event

		:param event: Event name
		:param callback: Callback that could be triggered on this event
		:param kwargs: Custom kwargs for the callback
		:return:
		"""
		if not isinstance(event, BasicEvent):
			event_class = self._get_event_class()
			event = event_class(self.__get_str_event(event))
		if event.name not in self._event_callbacks:
			self._event_callbacks[event.name] = {}
		self._events_cache_uid[event.uid] = event
		self._events_cache_name[event.name] = event
		self._event_callbacks[event.name][event.uid] = (callback, kwargs)
		return event

	def event_del(self, uid: UUID):
		"""
		Remove specific event by event-uid

		The UID of the event is available at the `BasicEvent` instance returned from `on_event()` method

		:param uid: Event-UID
		:return: None
		"""
		if uid in self._events_cache_uid:
			event = self._events_cache_uid[uid]
			del self._event_callbacks[event.name][uid]
			del self._events_cache_uid[uid]

	def event_purge(self, event: EventType):
		"""
		Remove a certain registered event on the object
		:param event:
		:return:
		"""
		event = self.__get_str_event(event)
		if event in self._event_callbacks and self._event_callbacks[event]:
			for uid, callbacks in self._event_callbacks[event].items():
				del self._events_cache_uid[uid]
			del self._event_callbacks[event]

	def event_purge_all(self):
		"""
		Remove all the registered events on the object
		:return: None
		"""
		self._event_callbacks = {}
		self._events_cache_uid = {}

	def event_run(self, event: EventType, *args, **kwargs) -> "BasicEventResult | None":
		"""
		Trigger an event

		It allows also additionally provide *args and **kwargs,
		those will be merged with those that assigned during event registration

		:param event: Event name
		:param args: Optional args for a callback
		:param kwargs: Optional kwargs for a callback
		:return: BasicEventResult (unless redefined) or None
		"""
		event = self.__get_str_event(event)
		if event not in self._events_cache_name:
			return None

		event = self._events_cache_name[event]

		if event.name in self._event_callbacks and self._event_callbacks[event.name]:
			events_result_class = self._get_events_result_class()
			result = events_result_class()
			for uid, callback_group in self._event_callbacks[event.name].items():
				callback, callback_kwargs = callback_group
				callback_kwargs.update(kwargs)
				event_call_class = self._get_event_call_class()
				event_call = event_call_class(event, callback)
				try:
					call_res = event_call(*args, **callback_kwargs)
					result.append(event_call, call_res)
				except InterruptEventSequence as e:
					event_call.set_interrupted(True)
					result.append(event_call, e.result)
					break

			return result

		return None

	@classmethod
	def _get_event_class(cls) -> type["BasicEvent"]:
		"""
		Can be redefined with a custom `Event` class
		:return: Event class
		"""
		return BasicEvent

	@classmethod
	def _get_event_call_class(cls) -> type["BasicEventCall"]:
		"""
		Can be redefined with a custom `EventCall` class
		:return: EventCall class
		"""
		from simputils.events.components.BasicEventCall import BasicEventCall
		return BasicEventCall

	@classmethod
	def _get_events_result_class(cls) -> type["BasicEventResult"]:
		"""
		Can be redefined with a custom `EventResult` class
		:return: EventResult class
		"""
		from simputils.events.components.BasicEventResult import BasicEventResult
		return BasicEventResult
