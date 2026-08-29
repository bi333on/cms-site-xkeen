"""
Генерация favicon-иконок для сайта без внешних библиотек (чистый Python).
Создаёт: favicon.svg (уже есть), favicon-16x16.png, favicon-32x32.png,
apple-touch-icon.png, favicon.ico (16/32/48).
Запуск: python generate_favicon.py
"""
import zlib
import struct
import math
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images")

BG = (26, 26, 46, 255)        # тёмный фон #1A1A2E
STAR = (255, 107, 0, 255)     # оранжевая звезда #FF6B00


def star_points(cx, cy, r_outer, r_inner):
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def point_in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def make_raw_rgba(size):
    cx = cy = size / 2.0
    r_outer = size * 0.34
    r_inner = size * 0.14
    poly = star_points(cx, cy, r_outer, r_inner)
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter byte (None)
        for x in range(size):
            if point_in_poly(x + 0.5, y + 0.5, poly):
                raw += bytes(STAR)
            else:
                raw += bytes(BG)
    return bytes(raw)


def make_png(size):
    raw = make_raw_rgba(size)

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    idat = zlib.compress(raw, 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def make_ico(pngs):
    """pngs: список (size, png_bytes). Vista+ поддерживает PNG внутри ICO."""
    count = len(pngs)
    header = struct.pack("<HHH", 0, 1, count)
    entries = b""
    blobs = b""
    offset = 6 + 16 * count
    for size, png in pngs:
        w = size if size < 256 else 0
        entries += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(png), offset)
        blobs += png
        offset += len(png)
    return header + entries + blobs


def main():
    os.makedirs(BASE, exist_ok=True)

    png16 = make_png(16)
    png32 = make_png(32)
    png180 = make_png(180)

    with open(os.path.join(BASE, "favicon-16x16.png"), "wb") as f:
        f.write(png16)
    with open(os.path.join(BASE, "favicon-32x32.png"), "wb") as f:
        f.write(png32)
    with open(os.path.join(BASE, "apple-touch-icon.png"), "wb") as f:
        f.write(png180)

    png48 = make_png(48)
    ico = make_ico([(16, png16), (32, png32), (48, png48)])
    with open(os.path.join(BASE, "favicon.ico"), "wb") as f:
        f.write(ico)

    print("Готово: favicon-16x16.png, favicon-32x32.png, apple-touch-icon.png, favicon.ico")


if __name__ == "__main__":
    main()
