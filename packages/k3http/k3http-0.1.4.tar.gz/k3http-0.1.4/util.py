#!/usr/bin/env python3
# coding: utf-8


def headers_add_host(headers, address):
    """
    If there is no Host field in the headers, insert the address as a Host into the headers.

    :param headers: a 'dict'(header name, header value) of http request headers
    :param address: a string represents a domain name
    :return: headers after adding
    """

    headers.setdefault("Host", address)

    return headers


def request_add_host(request, address):
    """
    If the request has no headers field, or request['headers'] does not have a Host field, then add address to Host.

    :param request: a dict(request key, request name) of http request
    :param address: a string represents a domain name
    :return: request after adding
    """

    request.setdefault("headers", {})
    request["headers"].setdefault("Host", address)

    return request
