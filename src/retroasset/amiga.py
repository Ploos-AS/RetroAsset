import struct

from .indexed import IndexedBitmap


def row_bytes(width: int) -> int:
    """ILBM rows are word aligned."""
    return ((width + 15) // 16) * 2


def pack_planar(bitmap: IndexedBitmap) -> bytes:
    stride = row_bytes(bitmap.width)
    out = bytearray()

    # ILBM BODY is interleaved by row: plane 0 row, plane 1 row, ...
    for y in range(bitmap.height):
        for plane in range(bitmap.planes):
            row = bytearray(stride)
            for x in range(bitmap.width):
                pixel = bitmap.pixels[y * bitmap.width + x]
                if pixel & (1 << plane):
                    row[x // 8] |= 1 << (7 - (x % 8))
            out.extend(row)
    return bytes(out)


def _chunk(chunk_id: bytes, payload: bytes) -> bytes:
    if len(chunk_id) != 4:
        raise ValueError("IFF chunk id must be four bytes")
    pad = b"\0" if len(payload) & 1 else b""
    return chunk_id + struct.pack(">I", len(payload)) + payload + pad


def encode_ilbm(bitmap: IndexedBitmap) -> bytes:
    if bitmap.planes > 8:
        raise ValueError("M0.2 ILBM exporter supports at most 8 bitplanes")

    # BMHD: w,h,x,y,nPlanes,masking,compression,pad1,transparent,
    #       xAspect,yAspect,pageWidth,pageHeight
    bmhd = struct.pack(
        ">HHhhBBBBHBBhh",
        bitmap.width, bitmap.height, 0, 0,
        bitmap.planes, 0, 0, 0, 0,
        10, 11, bitmap.width, bitmap.height,
    )
    cmap = bytes(channel for rgb in bitmap.palette for channel in rgb)
    body = pack_planar(bitmap)
    contents = b"ILBM" + _chunk(b"BMHD", bmhd) + _chunk(b"CMAP", cmap) + _chunk(b"BODY", body)
    return b"FORM" + struct.pack(">I", len(contents)) + contents
