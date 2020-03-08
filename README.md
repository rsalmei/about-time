[![Coverage](https://img.shields.io/badge/coverage-100%25-green.svg)]()
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/rsalmei/about-time/graphs/commit-activity)
[![PyPI version](https://img.shields.io/pypi/v/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI status](https://img.shields.io/pypi/status/about-time.svg)](https://pypi.python.org/pypi/about-time/)


# about-time
## The missing Python framework to track timing of code blocks.


## What does it do?

Did you ever need to:
- log the duration of an operation;
- extract time metrics to send to a log or to a time series database;
- or even benchmark some refactoring?

Yes, normally a simple `start = time.time()` and `end = time.time() - start` would do it, but what if you need to track two or more blocks at the same time? Or simultaneously the whole duration **and** its constituent parts? 

Behold!

```python
import time
from about_time import about_time

def func1():
    time.sleep(.350)

def func2():
    time.sleep(.650)

with about_time() as at:
    at1 = about_time(func1)
    at2 = about_time(func2)

print(at1.duration_human)  # prints "353.78ms"
print(at2.duration_human)  # prints "654.36ms"
print(at.duration_human)   # prints "1.01s"
```

How cool is that?
I even smartly convert the duration to something readable! Instead of ".0000141233333s", you get `14.12us` which is much nicer! (of course the actual `duration` is available too)

So, this tool measures the execution time of blocks of code, supports conversion to a beautiful human friendly representation, and can even count iterations and thus infer the system throughput!


## Install it

Just do in your python venv:

```bash
$ pip install about-time
```


## Use it

There's three modes of operation: context manager, callable and counter. In the introduction you've 
already seen context manager and callable.


### 1. Use it like a context manager:

```python
from about_time import about_time

with about_time() as at:
    # the code to be measured...

print('The whole block took:', at.duration_human)
# you could also get the actual float in seconds with `at.duration`
```


### 2. Use it with a callable:

```python
from about_time import about_time

at = about_time(some_func)

print('The result is:', at.result, 'and took:', at.duration_human)
```

In this mode, there will be a new field called `result` to get the outcome of the function!


### 3. Use it like a counter:

```python
from about_time import about_time

for item in about_time(func_result, iterable_or_generator):
    # use item any way you want.
    process(item)
```

So, just wrap your `iterable` and iterate as usual! Since it obviously have duration information, and now the number of iterations, it can also calculate the throughput of the whole block! Specially useful in generators, which do not have length.

The `func_result` is any callable to receive the timer object (most normally will be an inner function), which will be called when the iterable is exhausted, bringing the timing information.

```python
from about_time import about_time

def my_function():
    def on_result(at):
        print('func: size=%d throughput=%s', at.count, at.throughput_human)

    for item in about_time(on_result, iterable_or_generator):
        # use item any way you want.
        process(item)

    # when the items are exhausted, the `on_result` function will be called!
```

In this mode, there will be two new fields, called `count` and... Yes! There's also a `throughput_human`!


## Humans are first class citizens :)

### duration

I've considered two key concepts in designing the human friendly functions: `3.44s` is more meaningful than `3.43584783784s`, and `14.12us` is much nicer than `.0000141233333s`. So saying it another way, I round values to two decimal places at most, and find the smaller unit to represent it, minimizing values smaller than `1`.

Note that it dynamically finds the best unit to represent the value, considering even the rounding been applied. So if a value is for example `0.999999`, it would end up like `1000.0ms` after rounded, but it is auto-upgraded to the next unit and you get `1.0s`!

The `duration_human` changes seamlessly from nanoseconds to hours. Values smaller than 60 seconds are rendered with two digits precision at most (zeros to the right of the decimal point are not shown), and starting from 1 minute, it changes to a "hours:minutes:seconds.M" milliseconds.

Much more humanly humm? ;)


### throughput

I've made the `throughput_human` with similar logic, because to the human brain it is much trickier to figure out! If something took `1165263` seconds to handle `123` items, how fast did it go? It's not obvious...
Even dividing them to find out the time per item, we get `9473` seconds/item, which also don't mean much. 
Dividing by `3600` we get `2.63` hours per item, which is much better, and the throughput that I calculate is returned nicely as `0.38/h`... Now we know how fast is that process!

The tool has per-second, per-minute and per-hour calculations.


### Some examples of conversions to human (directly from the unit tests):

duration (float seconds) | duration_human
:---: | :---:
.00000000185 | '1.85ns'
.000000999996 | '1.0us'
.00001 | '10.0us'
.0000156 | '15.6us'
.01 | '10.0ms'
.0141233333333 | '14.12ms'
.1099999 | '110.0ms'
.1599999 | '160.0ms'
.8015 | '801.5ms'
3.434999 | '3.43s'
59.999 | '0:01:00'
68.5 | '0:01:08.5'
125.825 | '0:02:05.8'
4488.395 | '1:14:48.4'


duration (float seconds) | number of elements | throughput_human
:---: | :---: | :---:
1\. | 10 | '10.0/s'
1\. | 2500 | '2500.0/s'
2\. | 1 | '30.0/m'
2\. | 10 | '5.0/s'
1.981981981981982 | 11 | '5.55/s'
100\. | 10 | '6.0/m'
1600\. | 3 | '6.75/h'
.99 | 1 | '1.01/s'
1165263\. | 123 | '0.38/h'


### Accuracy

This tool supports all versions of python, but in pythons >= `3.3`, the code uses the new `time.perf_counter` to achieve much higher resolution and smaller propagating of errors. In older versions, it uses `time.time`.


## License
This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.


## Nice huh?

Thank you for your interest!

I've put much ❤️ and effort into this.

I wish you have fun using this tool! :)
