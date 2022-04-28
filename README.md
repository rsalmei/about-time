[<img align="right" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" width="217px" height="51x">](https://www.buymeacoffee.com/rsalmei)
[<img align="right" alt="Donate with PayPal button" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif">](https://www.paypal.com/donate?business=6SWSHEB5ZNS5N&no_recurring=0&item_name=I%27m+the+author+of+alive-progress%2C+clearly+and+about-time.+Thank+you+for+appreciating+my+work%21&currency_code=USD)

# about-time
### A cool helper for tracking time and throughput of code blocks, with beautiful human friendly renditions.

[![Coverage](https://img.shields.io/badge/coverage-100%25-green.svg)]()
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/rsalmei/about-time/graphs/commit-activity)
[![PyPI version](https://img.shields.io/pypi/v/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI status](https://img.shields.io/pypi/status/about-time.svg)](https://pypi.python.org/pypi/about-time/)
[![PyPI Downloads](https://pepy.tech/badge/about-time)](https://pepy.tech/project/about-time)

## What does it do?

Did you ever need to measure the duration of an operation? Yeah, this is easy.

But how to:
- measure the duration of two or more blocks at the same time, including the whole duration?
- instrument a code to cleanly retrieve duration in one line, to log or send to a time series database?
- easily see human friendly durations with units like *ms* (milliseconds), *us* (microseconds) and even *ns* (nanoseconds)?
- measure the throughput of a block? it is way harder, as it needs to measure both duration and iterations!
- easily see human friendly throughputs in "per second", "per minute", "per hour" or even "per day"?

Yes, it can get complex! And even while one could do it, it would probably get messy and pollute the code being instrumented.

I have the solution, behold!

```python
from about_time import about_time


def some_func():
    import time
    time.sleep(85e-3)
    return True


def main():
    with about_time() as t1:  # <-- use it like a context manager!

        t2 = about_time(some_func)  # <-- use it with any callable!!

        t3 = about_time(x * 2 for x in range(5000))  # <-- use it with any iterable or generator!!!
        data = [x for x in t3]  # then just iterate!

    print(f'total: {t1.duration_human}')
    print(f'  some_func: {t2.duration_human} -> result: {t2.result}')
    print(f'  generator: {t3.duration_human} -> {t3.count} elements, throughput: {t3.throughput_human}, result_len: {len(data)}')
```

This `main()` function prints:
```
total: 90.6ms
  some_func: 90.0ms -> result: True
  generator: 525µs -> 5000 elements, throughput: 9.52M/s, result_len: 5000
```

How cool is that? 😲👏

You can also get the duration in seconds if needed:
```
In [7]: t1.duration
Out[7]: 0.09056673200064251
```
But `90.6ms` is way better, isn't it?

So, `about_time` measures code blocks, both time and throughput, and converts to beautiful human friendly representations! 👏


## Get it

Just install with pip:

```bash
❯ pip install about-time
```


## Use it

There're three modes of operation: context manager, callable and throughput. Let's dive in.


### 1. Use it like a context manager:

```python
from about_time import about_time

with about_time() as at:
    # the code to be measured...
    # any lenghty block.

print(f'The whole block took: {at.duration_human}')
```

This way you can nicely wrap any amount of code.

> In this mode, there are the basic fields `duration` and `duration_human`.


### 2. Use it with any callable:

```python
from about_time import about_time

at = about_time(some_func)

print(f'The whole block took: {at.duration_human}')
print(f'And the result was: {at.result}')

```

This way you have a nice one liner, and do not need to increase the indent of your code.

> In this mode, there is an additional field `result`, with the return of the callable.

If the callable have params, you can use a `lambda` or (📌 new) simply send them:

```python
def add(n, m):
    return n + m

at = about_time(add, 1, 41)
# or:
at = about_time(add, n=1, m=41)
# or even:
at = about_time(lambda: add(1, 41))

```


### 3. Use it with any iterable or generator:

```python
from about_time import about_time

at = about_time(iterable)
for item in at:
    # process item.

print(f'The whole block took: {at.duration_human}')
print(f'It was detected {at.count} elements')
print(f'The throughput was: {at.throughput_human}')
```

This way `about_time` also extracts the number of iterations, and with the measured duration it calculates the throughput of the whole loop! Specially useful with generators, which do not have length.

> In this mode, there are the additional fields `count`, `throughput` and `throughput_human`, which should be self-descriptive at this point.

Cool tricks under the hood:
- you can use it even with generator expressions, anything that is iterable to python!
- you can consume it not only in a `for` loop, but also in {list|dict|set} comprehensions, `map()`s, `filter()`s, `sum()`s, `max()`s, `list()`s, etc, thus any function that expects an iterator! 👏
- the timer only starts when the first element is queried, so you can initialize whatever you need before entering the loop! 👏
- the `count` and `throughput`/`throughput_human` fields are updated in **real time**, so you can use them even inside the loop!


## Accuracy

`about_time` supports all versions of python, but in pythons >= `3.3` it performs even better, with much higher resolution and smaller propagation of errors, thanks to the new `time.perf_counter`. In older versions, it uses `time.time` as usual.


## The human duration magic

I've used just one key concept in designing the human duration features: cleanliness.
> `3.44s` is more meaningful than `3.43584783784s`, and `14.1us` is much nicer than `.0000141233333s`.

So what I do is: round values to at most two decimal places (three significant digits), and find the best scale unit to represent them, minimizing resulting values smaller than `1`. The search for the best unit considers even the rounding been applied!
> `0.000999999` does not end up as `999.99us` (truncate) nor `1000.0us` (bad unit), but is auto-upgraded to the next unit `1.0ms`!

The `duration_human` units change seamlessly from nanoseconds to hours.
  - values smaller than 60 seconds are always rendered as "num.D[D]unit", with one or two decimals;
  - from 1 minute onward it changes to "H:MM:SS".

It feels much more humane, humm? ;)

Some examples:

| duration (float seconds) | duration_human |
|:------------------------:|:--------------:|
|       .00000000185       |    '1.85ns'    |
|      .000000999996       |    '1.00us'    |
|          .00001          |    '10.0us'    |
|         .0000156         |    '15.6us'    |
|           .01            |    '10.0ms'    |
|      .0141233333333      |    '14.1ms'    |
|         .1099999         |    '110ms'     |
|         .1599999         |    '160ms'     |
|          .8015           |    '802ms'     |
|         3.434999         |    '3.43s'     |
|          59.999          |   '0:01:00'    |
|           68.5           |   '0:01:08'    |
|         125.825          |   '0:02:05'    |
|         4488.395         |   '1:14:48'    |


## The human throughput magic

I've made the `throughput_human` with a similar logic. It is funny how much trickier "throughput" is to the human brain!
> If something took `1165263 seconds` to handle `123 items`, how fast did it go? It's not obvious...

It doesn't help even if we divide the duration by the number of items, `9473 seconds/item`, which still does not mean much. How fast was that? We can't say.
<br>How many items did we do per time unit?
> Oh, we just need to invert it, so `0,000105555569858 items/second`, there it is! 😂

To make some sense of it we need to multiply that by 3600 (seconds in an hour) to get `0.38/h`, which is much better, and again by 24 (hours in a day) to finally get `9.12/d`!! Now we know how fast that process was! \o/ As you see, it's not easy at all.

The `throughput_human` unit changes seamlessly from per-second, per-minute, per-hour, and per-day.
<br>It also automatically inserts SI-prefixes, like k, M, and G. 👍

| duration (float seconds) | number of elements | throughput_human |
|:------------------------:|:------------------:|:----------------:|
|           1\.            |         10         |     '10.0/s'     |
|           1\.            |        2500        |    '2.50k/s'     |
|           1\.            |      1825000       |    '1.82M/s'     |
|           2\.            |         1          |     '30.0/m'     |
|           2\.            |         10         |     '5.00/s'     |
|    1.981981981981982     |         11         |     '5.55/s'     |
|          100\.           |         10         |     '6.00/m'     |
|          1600\.          |         3          |     '6.75/h'     |
|           .99            |         1          |     '1.01/s'     |
|        1165263\.         |        123         |     '9.12/d'     |


## Changelog highlights:
- 3.2.0: both durations and throughputs now use 3 significant digits; throughputs now include SI-prefixes
- 3.1.1: make `duration_human()` and `throughput_human()` available for external use
- 3.1.0: include support for parameters in callable mode; official support for python 3.8, 3.9 and 3.10
- 3.0.0: greatly improved the counter/throughput mode, with a single argument and working in real time
- 2.0.0: feature complete, addition of callable and throughput modes
- 1.0.0: first public release, context manager mode


## License
This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.


---
Maintaining an open source project is hard and time-consuming, and I've put much ❤️ and effort into this.

If you've appreciated my work, you can back me up with a donation! Thank you 😊

[<img align="right" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" width="217px" height="51x">](https://www.buymeacoffee.com/rsalmei)
[<img align="right" alt="Donate with PayPal button" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif">](https://www.paypal.com/donate?business=6SWSHEB5ZNS5N&no_recurring=0&item_name=I%27m+the+author+of+alive-progress%2C+clearly+and+about-time.+Thank+you+for+appreciating+my+work%21&currency_code=USD)

---
