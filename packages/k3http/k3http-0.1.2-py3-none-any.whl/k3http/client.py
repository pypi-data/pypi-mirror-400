#!/usr/bin/env python3
# coding: utf-8

import errno
import logging
import select
import socket

import k3stopwatch

logger = logging.getLogger(__name__)


class HttpError(Exception):
    # The base class of the other exceptions in this module. It is a subclass of 'Exception'.
    pass


class LineTooLongError(HttpError):
    # A subclass of 'HttpError'. Raise if length of line is greater or equal than 65536 when read response status line, headers and get length of chunked block.
    pass


class ChunkedSizeError(HttpError):
    # A subclass of 'HttpError'. Raise if failed to get length of chunked block.
    pass


class NotConnectedError(HttpError):
    # A subclass of 'HttpError'. Raise if send data without connecting to server.
    pass


class ResponseNotReadyError(HttpError):
    # A subclass of 'HttpError'. Raise if response is unavailable.
    pass


class HeadersError(HttpError):
    # A subclass of 'HttpError'. Raise if failed to read response headers.
    pass


class BadStatusLineError(HttpError):
    # A subclass of 'HttpError'. Raise if failed to read response status line.
    pass


MAX_LINE_LENGTH = 65536
LINE_RECV_LENGTH = 1024 * 4


class Client(object):
    """
    HTTP client class

    :param host: server address, ip or domain, type is 'str'
    :param port: server port, type is 'int'
    :param timeout: set a timeout on blocking socket operations, unit is second, default is 60. The value argument can be a nonnegative float expressing seconds, or 'None'. if 'None', it is equivalent to 'socket.setblocking(1)'. if '0.0', it is equivalent to 'socket.setblocking(0)'.
    :param stopwatch_kwargs: is an dictionary used as keyword arguments when initializing stopwatch instance.
    :param https_context: a 'ssl.SSLContext' instance describing the various SSL options. Defaults to 'None'.
    """

    stopwatch_root_name = "k3http.Client"

    def __init__(self, host, port, timeout=60, stopwatch_kwargs=None, https_context=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.chunked = False
        self.chunk_left = None
        self.content_length = None
        self.has_read = 0
        self.status = None
        self.headers = {}
        self.recv_iter = None
        self.https_context = https_context
        self.request_chunked_encoded = False

        self.stopwatch_kwargs = {
            # min_tracing_milliseconds=0 to trace all events. StopWatch trace
            # only event those cost less than min_tracing_milliseconds
            "min_tracing_milliseconds": 0,
        }

        if stopwatch_kwargs is not None:
            self.stopwatch_kwargs.update(stopwatch_kwargs)

        self.stopwatch = k3stopwatch.StopWatch(**self.stopwatch_kwargs)
        self.stopwatch_started = False

    def get_trace_str(self):
        """

        :return: a string shows time spent on each phase of a request. The following fields would presents in it:

        conn: 0.000001 -;
        send_header: 0.000000 -;
        recv_status: 0.000000 -;
        recv_header: 0.000000 -;
        recv_body: 0.000000 -;
        recv_body: 0.000000 -;
        exception: 0.000000 -;
        pykit.http.Client: 0.000002 Exception:ValueError

        The numbers are time in second.
        There might be less fields in the result, if request failed.
        It is also possible some of the above fields appear more than once.
        For example if a server responds a '100-Continue' status line and a '200-OK' status line, there would be two 'recv_status' fields.
        If the caller calls 'http.Client.read_body' more than one time, there would be more than one 'recv_body' fields.
        """

        tr = self.get_trace()
        rst = []
        for t in tr:
            ent = "{name}: {time:.6f} {annotation}".format(
                name=t["name"], time=float("{:.6f}".format(t["time"])), annotation=",".join(t["annotation"]) or "-"
            )
            rst.append(ent)

        return "; ".join(rst)

    def get_trace(self):
        sw = self.get_and_end_stopwatch()
        rst = []
        for t in sw.get_last_trace_report():
            ent = dict(
                name=t.name,
                time=t.end_time - t.start_time,
                annotation=[self._human_annotation(an) for an in t.trace_annotations],
            )

            rst.append(ent)

        return rst

    def _human_annotation(self, annotation):
        an = annotation
        return "{key}:{value}".format(key=an.key, value=an.value)

    def get_and_end_stopwatch(self):
        """stopwatch must be stopped before it can be read"""
        self.end_stopwatch()
        return self.stopwatch

    def end_stopwatch(self):
        if self.stopwatch_started:
            self.stopwatch.end(self.stopwatch_root_name)
            self.stopwatch_started = False

    def start_stopwatch(self):
        if self.stopwatch_started:
            return

        self.stopwatch.start(self.stopwatch_root_name)
        self.stopwatch_started = True

    def __del__(self):
        self._close()

    def request(self, uri, method="GET", headers=None):
        """
        Send http request without body and read response status line, headers.
        After it, get response status code with 'http.Client.status',
        get response headers with 'http.Client.headers'.

        :param uri: specifies the object being requested
        :param method: specifies an HTTP request method
        :param headers: a 'dict'(header name, header value) of http request headers
        :return: nothing
        """

        self.send_request(uri, method=method, headers=headers)

        self.read_response()

    def send_request(self, uri, method="GET", headers=None):
        """
        Connect to server and send http request.

        :param uri: specifies the object being requested
        :param method: specifies an HTTP request method
        :param headers: a 'dict'(header name, header value) of http request headers
        :return: nothing
        """

        self._reset_request()
        self.method = method

        self.start_stopwatch()

        with self.stopwatch.timer("conn"):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            if self.https_context is not None:
                self.sock = self.https_context.wrap_socket(self.sock, server_hostname=self.host)

        bufs = [
            "{method} {uri} HTTP/1.1".format(method=method, uri=uri),
        ]

        headers = headers or {}
        if "Host" not in headers and "host" not in headers:
            headers["Host"] = self.host

        if headers.get("Transfer-Encoding") == "chunked":
            self.request_chunked_encoded = True

        for k, v in headers.items():
            bufs.append("%s: %s" % (k, v))

        bufs.extend(["", ""])

        with self.stopwatch.timer("send_header"):
            self.sock.sendall(("\r\n".join(bufs)).encode("utf-8"))

    def send_body(self, body):
        """
        Send http request body. It should be a 'str' of data to send after the headers are finished

        :param body: a 'str' of http request body.
        :return: nothing
        """

        if self.sock is None:
            raise NotConnectedError("socket object is None")

        with self.stopwatch.timer("send_body"):
            if self.request_chunked_encoded:
                body = "{0:x}\r\n{1}\r\n".format(len(body), body)

            self.sock.sendall(body.encode("utf-8"))

    def read_status(self, skip_100=True):
        """
        Read response status line and return the status code. Cache the response status code with http.Client.status

        :param skip_100: nothing
        :return: response status code.
        """

        if self.status is not None or self.sock is None:
            raise ResponseNotReadyError("response is unavailable")

        if self.recv_iter is None:
            self.recv_iter = _recv_loop(self.sock, self.timeout)
            next(self.recv_iter)

        # read until we get a non-100 response
        while True:
            status = self._get_response_status()
            if status >= 200:
                break

            # skip the header from the 100 response
            with self.stopwatch.timer("recv_skip_header"):
                while True:
                    skip = self._readline()
                    if skip.strip() == "":
                        break

            if skip_100 is False:
                return status

        self.status = status
        return status

    def read_headers(self):
        with self.stopwatch.timer("recv_header"):
            while True:
                line = self._readline()
                if line == "":
                    break

                kv = line.strip().split(":", 1)
                if len(kv) < 2:
                    raise HeadersError("invalid headers param line:%s" % (line))
                self.headers[kv[0].lower()] = kv[1].strip()

        if self.status in (204, 304) or self.method == "HEAD":
            self.content_length = 0
            return self.headers

        code = self.headers.get("transfer-encoding", "")
        if code.lower() == "chunked":
            self.chunked = True
            return self.headers

        length = self.headers.get("content-length", "0")

        try:
            self.content_length = int(length)
        except ValueError as e:
            logger.error(repr(e) + " while get content-length length:{l}".format(l=length))
            raise HeadersError("invalid content-length")

        return self.headers

    def read_response(self):
        """
        Read response status line, headers and return them.
        Cache the status code with 'http.Client.status' Cache the response headers with 'http.Client.headers'

        :return: two values,

                status: response status code, type is int

                headers: response headers, it is a dict(header name , header value).
        """

        self.read_status()
        self.read_headers()

        return self.status, self.headers

    def read_body(self, size):
        """
        Read and return the response body.

        :param size: need read size, if greater than left size use the min one, if 'None' read left unread body.
        :return: the response body.
        """

        with self.stopwatch.timer("recv_body"):
            return self._read_body(size)

    def readlines(self, delimiter=None):
        """
        Read and yield one line in response body each time.

        :param delimiter: specify the delimiter between each line, defalut supporting '\n'.
        :return: a generator yileding one line including delimiter in response body each time.
        """

        if delimiter is None:
            delimiter = "\n"

        buf = ""
        while True:
            tmp = self._read_body(MAX_LINE_LENGTH)

            if tmp == "":
                if buf != "":
                    yield buf
                break

            buf += tmp

            lines = buf.split(delimiter)
            buf = lines.pop()

            for line in lines:
                yield line + delimiter

    def _read_body(self, size):
        if size is not None and size <= 0:
            return ""

        if self.chunked:
            buf = self._read_chunked(size)
            self.has_read += len(buf)
            return buf

        if size is None:
            size = self.content_length - self.has_read
        else:
            size = min(size, self.content_length - self.has_read)

        if size <= 0:
            return ""

        buf = self._read(size)
        self.has_read += size

        return buf

    def _close(self):
        if self.recv_iter is not None:
            try:
                self.recv_iter.close()
            except Exception as e:
                logger.exception(repr(e) + " while close recv_iter")

        self.recv_iter = None

        if self.sock is not None:
            try:
                self.sock.close()
            except Exception as e:
                logger.exception(repr(e) + " while close sock")

        self.sock = None

    def _reset_request(self):
        self._close()
        self.chunked = False
        self.chunk_left = None
        self.content_length = None
        self.has_read = 0
        self.status = None
        self.headers = {}
        self.request_chunked_encoded = False

    def _read(self, size):
        return self.recv_iter.send(("block", size))

    def _readline(self):
        return self.recv_iter.send(("line", None))

    def _get_response_status(self):
        with self.stopwatch.timer("recv_status"):
            line = self._readline()

        vals = line.split(None, 2)
        if len(vals) < 2:
            raise BadStatusLineError("invalid status line:{l}".format(l=line))

        ver, status = vals[0], vals[1]

        try:
            status = int(status)
        except ValueError as e:
            logger.error(repr(e) + " while get response status")
            raise BadStatusLineError("status is not int:{l}".format(l=line))

        if not ver.startswith("HTTP/") or status < 100 or status > 999:
            raise BadStatusLineError("invalid status line:{l}".format(l=line))

        return status

    def _get_chunk_size(self):
        line = self._readline()

        i = line.find(";")
        if i >= 0:
            # strip chunk-extensions
            line = line[:i]

        try:
            chunk_size = int(line, 16)
        except ValueError as e:
            logger.error(repr(e) + " while get chunk size line:{l}".format(l=line))
            raise ChunkedSizeError("invalid chunk size")

        return chunk_size

    def _read_chunked(self, size):
        buf = []

        if self.chunk_left == 0:
            return ""

        while size is None or size > 0:
            if self.chunk_left is None:
                self.chunk_left = self._get_chunk_size()

            if self.chunk_left == 0:
                break

            if size is not None:
                read_size = min(size, self.chunk_left)
                size -= read_size
            else:
                read_size = self.chunk_left

            buf.append(self._read(read_size))
            self.chunk_left -= read_size

            if self.chunk_left == 0:
                self._read(len("\r\n"))
                self.chunk_left = None

        if self.chunk_left == 0:
            while True:
                line = self._readline()
                if line == "":
                    break

        return "".join(buf)

    def set_timeout(self, timeout):
        self.timeout = timeout

        if self.sock is not None:
            self.sock.settimeout(timeout)


def _recv_loop(sock, timeout):
    bufs = [""]
    mode, size = yield

    while True:
        if mode == "line":
            buf = bufs[0]
            if "\r\n" in buf:
                rst, buf = buf.split("\r\n", 1)
                bufs[0] = buf
                mode, size = yield rst
                continue
            else:
                if len(buf) >= MAX_LINE_LENGTH:
                    raise LineTooLongError("line length greater than max_len:{l}".format(l=len(buf)))
                else:
                    buf += _recv(sock, timeout, LINE_RECV_LENGTH)
                    bufs[0] = buf
                    continue
        else:
            total = len(bufs[0])
            while total < size:
                bufs.append(_recv(sock, timeout, size - total))
                total += len(bufs[-1])

            rst = "".join(bufs)
            if size < len(rst):
                bufs = [rst[size:]]
                rst = rst[:size]
            else:
                bufs = [""]
            mode, size = yield rst


def _recv(sock, timeout, size):
    buf = ""
    for _ in range(2):
        try:
            buf = (sock.recv(size)).decode("utf-8")
            break
        except socket.error as e:
            if len(e.args) <= 0 or e.args[0] != errno.EAGAIN:
                raise

            evin, evout, everr = select.select([sock.fileno()], [], [], timeout)

            if len(evin) <= 0:
                raise socket.timeout("{second}s timeout while recv".format(second=timeout))

    if len(buf) <= 0:
        raise socket.error("got empty when recv {l} bytes".format(l=size))

    return buf
