#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el icono de VectorCAD (VectorCAD.iconset + VectorCAD.icns + VectorCAD.png).

Dibuja el icono con QPainter (la única dependencia es PySide6, ya requerida por
la aplicación). En macOS convierte el .iconset a .icns con `iconutil`.

Diseño: cuerpo redondeado tipo macOS con degradado azul de plano, cuadrícula,
escuadra de dibujo, curva vectorial con tiradores y cursor de precisión.

Uso:
    python make_icon.py [directorio_salida]
"""

from __future__ import annotations

import os
import subprocess
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui  # noqa: E402

TOP = "#3b6cff"
BOTTOM = "#0a1a52"
GRID = (255, 255, 255, 22)
GRID_MAJOR = (255, 255, 255, 44)
WHITE = "#f4f7ff"
CYAN = "#5ee6ff"
ORANGE = "#ffb21f"

SIZES = [16, 32, 64, 128, 256, 512, 1024]
ICONSET = [
    ("icon_16x16.png", 16), ("icon_16x16@2x.png", 32),
    ("icon_32x32.png", 32), ("icon_32x32@2x.png", 64),
    ("icon_128x128.png", 128), ("icon_128x128@2x.png", 256),
    ("icon_256x256.png", 256), ("icon_256x256@2x.png", 512),
    ("icon_512x512.png", 512), ("icon_512x512@2x.png", 1024),
]

P = QtCore.QPointF


def draw(size: int) -> QtGui.QImage:
    img = QtGui.QImage(size, size, QtGui.QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(img)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
    p.scale(size / 1024.0, size / 1024.0)          # todo se dibuja en 1024×1024
    small = size <= 32

    body = QtCore.QRectF(100, 100, 824, 824)
    radius = 186.0

    # sombra suave (capas translúcidas desplazadas hacia abajo)
    for i in range(14, 0, -1):
        sh = QtGui.QPainterPath()
        sh.addRoundedRect(body.adjusted(-i * 0.6, i * 1.1, i * 0.6, i * 1.6),
                          radius + i, radius + i)
        p.fillPath(sh, QtGui.QColor(0, 0, 0, 7))

    path = QtGui.QPainterPath()
    path.addRoundedRect(body, radius, radius)
    grad = QtGui.QLinearGradient(body.topLeft(), body.bottomLeft())
    grad.setColorAt(0.0, QtGui.QColor(TOP))
    grad.setColorAt(1.0, QtGui.QColor(BOTTOM))
    p.fillPath(path, QtGui.QBrush(grad))

    p.save()
    p.setClipPath(path)

    # brillo superior
    gl = QtGui.QLinearGradient(P(0, 100), P(0, 520))
    gl.setColorAt(0.0, QtGui.QColor(255, 255, 255, 46))
    gl.setColorAt(1.0, QtGui.QColor(255, 255, 255, 0))
    p.fillRect(QtCore.QRectF(100, 100, 824, 420), QtGui.QBrush(gl))

    # cuadrícula de plano
    if not small:
        step = 824 / 12.0
        for i in range(1, 12):
            major = i % 4 == 0
            pen = QtGui.QPen(QtGui.QColor(*(GRID_MAJOR if major else GRID)),
                             4.5 if major else 2.5)
            p.setPen(pen)
            x = 100 + i * step
            p.drawLine(P(x, 100), P(x, 924))
            p.drawLine(P(100, x), P(924, x))

    # escuadra (triángulo rectángulo) con calado interior
    tri = QtGui.QPainterPath(P(262, 236))
    tri.lineTo(P(262, 772))
    tri.lineTo(P(798, 772))
    tri.closeSubpath()
    hole = QtGui.QPainterPath(P(352, 470))
    hole.lineTo(P(352, 682))
    hole.lineTo(P(564, 682))
    hole.closeSubpath()
    square = tri.subtracted(hole)
    p.fillPath(square, QtGui.QColor(255, 255, 255, 38))
    pen = QtGui.QPen(QtGui.QColor(WHITE), 34 if not small else 60)
    pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
    p.drawPath(tri)
    if not small:
        pen.setWidthF(16)
        p.setPen(pen)
        p.drawPath(hole)
        # marcas de regla en el cateto vertical
        pen.setWidthF(9)
        p.setPen(pen)
        for k in range(1, 9):
            y = 772 - k * 56
            if y < 300:
                break
            L = 44 if k % 2 == 0 else 26
            p.drawLine(P(262, y), P(262 + L, y))

    # curva vectorial con tiradores
    a, c1, c2, b = P(196, 600), P(360, 196), P(612, 846), P(842, 330)
    curve = QtGui.QPainterPath(a)
    curve.cubicTo(c1, c2, b)
    if not small:
        hp = QtGui.QPen(QtGui.QColor(CYAN), 7)
        hp.setDashPattern([3, 2.4])
        p.setPen(hp)
        p.drawLine(a, c1)
        p.drawLine(b, c2)
    glow = QtGui.QPen(QtGui.QColor(94, 230, 255, 70), 64 if not small else 90)
    glow.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
    p.setPen(glow)
    p.drawPath(curve)
    cp = QtGui.QPen(QtGui.QColor(CYAN), 30 if not small else 56)
    cp.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
    p.setPen(cp)
    p.drawPath(curve)
    if not small:
        p.setPen(QtGui.QPen(QtGui.QColor(CYAN), 8))
        p.setBrush(QtGui.QColor(BOTTOM))
        for q in (c1, c2):
            p.drawEllipse(q, 22, 22)
        p.setPen(QtGui.QPen(QtGui.QColor(CYAN), 9))
        p.setBrush(QtGui.QColor(WHITE))
        for q in (a, b):
            p.drawRect(QtCore.QRectF(q.x() - 30, q.y() - 30, 60, 60))

    # cursor de precisión (cruz + caja de captura)
    o = P(700, 690)
    p.setPen(QtGui.QPen(QtGui.QColor(10, 18, 60, 120), 26))
    p.drawLine(o + P(-118, 4), o + P(122, 4))
    p.drawLine(o + P(4, -118), o + P(4, 122))
    cur = QtGui.QPen(QtGui.QColor(ORANGE), 18 if not small else 40)
    cur.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
    p.setPen(cur)
    p.drawLine(o + P(-118, 0), o + P(-40, 0))
    p.drawLine(o + P(40, 0), o + P(118, 0))
    p.drawLine(o + P(0, -118), o + P(0, -40))
    p.drawLine(o + P(0, 40), o + P(0, 118))
    p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
    p.drawRect(QtCore.QRectF(o.x() - 26, o.y() - 26, 52, 52))

    p.restore()

    # borde interior sutil
    p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 50), 5))
    p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
    p.drawPath(path)
    p.end()
    return img


def main() -> int:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    app = QtGui.QGuiApplication.instance() or QtGui.QGuiApplication([])
    _ = app
    iconset = os.path.join(out, "VectorCAD.iconset")
    os.makedirs(iconset, exist_ok=True)
    cache = {n: draw(n) for n in SIZES}
    for name, n in ICONSET:
        cache[n].save(os.path.join(iconset, name), "PNG")
    cache[1024].save(os.path.join(out, "VectorCAD.png"), "PNG")
    print(f"iconset -> {iconset}")

    icns = os.path.join(out, "VectorCAD.icns")
    if sys.platform == "darwin":
        try:
            subprocess.run(["iconutil", "-c", "icns", iconset, "-o", icns],
                           check=True, timeout=60)
            print(f"icns    -> {icns}")
        except Exception as ex:
            print(f"aviso: iconutil falló ({ex}); se usará el .iconset", file=sys.stderr)
    else:
        print("aviso: iconutil sólo existe en macOS; ejecuta allí para obtener el .icns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
