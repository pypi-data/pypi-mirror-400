"""Shared base classes for resources."""

from typing import Any


class BaseResource:
    def __init__(self, transport: Any):
        self._transport = transport


class AsyncBaseResource:
    def __init__(self, transport: Any):
        self._transport = transport
