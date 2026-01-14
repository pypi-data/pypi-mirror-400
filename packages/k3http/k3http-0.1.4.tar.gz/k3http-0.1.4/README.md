# k3http

[![Action-CI](https://github.com/pykit3/k3http/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3http/actions/workflows/python-package.yml)
[![Build Status](https://travis-ci.com/pykit3/k3http.svg?branch=master)](https://travis-ci.com/pykit3/k3http)
[![Documentation Status](https://readthedocs.org/projects/k3http/badge/?version=stable)](https://k3http.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3http)](https://pypi.org/project/k3http)

We find that 'httplib' must work in blocking mode and it can not have a timeout when recving response.

k3http is a component of [pykit3] project: a python3 toolkit set.


HTTP/1.1 client

Use this module, we can set timeout, if timeout raise a 'socket.timeout'.



# Install

```
pip install k3http
```

# Synopsis

```python

import k3http
import urllib
import socket

headers = {
    'Host': '127.0.0.1',
    'Accept-Language': 'en, mi',
}

try:
    h = k3http.Client('127.0.0.1', 80)

    # send http reqeust without body
    # read response status line
    # read response headers
    h.request('/test.txt', method='GET', headers=headers)

    status = h.status
    # response code return from http server, type is int
    # 200
    # 302
    # 404
    # ...

    res_headers = h.headers
    # response headers except status line
    # res_headers = {
    #   'Content-Type': 'text/html;charset=utf-8',
    #   'Content-Length': 1024,
    #   ...
    # }

    # get response body
    print(h.read_body(None))
except (socket.error, k3http.HttpError) as e:
    print(repr(e))



content = urllib.urlencode({'f': 'foo', 'b': 'bar'})
headers = {
    'Host': 'www.example.com',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Content-Length': len(content),
}

try:
    h = k3http.Client('127.0.0.1', 80)

    # send http reqeust
    h.send_request('http://www.example.com', method='POST', headers=headers)

    # send http request body
    h.send_body(content)

    # read response status line and headers
    status, headers = h.read_response()

    # read response body
    print(h.read_body(None))
except (socket.error, k3http.HttpError) as e:
    print(repr(e))

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3