"""
Генерация og-image.png (1200x630) для соцсетей/мессенджеров.
Чистый Python, без внешних библиотек.
Запуск: python generate_og_image.py
"""
import zlib
import struct
import math
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images")
W = 1200
H = 630

BG = (26, 26, 46)          # #1A1A2E
ORANGE = (255, 107, 0)     # #FF6B00
ORANGE_DARK = (229, 95, 0) # #E55F00


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


def point_in_circle(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2


def make_raw():
    raw = bytearray()
    # Центральная звезда
    star = star_points(W / 2, H / 2 - 20, 170, 68)
    # Кольцо (контур)
    ring_cx, ring_cy, ring_r = W / 2, H / 2 - 20, 250

    for y in range(H):
        raw.append(0)  # filter byte
        for x in range(W):
            # Верхняя и нижняя оранжевые полосы
            if y < 8 or y >= H - 8:
                raw += bytes([*ORANGE])
                continue

            # Кольцо
            d = math.sqrt((x - ring_cx) ** 2 + (y - ring_cy) ** 2)
            if ring_r - 6 <= d <= ring_r + 6:
                raw += bytes([*ORANGE])
                continue

            # Звезда
            if point_in_poly(x + 0.5, y + 0.5, star):
                raw += bytes([*ORANGE])
                continue

            # Лёгкая виньетка
            raw += bytes([*BG])
    return bytes(raw)


def make_png(w, h, raw):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)  # RGB
    idat = zlib.compress(raw, 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def main():
    os.makedirs(BASE, exist_ok=True)
    raw = make_raw()
    png = make_png(W, H, raw)
    with open(os.path.join(BASE, "og-image.png"), "wb") as f:
        f.write(png)
    print("Готово: og-image.png (1200x630)")


if __name__ == "__main__":
    main()
