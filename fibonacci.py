import os
from flask import Flask
from flask import request
import redis


REDIS_HOST = os.environ.get("REDIS_HOST", 'redis')
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

app = Flask(__name__)
class location():
    main  = '/fibonacci'         # точка входа
    clear = main + '/clear'      # точка для сброс кэша

redis_prefix = 'fib_'            # префикс для сохранения значений в redis
MAX_N = 500                      # ограничение из-за рекурсии

page = """
<html>
<head>
   <title>Fibonacci calculation</title>
</head>
<body>
  Choose variant of calculation:<br>
  <a href="{location.main}?n=1">fibonacci(1)</a><br>
  <a href="{location.main}?n=2">fibonacci(2)</a><br>
  <a href="{location.main}?n=3">fibonacci(3)</a><br>
  <a href="{location.main}?n=5">fibonacci(5)</a><br>
  <a href="{location.main}?n=10">fibonacci(10)</a><br>
  <a href="{location.main}?n=50">fibonacci(50)</a><br>
  <a href="{location.main}?n=100">fibonacci(100)</a><br>
  <a href="{location.main}?n=300">fibonacci(300)</a><br>
  <hr>
  ... or type custom ({maximum} maximum due to recursion restrictions):<br>
  <form method="get" action="{location.main}">
    <input type="number" name="n" min="1" max="{maximum}" value="{value}"><br>
    <button>Submit</button>
  </form>
  <form method="get" action="{location.clear}">
    <button>Clear cache</button>
  </form>
  <hr>
{result}
</body>
</html>
"""


def fib(n, cache, calcs=0):
    """
    рекурсивно считает числа Фибоначи
    _n_ - номер числа,
    _cache_ - объект кэша,
    _calcs_ - сколько раз пришлось считать, т.к. числа не было в кэше
    """
    if n<3:
        return 1, calcs
    else:
        found = cache.get(f'{redis_prefix}{n}')
        if found:
            return int(found), calcs
        else:
            fib_1, calcs = fib(n-1, cache, calcs)
            fib_2, calcs = fib(n-2, cache, calcs)
            new_fib = fib_1 + fib_2
            cache.set(f'{redis_prefix}{n}', new_fib)
            return int(new_fib), calcs + 1


def fib_calc(n):
    try:
        cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        res, calc = fib(n, cache)
    except Exception as e:
        return str(e)
    else:
        return f'fibonacci({n}) = {res}<br>calcs without cache: {calc}'


def clear_cache():
    try:
        cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        cache.flushdb()
    except Exception as e:
        return str(e)
    else:
        return None


@app.route(location.main)
def fib_html():
    n = request.args.get('n')
    if not n:
        return page.format(location=location, maximum=MAX_N, value=MAX_N,
                result='')
    else:
        try:
            n = int(n)
        except ValueError:
            return page.format(location=location, maximum=MAX_N, value=MAX_N,
                    result='Incorrect number')
        else:
            if n<1 or n>1000:
                return page.format(location=location, maximum=MAX_N, value=MAX_N,
                        result='Number is out of range')

    return page.format(location=location, maximum=MAX_N, value=n,
            result=fib_calc(n))


@app.route(location.clear)
def clear_html():
    error = clear_cache()
    if not error:
        return page.format(location=location, maximum=MAX_N, value=MAX_N,
                result='Cache cleared')
    else:
        return page.format(location=location, maximum=MAX_N, value=MAX_N,
                result=error)


if __name__ == '__main__':
    app.run()
