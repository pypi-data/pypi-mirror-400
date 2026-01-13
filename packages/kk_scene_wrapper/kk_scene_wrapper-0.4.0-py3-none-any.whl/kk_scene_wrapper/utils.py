import re
from typing import Generator, Iterable, Tuple


def int_to_bytes(number: int) -> bytes:
    # Calculate the minimum number of bytes required to represent the integer
    min_bytes = (number.bit_length() + 7) // 8
    # Convert the integer to a big-endian byte string of the minimum length
    return number.to_bytes(min_bytes, byteorder="big")


def flag_to_int_array(flag: bytes) -> Tuple[int, int]:
    return int.from_bytes(flag[0:1], byteorder="big"), int.from_bytes(
        flag[1:], byteorder="big"
    )


def sfx_terms() -> "Generator[bytes]":
    for term in ("sound", "sounds", "audio", "voice", "voices", "moan"):
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")
    for term in ["3DSE"]:
        yield term.encode("utf-8")

    yield "piston".encode("utf-8")

    yield rb"\(S\)\s{0,1}\w{2,}"
    yield rb"name=\"\(S\).+\""
    yield rb'name="[^"]*moan[^"]*"'
    yield rb'name="[^"]*piston[^"]*"'
    yield rb"org\.fox\.thebirdofhermes"


def sfx_extra_terms() -> "Generator[bytes]":
    for term in ["sfx"]:
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")
    for term in ("SE", "VA"):
        yield term.encode("utf-8")


def animation_terms() -> "Generator[bytes]":
    for term in ("animation", "motion", "move", "armature"):
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")


def body_terms() -> "Generator[bytes]":
    for term in (
        "body",
        "hips",
        "waist",
        "chest",
        "thigh",
        "head",
        "neck",
        "shoulder",
        "hand",
        "finger",
        "knee",
        "foot",
        "elbow",
    ):
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")


def body_extra_terms() -> "Generator[bytes]":
    for term in ("arm", "leg"):
        yield term.encode("utf-8")
        yield term.capitalize().encode("utf-8")
        yield term.upper().encode("utf-8")


def make_terms_regex(terms: "Iterable[bytes]") -> "re.Pattern":
    # Combine terms and custom patterns into a single regex pattern
    all_patterns = []
    for term in terms:
        if b"\\" in term:  # If the term contains a backslash, treat it as a regex pattern
            all_patterns.append(term)
        else:  # Otherwise, escape the term
            all_patterns.append(re.escape(term))
    # For a term to be considered "found" it must be preceded by 2, and followed by 1, non-word characters (except .) or spaces
    return re.compile(
        rb"(?<![\[{(\w._:;'\"?+=-]{2})("
        + b"|".join(all_patterns)
        + rb")(?![\w._:;'\"?+=)}\]-])",
    )
