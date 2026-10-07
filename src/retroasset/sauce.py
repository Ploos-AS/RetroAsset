from dataclasses import dataclass


@dataclass(frozen=True)
class Sauce:
    title: str = ""
    author: str = ""
    group: str = ""
    date: str = ""
    data_type: int = 1
    file_type: int = 1
    tinfo1: int = 0
    tinfo2: int = 0


def _field(text: str, size: int) -> bytes:
    raw = text.encode("cp437", errors="replace")[:size]
    return raw.ljust(size, b" ")


def encode_sauce(meta: Sauce, file_size: int) -> bytes:
    if file_size < 0 or file_size > 0xffffffff:
        raise ValueError("SAUCE file size out of range")
    import struct
    return (
        b"SAUCE00"
        + _field(meta.title, 35)
        + _field(meta.author, 20)
        + _field(meta.group, 20)
        + _field(meta.date, 8)
        + struct.pack("<I", file_size)
        + bytes((meta.data_type, meta.file_type))
        + struct.pack("<HHHH", meta.tinfo1, meta.tinfo2, 0, 0)
        + b"\0\0"
        + b"\0" * 22
    )


def decode_sauce(data: bytes) -> tuple[bytes, Sauce | None]:
    import struct
    if len(data) < 128 or data[-128:-121] != b"SAUCE00":
        return data, None
    rec = data[-128:]
    def txt(start, size):
        return rec[start:start + size].decode("cp437").rstrip(" \0")
    file_size = struct.unpack("<I", rec[90:94])[0]
    meta = Sauce(
        title=txt(7, 35),
        author=txt(42, 20),
        group=txt(62, 20),
        date=txt(82, 8),
        data_type=rec[94],
        file_type=rec[95],
        tinfo1=struct.unpack("<H", rec[96:98])[0],
        tinfo2=struct.unpack("<H", rec[98:100])[0],
    )
    payload = data[:min(file_size, len(data) - 128)]
    return payload, meta
