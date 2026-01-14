# hydra_router/utils/HydraMsg.py
#
#   Hydra Router
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2025-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/hydra_router
#    Website: https://hydra-router.readthedocs.io/en/latest
#    License: GPL 3.0

import uuid
from typing import Optional


class HydraMsg:
    """
    Structured message class for HydraRouter communication protocol.

    HydraMsg provides a standardized message format for communication between
    HydraClient and HydraServer instances. Each message contains sender/target
    identification, method specification, and optional payload data.
    """

    def __init__(
        self,
        sender: Optional[str] = None,
        target: Optional[str] = None,
        method: Optional[str] = None,
        payload: Optional[str] = None,
    ) -> None:
        """
        Initialize a new HydraMsg instance.

        Args:
            sender (Optional[str]): Identifier of the message sender
            target (Optional[str]): Identifier of the intended message recipient
            method (Optional[str]): Method or action to be performed
            payload (Optional[str]): Message data or parameters as JSON string

        Returns:
            None
        """
        self._sender = sender
        self._target = target
        self._method = method
        self._payload = payload

        self._id = uuid.uuid4()

    def sender(self, sender=None):
        if sender is not None:
            self._sender = sender
        return self._sender

    def target(self, target=None):
        if target is not None:
            self._target = target
        return self._target

    def method(self, method=None):
        if method is not None:
            self._method = method
        return self._method

    def payload(self, payload=None):
        if payload is not None:
            self._payload = payload
        return self._payload
