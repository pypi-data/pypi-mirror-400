"""Miscellaneous functions (https://mariadb.com/kb/en/miscellaneous-functions/)."""

from sqlfactory.func.base import Function
from sqlfactory.statement import Statement


class GetLock(Function):
    """Tries to obtain a lock with a name."""

    def __init__(self, name: str | Statement, timeout: int | Statement) -> None:
        super().__init__("GET_LOCK", name, timeout)


class Inet6Aton(Function):
    """Converts an IPv6 address from its string representation to a binary string."""

    def __init__(self, ip: str | Statement) -> None:
        super().__init__("INET6_ATON", ip)


class Inet6Ntoa(Function):
    """Converts an IPv6 address from its binary string representation to a string."""

    def __init__(self, ip: str | Statement) -> None:
        super().__init__("INET6_NTOA", ip)


class InetAton(Function):
    """Converts an IPv4 address from its string representation to a number."""

    def __init__(self, ip: str | Statement) -> None:
        super().__init__("INET_ATON", ip)


class InetNtoa(Function):
    """Converts an IP number to a string representation."""

    def __init__(self, ip: int | Statement) -> None:
        super().__init__("INET_NTOA", ip)


class IsFreeLock(Function):
    """Checks whether a named lock is free."""

    def __init__(self, name: str | Statement) -> None:
        super().__init__("IS_FREE_LOCK", name)


class IsIpv4(Function):
    """Checks whether a string is an IPv4 address."""

    def __init__(self, ip: str | Statement) -> None:
        super().__init__("IS_IPV4", ip)


class IsIpv4Compat(Function):
    """Checks whether IPv6 address is a valid IPv4-compatible address."""

    def __init__(self, ip: str | Statement) -> None:
        super().__init__("IS_IPV4_COMPAT", ip)


class IsIpv4Mapped(Function):
    """Checks whether IPv6 is an IPv4-mapped address."""

    def __init__(self, ip: str) -> None:
        super().__init__("IS_IPV4_MAPPED", ip)


class IsIpv6(Function):
    """Checks whether a string is an IPv6 address."""

    def __init__(self, ip: str | Statement) -> None:
        super().__init__("IS_IPV6", ip)


class IsUsedLock(Function):
    """Checks whether a named lock is in use."""

    def __init__(self, name: str | Statement) -> None:
        super().__init__("IS_USED_LOCK", name)


class MasterGtidWait(Function):
    """Waits until the slave reaches a specified GTID position."""

    def __init__(self, gtid_set: str | Statement, timeout: int | Statement | None = None) -> None:
        if timeout is not None:
            super().__init__("MASTER_GTID_WAIT", gtid_set, timeout)
        else:
            super().__init__("MASTER_GTID_WAIT", gtid_set)


class MasterPosWait(Function):
    """Waits until the slave reaches a specified binary log position."""

    def __init__(self, log_file: str | Statement, log_pos: int | Statement, timeout: int | Statement | None = None) -> None:
        if timeout is not None:
            super().__init__("MASTER_POS_WAIT", log_file, log_pos, timeout)
        else:
            super().__init__("MASTER_POS_WAIT", log_file, log_pos)


class ReleaseAllLocks(Function):
    """Releases all named locks."""

    def __init__(self) -> None:
        super().__init__("RELEASE_ALL_LOCKS")


class ReleaseLock(Function):
    """Releases a named lock."""

    def __init__(self, name: str | Statement) -> None:
        super().__init__("RELEASE_LOCK", name)


class Sleep(Function):
    """Sleeps for a specified number of seconds."""

    def __init__(self, seconds: int | Statement) -> None:
        super().__init__("SLEEP", seconds)


class SysGuid(Function):
    """Returns a globally unique identifier."""

    def __init__(self) -> None:
        super().__init__("SYS_GUID")


class Uuid(Function):
    """Returns a universally unique identifier."""

    def __init__(self) -> None:
        super().__init__("UUID")


class UuidShort(Function):
    """Returns a short universally unique identifier."""

    def __init__(self) -> None:
        super().__init__("UUID_SHORT")
