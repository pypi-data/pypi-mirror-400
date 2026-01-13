# Python SimpUtils Events

[//]: # (TODO   Add more examples, documentation and use-cases)

## An example

```python
from datetime import datetime, timezone
from enum import Enum

from simputils.events.abstract.Eventful import Eventful
from simputils.events.components.BasicEventCall import BasicEventCall
from simputils.events.components.BasicEventResult import BasicEventResult
from simputils.events.exceptions.InterruptEventSequence import InterruptEventSequence


# Creating event names as str-backed enum
class MyEventEnum(str, Enum):
	BEFORE = "evt-before"
	AFTER = "evt-after"


# Creating target class to which we will be attaching events
class MyObj(Eventful):

	@classmethod
	def _display_summary(cls, sub_results: list):
		for item in sub_results:
			for desc in item:
				print(">>> ", desc)

	def prepare_data(self, name: str, surname: str, age: int):
		sub_res = self.event_run(MyEventEnum.BEFORE, name, surname, age)
		if sub_res:
			self._display_summary(sub_res.results)
		else:
			print("No pre-processed description prepared")

		sub_res_2 = self.event_run(MyEventEnum.AFTER, datetime.now(timezone.utc))

		return self._preprocess_results(sub_res) + self._preprocess_results(sub_res_2)

	@classmethod
	def _preprocess_results(cls, sub_res: BasicEventResult) -> list:
		res = []
		call: BasicEventCall
		for call, call_res in sub_res:
			if call_res is not None:
				for item in call_res:
					res.append(item)
			if call.interrupted:
				res.append(f"{call.callback.__name__}() INTERRUPTED")
		return res

# Callback for "on_event" of "BEFORE"
def on_before(call: BasicEventCall, name: str, surname: str, age: int) -> list[str]:
	res = [
		f"[[event \"{call.event}\" adjusted through `{call.callback.__name__}()` callback]]",
		f"Name: {name} {surname}",
		f"Age: {age}"
	]
	return res


# Callback for "on_event" of "AFTER"
def on_after(call: BasicEventCall, ts: datetime) -> list[str]:
	res = [
		f"[[event \"{call.event}\" adjusted through `{call.callback.__name__}()` callback]]",
		f"Finished at: {ts}"
	]
	# raise InterruptEventSequence(res)
	return res


def main():
	obj = MyObj()
	obj.on_event(MyEventEnum.BEFORE, on_before)
	obj.on_event(MyEventEnum.AFTER, on_after)
	obj.on_event(MyEventEnum.AFTER, on_after)

	descriptions = obj.prepare_data("Ivan", "Ponomarev", 35)

	print(f"Resulting descriptions:")
	for desc in descriptions:
		print("##\t", desc)


if __name__ == "__main__":
	main()

```

Output:
```text
>>>  [[event "<BasicEvent evt-before>" adjusted through `on_before()` callback]]
>>>  Name: Ivan Ponomarev
>>>  Age: 35
Resulting descriptions:
##	 [[event "<BasicEvent evt-before>" adjusted through `on_before()` callback]]
##	 Name: Ivan Ponomarev
##	 Age: 35
##	 [[event "<BasicEvent evt-after>" adjusted through `on_after()` callback]]
##	 Finished at: 2026-01-07 10:07:04.820497+00:00
##	 [[event "<BasicEvent evt-after>" adjusted through `on_after()` callback]]
##	 Finished at: 2026-01-07 10:07:04.820497+00:00
```

In case if `# raise InterruptEventSequence(res)` is uncommented, the output would be:
```text
>>>  [[event "<BasicEvent evt-before>" adjusted through `on_before()` callback]]
>>>  Name: Ivan Ponomarev
>>>  Age: 35
Resulting descriptions:
##	 [[event "<BasicEvent evt-before>" adjusted through `on_before()` callback]]
##	 Name: Ivan Ponomarev
##	 Age: 35
##	 [[event "<BasicEvent evt-after>" adjusted through `on_after()` callback]]
##	 Finished at: 2026-01-07 10:08:08.767001+00:00
##	 on_after() INTERRUPTED
```