from __future__ import annotations

from platform import machine, system

from utilities.iterables import OneEmptyError, one

SYSTEM_NAMES = {"Darwin", "Linux"}
if (SYSTEM_NAME := system()) not in SYSTEM_NAMES:
    msg = f"Invalid system name; must be in {SYSTEM_NAMES} but got {SYSTEM_NAME!r}"
    raise ValueError(msg)
MACHINE_TYPE = machine()
MACHINE_TYPE_GROUPS: set[frozenset[str]] = {
    frozenset(["amd64", "intel64", "x64", "x86_64"]),
    frozenset(["aarch64", "arm64"]),
}
try:
    MACHINE_TYPE_GROUP = one(g for g in MACHINE_TYPE_GROUPS if MACHINE_TYPE in g)
except OneEmptyError:
    msg = f"Invalid machine type; must be in {MACHINE_TYPE_GROUPS} but got {MACHINE_TYPE!r}"
    raise ValueError(msg) from None


__all__ = [
    "MACHINE_TYPE",
    "MACHINE_TYPE_GROUP",
    "MACHINE_TYPE_GROUPS",
    "SYSTEM_NAME",
    "SYSTEM_NAMES",
]
