[<img align="right" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" width="217px" height="51x">](https://www.buymeacoffee.com/rsalmei)

# about-time
#### Easily measure timing and throughput of code blocks, with beautiful human friendly representations.

[![Coverage](https://img.shields.io/badge/coverage-100%25-green.svg)]()
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/rsalmei/about-time/graphs/commit-activity)
[![PyPI version](https://img.shields.io/pypi/v/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI status](https://img.shields.io/pypi/status/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI Downloads](https://pepy.tech/badge/about-time)](https://pepy.tech/project/about-time)

## What does it do?

Did you ever need to log the duration of an operation? Yeah, this is easy, but:
- log the duration of two or more operations at the same time, including the whole duration?
- instrument a code to retrieve time metrics to send to a log or time series database?
- easily see durations with units like *us* microseconds and *ms* milliseconds?
- easily see the throughput of a bottleneck in items/second to benchmark a refactoring?

Yes, it can get kinda complex, and even while doable, it will for sure taint your code and make you lose focus.

I have the solution, behold!

```python
import time
from about_time import about_time

def func():
    time.sleep(85e-3)
    return True

with about_time() as at1:
    at2 = about_time(func)

    at3 = about_time(x * 2 for x in range(5))
    data = [x for x in at3]
    

print('total:', at1.duration_human)
print(' func:', at2.duration_human, '->', at2.result)
print(' iter:', at3.duration_human, 'count:', at3.count, '@', at3.throughput_human, '->', data)
```

This prints:
```
total: 85.12ms
 func: 85.04ms -> True
 iter: 6.68us count: 5 @ 748614.98/s -> [0, 2, 4, 6, 8]
```

How cool is that? 😲

It's much nicer to see `85.12ms` instead of this right?

```
In [7]: at1.duration
Out[7]: 0.08511673200064251
```

So, `about_time` measures code blocks, both time and throughput, and converts to beautiful human friendly representations! 👏


## Install it

Just do in your python venv:

```bash
$ pip install about-time
```


## Use it

There's three modes of operation: context manager, callable and throughput. Let's dive in.


### 1. Use it like a context manager:

```python
from about_time import about_time

with about_time() as at:
    # the code to be measured...

print('The whole block took:', at.duration_human)
```

This way you can nicely wrap any amount of code.

> In this mode, there are the basic fields `duration` and `duration_human`.


### 2. Use it with a callable:

```python
from about_time import about_time

at = about_time(some_func)

print('The result was:', at.result, 'and took:', at.duration_human)
```

This way you have a one liner, and do not need to increase the indent of your code.

> In this mode, there is the field `result`, in addition to the basic ones.

If your function have params, you can use a `lambda` or (📌 new) simply send them:

```python
from about_time import about_time

def add(number):
    return number + 1

at = about_time(add, 42)
# or even:
at = about_time(add, number=42)

print('The result was:', at.result, 'and took:', at.duration_human)
```


### 3. Use it with an iterable or generator:

```python
from about_time import about_time

at = about_time(iterable)
for item in at:
    # process item.

print('The whole block took:', at.duration_human)
print('Total items processed:', at.count)
print('Throughput:', at.throughput_human)
```

This way `about_time` can extract iterations info, and together with the duration info, calculates the throughput of the whole loop! Specially useful with generators, which do not have length.

> In this mode, there are the fields `count` and `throughput_human`, in addition to the basic ones.

Note:
- you can send even generator expressions, anything that is iterable to python!
- you can consume not only in a `for` loop, but also in comprehensions, `map()`s, `filter()`s, `sum()`s, `max()`s, `list()`s, etc, thus any function that expects an iterator!

> Cool tricks under the hood:
> - the timer only triggers when the first element is queried, so you can initialize whatever you need before entering the loop!
> - the `count` and `throughput_human` methods are updated in *real time*, so you can use them even inside the loop!


## Humans are first class citizens :)

### duration

I've considered two key concepts in designing the human friendly features: `3.44s` is more meaningful than `3.43584783784s`, and `14.12us` is much nicer than `.0000141233333s`. So what I do is: round values to at most two decimal places, and find the best scale unit to represent them, minimizing resulting values smaller than `1`.

> The search for the best unit considers even the rounding been applied! So for example `0.999999` does not end up like `999.99us` (truncate) nor `1000.0us` (bad unit), but is auto-upgraded to the next unit `1.0ms`!

The `duration_human` ranges seamlessly from nanoseconds to hours. Values smaller than 60 seconds are rendered with at most two decimal digits as "DDD.D[D]xs", and above 1 minute it changes to "hours:minutes:seconds.M".

Much more humanly humm? ;)

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


### throughput

I've made the `throughput_human` with a similar logic. It is funny how much trickier "throughput" is to the human brain! For example if something took "1165263 seconds" to handle "123 items", how fast did it go? It's not obvious...

Even dividing the duration by the number of items, we get "9473 seconds/item", which also do not mean much. To make some sense of it we need to divide again by 3600 (seconds in an hour) to finally get "2.63 hours/item", which is much better. But throughput is the inverse of that (items/time), so `about_time` nicely returns it as `0.38/h`... Now we know how fast was that process!

> `about_time` has per-second, per-minute and per-hour units.

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

`about_time` supports all versions of python, but in pythons >= `3.3` it performs better with much higher resolution and smaller propagating of errors, thanks to the new `time.perf_counter`. In older versions, it uses `time.time` as usual.


## Changelog highlights:
- 3.1.0: include support for parameters in callable mode; official support for python 3.8, 3.9 and 3.10
- 3.0.0: greatly improved the counter/throughput mode, with a single argument and working in real time
- 2.0.0: feature complete, addition of callable and throughput modes
- 1.0.0: first public release, context manager mode


## License
This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.


## Nice huh?

Thank you for your interest!

I've put much ❤️ and effort into this.
<br>If you appreciate my work you can sponsor me, buy me a coffee! The button is on the top right of the page (the big orange one, it's hard to miss 😊)
