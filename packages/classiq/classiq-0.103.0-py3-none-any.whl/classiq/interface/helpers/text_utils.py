from collections.abc import Sequence, Sized


def s(items: Sized | int) -> str:
    if isinstance(items, Sized):
        items = len(items)
    return "" if items == 1 else "s"


def are(items: Sized) -> str:
    return "is" if len(items) == 1 else "are"


def were(items: Sized) -> str:
    return "was" if len(items) == 1 else "were"


def an(items: Sized) -> str:
    return "an " if len(items) == 1 else ""


def they(items: Sized) -> str:
    return "it" if len(items) == 1 else "they"


def conj(items: Sized) -> str:
    return "s" if len(items) == 1 else ""


def readable_list(items: Sequence, quote: bool = False) -> str:
    if quote:
        items = [repr(str(item)) for item in items]
    if len(items) == 1:
        return str(items[0])
    return f"{', '.join(items[:-1])}{',' if len(items) > 2 else ''} and {items[-1]}"
