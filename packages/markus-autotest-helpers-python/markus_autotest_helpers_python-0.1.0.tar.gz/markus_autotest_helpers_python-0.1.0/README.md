# Python Helper

Helper functions and classes for executing python unit tests.

## Installation

```shell
pip install markus-autotest-helpers-python
```

## General helpers

### bound_timeout(`seconds`)
Return a decorator that will time out the test case after `seconds` seconds. 

A MarkUs-compatible function wrapper based on `timeout_decorator` that will return the original error message if one is raised instead of a Timeout. A TimeoutError will be raised if the provided time (in seconds) is exceeded.

#### Usage

```python
@bound_timeout(10)	# This will timeout if my_function takes longer than 10 seconds to run.
def my_function() -> None:
	...
```
