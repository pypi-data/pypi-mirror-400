from __future__ import annotations
import collections.abc
import datetime
import typing
__all__: list[str] = ['SpwRmapTCPNode', 'TargetNode', 'disable_debug', 'enable_debug', 'is_debug_enabled', 'set_debug_enabled']
class SpwRmapTCPNode:
    def __init__(self, ip_address: str, port: str) -> None:
        ...
    def connect(self, timeout: datetime.timedelta = ...) -> None:
        ...
    def read(self, target_node: TargetNode, memory_address: typing.SupportsInt, data_length: typing.SupportsInt) -> list[int]:
        ...
    def write(self, target_node: TargetNode, memory_address: typing.SupportsInt, data: collections.abc.Sequence[typing.SupportsInt]) -> None:
        ...
class TargetNode:
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, logical_address: typing.SupportsInt, target_spacewire_address: collections.abc.Sequence[typing.SupportsInt], reply_address: collections.abc.Sequence[typing.SupportsInt]) -> None:
        ...
    @property
    def logical_address(self) -> int:
        ...
    @logical_address.setter
    def logical_address(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def reply_address(self) -> list[int]:
        ...
    @reply_address.setter
    def reply_address(self, arg0: collections.abc.Sequence[typing.SupportsInt]) -> None:
        ...
    @property
    def target_spacewire_address(self) -> list[int]:
        ...
    @target_spacewire_address.setter
    def target_spacewire_address(self, arg0: collections.abc.Sequence[typing.SupportsInt]) -> None:
        ...
def disable_debug() -> None:
    """
    Disable runtime debug logging
    """
def enable_debug() -> None:
    """
    Enable runtime debug logging
    """
def is_debug_enabled() -> bool:
    """
    Check if runtime debug logging is enabled
    """
def set_debug_enabled(enabled: bool) -> None:
    """
    Enable or disable runtime debug logging
    """
