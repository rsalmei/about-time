[![Coverage](https://img.shields.io/badge/coverage-100%25-green.svg)]()
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/rsalmei/about-time/graphs/commit-activity)
[![PyPI version](https://img.shields.io/pypi/v/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI status](https://img.shields.io/pypi/status/about-time.svg)](https://pypi.python.org/pypi/about-time/)


# about-time
## Small tool to track time of Python code blocks.


## What does it do?

Sometimes I need something to log code execution, or to extract metrics to send to influx, so I've created this tool.

A simple `start = time.time()` and `end = time.time() - start` does not cut it when you need to track two or more lines/blocks at the same time, or simultaneously whole/part relationship of blocks.

This tool measures the execution time of blocks of code, and can even count iterations and the system throughput, with beautiful "human" representations.


## How do I install it?

Just do in your python venv:

```bash
$ pip install about-time
```


## How to use it?

There's three modes of operation: context manager, callable handler and iterator metrics.


### 1. Use it like a context manager:

```python
from about_time import about_time

with about_time() as t_whole:
    with about_time() as t_1:
        func_1()
    with about_time() as t_2:
        func_2('params')
```

Then, get the timings like this:

```python
# python 3.7 example, using f strings.
print(f'func_1 time: {t_1.duration_human}')
print(f'func_2 time: {t_2.duration_human}')
print(f'total time: {t_whole.duration_human}')
```

There's also the `duration` property, which returns the actual float time in seconds.

```python
secs = t_whole.duration
```


### 2. Use it like a callable handler:

```python
t_1 = about_time(func_1)
t_2 = about_time(lambda: func_2('params'))
```

If you use the callable handler syntax, there will be a new field called `result` to get the outcome of the function!

```python
results = t_1.result, t_2.result
```

Or you can mix and match both:

```python
with about_time() as t_whole:
    t_1 = about_time(func_1)
    t_2 = about_time(lambda: func_2('params'))
```


### 3. Use it to count iterations and measure throughput:

Wrap your iterable and just iterate it! Since it internally have duration information, it can also calculate the throughput of the whole block. Specially useful in generators, which do not have length.

This mode requires a function parameter to receive the timer object (which can be an inner function or a lambda), enabling you to use a `for` loop normally, and the callback will be called when the iterable is exhausted, with the timing information.

```python
def callback(t_func):
    logger.info('func: size=%d throughput=%s', t_func.count,
                                               t_func.throughput_human)
items = filter(...)
for item in about_time(callback, items):
    # use item any way you want.
    process(item)

# the callback is already called upon getting here.
```


## Some nice features

### Humans are first class citizens :)

I've considered two key concepts in designing the human friendly functions: `3.44s` is more meaningful than `3.43584783784s`, and `14.12us` is much nicer than `.0000141233333s`. So saying it another way, I round values to two decimal places at most, and finds the smaller unit to represent it, minimizing values smaller than `1`.

Note that it dynamically finds the best unit to represent the value, considering even the rounding been applied. So if a value is for example `0.999999`, it would end up like `1000.0ms` after rounded, but it is auto-upgraded to the next unit `1.0s`.

The `duration_human` changes seamlessly from nanoseconds to hours. Values smaller than 60 seconds are rendered with two digits precision at most (zeros to the right of the decimal point are not shown), and starting from 1 minute, an "hours:minutes:seconds.M" milliseconds (with only one digit precision). Some examples directly from the unit tests:

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

The `throughput_human` has similar logic, and to human brain it is much trickier to figure out: If it took `1165263` seconds to handle `123` items, how fast it did? Even dividing to find out the time per item `9473` seconds don't mean much. Dividing by `3600` we get `2.63` hours per item, and the throughput is returned nicely as `0.38/h`. The tool has per-second, per-minute and per-hour. Some examples:

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

This tool supports all versions of python, but in pythons >= `3.3`, the code uses the new `time.perf_counter` to gain from the higher resolution and smaller propagating of errors. In older versions, it uses `time.time`.


## License
This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.


## Nice huh?

Thanks for your interest!

I wish you have fun using this tool! :)
