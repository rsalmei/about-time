[![Coverage](https://img.shields.io/badge/coverage-100%25-green.svg)]()
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/rsalmei/about-time/graphs/commit-activity)
[![PyPI version](https://img.shields.io/pypi/v/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI status](https://img.shields.io/pypi/status/about-time.svg)](https://pypi.python.org/pypi/about-time/)

# about-time
## Small tool to track time of Python code blocks.


# What does it do?

There are several times we need to instrument and log code execution, to see where complex pipelines are spending the most time in.

A simple `start = time.time()` and `end = time.time() - start` does not cut it when we want to track several lines at the same time, and/or whole blocks with line granularity.


# How to use it?

The tool supports being used like a context manager or a callable handler.

Like this:

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
print(f'func_1 time: {t_1.duration_human}')
print(f'func_2 time: {t_2.duration_human}')
print(f'total time: {t_whole.duration_human}')
```

There's also the `duration` property, which returns the actual float time in seconds.

You can also use it like:

```python
t = about_time(func_1)
t = about_time(lambda: func_2('params'))
```

Or you mix and match both:

```python
with about_time() as t_whole:
    t_1 = about_time(func_1)
    t_2 = about_time(lambda: func_2('params'))
```


# How do I install it?

```bash
$ pip install about-time
```


## License
This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.


## Nice huh?

Thanks for your interest!

I wish you have fun using this tool! :)
