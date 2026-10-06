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


def unpack_planar(data: bytes, width: int, height: int, planes: int) -> tuple[int, ...]:
    stride = row_bytes(width)
    expected = stride * height * planes
    if len(data) != expected:
        raise ValueError("planar data size does not match geometry")
    pixels = [0] * (width * height)
    offset = 0
    for y in range(height):
        for plane in range(planes):
            row = data[offset:offset + stride]
            offset += stride
            for x in range(width):
                if row[x // 8] & (1 << (7 - (x % 8))):
                    pixels[y * width + x] |= 1 << plane
    return tuple(pixels)


def decode_ilbm(data: bytes) -> IndexedBitmap:
    if data[:4] != b"FORM" or data[8:12] != b"ILBM":
        raise ValueError("not an ILBM FORM")
    pos = 12
    bmhd = cmap = body = None
    while pos + 8 <= len(data):
        chunk_id = data[pos:pos + 4]
        size = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        payload = data[pos + 8:pos + 8 + size]
        pos += 8 + size + (size & 1)
        if chunk_id == b"BMHD":
            bmhd = payload
        elif chunk_id == b"CMAP":
            cmap = payload
        elif chunk_id == b"BODY":
            body = payload
    if bmhd is None or cmap is None or body is None:
        raise ValueError("ILBM requires BMHD, CMAP and BODY")
    width, height, _, _, planes, _, compression, _, _, _, _, _, _ = struct.unpack(
        ">HHhhBBBBHBBhh", bmhd
    )
    if compression != 0:
        raise ValueError("compressed ILBM decoding not implemented yet")
    palette = tuple(tuple(cmap[i:i + 3]) for i in range(0, len(cmap), 3))
    pixels = unpack_planar(body, width, height, planes)
    return IndexedBitmap(width, height, pixels, palette)
