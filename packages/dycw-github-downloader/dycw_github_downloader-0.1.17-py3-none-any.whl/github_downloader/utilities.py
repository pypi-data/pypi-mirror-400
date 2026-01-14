from __future__ import annotations

from typing import assert_never

from typed_settings import Secret


def convert_token(x: str | None, /) -> Secret[str] | None:
    match x:
        case Secret():
            match x.get_secret_value():
                case None:
                    return None
                case str() as inner:
                    y = inner.strip("\n")
                    return None if y == "" else Secret(y)
                case never:
                    assert_never(never)
        case str():
            y = x.strip("\n")
            return None if y == "" else Secret(y)
        case None:
            return None
        case never:
            assert_never(never)


__all__ = ["convert_token"]
