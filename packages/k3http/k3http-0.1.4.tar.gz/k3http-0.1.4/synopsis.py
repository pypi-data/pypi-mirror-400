import k3http
import urllib
import socket

headers = {
    "Host": "127.0.0.1",
    "Accept-Language": "en, mi",
}

try:
    h = k3http.Client("127.0.0.1", 80)

    # send http reqeust without body
    # read response status line
    # read response headers
    h.request("/test.txt", method="GET", headers=headers)

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


content = urllib.urlencode({"f": "foo", "b": "bar"})
headers = {
    "Host": "www.example.com",
    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    "Content-Length": len(content),
}

try:
    h = k3http.Client("127.0.0.1", 80)

    # send http reqeust
    h.send_request("http://www.example.com", method="POST", headers=headers)

    # send http request body
    h.send_body(content)

    # read response status line and headers
    status, headers = h.read_response()

    # read response body
    print(h.read_body(None))
except (socket.error, k3http.HttpError) as e:
    print(repr(e))
