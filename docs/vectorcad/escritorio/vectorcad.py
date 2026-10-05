#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VectorCAD 5.0 — Sistema de dibujo 2D vectorial paramétrico.

Tablero de dibujo digital nativo en Python: lienzo cartesiano + intérprete de
comandos con el diccionario de alias de AutoCAD/Rhino, motor geométrico propio,
operaciones booleanas (Shapely), exportación DXF/SVG/JSON y consola Python
embebida para automatización.

Novedades 5.0: entrada dinámica (distancia/ángulo con Tab), grosores de línea
reales (ByLayer, LWT), gestión avanzada de capas, impresora PDF vectorial con
cajetín, lectura DWG con LibreDWG integrado y lienzo con caché de dibujo.

Ejecutar:
    python vectorcad.py

Dependencias:
    pip install PySide6            (obligatoria: GUI)
    pip install ezdxf shapely      (opcionales: DXF y booleanas robustas)
"""

from __future__ import annotations

import copy
import glob
import inspect
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
#  Compatibilidad Qt
# --------------------------------------------------------------------------- #
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF, Signal
    QT_LIB = "PySide6"
except ImportError:  # pragma: no cover
    try:
        from PyQt6 import QtCore, QtGui, QtWidgets
        from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
        from PyQt6.QtCore import pyqtSignal as Signal
        QT_LIB = "PyQt6"
    except ImportError:
        sys.stderr.write("VectorCAD requiere PySide6 o PyQt6:  pip install PySide6\n")
        raise SystemExit(1)

try:
    import ezdxf
    HAS_EZDXF = True
except Exception:
    HAS_EZDXF = False

try:
    from shapely.geometry import Polygon as ShPolygon
    from shapely.geometry import MultiPolygon as ShMultiPolygon
    from shapely.ops import unary_union
    HAS_SHAPELY = True
except Exception:
    HAS_SHAPELY = False


APP_NAME = "VectorCAD"
APP_VERSION = "5.0"

#: Carpeta de datos de la instalación (entorno, LibreDWG integrado, icono).
SUPPORT_DIR = os.path.expanduser("~/Library/Application Support/VectorCAD") \
    if sys.platform == "darwin" else os.path.expanduser("~/.local/share/vectorcad")

# --------------------------------------------------------------------------- #
#  Soporte DWG
#
#  DWG es un formato binario propietario sin especificación pública, así que no
#  se lee directamente: se delega en un conversor externo que produce un DXF
#  temporal, y ese DXF se importa con la ruta ya existente.
#
#  Conversores admitidos, en orden de preferencia:
#    1. ODA File Converter (Open Design Alliance, gratuito, registro previo).
#       Máxima fidelidad y soporte hasta DWG 2018+.
#       CLI:  ODAFileConverter <dir_ent> <dir_sal> <versión> <formato>
#                              <recursivo> <auditar> [filtro]
#    2. LibreDWG integrado: el instalador lo compila desde el código fuente
#       oficial de GNU en <SUPPORT_DIR>/libredwg, sin Homebrew.
#    3. LibreDWG del sistema (`brew install libredwg`, apt…).
#       CLI:  dwg2dxf -y -o salida.dxf entrada.dwg   (alternativa: dwgread -O DXF)
#
#  El DXF resultante se lee con el modo de recuperación de ezdxf, que tolera
#  las pequeñas irregularidades que suelen producir los conversores.
#  La ruta puede forzarse con la variable de entorno VECTORCAD_DWG_CONVERTER.
# --------------------------------------------------------------------------- #
DWG_ENV_VAR = "VECTORCAD_DWG_CONVERTER"

_BUNDLED_DWG_DIRS = [
    os.path.join(SUPPORT_DIR, "libredwg", "bin"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "libredwg", "bin"),
]

_ODA_CANDIDATES = [
    "/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter",
    os.path.expanduser("~/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"),
    "/usr/bin/ODAFileConverter",
    "/usr/local/bin/ODAFileConverter",
    "/opt/oda/ODAFileConverter",
]
_ODA_GLOBS = [
    r"C:\Program Files\ODA\*\ODAFileConverter.exe",
    r"C:\Program Files (x86)\ODA\*\ODAFileConverter.exe",
    os.path.expanduser("~/Applications/ODAFileConverter*.AppImage"),
    os.path.expanduser("~/Apps/ODAFileConverter*.AppImage"),
]
# Homebrew en Apple Silicon no está en el PATH de las apps lanzadas desde el Finder.
_EXTRA_BIN_DIRS = _BUNDLED_DWG_DIRS + [
    "/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin",
    os.path.expanduser("~/.local/bin")]

_dwg_conv_cache: Optional[Tuple[str, str]] = None
_dwg_conv_done = False


def _which(name: str) -> Optional[str]:
    p = shutil.which(name)
    if p:
        return p
    for d in _EXTRA_BIN_DIRS:
        cand = os.path.join(d, name)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


def find_dwg_converter(refresh: bool = False) -> Optional[Tuple[str, str]]:
    """Devuelve ``("oda"|"libredwg", ruta)`` o ``None`` si no hay conversor."""
    global _dwg_conv_cache, _dwg_conv_done
    if _dwg_conv_done and not refresh:
        return _dwg_conv_cache

    found: Optional[Tuple[str, str]] = None

    forced = os.environ.get(DWG_ENV_VAR, "").strip().strip('"')
    if forced and os.path.isfile(forced):
        base = os.path.basename(forced).lower()
        kind = "libredwg" if "dwg2dxf" in base else "oda"
        found = (kind, forced)

    if found is None:
        for c in _ODA_CANDIDATES:
            if os.path.isfile(c) and os.access(c, os.X_OK):
                found = ("oda", c)
                break

    if found is None:
        p = _which("ODAFileConverter") or _which("ODAFileConverter.exe")
        if p:
            found = ("oda", p)

    if found is None:
        for pattern in _ODA_GLOBS:
            hits = sorted(glob.glob(pattern))
            if hits:
                found = ("oda", hits[-1])
                break

    if found is None:
        for d in _BUNDLED_DWG_DIRS:
            cand = os.path.join(d, "dwg2dxf")
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                found = ("libredwg", cand)
                break

    if found is None:
        p = _which("dwg2dxf")
        if p:
            found = ("libredwg", p)

    _dwg_conv_cache = found
    _dwg_conv_done = True
    return found


def dwg_converter_name() -> str:
    conv = find_dwg_converter()
    if not conv:
        return "ninguno"
    if conv[0] == "libredwg" and any(conv[1].startswith(d) for d in _BUNDLED_DWG_DIRS):
        return "LibreDWG (integrado)"
    return {"oda": "ODA File Converter", "libredwg": "LibreDWG"}[conv[0]]


def dwg_install_hint() -> str:
    """Instrucciones de instalación según el sistema."""
    if sys.platform == "darwin":
        return ("Para leer DWG vuelve a ejecutar install_macos.command: compila e integra\n"
                "LibreDWG automáticamente (no requiere Homebrew). Alternativas:\n"
                "  · LibreDWG del sistema:   brew install libredwg\n"
                "  · ODA File Converter (mayor fidelidad): "
                "https://www.opendesign.com/guestfiles/oda_file_converter\n"
                f"Si ya lo tienes en otra ruta, define {DWG_ENV_VAR}=/ruta/al/ejecutable")
    if sys.platform.startswith("win"):
        return ("Para leer DWG instala el ODA File Converter "
                "(https://www.opendesign.com/guestfiles/oda_file_converter) "
                f"o define {DWG_ENV_VAR} con la ruta del ejecutable.")
    return ("Para leer DWG instala LibreDWG (apt/dnf: libredwg-tools) o el "
            "ODA File Converter; en un servidor sin pantalla, el segundo "
            f"necesita xvfb. También puedes definir {DWG_ENV_VAR}.")


def _run_converter(args: List[str], timeout: int) -> Tuple[int, str]:
    """Ejecuta el conversor sin abrir consola en Windows."""
    kwargs: Dict[str, Any] = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=timeout)
    if sys.platform.startswith("win"):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = si
    try:
        cp = subprocess.run(args, **kwargs)
        return cp.returncode, (cp.stdout or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"El conversor DWG no respondió en {timeout} s.")


def dwg_to_dxf(path: str, out_dir: Optional[str] = None,
               version: str = "ACAD2018", timeout: int = 180) -> str:
    """Convierte un DWG en un DXF y devuelve la ruta del DXF resultante.

    Lanza ``RuntimeError`` con un mensaje accionable si no hay conversor o si la
    conversión falla.
    """
    if not os.path.isfile(path):
        raise RuntimeError(f"No existe el archivo: {path}")
    conv = find_dwg_converter(refresh=True)
    if conv is None:
        raise RuntimeError("No hay ningún conversor DWG instalado.\n" + dwg_install_hint())
    kind, exe = conv
    out_dir = out_dir or tempfile.mkdtemp(prefix="vcad_dwg_")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(path))[0]
    out_dxf = os.path.join(out_dir, stem + ".dxf")

    if kind == "libredwg":
        # Varias estrategias: dwg2dxf nativo, forzando R2000 (más tolerante) y
        # dwgread, que usa otra ruta de escritura dentro de la biblioteca.
        dwgread = os.path.join(os.path.dirname(exe), "dwgread")
        attempts = [[exe, "-y", "-o", out_dxf, os.path.abspath(path)],
                    [exe, "-y", "--as", "r2000", "-o", out_dxf, os.path.abspath(path)]]
        if os.path.isfile(dwgread):
            attempts.append([dwgread, "-O", "DXF", "-o", out_dxf, os.path.abspath(path)])
        code, out = -1, ""
        for args in attempts:
            if os.path.isfile(out_dxf):
                os.remove(out_dxf)
            code, out = _run_converter(args, timeout)
            if os.path.isfile(out_dxf) and os.path.getsize(out_dxf) > 200:
                return out_dxf
        raise RuntimeError(f"LibreDWG no pudo convertir el archivo (código {code}).\n"
                           f"{out.strip()[:400]}")

    # ODA File Converter: trabaja por carpetas, así que se aísla el archivo en
    # un directorio temporal propio para no procesar toda la carpeta de origen.
    in_dir = tempfile.mkdtemp(prefix="vcad_dwg_in_")
    shutil.copy2(path, os.path.join(in_dir, os.path.basename(path)))
    args = [exe, in_dir, out_dir, version, "DXF", "0", "1", os.path.basename(path)]
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        # El conversor es una aplicación Qt y necesita un display aunque no
        # muestre ventana alguna.
        xvfb = _which("xvfb-run")
        if xvfb:
            args = [xvfb, "-a"] + args
    try:
        code, out = _run_converter(args, timeout)
    finally:
        shutil.rmtree(in_dir, ignore_errors=True)
    # El ODA devuelve 0 aunque falle un archivo: la comprobación real es la
    # existencia del DXF de salida.
    if not os.path.isfile(out_dxf):
        alt = [f for f in os.listdir(out_dir) if f.lower().endswith(".dxf")]
        if alt:
            return os.path.join(out_dir, alt[0])
        raise RuntimeError(f"El ODA File Converter no generó el DXF (código {code}).\n"
                           f"{out.strip()[:400]}")
    return out_dxf


def dxf_to_dwg(dxf_path: str, dwg_path: str, version: str = "ACAD2018",
               timeout: int = 180) -> str:
    """Convierte un DXF en DWG. Devuelve la ruta escrita."""
    conv = find_dwg_converter(refresh=True)
    if conv is None:
        raise RuntimeError("No hay ningún conversor DWG instalado.\n" + dwg_install_hint())
    kind, exe = conv
    out_dir = os.path.dirname(os.path.abspath(dwg_path)) or "."
    stem = os.path.splitext(os.path.basename(dwg_path))[0]

    if kind == "libredwg":
        exe2 = _which("dxf2dwg") or os.path.join(os.path.dirname(exe), "dxf2dwg")
        if not os.path.isfile(exe2):
            raise RuntimeError("LibreDWG no incluye dxf2dwg en esta instalación.")
        # LibreDWG sólo escribe hasta R2000.
        args = [exe2, "-y", "--as", "r2000", "-o", dwg_path, os.path.abspath(dxf_path)]
        code, out = _run_converter(args, timeout)
        if not os.path.isfile(dwg_path):
            raise RuntimeError(f"dxf2dwg falló (código {code}).\n{out.strip()[:400]}")
        return dwg_path

    in_dir = tempfile.mkdtemp(prefix="vcad_dxf_in_")
    shutil.copy2(dxf_path, os.path.join(in_dir, stem + ".dxf"))
    args = [exe, in_dir, out_dir, version, "DWG", "0", "1", stem + ".dxf"]
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        xvfb = _which("xvfb-run")
        if xvfb:
            args = [xvfb, "-a"] + args
    try:
        code, out = _run_converter(args, timeout)
    finally:
        shutil.rmtree(in_dir, ignore_errors=True)
    produced = os.path.join(out_dir, stem + ".dwg")
    if not os.path.isfile(produced):
        raise RuntimeError(f"El ODA File Converter no generó el DWG (código {code}).\n"
                           f"{out.strip()[:400]}")
    if os.path.abspath(produced) != os.path.abspath(dwg_path):
        shutil.move(produced, dwg_path)
    return dwg_path


# --------------------------------------------------------------------------- #
#  Tema visual
# --------------------------------------------------------------------------- #
THEME = {
    "canvas": "#141417",
    "grid_minor": "#202024",
    "grid_major": "#2b2b31",
    "axis_x": "#6a3030",
    "axis_y": "#306a30",
    "crosshair": "#55555f",
    "entity": "#e2e2e6",
    "selected": "#ffd54f",
    "ghost": "#4fc3f7",
    "snap": "#ff7043",
    "window_sel": "#3d7bff",
    "cross_sel": "#4caf50",
    "text": "#e6e6e6",
    "panel": "#161619",
    "panel_alt": "#1e1e23",
    "line": "#2a2a31",
    "muted": "#9a9aa2",
}

PALETTE = ["#e2e2e6", "#ff5252", "#ffd54f", "#66bb6a", "#4fc3f7",
           "#ba68c8", "#ff8a65", "#4db6ac", "#9e9e9e", "#f06292"]

# Grosores de línea normalizados (mm), como en AutoCAD / ISO 128.
LINEWEIGHTS = [0.00, 0.05, 0.09, 0.13, 0.15, 0.18, 0.20, 0.25, 0.30, 0.35, 0.40,
               0.50, 0.53, 0.60, 0.70, 0.80, 0.90, 1.00, 1.06, 1.20, 1.40, 1.58,
               2.00, 2.11]
LW_BYLAYER = -1.0          # el grosor lo decide la capa
LW_DEFAULT = 0.25          # grosor de la capa por omisión
LT_BYLAYER = "ByLayer"


def lw_label(lw: float) -> str:
    if lw is None or lw < 0:
        return "PorCapa"
    return f"{lw:.2f} mm"

TOL = 1e-9
ANG_TOL = 1e-9

# =========================================================================== #
#  1. NÚCLEO GEOMÉTRICO  (modelo puro en tuplas: independiente de Qt)
# =========================================================================== #
Vec = Tuple[float, float]


def vadd(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1])


def vsub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1])


def vmul(a: Vec, k: float) -> Vec:
    return (a[0] * k, a[1] * k)


def vdot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1]


def vcross(a: Vec, b: Vec) -> float:
    return a[0] * b[1] - a[1] * b[0]


def vlen(a: Vec) -> float:
    return math.hypot(a[0], a[1])


def vdist(a: Vec, b: Vec) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def vnorm(a: Vec) -> Vec:
    n = vlen(a)
    return (a[0] / n, a[1] / n) if n > TOL else (0.0, 0.0)


def vperp(a: Vec) -> Vec:
    """Normal izquierda (giro +90°)."""
    return (-a[1], a[0])


def vlerp(a: Vec, b: Vec, t: float) -> Vec:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def vangle(a: Vec, b: Vec) -> float:
    return math.atan2(b[1] - a[1], b[0] - a[0])


def vrot(p: Vec, c: Vec, ang: float) -> Vec:
    ca, sa = math.cos(ang), math.sin(ang)
    dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca)


def vmirror(p: Vec, p1: Vec, p2: Vec) -> Vec:
    d = vsub(p2, p1)
    l2 = vdot(d, d) or 1e-12
    t = vdot(vsub(p, p1), d) / l2
    f = vadd(p1, vmul(d, t))
    return (2 * f[0] - p[0], 2 * f[1] - p[1])


def norm_ang(a: float) -> float:
    a = math.fmod(a, 2 * math.pi)
    return a + 2 * math.pi if a < 0 else a


def ang_in_arc(a: float, a0: float, a1: float) -> bool:
    """¿El ángulo `a` cae dentro del arco CCW que va de a0 a a1?"""
    span = norm_ang(a1 - a0)
    if span < ANG_TOL:
        span = 2 * math.pi
    return norm_ang(a - a0) <= span + 1e-9


def fmt(v: float, n: int = 4) -> str:
    s = f"{v:.{n}f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-") else "0"


# ---------- distancias e intersecciones --------------------------------- #
def dist_point_seg(p: Vec, a: Vec, b: Vec) -> float:
    d = vsub(b, a)
    l2 = vdot(d, d)
    if l2 < TOL:
        return vdist(p, a)
    t = max(0.0, min(1.0, vdot(vsub(p, a), d) / l2))
    return vdist(p, vadd(a, vmul(d, t)))


def closest_on_seg(p: Vec, a: Vec, b: Vec) -> Vec:
    d = vsub(b, a)
    l2 = vdot(d, d)
    if l2 < TOL:
        return a
    t = max(0.0, min(1.0, vdot(vsub(p, a), d) / l2))
    return vadd(a, vmul(d, t))


def dist_point_arc(p: Vec, c: Vec, r: float, a0: float, a1: float) -> float:
    a = math.atan2(p[1] - c[1], p[0] - c[0])
    if ang_in_arc(a, a0, a1):
        return abs(vdist(p, c) - r)
    e0 = (c[0] + r * math.cos(a0), c[1] + r * math.sin(a0))
    e1 = (c[0] + r * math.cos(a1), c[1] + r * math.sin(a1))
    return min(vdist(p, e0), vdist(p, e1))


def int_line_line(p1: Vec, p2: Vec, p3: Vec, p4: Vec,
                  inf1: bool = False, inf2: bool = False) -> List[Vec]:
    d1, d2 = vsub(p2, p1), vsub(p4, p3)
    den = vcross(d1, d2)
    if abs(den) < 1e-12:
        return []
    w = vsub(p3, p1)
    t = vcross(w, d2) / den
    u = vcross(w, d1) / den
    if not inf1 and not (-1e-9 <= t <= 1 + 1e-9):
        return []
    if not inf2 and not (-1e-9 <= u <= 1 + 1e-9):
        return []
    return [vadd(p1, vmul(d1, t))]


def int_line_circle(p1: Vec, p2: Vec, c: Vec, r: float,
                    inf: bool = False) -> List[Vec]:
    d = vsub(p2, p1)
    f = vsub(p1, c)
    a = vdot(d, d)
    if a < 1e-18:
        return []
    b = 2 * vdot(f, d)
    cc = vdot(f, f) - r * r
    disc = b * b - 4 * a * cc
    if disc < -1e-12:
        return []
    sq = math.sqrt(max(disc, 0.0))
    out = []
    for t in ((-b - sq) / (2 * a), (-b + sq) / (2 * a)):
        if inf or -1e-9 <= t <= 1 + 1e-9:
            out.append(vadd(p1, vmul(d, t)))
    return out


def int_circle_circle(c1: Vec, r1: float, c2: Vec, r2: float) -> List[Vec]:
    d = vdist(c1, c2)
    if d < TOL or d > r1 + r2 + 1e-9 or d < abs(r1 - r2) - 1e-9:
        return []
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h2 = r1 * r1 - a * a
    h = math.sqrt(max(h2, 0.0))
    base = vadd(c1, vmul(vnorm(vsub(c2, c1)), a))
    n = vperp(vnorm(vsub(c2, c1)))
    if h < 1e-9:
        return [base]
    return [vadd(base, vmul(n, h)), vsub(base, vmul(n, h))]


# ---------- primitivas normalizadas -------------------------------------- #
#  ("seg", a, b)                     segmento
#  ("arc", c, r, a0, a1)             arco CCW (círculo completo: a0=0, a1=2pi)
def prim_dist(pr, p: Vec) -> float:
    if pr[0] == "seg":
        return dist_point_seg(p, pr[1], pr[2])
    return dist_point_arc(p, pr[1], pr[2], pr[3], pr[4])


def prim_int(p: tuple, q: tuple, inf_p: bool = False, inf_q: bool = False) -> List[Vec]:
    """Intersección entre dos primitivas, filtrando por rango de arco."""
    if p[0] == "seg" and q[0] == "seg":
        return int_line_line(p[1], p[2], q[1], q[2], inf_p, inf_q)
    if p[0] == "seg" and q[0] == "arc":
        pts = int_line_circle(p[1], p[2], q[1], q[2], inf_p)
        return [x for x in pts
                if ang_in_arc(math.atan2(x[1] - q[1][1], x[0] - q[1][0]), q[3], q[4])]
    if p[0] == "arc" and q[0] == "seg":
        return prim_int(q, p, inf_q, inf_p)
    pts = int_circle_circle(p[1], p[2], q[1], q[2])
    out = []
    for x in pts:
        if ang_in_arc(math.atan2(x[1] - p[1][1], x[0] - p[1][0]), p[3], p[4]) and \
           ang_in_arc(math.atan2(x[1] - q[1][1], x[0] - q[1][0]), q[3], q[4]):
            out.append(x)
    return out


def arc_points(c: Vec, r: float, a0: float, a1: float, seg: int = 0) -> List[Vec]:
    span = norm_ang(a1 - a0)
    if span < ANG_TOL:
        span = 2 * math.pi
    if seg <= 0:
        seg = max(8, int(abs(span) / (math.pi / 36)))
    return [(c[0] + r * math.cos(a0 + span * i / seg),
             c[1] + r * math.sin(a0 + span * i / seg)) for i in range(seg + 1)]


# ---------- polígonos ---------------------------------------------------- #
def poly_area(pts: List[Vec]) -> float:
    a = 0.0
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        a += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
    return a / 2.0


def poly_centroid(pts: List[Vec]) -> Vec:
    a = poly_area(pts)
    if abs(a) < 1e-12:
        n = max(len(pts), 1)
        return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
    cx = cy = 0.0
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        cr = pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
        cx += (pts[i][0] + pts[j][0]) * cr
        cy += (pts[i][1] + pts[j][1]) * cr
    return (cx / (6 * a), cy / (6 * a))


def point_in_poly(p: Vec, poly: List[Vec]) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > p[1]) != (yj > p[1]):
            if p[0] < (xj - xi) * (p[1] - yi) / (yj - yi + 1e-15) + xi:
                inside = not inside
        j = i
    return inside


def offset_polyline(pts: List[Vec], d: float, closed: bool) -> List[Vec]:
    """Offset con unión en inglete; d>0 desplaza hacia la normal izquierda."""
    n = len(pts)
    if n < 2:
        return list(pts)
    segs = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        a, b = pts[i], pts[(i + 1) % n]
        nrm = vmul(vperp(vnorm(vsub(b, a))), d)
        segs.append((vadd(a, nrm), vadd(b, nrm)))
    out: List[Vec] = []
    m = len(segs)
    if not closed:
        out.append(segs[0][0])
    for i in range(m if closed else m - 1):
        s1 = segs[i]
        s2 = segs[(i + 1) % m]
        ip = int_line_line(s1[0], s1[1], s2[0], s2[1], inf1=True, inf2=True)
        out.append(ip[0] if ip else s1[1])
    if not closed:
        out.append(segs[-1][1])
    return out


def hatch_lines(poly: List[Vec], angle: float, spacing: float) -> List[Tuple[Vec, Vec]]:
    """Achurado por barrido: líneas paralelas recortadas contra el polígono."""
    if len(poly) < 3 or spacing <= 0:
        return []
    c = poly_centroid(poly)
    rp = [vrot(p, c, -angle) for p in poly]
    ys = [p[1] for p in rp]
    y0, y1 = min(ys), max(ys)
    if (y1 - y0) / spacing > 4000:
        return []
    out = []
    y = math.floor(y0 / spacing) * spacing + spacing
    n = len(rp)
    while y < y1:
        xs = []
        for i in range(n):
            a, b = rp[i], rp[(i + 1) % n]
            if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                t = (y - a[1]) / (b[1] - a[1])
                xs.append(a[0] + t * (b[0] - a[0]))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            if xs[i + 1] - xs[i] > 1e-9:
                out.append((vrot((xs[i], y), c, angle),
                            vrot((xs[i + 1], y), c, angle)))
        y += spacing
    return out


def catmull_rom(pts: List[Vec], samples: int = 16) -> List[Vec]:
    """Interpolación suave (spline) que pasa por los puntos de control."""
    if len(pts) < 3:
        return list(pts)
    ext = [pts[0]] + list(pts) + [pts[-1]]
    out = [pts[0]]
    for i in range(len(ext) - 3):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for s in range(1, samples + 1):
            t = s / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


# =========================================================================== #
#  2. ENTIDADES
# =========================================================================== #
ENTITY_TYPES: Dict[str, type] = {}


def register(cls):
    ENTITY_TYPES[cls.kind] = cls
    return cls


class Entity:
    """Entidad vectorial. El modelo es Python puro (tuplas), sin tipos Qt."""

    kind = "Entity"
    _seq = 0

    def __init__(self, layer: str = "0", color: Optional[str] = None,
                 linetype: str = LT_BYLAYER, lineweight: float = LW_BYLAYER):
        Entity._seq += 1
        self.id = Entity._seq
        self.layer = layer
        self.color = color              # None => ByLayer
        self.linetype = linetype
        self.lineweight = lineweight
        self.selected = False
        self.group: Optional[int] = None

    # --- geometría ------------------------------------------------------ #
    def primitives(self) -> List[tuple]:
        return []

    def bbox(self) -> Tuple[float, float, float, float]:
        pts = self.sample()
        if not pts:
            return (0.0, 0.0, 0.0, 0.0)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    def sample(self) -> List[Vec]:
        """Puntos suficientes para bbox y cruces de ventana."""
        out: List[Vec] = []
        for pr in self.primitives():
            if pr[0] == "seg":
                out += [pr[1], pr[2]]
            else:
                out += arc_points(pr[1], pr[2], pr[3], pr[4])
        return out

    def snaps(self) -> List[Tuple[str, Vec]]:
        return []

    def dist_to(self, p: Vec) -> float:
        prs = self.primitives()
        if not prs:
            x0, y0, x1, y1 = self.bbox()
            return dist_point_seg(p, (x0, y0), (x1, y1))
        return min(prim_dist(pr, p) for pr in prs)

    def hit(self, p: Vec, tol: float) -> bool:
        return self.dist_to(p) <= tol

    def length(self) -> float:
        tot = 0.0
        for pr in self.primitives():
            if pr[0] == "seg":
                tot += vdist(pr[1], pr[2])
            else:
                span = norm_ang(pr[4] - pr[3]) or 2 * math.pi
                tot += pr[2] * span
        return tot

    def polygon(self) -> Optional[List[Vec]]:
        """Contorno cerrado (para área y booleanas), o None."""
        return None

    def area(self) -> float:
        poly = self.polygon()
        return abs(poly_area(poly)) if poly else 0.0

    def explode(self) -> List["Entity"]:
        return []

    # --- transformaciones ------------------------------------------------ #
    def _map(self, fn: Callable[[Vec], Vec]):
        raise NotImplementedError

    def _rot_extra(self, a: float):
        pass

    def _scale_extra(self, f: float):
        pass

    def _mirror_extra(self, ax: float):
        pass

    def translate(self, d: Vec):
        self._map(lambda p: vadd(p, d))

    def rotate(self, c: Vec, a: float):
        self._map(lambda p: vrot(p, c, a))
        self._rot_extra(a)

    def scale(self, c: Vec, f: float):
        self._map(lambda p: vadd(c, vmul(vsub(p, c), f)))
        self._scale_extra(abs(f))

    def mirror(self, p1: Vec, p2: Vec):
        ax = vangle(p1, p2)
        self._map(lambda p: vmirror(p, p1, p2))
        self._mirror_extra(ax)

    def clone(self) -> "Entity":
        c = copy.deepcopy(self)
        Entity._seq += 1
        c.id = Entity._seq
        c.selected = False
        return c

    # --- dibujo ---------------------------------------------------------- #
    def draw(self, g: "QtGui.QPainter", view, pen: "QtGui.QPen"):
        g.setPen(pen)
        g.setBrush(Qt.BrushStyle.NoBrush)
        for pr in self.primitives():
            if pr[0] == "seg":
                g.drawLine(view.to_screen(pr[1]), view.to_screen(pr[2]))
            else:
                view.draw_arc(g, pr[1], pr[2], pr[3], pr[4])

    # --- serialización ---------------------------------------------------- #
    def _base_dict(self) -> dict:
        return {"kind": self.kind, "layer": self.layer, "color": self.color,
                "linetype": self.linetype, "lineweight": self.lineweight}

    def to_dict(self) -> dict:
        return self._base_dict()

    @classmethod
    def from_dict(cls, d: dict) -> "Entity":
        raise NotImplementedError

    @staticmethod
    def build(d: dict) -> Optional["Entity"]:
        c = ENTITY_TYPES.get(d.get("kind", ""))
        if not c:
            return None
        e = c.from_dict(d)
        e.layer = d.get("layer", "0")
        e.color = d.get("color")
        e.linetype = d.get("linetype", LT_BYLAYER)
        e.lineweight = d.get("lineweight", LW_BYLAYER)
        return e

    def dxf_attribs(self) -> dict:
        """Capa, color, tipo y grosor de línea en formato DXF."""
        a: Dict[str, Any] = {"layer": self.layer}
        if self.color:
            try:
                a["true_color"] = ezdxf.colors.rgb2int(_hex_rgb(self.color))
            except Exception:
                pass
        if self.linetype and self.linetype != LT_BYLAYER:
            a["linetype"] = LT_DXF.get(self.linetype, "Continuous")
        if self.lineweight is not None and self.lineweight >= 0:
            a["lineweight"] = int(round(self.lineweight * 100))
        return a

    def to_dxf(self, msp):
        pass

    def props(self) -> List[Tuple[str, str, str]]:
        """(clave, etiqueta, valor) editable en el panel de propiedades."""
        return []

    def set_prop(self, key: str, value: str) -> bool:
        return False


def _attrs(e: Entity) -> dict:
    """Propiedades generales que una entidad derivada hereda de su origen."""
    return dict(layer=e.layer, color=e.color, linetype=e.linetype,
                lineweight=e.lineweight)


@register
class Line(Entity):
    kind = "Line"

    def __init__(self, p1: Vec, p2: Vec, **kw):
        super().__init__(**kw)
        self.p1 = tuple(p1)
        self.p2 = tuple(p2)

    def primitives(self):
        return [("seg", self.p1, self.p2)]

    def snaps(self):
        return [("end", self.p1), ("end", self.p2),
                ("mid", vlerp(self.p1, self.p2, 0.5))]

    def _map(self, fn):
        self.p1 = fn(self.p1)
        self.p2 = fn(self.p2)

    def to_dict(self):
        d = self._base_dict()
        d.update(p1=list(self.p1), p2=list(self.p2))
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(tuple(d["p1"]), tuple(d["p2"]))

    def to_dxf(self, msp):
        msp.add_line(self.p1, self.p2, dxfattribs=self.dxf_attribs())

    def props(self):
        return [("x1", "Inicio X", fmt(self.p1[0])), ("y1", "Inicio Y", fmt(self.p1[1])),
                ("x2", "Fin X", fmt(self.p2[0])), ("y2", "Fin Y", fmt(self.p2[1])),
                ("len", "Longitud", fmt(vdist(self.p1, self.p2))),
                ("ang", "Ángulo", fmt(math.degrees(vangle(self.p1, self.p2)), 2))]

    def set_prop(self, key, value):
        try:
            v = float(value)
        except ValueError:
            return False
        if key == "x1":
            self.p1 = (v, self.p1[1])
        elif key == "y1":
            self.p1 = (self.p1[0], v)
        elif key == "x2":
            self.p2 = (v, self.p2[1])
        elif key == "y2":
            self.p2 = (self.p2[0], v)
        elif key == "len":
            self.p2 = vadd(self.p1, vmul(vnorm(vsub(self.p2, self.p1)) or (1.0, 0.0), v))
        elif key == "ang":
            L = vdist(self.p1, self.p2)
            a = math.radians(v)
            self.p2 = vadd(self.p1, (L * math.cos(a), L * math.sin(a)))
        else:
            return False
        return True


@register
class Polyline(Entity):
    kind = "Polyline"

    def __init__(self, points: List[Vec], closed: bool = False, **kw):
        super().__init__(**kw)
        self.points = [tuple(p) for p in points]
        self.closed = bool(closed)

    def primitives(self):
        out = []
        n = len(self.points)
        rng = range(n) if self.closed else range(n - 1)
        for i in rng:
            out.append(("seg", self.points[i], self.points[(i + 1) % n]))
        return out

    def snaps(self):
        out = [("end", p) for p in self.points]
        for pr in self.primitives():
            out.append(("mid", vlerp(pr[1], pr[2], 0.5)))
        if self.closed and len(self.points) > 2:
            out.append(("cen", poly_centroid(self.points)))
        return out

    def _map(self, fn):
        self.points = [fn(p) for p in self.points]

    def polygon(self):
        return list(self.points) if (self.closed and len(self.points) >= 3) else None

    def explode(self):
        return [Line(pr[1], pr[2], **_attrs(self))
                for pr in self.primitives()]

    def draw(self, g, view, pen):
        g.setPen(pen)
        g.setBrush(Qt.BrushStyle.NoBrush)
        if len(self.points) < 2:
            return
        poly = QtGui.QPolygonF([view.to_screen(p) for p in self.points])
        if self.closed:
            g.drawPolygon(poly)
        else:
            g.drawPolyline(poly)

    def to_dict(self):
        d = self._base_dict()
        d.update(points=[list(p) for p in self.points], closed=self.closed)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls([tuple(p) for p in d["points"]], d.get("closed", False))

    def to_dxf(self, msp):
        msp.add_lwpolyline(self.points, close=self.closed,
                           dxfattribs=self.dxf_attribs())

    def props(self):
        return [("n", "Vértices", str(len(self.points))),
                ("closed", "Cerrada (0/1)", "1" if self.closed else "0"),
                ("len", "Longitud", fmt(self.length())),
                ("area", "Área", fmt(self.area()))]

    def set_prop(self, key, value):
        if key == "closed":
            self.closed = value.strip() in ("1", "true", "True", "si", "sí")
            return True
        return False


@register
class Circle(Entity):
    kind = "Circle"

    def __init__(self, center: Vec, radius: float, **kw):
        super().__init__(**kw)
        self.center = tuple(center)
        self.radius = float(radius)

    def primitives(self):
        return [("arc", self.center, self.radius, 0.0, 2 * math.pi)]

    def snaps(self):
        c, r = self.center, self.radius
        return [("cen", c), ("qua", (c[0] + r, c[1])), ("qua", (c[0] - r, c[1])),
                ("qua", (c[0], c[1] + r)), ("qua", (c[0], c[1] - r))]

    def _map(self, fn):
        self.center = fn(self.center)

    def _scale_extra(self, f):
        self.radius *= f

    def polygon(self):
        return arc_points(self.center, self.radius, 0, 2 * math.pi, 72)[:-1]

    def draw(self, g, view, pen):
        g.setPen(pen)
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.drawEllipse(view.to_screen(self.center),
                      self.radius * view.scale, self.radius * view.scale)

    def to_dict(self):
        d = self._base_dict()
        d.update(center=list(self.center), radius=self.radius)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(tuple(d["center"]), d["radius"])

    def to_dxf(self, msp):
        msp.add_circle(self.center, self.radius, dxfattribs=self.dxf_attribs())

    def props(self):
        return [("cx", "Centro X", fmt(self.center[0])),
                ("cy", "Centro Y", fmt(self.center[1])),
                ("r", "Radio", fmt(self.radius)),
                ("d", "Diámetro", fmt(2 * self.radius)),
                ("area", "Área", fmt(self.area()))]

    def set_prop(self, key, value):
        try:
            v = float(value)
        except ValueError:
            return False
        if key == "cx":
            self.center = (v, self.center[1])
        elif key == "cy":
            self.center = (self.center[0], v)
        elif key == "r":
            self.radius = abs(v)
        elif key == "d":
            self.radius = abs(v) / 2
        else:
            return False
        return True


@register
class Arc(Entity):
    kind = "Arc"

    def __init__(self, center: Vec, radius: float, a0: float, a1: float, **kw):
        super().__init__(**kw)
        self.center = tuple(center)
        self.radius = float(radius)
        self.a0 = float(a0)
        self.a1 = float(a1)

    def primitives(self):
        return [("arc", self.center, self.radius, self.a0, self.a1)]

    def pt(self, a):
        return (self.center[0] + self.radius * math.cos(a),
                self.center[1] + self.radius * math.sin(a))

    def snaps(self):
        mid = self.a0 + (norm_ang(self.a1 - self.a0) or 2 * math.pi) / 2
        return [("cen", self.center), ("end", self.pt(self.a0)),
                ("end", self.pt(self.a1)), ("mid", self.pt(mid))]

    def _map(self, fn):
        self.center = fn(self.center)

    def _rot_extra(self, a):
        self.a0 += a
        self.a1 += a

    def _scale_extra(self, f):
        self.radius *= f

    def _mirror_extra(self, ax):
        self.a0, self.a1 = 2 * ax - self.a1, 2 * ax - self.a0

    def draw(self, g, view, pen):
        g.setPen(pen)
        g.setBrush(Qt.BrushStyle.NoBrush)
        view.draw_arc(g, self.center, self.radius, self.a0, self.a1)

    def to_dict(self):
        d = self._base_dict()
        d.update(center=list(self.center), radius=self.radius, a0=self.a0, a1=self.a1)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(tuple(d["center"]), d["radius"], d["a0"], d["a1"])

    def to_dxf(self, msp):
        msp.add_arc(self.center, self.radius, math.degrees(self.a0),
                    math.degrees(self.a1), dxfattribs=self.dxf_attribs())

    def props(self):
        return [("cx", "Centro X", fmt(self.center[0])),
                ("cy", "Centro Y", fmt(self.center[1])),
                ("r", "Radio", fmt(self.radius)),
                ("a0", "Áng. inicial", fmt(math.degrees(self.a0), 2)),
                ("a1", "Áng. final", fmt(math.degrees(self.a1), 2)),
                ("len", "Longitud", fmt(self.length()))]

    def set_prop(self, key, value):
        try:
            v = float(value)
        except ValueError:
            return False
        if key == "cx":
            self.center = (v, self.center[1])
        elif key == "cy":
            self.center = (self.center[0], v)
        elif key == "r":
            self.radius = abs(v)
        elif key == "a0":
            self.a0 = math.radians(v)
        elif key == "a1":
            self.a1 = math.radians(v)
        else:
            return False
        return True


@register
class Ellipse(Entity):
    kind = "Ellipse"

    def __init__(self, center: Vec, rx: float, ry: float, angle: float = 0.0, **kw):
        super().__init__(**kw)
        self.center = tuple(center)
        self.rx = float(rx)
        self.ry = float(ry)
        self.angle = float(angle)

    def polygon(self, n: int = 72):
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        out = []
        for i in range(n):
            t = 2 * math.pi * i / n
            x, y = self.rx * math.cos(t), self.ry * math.sin(t)
            out.append((self.center[0] + x * ca - y * sa,
                        self.center[1] + x * sa + y * ca))
        return out

    def primitives(self):
        pts = self.polygon(48)
        return [("seg", pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]

    def snaps(self):
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        out = [("cen", self.center)]
        for x, y in ((self.rx, 0), (-self.rx, 0), (0, self.ry), (0, -self.ry)):
            out.append(("qua", (self.center[0] + x * ca - y * sa,
                                self.center[1] + x * sa + y * ca)))
        return out

    def _map(self, fn):
        self.center = fn(self.center)

    def _rot_extra(self, a):
        self.angle += a

    def _scale_extra(self, f):
        self.rx *= f
        self.ry *= f

    def _mirror_extra(self, ax):
        self.angle = 2 * ax - self.angle

    def draw(self, g, view, pen):
        g.setPen(pen)
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.save()
        g.translate(view.to_screen(self.center))
        g.rotate(-math.degrees(self.angle))
        g.drawEllipse(QPointF(0, 0), self.rx * view.scale, self.ry * view.scale)
        g.restore()

    def to_dict(self):
        d = self._base_dict()
        d.update(center=list(self.center), rx=self.rx, ry=self.ry, angle=self.angle)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(tuple(d["center"]), d["rx"], d["ry"], d.get("angle", 0.0))

    def to_dxf(self, msp):
        major = (self.rx * math.cos(self.angle), self.rx * math.sin(self.angle))
        ratio = max(min(self.ry / self.rx, 1.0), 1e-6) if self.rx else 1.0
        msp.add_ellipse(self.center, major_axis=major, ratio=ratio,
                        dxfattribs=self.dxf_attribs())

    def props(self):
        return [("cx", "Centro X", fmt(self.center[0])),
                ("cy", "Centro Y", fmt(self.center[1])),
                ("rx", "Radio mayor", fmt(self.rx)), ("ry", "Radio menor", fmt(self.ry)),
                ("rot", "Rotación", fmt(math.degrees(self.angle), 2))]

    def set_prop(self, key, value):
        try:
            v = float(value)
        except ValueError:
            return False
        if key == "cx":
            self.center = (v, self.center[1])
        elif key == "cy":
            self.center = (self.center[0], v)
        elif key == "rx":
            self.rx = abs(v)
        elif key == "ry":
            self.ry = abs(v)
        elif key == "rot":
            self.angle = math.radians(v)
        else:
            return False
        return True


@register
class PointEnt(Entity):
    kind = "Point"

    def __init__(self, pos: Vec, **kw):
        super().__init__(**kw)
        self.pos = tuple(pos)

    def bbox(self):
        return (self.pos[0], self.pos[1], self.pos[0], self.pos[1])

    def sample(self):
        return [self.pos]

    def snaps(self):
        return [("nod", self.pos)]

    def dist_to(self, p):
        return vdist(p, self.pos)

    def _map(self, fn):
        self.pos = fn(self.pos)

    def draw(self, g, view, pen):
        g.setPen(pen)
        c = view.to_screen(self.pos)
        m = getattr(view, "marker", 4.0)
        g.drawLine(c + QPointF(-m, 0), c + QPointF(m, 0))
        g.drawLine(c + QPointF(0, -m), c + QPointF(0, m))

    def to_dict(self):
        d = self._base_dict()
        d.update(pos=list(self.pos))
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(tuple(d["pos"]))

    def to_dxf(self, msp):
        msp.add_point(self.pos, dxfattribs=self.dxf_attribs())

    def props(self):
        return [("x", "X", fmt(self.pos[0])), ("y", "Y", fmt(self.pos[1]))]

    def set_prop(self, key, value):
        try:
            v = float(value)
        except ValueError:
            return False
        self.pos = (v, self.pos[1]) if key == "x" else (self.pos[0], v)
        return True


TEXT_LINE_STEP = 1.6        # interlineado en alturas de texto (como MTEXT)
_TEXT_FONT_PX = 100.0
_text_font: Optional["QtGui.QFont"] = None


def draw_cad_text(g: "QtGui.QPainter", at: QPointF, angle: float, hpx: float, text: str,
                  halign: int = 0, valign: int = 0):
    """Texto CAD a escala exacta: `hpx` es la altura de mayúsculas en píxeles.

    Se dibuja con una fuente de tamaño fijo y se escala el pintor, de modo que
    el tamaño no se redondea y en PDF/SVG el texto sigue siendo vectorial.
    """
    global _text_font
    if not text or hpx < 0.35:
        return
    lines = text.split("\n")
    step = hpx * TEXT_LINE_STEP
    total = hpx + (len(lines) - 1) * step
    ytop = {3: 0.0, 2: -total / 2}.get(valign, -total)     # borde superior (pantalla)
    g.save()
    g.translate(at)
    if angle:
        g.rotate(-math.degrees(angle))
    if hpx < 1.6:                         # demasiado pequeño: una raya representa la línea
        for i, ln in enumerate(lines):
            w = len(ln) * hpx * 0.6
            x = {1: -w / 2, 2: -w}.get(halign, 0.0)
            y = ytop + hpx + i * step
            g.drawLine(QPointF(x, y - hpx / 2), QPointF(x + w, y - hpx / 2))
        g.restore()
        return
    if _text_font is None:
        _text_font = QtGui.QFont("Helvetica")
        _text_font.setPixelSize(int(_TEXT_FONT_PX))
    g.setFont(_text_font)
    fm = QtGui.QFontMetricsF(_text_font)
    k = hpx / (fm.capHeight() or _TEXT_FONT_PX * 0.72)
    for i, ln in enumerate(lines):
        w = fm.horizontalAdvance(ln) * k
        x = {1: -w / 2, 2: -w}.get(halign, 0.0)
        y = ytop + hpx + i * step
        g.save()
        g.translate(x, y)
        g.scale(k, k)
        g.drawText(QPointF(0, 0), ln)
        g.restore()
    g.restore()


@register
class TextEnt(Entity):
    kind = "Text"

    def __init__(self, pos: Vec, text: str, height: float = 2.5,
                 angle: float = 0.0, halign: int = 0, valign: int = 0, **kw):
        super().__init__(**kw)
        self.pos = tuple(pos)
        self.text = str(text)
        self.height = float(height)
        self.angle = float(angle)
        self.halign = int(halign)       # 0 izquierda · 1 centro · 2 derecha
        self.valign = int(valign)       # 0 línea base · 1 inferior · 2 medio · 3 superior

    def bbox(self):
        lines = self.text.split("\n") or [""]
        h = self.height
        w = max(max(len(l) for l in lines), 1) * h * 0.6
        total = h + (len(lines) - 1) * h * TEXT_LINE_STEP
        x0 = {1: -w / 2, 2: -w}.get(self.halign, 0.0)
        ytop = {3: 0.0, 2: total / 2}.get(self.valign, total)
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        corners = [(x0, ytop - total), (x0 + w, ytop - total),
                   (x0 + w, ytop), (x0, ytop)]
        pts = [(self.pos[0] + x * ca - y * sa, self.pos[1] + x * sa + y * ca)
               for x, y in corners]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    def sample(self):
        x0, y0, x1, y1 = self.bbox()
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    def snaps(self):
        return [("ins", self.pos)]

    def dist_to(self, p):
        x0, y0, x1, y1 = self.bbox()
        if x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
            return 0.0
        return min(dist_point_seg(p, (x0, y0), (x1, y0)),
                   dist_point_seg(p, (x1, y0), (x1, y1)),
                   dist_point_seg(p, (x1, y1), (x0, y1)),
                   dist_point_seg(p, (x0, y1), (x0, y0)))

    def _map(self, fn):
        self.pos = fn(self.pos)

    def _rot_extra(self, a):
        self.angle += a

    def _scale_extra(self, f):
        self.height *= f

    def _mirror_extra(self, ax):
        self.angle = 2 * ax - self.angle

    def draw(self, g, view, pen):
        g.setPen(pen)
        draw_cad_text(g, view.to_screen(self.pos), self.angle, self.height * view.scale,
                      self.text, self.halign, self.valign)

    def to_dict(self):
        d = self._base_dict()
        d.update(pos=list(self.pos), text=self.text, height=self.height,
                 angle=self.angle, halign=self.halign, valign=self.valign)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(tuple(d["pos"]), d.get("text", ""), d.get("height", 2.5),
                   d.get("angle", 0.0), d.get("halign", 0), d.get("valign", 0))

    def to_dxf(self, msp):
        if "\n" in self.text:
            att = {3: 1, 2: 4}.get(self.valign, 7) + min(max(self.halign, 0), 2)
            msp.add_mtext(self.text.replace("\n", "\\P"), dxfattribs={
                **self.dxf_attribs(), "char_height": self.height, "insert": self.pos,
                "rotation": math.degrees(self.angle), "attachment_point": att})
            return
        t = msp.add_text(self.text, dxfattribs={
            **self.dxf_attribs(), "height": self.height,
            "rotation": math.degrees(self.angle)})
        try:
            if self.halign or self.valign:
                t.dxf.halign = self.halign
                t.dxf.valign = self.valign
                t.dxf.align_point = self.pos
            t.dxf.insert = self.pos
        except Exception:
            t.dxf.insert = self.pos

    def props(self):
        return [("txt", "Texto", self.text), ("h", "Altura", fmt(self.height)),
                ("rot", "Rotación", fmt(math.degrees(self.angle), 2)),
                ("x", "X", fmt(self.pos[0])), ("y", "Y", fmt(self.pos[1]))]

    def set_prop(self, key, value):
        if key == "txt":
            self.text = value
            return True
        try:
            v = float(value)
        except ValueError:
            return False
        if key == "h":
            self.height = abs(v) or 1.0
        elif key == "rot":
            self.angle = math.radians(v)
        elif key == "x":
            self.pos = (v, self.pos[1])
        elif key == "y":
            self.pos = (self.pos[0], v)
        else:
            return False
        return True


@register
class Leader(Entity):
    kind = "Leader"

    def __init__(self, points: List[Vec], text: str = "", height: float = 2.5, **kw):
        super().__init__(**kw)
        self.points = [tuple(p) for p in points]
        self.text = str(text)
        self.height = float(height)

    def primitives(self):
        return [("seg", self.points[i], self.points[i + 1])
                for i in range(len(self.points) - 1)]

    def snaps(self):
        return [("end", p) for p in self.points]

    def _map(self, fn):
        self.points = [fn(p) for p in self.points]

    def _scale_extra(self, f):
        self.height *= f

    def draw(self, g, view, pen):
        g.setPen(pen)
        g.setBrush(Qt.BrushStyle.NoBrush)
        if len(self.points) >= 2:
            g.drawPolyline(QtGui.QPolygonF([view.to_screen(p) for p in self.points]))
            view.draw_arrow(g, self.points[1], self.points[0], pen.color())
        if self.text and self.points:
            draw_cad_text(g, view.to_screen(self.points[-1]) + QPointF(6, -4), 0.0,
                          self.height * view.scale, self.text)

    def to_dict(self):
        d = self._base_dict()
        d.update(points=[list(p) for p in self.points], text=self.text,
                 height=self.height)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls([tuple(p) for p in d["points"]], d.get("text", ""),
                   d.get("height", 2.5))

    def to_dxf(self, msp):
        msp.add_lwpolyline(self.points, dxfattribs=self.dxf_attribs())
        if self.text:
            t = msp.add_text(self.text, dxfattribs={**self.dxf_attribs(),
                                                    "height": self.height})
            try:
                t.set_placement(self.points[-1])
            except Exception:
                pass

    def props(self):
        return [("txt", "Texto", self.text), ("h", "Altura", fmt(self.height))]

    def set_prop(self, key, value):
        if key == "txt":
            self.text = value
            return True
        if key == "h":
            try:
                self.height = abs(float(value)) or 1.0
                return True
            except ValueError:
                return False
        return False


@register
class Hatch(Entity):
    kind = "Hatch"

    def __init__(self, boundary: List[Vec], angle: float = math.pi / 4,
                 spacing: float = 2.0, solid: bool = False, **kw):
        super().__init__(**kw)
        self.boundary = [tuple(p) for p in boundary]
        self.angle = float(angle)
        self.spacing = float(spacing)
        self.solid = bool(solid)

    def polygon(self):
        return list(self.boundary) if len(self.boundary) >= 3 else None

    def primitives(self):
        n = len(self.boundary)
        return [("seg", self.boundary[i], self.boundary[(i + 1) % n]) for i in range(n)]

    def snaps(self):
        return [("end", p) for p in self.boundary]

    def _map(self, fn):
        self.boundary = [fn(p) for p in self.boundary]

    def _rot_extra(self, a):
        self.angle += a

    def _scale_extra(self, f):
        self.spacing *= f

    def draw(self, g, view, pen):
        g.setPen(pen)
        poly = QtGui.QPolygonF([view.to_screen(p) for p in self.boundary])
        if self.solid:
            col = QtGui.QColor(pen.color())
            col.setAlpha(90)
            g.setBrush(QtGui.QBrush(col))
            g.drawPolygon(poly)
            g.setBrush(Qt.BrushStyle.NoBrush)
            return
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.drawPolygon(poly)
        thin = QtGui.QPen(pen)
        thin.setWidthF(max(0.8, pen.widthF() * 0.6))
        g.setPen(thin)
        for a, b in hatch_lines(self.boundary, self.angle, self.spacing):
            g.drawLine(view.to_screen(a), view.to_screen(b))

    def to_dict(self):
        d = self._base_dict()
        d.update(boundary=[list(p) for p in self.boundary], angle=self.angle,
                 spacing=self.spacing, solid=self.solid)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls([tuple(p) for p in d["boundary"]], d.get("angle", 0.785),
                   d.get("spacing", 2.0), d.get("solid", False))

    def to_dxf(self, msp):
        msp.add_lwpolyline(self.boundary, close=True, dxfattribs=self.dxf_attribs())
        if not self.solid:
            for a, b in hatch_lines(self.boundary, self.angle, self.spacing):
                msp.add_line(a, b, dxfattribs=self.dxf_attribs())

    def props(self):
        return [("ang", "Ángulo", fmt(math.degrees(self.angle), 2)),
                ("sp", "Separación", fmt(self.spacing)),
                ("solid", "Sólido (0/1)", "1" if self.solid else "0"),
                ("area", "Área", fmt(self.area()))]

    def set_prop(self, key, value):
        if key == "solid":
            self.solid = value.strip() in ("1", "true", "si", "sí")
            return True
        try:
            v = float(value)
        except ValueError:
            return False
        if key == "ang":
            self.angle = math.radians(v)
        elif key == "sp":
            self.spacing = max(abs(v), 1e-3)
        else:
            return False
        return True


@register
class Dimension(Entity):
    """Cota: aligned | horizontal | vertical | radius | diameter | angular."""
    kind = "Dimension"

    def __init__(self, dtype: str, p1: Vec, p2: Vec, pos: Vec,
                 p3: Optional[Vec] = None, text: Optional[str] = None,
                 height: float = 2.5, **kw):
        super().__init__(**kw)
        self.dtype = dtype
        self.p1 = tuple(p1)
        self.p2 = tuple(p2)
        self.pos = tuple(pos)
        self.p3 = tuple(p3) if p3 else None
        self.text = text
        self.height = float(height)

    # -- cálculo de la geometría de cota --------------------------------- #
    def geometry(self):
        """Devuelve (lista_de_segmentos, punto_texto, angulo_texto, etiqueta)."""
        segs: List[Tuple[Vec, Vec]] = []
        if self.dtype in ("aligned", "horizontal", "vertical"):
            if self.dtype == "horizontal":
                d = (1.0, 0.0)
            elif self.dtype == "vertical":
                d = (0.0, 1.0)
            else:
                d = vnorm(vsub(self.p2, self.p1)) or (1.0, 0.0)
            n = vperp(d)
            off = vdot(vsub(self.pos, self.p1), n)
            t1 = vdot(vsub(self.p1, self.p1), d)
            t2 = vdot(vsub(self.p2, self.p1), d)
            base = self.p1
            q1 = vadd(vadd(base, vmul(d, t1)), vmul(n, off))
            q2 = vadd(vadd(base, vmul(d, t2)), vmul(n, off))
            value = abs(t2 - t1)
            segs += [(self.p1, q1), (self.p2, q2), (q1, q2)]
            mid = vlerp(q1, q2, 0.5)
            ang = math.atan2(d[1], d[0])
            if ang > math.pi / 2 or ang < -math.pi / 2:
                ang += math.pi
            tp = vadd(mid, vmul(vperp((math.cos(ang), math.sin(ang))),
                                self.height * 0.5))
            label = self.text or fmt(value, 2)
            return segs, tp, ang, label, (q1, q2)
        if self.dtype in ("radius", "diameter"):
            c = self.p1
            r = vdist(self.p1, self.p2)
            d = vnorm(vsub(self.p2, c)) or (1.0, 0.0)
            a = vadd(c, vmul(d, r))
            b = vsub(c, vmul(d, r)) if self.dtype == "diameter" else c
            segs.append((b, a))
            segs.append((a, self.pos))
            value = 2 * r if self.dtype == "diameter" else r
            pre = "Ø" if self.dtype == "diameter" else "R"
            label = self.text or (pre + fmt(value, 2))
            return segs, vadd(self.pos, (self.height * 0.3, self.height * 0.3)), 0.0, \
                label, (b, a)
        # angular
        v = self.p1
        a1 = vangle(v, self.p2)
        a2 = vangle(v, self.p3 or self.p2)
        r = vdist(v, self.pos)
        pts = arc_points(v, r, a1, a2)
        for i in range(len(pts) - 1):
            segs.append((pts[i], pts[i + 1]))
        segs.append((v, vadd(v, vmul(vnorm(vsub(self.p2, v)), r * 1.1))))
        segs.append((v, vadd(v, vmul(vnorm(vsub(self.p3 or self.p2, v)), r * 1.1))))
        deg = math.degrees(norm_ang(a2 - a1))
        label = self.text or (fmt(deg, 2) + "°")
        tp = pts[len(pts) // 2]
        return segs, tp, 0.0, label, (pts[0], pts[-1])

    def primitives(self):
        segs, _, _, _, _ = self.geometry()
        return [("seg", a, b) for a, b in segs]

    def snaps(self):
        return [("end", self.p1), ("end", self.p2)]

    def _map(self, fn):
        self.p1 = fn(self.p1)
        self.p2 = fn(self.p2)
        self.pos = fn(self.pos)
        if self.p3:
            self.p3 = fn(self.p3)

    def _scale_extra(self, f):
        self.height *= f

    def measurement(self) -> float:
        if self.dtype == "horizontal":
            return abs(self.p2[0] - self.p1[0])
        if self.dtype == "vertical":
            return abs(self.p2[1] - self.p1[1])
        if self.dtype == "radius":
            return vdist(self.p1, self.p2)
        if self.dtype == "diameter":
            return 2 * vdist(self.p1, self.p2)
        if self.dtype == "angular":
            return math.degrees(norm_ang(vangle(self.p1, self.p3 or self.p2) -
                                         vangle(self.p1, self.p2)))
        return vdist(self.p1, self.p2)

    def draw(self, g, view, pen):
        segs, tp, ang, label, arrows = self.geometry()
        g.setPen(pen)
        g.setBrush(Qt.BrushStyle.NoBrush)
        for a, b in segs:
            g.drawLine(view.to_screen(a), view.to_screen(b))
        a, b = arrows
        view.draw_arrow(g, b, a, pen.color())
        view.draw_arrow(g, a, b, pen.color())
        draw_cad_text(g, view.to_screen(tp), ang, self.height * view.scale, label, 1, 1)

    def to_dict(self):
        d = self._base_dict()
        d.update(dtype=self.dtype, p1=list(self.p1), p2=list(self.p2),
                 pos=list(self.pos), p3=list(self.p3) if self.p3 else None,
                 text=self.text, height=self.height)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("dtype", "aligned"), tuple(d["p1"]), tuple(d["p2"]),
                   tuple(d["pos"]), tuple(d["p3"]) if d.get("p3") else None,
                   d.get("text"), d.get("height", 2.5))

    def to_dxf(self, msp):
        for pr in self.primitives():
            msp.add_line(pr[1], pr[2], dxfattribs=self.dxf_attribs())
        _, tp, ang, label, _ = self.geometry()
        t = msp.add_text(label, dxfattribs={**self.dxf_attribs(),
                                            "height": self.height,
                                            "rotation": math.degrees(ang)})
        try:
            t.set_placement(tp)
        except Exception:
            pass

    def explode(self):
        out: List[Entity] = [Line(pr[1], pr[2], layer=self.layer)
                             for pr in self.primitives()]
        _, tp, ang, label, _ = self.geometry()
        out.append(TextEnt(tp, label, self.height, ang, layer=self.layer))
        return out

    def props(self):
        return [("type", "Tipo", self.dtype),
                ("val", "Medición", fmt(self.measurement(), 3)),
                ("txt", "Texto (vacío=auto)", self.text or ""),
                ("h", "Altura texto", fmt(self.height))]

    def set_prop(self, key, value):
        if key == "txt":
            self.text = value or None
            return True
        if key == "h":
            try:
                self.height = abs(float(value)) or 1.0
                return True
            except ValueError:
                return False
        return False


_ACTIVE_DOC: Optional["Document"] = None


@register
class BlockRef(Entity):
    kind = "BlockRef"

    def __init__(self, name: str, pos: Vec, scale: float = 1.0,
                 rot: float = 0.0, **kw):
        super().__init__(**kw)
        self.name = name
        self.pos = tuple(pos)
        self.sc = float(scale)
        self.rot = float(rot)

    def children(self) -> List[Entity]:
        doc = _ACTIVE_DOC
        if doc is None or self.name not in doc.blocks:
            return []
        out = []
        for e in doc.blocks[self.name]:
            c = copy.deepcopy(e)
            c.scale((0.0, 0.0), self.sc)
            c.rotate((0.0, 0.0), self.rot)
            c.translate(self.pos)
            c.layer = self.layer
            c.color = self.color
            out.append(c)
        return out

    def primitives(self):
        out = []
        for c in self.children():
            out += c.primitives()
        return out

    def sample(self):
        out = [self.pos]
        for c in self.children():
            out += c.sample()
        return out

    def snaps(self):
        out = [("ins", self.pos)]
        for c in self.children():
            out += c.snaps()
        return out

    def _map(self, fn):
        self.pos = fn(self.pos)

    def _rot_extra(self, a):
        self.rot += a

    def _scale_extra(self, f):
        self.sc *= f

    def draw(self, g, view, pen):
        for c in self.children():
            c.draw(g, view, pen)
        if getattr(view, "plotting", False):
            return
        g.setPen(pen)
        s = view.to_screen(self.pos)
        g.drawLine(s + QPointF(-3, 0), s + QPointF(3, 0))
        g.drawLine(s + QPointF(0, -3), s + QPointF(0, 3))

    def explode(self):
        return self.children()

    def to_dict(self):
        d = self._base_dict()
        d.update(name=self.name, pos=list(self.pos), sc=self.sc, rot=self.rot)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], tuple(d["pos"]), d.get("sc", 1.0), d.get("rot", 0.0))

    def to_dxf(self, msp):
        for c in self.children():
            c.to_dxf(msp)

    def props(self):
        return [("name", "Bloque", self.name), ("x", "X", fmt(self.pos[0])),
                ("y", "Y", fmt(self.pos[1])), ("sc", "Escala", fmt(self.sc)),
                ("rot", "Rotación", fmt(math.degrees(self.rot), 2))]

    def set_prop(self, key, value):
        try:
            v = float(value)
        except ValueError:
            return False
        if key == "x":
            self.pos = (v, self.pos[1])
        elif key == "y":
            self.pos = (self.pos[0], v)
        elif key == "sc":
            self.sc = v or 1.0
        elif key == "rot":
            self.rot = math.radians(v)
        else:
            return False
        return True


# =========================================================================== #
#  3. DOCUMENTO, CAPAS Y ENTRADA/SALIDA
# =========================================================================== #
class Layer:
    def __init__(self, name: str, color: str = "#e2e2e6", visible: bool = True,
                 locked: bool = False, linetype: str = "Continuous",
                 lineweight: float = LW_DEFAULT, plot: bool = True):
        self.name = name
        self.color = color
        self.visible = visible
        self.locked = locked
        self.linetype = linetype
        self.lineweight = lineweight
        self.plot = plot                 # False = la capa no se imprime

    def to_dict(self):
        return dict(name=self.name, color=self.color, visible=self.visible,
                    locked=self.locked, linetype=self.linetype,
                    lineweight=self.lineweight, plot=self.plot)

    @staticmethod
    def from_dict(d):
        return Layer(d["name"], d.get("color", "#e2e2e6"), d.get("visible", True),
                     d.get("locked", False), d.get("linetype", "Continuous"),
                     d.get("lineweight", LW_DEFAULT), d.get("plot", True))


#: Patrones de trazo en milímetros de papel (trazo, hueco, …).
LINETYPES = {
    "Continuous": [],
    "Dashed": [6, 3],
    "Dotted": [0.5, 2],
    "DashDot": [8, 2.5, 0.5, 2.5],
    "Hidden": [3, 1.5],
    "Center": [12, 3, 3, 3],
    "Phantom": [12, 2.5, 3, 2.5, 3, 2.5],
}
LT_LABEL = {"ByLayer": "PorCapa", "Continuous": "Continua", "Dashed": "Trazos",
            "Dotted": "Puntos", "DashDot": "Trazo-punto", "Hidden": "Oculta",
            "Center": "Eje", "Phantom": "Fantasma"}
#: nombre interno -> nombre de tipo de línea estándar en DXF (ezdxf setup=True)
LT_DXF = {"Continuous": "Continuous", "Dashed": "DASHED", "Dotted": "DOT",
          "DashDot": "DASHDOT", "Hidden": "HIDDEN", "Center": "CENTER",
          "Phantom": "PHANTOM"}


def lt_from_dxf(name: str) -> str:
    """Traduce un nombre de tipo de línea DXF al catálogo interno."""
    n = (name or "").upper()
    if n in ("", "BYLAYER", "BYBLOCK"):
        return LT_BYLAYER
    if n == "CONTINUOUS":
        return "Continuous"
    for key, pre in (("DASHDOT", "DashDot"), ("DOT", "Dotted"),
                     ("HIDDEN", "Hidden"), ("CENTER", "Center"), ("PHANTOM", "Phantom"),
                     ("DASH", "Dashed"), ("BORDER", "DashDot"), ("DIVIDE", "Phantom")):
        if key in n:
            return pre
    return "Dashed" if "TRAZ" in n or "DASH" in n else "Continuous"


class Document:
    UNDO_LIMIT = 80

    def __init__(self):
        global _ACTIVE_DOC
        self.entities: List[Entity] = []
        self.layers: Dict[str, Layer] = {"0": Layer("0")}
        self.current_layer = "0"
        # propiedades que reciben los objetos nuevos (None/-1/ByLayer = PorCapa)
        self.current_color: Optional[str] = None
        self.current_lineweight: float = LW_BYLAYER
        self.current_linetype: str = LT_BYLAYER
        self.blocks: Dict[str, List[Entity]] = {}
        self.groups: Dict[int, str] = {}
        self.units = "mm"
        self.filename: Optional[str] = None
        self.modified = False
        self.last_import_skipped: Dict[str, int] = {}
        self.last_import_notes: List[str] = []
        self._undo: List[Tuple[str, Any]] = []
        self._redo: List[Tuple[str, Any]] = []
        _ACTIVE_DOC = self

    # --- estado / deshacer ---------------------------------------------- #
    def _state(self):
        return (copy.deepcopy(self.entities), copy.deepcopy(self.layers),
                copy.deepcopy(self.blocks), dict(self.groups), self.current_layer)

    def _restore(self, st):
        self.entities, self.layers, self.blocks, self.groups, self.current_layer = \
            st[0], st[1], st[2], dict(st[3]), st[4]

    def push_undo(self, label: str = ""):
        self._undo.append((label, self._state()))
        if len(self._undo) > self.UNDO_LIMIT:
            self._undo.pop(0)
        self._redo.clear()
        self.modified = True

    def undo(self) -> Optional[str]:
        if not self._undo:
            return None
        label, st = self._undo.pop()
        self._redo.append((label, self._state()))
        self._restore(st)
        self.modified = True
        return label or "operación"

    def redo(self) -> Optional[str]:
        if not self._redo:
            return None
        label, st = self._redo.pop()
        self._undo.append((label, self._state()))
        self._restore(st)
        self.modified = True
        return label or "operación"

    # --- capas ------------------------------------------------------------ #
    def add_layer(self, name: str, color: Optional[str] = None) -> Layer:
        if name not in self.layers:
            if color is None:
                color = PALETTE[len(self.layers) % len(PALETTE)]
            self.layers[name] = Layer(name, color)
        return self.layers[name]

    def layer_of(self, e: Entity) -> Layer:
        return self.layers.get(e.layer) or self.layers[self.current_layer]

    def color_of(self, e: Entity) -> str:
        return e.color or self.layer_of(e).color

    def lineweight_of(self, e: Entity) -> float:
        """Grosor efectivo en mm (resuelve PorCapa)."""
        lw = e.lineweight
        if lw is None or lw < 0:
            lw = self.layer_of(e).lineweight
        return max(0.0, float(lw if lw is not None else LW_DEFAULT))

    def linetype_of(self, e: Entity) -> str:
        lt = e.linetype
        if not lt or lt in (LT_BYLAYER, "BYLAYER", "ByBlock", "BYBLOCK"):
            lt = self.layer_of(e).linetype
        return lt if lt in LINETYPES else "Continuous"

    def apply_current(self, e: Entity):
        """Asigna a una entidad nueva las propiedades actuales del dibujo."""
        if e.color is None and self.current_color:
            e.color = self.current_color
        if (e.lineweight is None or e.lineweight < 0) and self.current_lineweight >= 0:
            e.lineweight = self.current_lineweight
        if e.linetype in (None, "", LT_BYLAYER) and self.current_linetype != LT_BYLAYER:
            e.linetype = self.current_linetype

    def is_editable(self, e: Entity) -> bool:
        lay = self.layers.get(e.layer)
        return bool(lay and lay.visible and not lay.locked)

    def visible_entities(self) -> List[Entity]:
        return [e for e in self.entities
                if (self.layers.get(e.layer) or Layer("?")).visible]

    # --- entidades --------------------------------------------------------- #
    def add(self, e: Entity) -> Entity:
        if e.layer not in self.layers:
            e.layer = self.current_layer
        self.entities.append(e)
        self.modified = True
        return e

    def remove(self, ents: List[Entity]):
        ids = {id(e) for e in ents}
        self.entities = [e for e in self.entities if id(e) not in ids]
        self.modified = True

    def selection(self) -> List[Entity]:
        return [e for e in self.entities if e.selected]

    def clear_selection(self):
        for e in self.entities:
            e.selected = False

    def select_all(self):
        for e in self.entities:
            if self.is_editable(e):
                e.selected = True

    def expand_groups(self, ents: List[Entity]) -> List[Entity]:
        gids = {e.group for e in ents if e.group is not None}
        if not gids:
            return ents
        out = list(ents)
        for e in self.entities:
            if e.group in gids and e not in out:
                out.append(e)
        return out

    def bbox(self, ents: Optional[List[Entity]] = None):
        ents = ents if ents is not None else self.visible_entities()
        if not ents:
            return None
        bb = [e.bbox() for e in ents]
        return (min(b[0] for b in bb), min(b[1] for b in bb),
                max(b[2] for b in bb), max(b[3] for b in bb))

    # --- E/S --------------------------------------------------------------- #
    def to_json(self) -> str:
        return json.dumps({
            "app": APP_NAME, "version": APP_VERSION, "units": self.units,
            "current_layer": self.current_layer,
            "current_color": self.current_color,
            "current_lineweight": self.current_lineweight,
            "current_linetype": self.current_linetype,
            "layers": [l.to_dict() for l in self.layers.values()],
            "blocks": {k: [e.to_dict() for e in v] for k, v in self.blocks.items()},
            "groups": {str(k): v for k, v in self.groups.items()},
            "entities": [e.to_dict() for e in self.entities],
        }, indent=1, ensure_ascii=False)

    def load_json(self, text: str):
        d = json.loads(text)
        self.layers = {}
        for ld in d.get("layers", []):
            l = Layer.from_dict(ld)
            self.layers[l.name] = l
        if not self.layers:
            self.layers = {"0": Layer("0")}
        self.current_layer = d.get("current_layer", list(self.layers)[0])
        self.units = d.get("units", "mm")
        self.blocks = {k: [x for x in (Entity.build(e) for e in v) if x]
                       for k, v in d.get("blocks", {}).items()}
        self.groups = {int(k): v for k, v in d.get("groups", {}).items()}
        self.current_color = d.get("current_color")
        self.current_lineweight = d.get("current_lineweight", LW_BYLAYER)
        self.current_linetype = d.get("current_linetype", LT_BYLAYER)
        try:
            legacy = float(str(d.get("version", "0")).split(".")[0]) < 5
        except ValueError:
            legacy = True
        self.entities = []
        for ed in d.get("entities", []):
            e = Entity.build(ed)
            if e:
                if legacy:
                    # Antes de 5.0 todas las entidades guardaban 0.25/Continuous
                    # aunque en la práctica seguían a la capa.
                    if e.lineweight == 0.25:
                        e.lineweight = LW_BYLAYER
                    if e.linetype == "Continuous":
                        e.linetype = LT_BYLAYER
                self.entities.append(e)
        self._undo.clear()
        self._redo.clear()
        self.modified = False

    def export_dxf(self, path: str):
        if not HAS_EZDXF:
            raise RuntimeError("ezdxf no está instalado:  pip install ezdxf")
        doc = ezdxf.new("R2010", setup=True)
        doc.header["$LWDISPLAY"] = 1
        doc.header["$INSUNITS"] = {"mm": 4, "cm": 5, "m": 6, "in": 1, "ft": 2}.get(
            self.units, 4)
        msp = doc.modelspace()
        for lay in self.layers.values():
            if lay.name not in doc.layers:
                doc.layers.add(lay.name)
            try:
                dl = doc.layers.get(lay.name)
                dl.rgb = _hex_rgb(lay.color)
                dl.dxf.linetype = LT_DXF.get(lay.linetype, "Continuous")
                dl.dxf.lineweight = int(round(max(lay.lineweight, 0) * 100))
                dl.dxf.plot = 1 if lay.plot else 0
                if not lay.visible:
                    dl.off()
                if lay.locked:
                    dl.lock()
            except Exception:
                pass
        for e in self.entities:
            try:
                e.to_dxf(msp)
            except Exception:
                traceback.print_exc()
        doc.saveas(path)

    def import_dxf(self, path: str) -> int:
        return self.merge_import(read_drawing(path))

    def import_dwg(self, path: str) -> int:
        """Importa un DWG convirtiéndolo antes a DXF con un conversor externo."""
        return self.merge_import(read_drawing(path))

    def merge_import(self, res: "ImportResult") -> int:
        """Incorpora al documento el resultado de `read_drawing`."""
        empty = not self.entities
        for ld in res.layers:
            if ld.name not in self.layers:
                self.layers[ld.name] = ld
            elif empty:
                cur = self.layers[ld.name]
                cur.color, cur.linetype, cur.lineweight = ld.color, ld.linetype, ld.lineweight
                cur.visible, cur.locked, cur.plot = ld.visible, ld.locked, ld.plot
        for e in res.entities:
            if e.layer not in self.layers:
                self.add_layer(e.layer)
            self.entities.append(e)
        if empty and res.units:
            self.units = res.units
        self.modified = True
        self.last_import_skipped = res.skipped
        self.last_import_notes = res.notes
        return len(res.entities)

    def export_dwg(self, path: str, version: str = "ACAD2018") -> str:
        """Exporta a DWG pasando por un DXF temporal."""
        if not HAS_EZDXF:
            raise RuntimeError("ezdxf no está instalado:  pip install ezdxf")
        tmp_dir = tempfile.mkdtemp(prefix="vcad_dwg_out_")
        try:
            tmp_dxf = os.path.join(tmp_dir, os.path.splitext(os.path.basename(path))[0] + ".dxf")
            self.export_dxf(tmp_dxf)
            return dxf_to_dwg(tmp_dxf, path, version=version)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def export_svg(self, path: str, margin: float = 10.0):
        bb = self.bbox() or (0, 0, 100, 100)
        x0, y0, x1, y1 = bb
        w = (x1 - x0) + 2 * margin
        h = (y1 - y0) + 2 * margin
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}mm" '
                 f'height="{h:.2f}mm" viewBox="0 0 {w:.4f} {h:.4f}">',
                 f'<g transform="translate({-x0 + margin:.4f},{y1 + margin:.4f}) '
                 f'scale(1,-1)">']
        for e in self.entities:
            col = self.color_of(e)
            if not self.layer_of(e).visible:
                continue
            lw = max(self.lineweight_of(e), 0.05)
            for pr in e.primitives():
                if pr[0] == "seg":
                    parts.append(f'<line x1="{pr[1][0]:.4f}" y1="{pr[1][1]:.4f}" '
                                 f'x2="{pr[2][0]:.4f}" y2="{pr[2][1]:.4f}" '
                                 f'stroke="{col}" stroke-width="{lw}"/>')
                else:
                    pts = arc_points(pr[1], pr[2], pr[3], pr[4])
                    d = " ".join(f"{p[0]:.4f},{p[1]:.4f}" for p in pts)
                    parts.append(f'<polyline points="{d}" fill="none" '
                                 f'stroke="{col}" stroke-width="{lw}"/>')
            if isinstance(e, TextEnt):
                parts.append(
                    f'<text x="{e.pos[0]:.4f}" y="{e.pos[1]:.4f}" fill="{col}" '
                    f'font-size="{e.height}" transform="scale(1,-1) '
                    f'translate(0,{-2 * e.pos[1]:.4f})">{_xml_escape(e.text)}</text>')
        parts += ["</g>", "</svg>"]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))


def _xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _hex_rgb(h: str):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


#: Longitud con la que se materializan las líneas infinitas (XLINE, RAY).
INFINITE_LINE_LENGTH = 1.0e4

_BYBLOCK = "BYBLOCK"
_LW_BYBLOCK = -2.0


class ImportResult:
    """Resultado de leer un DXF/DWG, construido fuera del hilo de la interfaz."""

    def __init__(self):
        self.layers: List[Layer] = []
        self.entities: List[Entity] = []
        self.skipped: Dict[str, int] = {}
        self.units: Optional[str] = None
        self.notes: List[str] = []


def _aci_hex(aci: int) -> str:
    try:
        r, g, b = ezdxf.colors.aci2rgb(int(aci))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#e2e2e6"


def _dxf_color(e) -> Optional[str]:
    """Color de una entidad DXF: None = PorCapa, _BYBLOCK = PorBloque."""
    try:
        if e.dxf.hasattr("true_color"):
            r, g, b = ezdxf.colors.int2rgb(e.dxf.true_color)
            return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        pass
    aci = getattr(e.dxf, "color", 256)
    if aci is None or aci == 256:
        return None
    if aci == 0:
        return _BYBLOCK
    return _aci_hex(abs(aci))


def _dxf_lineweight(e) -> float:
    lw = getattr(e.dxf, "lineweight", -1)
    if lw is None or lw == -1:
        return LW_BYLAYER
    if lw == -2:
        return _LW_BYBLOCK
    if lw == -3:
        return LW_DEFAULT
    return max(0.0, lw / 100.0)


def _apply_dxf_style(new: List[Entity], e):
    """Copia color, tipo y grosor de la entidad DXF a las entidades nuevas."""
    col = _dxf_color(e)
    lw = _dxf_lineweight(e)
    lt = lt_from_dxf(getattr(e.dxf, "linetype", "BYLAYER"))
    for n in new:
        if getattr(n, "_dxf_styled", False):
            continue
        n.color, n.lineweight, n.linetype = col, lw, lt
        n._dxf_styled = True


def _resolve_byblock(subs: List[Entity], ins) -> None:
    """Las entidades de un bloque heredan del INSERT lo marcado PorBloque."""
    lay = getattr(ins.dxf, "layer", "0")
    col = _dxf_color(ins)
    lw = _dxf_lineweight(ins)
    for s in subs:
        if s.layer == "0":
            s.layer = lay
        if s.color == _BYBLOCK:
            s.color = None if col in (None, _BYBLOCK) else col
        if s.lineweight == _LW_BYBLOCK:
            s.lineweight = LW_BYLAYER if lw in (LW_BYLAYER, _LW_BYBLOCK) else lw


def _clean_styles(ents: List[Entity]):
    for n in ents:
        if n.color == _BYBLOCK:
            n.color = None
        if n.lineweight == _LW_BYBLOCK:
            n.lineweight = LW_BYLAYER
        if hasattr(n, "_dxf_styled"):
            del n._dxf_styled


def read_drawing(path: str, progress: Optional[Callable[[str], None]] = None
                 ) -> ImportResult:
    """Lee un DXF o DWG y lo traduce al modelo interno (sin tocar la GUI)."""
    if not HAS_EZDXF:
        raise RuntimeError("ezdxf no está instalado:  pip install ezdxf")
    say = progress or (lambda s: None)
    res = ImportResult()
    tmp_dir = None
    src = path
    try:
        if path.lower().endswith(".dwg"):
            say(f"Convirtiendo DWG con {dwg_converter_name()}…")
            tmp_dir = tempfile.mkdtemp(prefix="vcad_dwg_")
            src = dwg_to_dxf(path, out_dir=tmp_dir)
        say("Leyendo DXF…")
        try:
            dwg = ezdxf.readfile(src)
        except Exception:
            from ezdxf import recover
            dwg, auditor = recover.readfile(src)
            res.notes.append(f"El archivo tenía errores estructurales; se recuperó "
                             f"({len(auditor.fixes)} correcciones).")
        units = {1: "in", 2: "ft", 4: "mm", 5: "cm", 6: "m"}.get(
            int(dwg.header.get("$INSUNITS", 0) or 0))
        res.units = units
        for lay in dwg.layers:
            try:
                name = lay.dxf.name
                if lay.dxf.hasattr("true_color"):
                    r, g, b = lay.rgb
                    col = f"#{r:02x}{g:02x}{b:02x}"
                else:
                    col = _aci_hex(abs(lay.dxf.color or 7))
                lw = lay.dxf.lineweight
                lw = LW_DEFAULT if lw is None or lw < 0 else lw / 100.0
                lt = lt_from_dxf(lay.dxf.linetype)
                if lt == LT_BYLAYER:
                    lt = "Continuous"
                plot = bool(getattr(lay.dxf, "plot", 1)) and name.lower() != "defpoints"
                res.layers.append(Layer(name, col, not lay.is_off(), lay.is_locked(),
                                        lt, lw, plot))
            except Exception:
                continue
        msp = dwg.modelspace()
        say("Traduciendo entidades…")
        for e in msp:
            res.entities += _from_dxf_entity(e, res.skipped)
        _clean_styles(res.entities)
        # Algunos conversores (LibreDWG con DWG 2004–2007) leen mal el bit
        # «encendida» y entregan todas las capas apagadas: el dibujo se vería
        # vacío. Si ninguna capa con contenido queda visible, se encienden.
        used = {e.layer for e in res.entities}
        lays = [l for l in res.layers if l.name in used]
        if lays and not any(l.visible for l in lays):
            for l in res.layers:
                l.visible = True
            res.notes.append("Todas las capas venían apagadas (lectura del conversor); "
                             "se encendieron para mostrar el dibujo.")
        return res
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _from_dxf_entity(e, skipped: Optional[Dict[str, int]] = None,
                     depth: int = 0) -> List[Entity]:
    out = _from_dxf_entity_raw(e, skipped, depth)
    if out:
        _apply_dxf_style(out, e)
    return out


def _from_dxf_entity_raw(e, skipped: Optional[Dict[str, int]] = None,
                         depth: int = 0) -> List[Entity]:
    """Convierte una entidad DXF de ezdxf al modelo interno.

    `skipped` acumula, por tipo DXF, las entidades que no se pudieron traducir,
    para poder informarlo al usuario en vez de perderlas en silencio.
    """
    t = e.dxftype()
    lay = getattr(e.dxf, "layer", "0")

    def _skip() -> List[Entity]:
        if skipped is not None:
            skipped[t] = skipped.get(t, 0) + 1
        return []

    try:
        if t == "LINE":
            return [Line((e.dxf.start.x, e.dxf.start.y),
                         (e.dxf.end.x, e.dxf.end.y), layer=lay)]
        if t == "CIRCLE":
            return [Circle((e.dxf.center.x, e.dxf.center.y), e.dxf.radius, layer=lay)]
        if t == "ARC":
            return [Arc((e.dxf.center.x, e.dxf.center.y), e.dxf.radius,
                        math.radians(e.dxf.start_angle),
                        math.radians(e.dxf.end_angle), layer=lay)]
        if t == "ELLIPSE":
            major = (e.dxf.major_axis.x, e.dxf.major_axis.y)
            rx = vlen(major)
            return [Ellipse((e.dxf.center.x, e.dxf.center.y), rx, rx * e.dxf.ratio,
                            math.atan2(major[1], major[0]), layer=lay)]
        if t == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
            return [Polyline(pts, bool(e.closed), layer=lay)]
        if t == "POLYLINE":
            pts = [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
            return [Polyline(pts, bool(e.is_closed), layer=lay)]
        if t == "POINT":
            return [PointEnt((e.dxf.location.x, e.dxf.location.y), layer=lay)]
        if t == "TEXT" or t == "ATTRIB":
            txt = e.plain_text() if hasattr(e, "plain_text") else e.dxf.text
            h = getattr(e.dxf, "height", 2.5) or 2.5
            rot = math.radians(getattr(e.dxf, "rotation", 0.0) or 0.0)
            ha = int(getattr(e.dxf, "halign", 0) or 0)
            va = int(getattr(e.dxf, "valign", 0) or 0)
            p = e.dxf.insert
            if (ha or va) and ha not in (3, 5) and e.dxf.hasattr("align_point"):
                p = e.dxf.align_point
            if ha == 4:                      # «middle»: centrado en ambos sentidos
                ha, va = 1, 2
            if ha in (3, 5):
                ha, va = 0, 0
            return [TextEnt((p.x, p.y), txt, h, rot, min(ha, 2), va, layer=lay)]
        if t == "MTEXT":
            txt = e.plain_text(split=False) if hasattr(e, "plain_text") else e.text
            h = getattr(e.dxf, "char_height", 2.5) or 2.5
            try:
                rot = math.radians(e.get_rotation())
            except Exception:
                rot = math.radians(getattr(e.dxf, "rotation", 0.0) or 0.0)
            att = int(getattr(e.dxf, "attachment_point", 1) or 1)
            ha = (att - 1) % 3
            va = {0: 3, 1: 2, 2: 1}[(att - 1) // 3]
            ins = e.dxf.insert
            return [TextEnt((ins.x, ins.y), txt.replace("\r", ""), h, rot, ha, va, layer=lay)]
        if t == "SPLINE":
            pts = [(p.x, p.y) for p in e.flattening(0.05)]
            return [Polyline(pts, False, layer=lay)]
        if t in ("XLINE", "RAY"):
            # Líneas infinitas: se materializan acotadas para que sigan siendo
            # geometría utilizable sin arruinar la extensión del dibujo.
            p = e.dxf.start
            v = e.dxf.unit_vector
            L = INFINITE_LINE_LENGTH
            a = (p.x, p.y) if t == "RAY" else (p.x - v.x * L, p.y - v.y * L)
            b = (p.x + v.x * L, p.y + v.y * L)
            return [Line(a, b, layer=lay)]
        if t in ("SOLID", "TRACE", "3DFACE"):
            # El cuarto vértice puede repetir al tercero (triángulos).
            idx = [0, 1, 3, 2] if t in ("SOLID", "TRACE") else [0, 1, 2, 3]
            pts = []
            for i in idx:
                try:
                    v = getattr(e.dxf, f"vtx{i}")
                except Exception:
                    continue
                p = (v.x, v.y)
                if not pts or vlen((p[0] - pts[-1][0], p[1] - pts[-1][1])) > 1e-9:
                    pts.append(p)
            if len(pts) >= 3:
                return [Polyline(pts, True, layer=lay)]
            return _skip()
        if t == "HATCH":
            out: List[Entity] = []
            try:
                from ezdxf.path import from_hatch
                for path in from_hatch(e):
                    pts = [(p.x, p.y) for p in path.flattening(0.5)]
                    if len(pts) >= 2:
                        out.append(Polyline(pts, True, layer=lay))
            except Exception:
                for bp in getattr(e, "paths", []):
                    pts = [(v[0], v[1]) for v in getattr(bp, "vertices", [])]
                    if len(pts) >= 2:
                        out.append(Polyline(pts, True, layer=lay))
            return out or _skip()
        if t == "INSERT":
            out = []
            for sub in e.virtual_entities():
                out += _from_dxf_entity(sub, skipped, depth + 1)
            _resolve_byblock(out, e)
            return out
        if depth < 3:
            # Cotas, directrices múltiples, mlines y tablas: se explota la
            # geometría que el propio DXF lleva asociada.
            block = None
            if hasattr(e, "get_geometry_block"):
                try:
                    block = e.get_geometry_block()
                except Exception:
                    block = None
            if block is not None:
                out = []
                for sub in block:
                    out += _from_dxf_entity(sub, skipped, depth + 1)
                if out:
                    return out
            if hasattr(e, "virtual_entities"):
                out = []
                for sub in e.virtual_entities():
                    out += _from_dxf_entity(sub, skipped, depth + 1)
                if out:
                    return out
    except Exception:
        return _skip()
    return _skip()


# =========================================================================== #
#  4. LIENZO (Model Space)
# =========================================================================== #
OSNAP_MODES = ["end", "mid", "cen", "qua", "int", "per", "nod", "ins", "nea"]
OSNAP_LABEL = {"end": "Final", "mid": "Medio", "cen": "Centro", "qua": "Cuadrante",
               "int": "Intersección", "per": "Perpendicular", "nod": "Nodo",
               "ins": "Inserción", "nea": "Cercano"}


class Canvas(QtWidgets.QWidget):
    pointPicked = Signal(object)
    mouseMoved = Signal(object)
    selectionChanged = Signal()
    zoomChanged = Signal()

    def __init__(self, doc: Document):
        super().__init__()
        self.doc = doc
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.BlankCursor)
        self.setMinimumSize(400, 300)

        self.scale = 20.0
        self.pan = QPointF(320.0, 240.0)
        self.grid = 1.0
        self.show_grid = True
        self.snap_on = False
        self.osnap_on = True
        self.ortho = False
        self.polar = False
        self.polar_step = 15.0
        self.osnap_modes = {m: True for m in OSNAP_MODES}
        self.osnap_modes["nea"] = False
        self.osnap_modes["per"] = True

        self.mouse_screen = QPointF(0, 0)
        self.mouse_world: Vec = (0.0, 0.0)
        self.osnap_hit: Optional[Tuple[str, Vec]] = None
        self.base_point: Optional[Vec] = None      # referencia de goma/orto
        self.preview_fn: Optional[Callable[[Vec], List[Entity]]] = None
        self.pick_mode = False                     # el comando espera un punto
        self.select_mode = False                   # el comando espera selección

        self._panning = False
        self._pan_from: Optional[QPointF] = None
        self._sel_from: Optional[QPointF] = None
        self._sel_rect: Optional[QRectF] = None
        self._view_stack: List[Tuple[float, QPointF]] = []

        # grosores de línea en pantalla (LWT) y escala de visualización
        self.show_lwt = True
        self.lwt_scale = 1.0
        # entrada dinámica: restricción aplicada al punto y datos del rótulo
        self.constraint_fn: Optional[Callable[[Vec], Vec]] = None
        self.dyn_overlay_fn: Optional[Callable[[], List[Tuple[str, str, bool, bool]]]] = None
        # caché del dibujo (se regenera sólo cuando cambia el documento o la vista)
        self._cache: Optional[QtGui.QPixmap] = None
        self._cache_view: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._bb: Optional[List[Tuple[Tuple[float, float, float, float], Entity]]] = None
        self._regen_timer = QtCore.QTimer(self)
        self._regen_timer.setSingleShot(True)
        self._regen_timer.setInterval(140)
        self._regen_timer.timeout.connect(self._regen_view)

    # --- caché ---------------------------------------------------------------- #
    def update(self, *args):
        """Invalida la caché y repinta (cambió el documento o la vista)."""
        self._cache = None
        self._bb = None
        super().update(*args)

    def refresh_overlay(self):
        """Repinta sólo cursor, previsualización y rótulos (sin regenerar)."""
        super().update()

    def view_changed(self):
        """Zoom/encuadre interactivo: se reutiliza la imagen transformada y la
        regeneración completa se difiere hasta que el usuario se detiene."""
        self._regen_timer.start()
        super().update()

    def _regen_view(self):
        self._cache = None
        super().update()

    def bboxes(self) -> List[Tuple[Tuple[float, float, float, float], Entity]]:
        """Cajas envolventes de las entidades visibles, calculadas una vez."""
        if self._bb is None:
            out = []
            for e in self.doc.visible_entities():
                try:
                    out.append((e.bbox(), e))
                except Exception:
                    continue
            self._bb = out
        return self._bb

    def entities_near(self, w: Vec, r: float) -> List[Entity]:
        return [e for (x0, y0, x1, y1), e in self.bboxes()
                if x0 - r <= w[0] <= x1 + r and y0 - r <= w[1] <= y1 + r]

    def focusNextPrevChild(self, nxt):
        return False          # Tab pertenece a la entrada dinámica

    def keyPressEvent(self, ev):
        """Lo que se teclea sobre el lienzo va al intérprete de comandos."""
        win = self.window()
        ci = getattr(win, "cmd_input", None)
        k = ev.key()
        if ci is not None and (ev.text().strip() or k in (
                Qt.Key.Key_Tab, Qt.Key.Key_Backtab, Qt.Key.Key_Return,
                Qt.Key.Key_Enter, Qt.Key.Key_Backspace, Qt.Key.Key_Space)) \
                and not ev.modifiers() & (Qt.KeyboardModifier.ControlModifier |
                                          Qt.KeyboardModifier.MetaModifier):
            ci.setFocus()
            QtWidgets.QApplication.sendEvent(ci, QtGui.QKeyEvent(
                ev.type(), k, ev.modifiers(), ev.text()))
            return
        super().keyPressEvent(ev)

    # --- transformación --------------------------------------------------- #
    def to_screen(self, p: Vec) -> QPointF:
        return QPointF(p[0] * self.scale + self.pan.x(),
                       -p[1] * self.scale + self.pan.y())

    def to_world(self, s: QPointF) -> Vec:
        return ((s.x() - self.pan.x()) / self.scale,
                -(s.y() - self.pan.y()) / self.scale)

    def px(self, n: float) -> float:
        """n píxeles expresados en unidades de dibujo."""
        return n / self.scale

    # --- navegación -------------------------------------------------------- #
    def push_view(self):
        self._view_stack.append((self.scale, QPointF(self.pan)))
        if len(self._view_stack) > 30:
            self._view_stack.pop(0)

    def prev_view(self):
        if self._view_stack:
            self.scale, self.pan = self._view_stack.pop()
            self.update()
            self.zoomChanged.emit()

    def zoom_at(self, sp: QPointF, factor: float):
        before = self.to_world(sp)
        self.scale = max(1e-3, min(self.scale * factor, 1e6))
        self.pan = QPointF(sp.x() - before[0] * self.scale,
                           sp.y() + before[1] * self.scale)
        self.view_changed()
        self.zoomChanged.emit()

    def zoom_box(self, x0, y0, x1, y1, margin=0.08):
        w = max(x1 - x0, 1e-6)
        h = max(y1 - y0, 1e-6)
        self.push_view()
        self.scale = max(1e-3, min(self.width() * (1 - 2 * margin) / w,
                                   self.height() * (1 - 2 * margin) / h))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.pan = QPointF(self.width() / 2 - cx * self.scale,
                           self.height() / 2 + cy * self.scale)
        self.update()
        self.zoomChanged.emit()

    def zoom_extents(self, ents: Optional[List[Entity]] = None):
        bb = self.doc.bbox(ents)
        if bb is None:
            self.push_view()
            self.scale = 20.0
            self.pan = QPointF(self.width() / 2, self.height() / 2)
            self.update()
            self.zoomChanged.emit()
            return
        x0, y0, x1, y1 = bb
        if x1 - x0 < 1e-6 and y1 - y0 < 1e-6:
            x0, y0, x1, y1 = x0 - 10, y0 - 10, x1 + 10, y1 + 10
        self.zoom_box(x0, y0, x1, y1)

    # --- resolución del punto bajo el cursor -------------------------------- #
    def resolve_point(self, sp: QPointF) -> Vec:
        w = self.free_point(sp)
        if self.constraint_fn is not None:
            try:
                w = self.constraint_fn(w)
            except Exception:
                pass
        return w

    def free_point(self, sp: QPointF) -> Vec:
        """Punto bajo el cursor con refent, orto, polar y snap (sin restricciones)."""
        w = self.to_world(sp)
        if self.osnap_hit:
            return self.osnap_hit[1]
        if self.base_point is not None and (self.ortho or self.polar):
            b = self.base_point
            d = vsub(w, b)
            if self.ortho:
                if abs(d[0]) >= abs(d[1]):
                    w = (w[0], b[1])
                else:
                    w = (b[0], w[1])
            else:
                step = math.radians(self.polar_step)
                a = round(math.atan2(d[1], d[0]) / step) * step
                L = vlen(d)
                w = vadd(b, (L * math.cos(a), L * math.sin(a)))
        if self.snap_on and self.grid > 0:
            w = (round(w[0] / self.grid) * self.grid,
                 round(w[1] / self.grid) * self.grid)
        return w

    def _update_osnap(self, sp: QPointF):
        self.osnap_hit = None
        if not self.osnap_on:
            return
        tol = 14.0
        best = None
        best_d = tol
        w = self.mouse_world
        r = self.px(tol)
        near = self.entities_near(w, r)
        if len(near) > 40:              # zona densa: sólo los objetos más próximos
            near.sort(key=lambda e: e.dist_to(w))
            near = near[:40]
        for e in near:
            for kind, p in e.snaps():
                if not self.osnap_modes.get(kind, True):
                    continue
                if abs(p[0] - w[0]) > r or abs(p[1] - w[1]) > r:
                    continue
                s = self.to_screen(p)
                d = math.hypot(s.x() - sp.x(), s.y() - sp.y())
                if d < best_d:
                    best_d, best = d, (kind, p)
        # intersecciones: sólo entre los tramos que pasan junto al cursor
        if best is None and self.osnap_modes.get("int", True) and len(near) > 1:
            prims = []
            for idx, e in enumerate(near):
                for pr in e.primitives():
                    if prim_dist(pr, w) <= r:
                        prims.append((idx, pr))
                        if len(prims) > 60:
                            break
            for i in range(len(prims)):
                for j in range(i + 1, len(prims)):
                    if prims[i][0] == prims[j][0]:
                        continue
                    for ip in prim_int(prims[i][1], prims[j][1]):
                        s = self.to_screen(ip)
                        d = math.hypot(s.x() - sp.x(), s.y() - sp.y())
                        if d < best_d:
                            best_d, best = d, ("int", ip)
        # perpendicular al punto base
        if best is None and self.base_point is not None and \
                self.osnap_modes.get("per", True):
            for e in near:
                for pr in e.primitives():
                    if pr[0] != "seg":
                        continue
                    fp = closest_on_seg(self.base_point, pr[1], pr[2])
                    s = self.to_screen(fp)
                    d = math.hypot(s.x() - sp.x(), s.y() - sp.y())
                    if d < best_d:
                        best_d, best = d, ("per", fp)
        # cercano
        if best is None and self.osnap_modes.get("nea", False):
            w = self.mouse_world
            for e in near:
                for pr in e.primitives():
                    if pr[0] == "seg":
                        cp = closest_on_seg(w, pr[1], pr[2])
                    else:
                        a = math.atan2(w[1] - pr[1][1], w[0] - pr[1][0])
                        if not ang_in_arc(a, pr[3], pr[4]):
                            continue
                        cp = (pr[1][0] + pr[2] * math.cos(a),
                              pr[1][1] + pr[2] * math.sin(a))
                    s = self.to_screen(cp)
                    d = math.hypot(s.x() - sp.x(), s.y() - sp.y())
                    if d < best_d:
                        best_d, best = d, ("nea", cp)
        self.osnap_hit = best

    # --- eventos ------------------------------------------------------------ #
    def resizeEvent(self, ev):
        if ev.oldSize().width() > 0:
            self.pan += QPointF((ev.size().width() - ev.oldSize().width()) / 2,
                                (ev.size().height() - ev.oldSize().height()) / 2)
        else:
            self.pan = QPointF(self.width() / 2, self.height() / 2)
        self._cache = None
        super().resizeEvent(ev)

    def wheelEvent(self, ev):
        f = 1.15 if ev.angleDelta().y() > 0 else 1 / 1.15
        self.zoom_at(ev.position(), f)

    def mousePressEvent(self, ev):
        pos = ev.position()
        mods = ev.modifiers()
        if ev.button() == Qt.MouseButton.MiddleButton or \
           (ev.button() == Qt.MouseButton.LeftButton and
                mods & Qt.KeyboardModifier.ShiftModifier and not self.pick_mode):
            self._panning = True
            self._pan_from = pos
            return
        if ev.button() == Qt.MouseButton.RightButton:
            self.window().cancel_command()
            return
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        if self.pick_mode:
            self.pointPicked.emit(self.resolve_point(pos))
            return
        self._sel_from = QPointF(pos)

    def mouseMoveEvent(self, ev):
        pos = ev.position()
        self.mouse_screen = QPointF(pos)
        self.mouse_world = self.to_world(pos)
        if self._panning and self._pan_from is not None:
            self.pan += pos - self._pan_from
            self._pan_from = QPointF(pos)
            self.view_changed()
            return
        if self._sel_from is not None:
            self._sel_rect = QRectF(self._sel_from, pos).normalized()
            self._sel_rect_dir = pos.x() >= self._sel_from.x()
        self._update_osnap(pos)
        self.mouseMoved.emit(self.resolve_point(pos))
        self.refresh_overlay()

    def mouseReleaseEvent(self, ev):
        if self._panning:
            self._panning = False
            self._regen_timer.stop()
            self._regen_view()
            return
        if ev.button() != Qt.MouseButton.LeftButton or self._sel_from is None:
            return
        pos = ev.position()
        add = bool(ev.modifiers() & (Qt.KeyboardModifier.ShiftModifier |
                                     Qt.KeyboardModifier.ControlModifier))
        moved = math.hypot(pos.x() - self._sel_from.x(), pos.y() - self._sel_from.y())
        if moved < 4:
            self._click_select(self.to_world(pos), add)
        else:
            crossing = pos.x() < self._sel_from.x()
            r = QRectF(self._sel_from, pos).normalized()
            a = self.to_world(r.topLeft())
            b = self.to_world(r.bottomRight())
            self._window_select(min(a[0], b[0]), min(a[1], b[1]),
                                max(a[0], b[0]), max(a[1], b[1]), crossing, add)
        self._sel_from = None
        self._sel_rect = None
        self.selectionChanged.emit()
        self.update()

    def _click_select(self, w: Vec, add: bool):
        tol = self.px(7)
        hit = None
        best = 1e18
        for e in reversed(self.entities_near(w, tol)):
            if not self.doc.is_editable(e):
                continue
            d = e.dist_to(w)
            if d <= tol and d < best:
                best, hit = d, e
        if not add:
            self.doc.clear_selection()
        if hit is not None:
            targets = self.doc.expand_groups([hit])
            newval = not hit.selected if add else True
            for t in targets:
                t.selected = newval

    def _window_select(self, x0, y0, x1, y1, crossing: bool, add: bool):
        if not add:
            self.doc.clear_selection()
        picked = []
        for (bx0, by0, bx1, by1), e in self.bboxes():
            if not self.doc.is_editable(e):
                continue
            inside = bx0 >= x0 and by0 >= y0 and bx1 <= x1 and by1 <= y1
            if inside:
                picked.append(e)
            elif crossing:
                if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
                    continue
                touch = any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in e.sample())
                if not touch:
                    box = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                    prs = [("seg", box[i], box[(i + 1) % 4]) for i in range(4)]
                    touch = any(prim_int(pr, q) for pr in prs for q in e.primitives())
                if touch:
                    picked.append(e)
        for e in self.doc.expand_groups(picked):
            e.selected = True

    # --- dibujo -------------------------------------------------------------- #
    def pen_for(self, e: Entity, ghost: bool = False) -> QtGui.QPen:
        if ghost:
            pen = QtGui.QPen(QtGui.QColor(THEME["ghost"]))
            pen.setWidthF(1.4)
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setCosmetic(True)
            return pen
        col = THEME["selected"] if e.selected else self.doc.color_of(e)
        lwv = self.doc.lineweight_of(e)
        ltv = self.doc.linetype_of(e)
        key = (col, lwv, ltv, e.selected)
        memo = getattr(self, "_pen_memo", None)
        if memo is not None and key in memo:
            return memo[key]
        pen = QtGui.QPen(QtGui.QColor(col))
        if self.show_lwt:
            # 0.25 mm => 1 px, 0.50 => 2 px, 1.00 => 4 px … (como LWT de AutoCAD)
            w = max(1.0, min(lwv * 4.0 * self.lwt_scale, 14.0))
        else:
            w = 1.0
        if e.selected:
            w = max(w, 2.0)
        pen.setWidthF(w)
        pen.setCosmetic(True)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap if w > 2 else Qt.PenCapStyle.SquareCap)
        lt = LINETYPES.get(ltv, [])
        if lt:
            pen.setStyle(Qt.PenStyle.CustomDashLine)
            # el patrón se expresa en múltiplos del ancho de la pluma
            pen.setDashPattern([max(v * 2.2 / w, 0.3) for v in lt])
        if memo is not None:
            memo[key] = pen
        return pen

    def draw_arc(self, g: QtGui.QPainter, c: Vec, r: float, a0: float, a1: float):
        s = self.to_screen((c[0] - r, c[1] + r))
        rect = QRectF(s, QSizeF(2 * r * self.scale, 2 * r * self.scale))
        span = norm_ang(a1 - a0)
        if span < ANG_TOL:
            span = 2 * math.pi
        g.drawArc(rect, int(round(math.degrees(a0) * 16)),
                  int(round(math.degrees(span) * 16)))

    def draw_arrow(self, g: QtGui.QPainter, tail: Vec, tip: Vec,
                   color: QtGui.QColor, size: float = 9.0):
        a = self.to_screen(tail)
        b = self.to_screen(tip)
        d = QPointF(b.x() - a.x(), b.y() - a.y())
        L = math.hypot(d.x(), d.y())
        if L < 1e-6:
            return
        u = QPointF(d.x() / L, d.y() / L)
        n = QPointF(-u.y(), u.x())
        p1 = b - QPointF(u.x() * size, u.y() * size) + QPointF(n.x() * size * .3,
                                                               n.y() * size * .3)
        p2 = b - QPointF(u.x() * size, u.y() * size) - QPointF(n.x() * size * .3,
                                                               n.y() * size * .3)
        path = QtGui.QPolygonF([b, p1, p2])
        g.setBrush(QtGui.QBrush(color))
        g.drawPolygon(path)
        g.setBrush(Qt.BrushStyle.NoBrush)

    def _render_scene(self) -> QtGui.QPixmap:
        """Dibuja rejilla, ejes y entidades visibles en una imagen reutilizable."""
        dpr = self.devicePixelRatioF()
        pm = QtGui.QPixmap(max(1, int(self.width() * dpr)), max(1, int(self.height() * dpr)))
        pm.setDevicePixelRatio(dpr)
        pm.fill(QtGui.QColor(THEME["canvas"]))
        g = QtGui.QPainter(pm)
        g.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        if self.show_grid:
            self._draw_grid(g)
        self._draw_axes(g)
        vx0, vy1 = self.to_world(QPointF(0, 0))
        vx1, vy0 = self.to_world(QPointF(self.width(), self.height()))
        tiny = self.px(0.6)
        self._pen_memo = {}
        for (x0, y0, x1, y1), e in self.bboxes():
            if x1 < vx0 or x0 > vx1 or y1 < vy0 or y0 > vy1:
                continue                       # fuera de la vista
            try:
                if x1 - x0 < tiny and y1 - y0 < tiny and not isinstance(e, PointEnt):
                    s = self.to_screen((x0, y0))   # menor que un píxel
                    g.setPen(self.pen_for(e))
                    g.drawPoint(s)
                    continue
                e.draw(g, self, self.pen_for(e))
            except Exception:
                traceback.print_exc()
        self._pen_memo = None
        g.end()
        return pm

    def paintEvent(self, ev):
        cur = (self.scale, self.pan.x(), self.pan.y())
        if self._cache is None:
            self._cache = self._render_scene()
            self._cache_view = cur
        g = QtGui.QPainter(self)
        if self._cache_view == cur:
            g.drawPixmap(0, 0, self._cache)
        else:
            # imagen anterior desplazada/escalada mientras llega la regeneración
            cs, cpx, cpy = self._cache_view
            k = self.scale / cs if cs else 1.0
            g.fillRect(self.rect(), QtGui.QColor(THEME["canvas"]))
            g.save()
            g.translate(self.pan.x() - cpx * k, self.pan.y() - cpy * k)
            g.scale(k, k)
            g.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, False)
            g.drawPixmap(0, 0, self._cache)
            g.restore()
        g.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        if self.preview_fn is not None:
            try:
                for e in self.preview_fn(self.resolve_point(self.mouse_screen)) or []:
                    e.draw(g, self, self.pen_for(e, ghost=True))
            except Exception:
                pass
        self._draw_grips(g)
        if self.base_point is not None and self.pick_mode:
            pen = QtGui.QPen(QtGui.QColor(THEME["ghost"]))
            pen.setStyle(Qt.PenStyle.DotLine)
            pen.setCosmetic(True)
            g.setPen(pen)
            g.drawLine(self.to_screen(self.base_point), self.mouse_screen)
        self._draw_selection_box(g)
        self._draw_cursor(g)

    def _draw_grid(self, g):
        gs = self.grid if self.grid > 0 else 1.0
        while gs * self.scale < 8:
            gs *= 5 if (gs * self.scale) * 5 >= 8 else 10
        while gs * self.scale > 120:
            gs /= 10
        w, h = self.width(), self.height()
        x0 = self.to_world(QPointF(0, 0))[0]
        x1 = self.to_world(QPointF(w, 0))[0]
        y0 = self.to_world(QPointF(0, h))[1]
        y1 = self.to_world(QPointF(0, 0))[1]
        i0, i1 = math.floor(x0 / gs), math.ceil(x1 / gs)
        j0, j1 = math.floor(y0 / gs), math.ceil(y1 / gs)
        if i1 - i0 > 4000 or j1 - j0 > 4000:
            return
        minor = QtGui.QPen(QtGui.QColor(THEME["grid_minor"]))
        minor.setCosmetic(True)
        major = QtGui.QPen(QtGui.QColor(THEME["grid_major"]))
        major.setCosmetic(True)
        for i in range(i0, i1 + 1):
            g.setPen(major if i % 10 == 0 else minor)
            x = self.to_screen((i * gs, 0)).x()
            g.drawLine(QPointF(x, 0), QPointF(x, h))
        for j in range(j0, j1 + 1):
            g.setPen(major if j % 10 == 0 else minor)
            y = self.to_screen((0, j * gs)).y()
            g.drawLine(QPointF(0, y), QPointF(w, y))

    def _draw_axes(self, g):
        o = self.to_screen((0.0, 0.0))
        p = QtGui.QPen(QtGui.QColor(THEME["axis_x"]))
        p.setWidthF(1.4)
        p.setCosmetic(True)
        g.setPen(p)
        g.drawLine(QPointF(0, o.y()), QPointF(self.width(), o.y()))
        p = QtGui.QPen(QtGui.QColor(THEME["axis_y"]))
        p.setWidthF(1.4)
        p.setCosmetic(True)
        g.setPen(p)
        g.drawLine(QPointF(o.x(), 0), QPointF(o.x(), self.height()))

    def _draw_grips(self, g):
        sel = [e for e in self.doc.entities if e.selected]
        if not sel:
            return
        pen = QtGui.QPen(QtGui.QColor(THEME["selected"]))
        pen.setCosmetic(True)
        g.setPen(pen)
        g.setBrush(QtGui.QBrush(QtGui.QColor(THEME["selected"])))
        n = 0
        for e in sel:
            for kind, p in e.snaps():
                if kind not in ("end", "cen", "ins", "nod"):
                    continue
                s = self.to_screen(p)
                g.drawRect(QRectF(s.x() - 3, s.y() - 3, 6, 6))
                n += 1
                if n > 400:
                    break
            if n > 400:
                break
        g.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_selection_box(self, g):
        if self._sel_rect is None:
            return
        crossing = not getattr(self, "_sel_rect_dir", True)
        col = QtGui.QColor(THEME["cross_sel"] if crossing else THEME["window_sel"])
        pen = QtGui.QPen(col)
        pen.setCosmetic(True)
        pen.setStyle(Qt.PenStyle.DashLine if crossing else Qt.PenStyle.SolidLine)
        g.setPen(pen)
        fill = QtGui.QColor(col)
        fill.setAlpha(38)
        g.setBrush(QtGui.QBrush(fill))
        g.drawRect(self._sel_rect)
        g.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_cursor(self, g):
        s = self.mouse_screen
        pen = QtGui.QPen(QtGui.QColor(THEME["crosshair"]))
        pen.setCosmetic(True)
        g.setPen(pen)
        g.drawLine(QPointF(0, s.y()), QPointF(self.width(), s.y()))
        g.drawLine(QPointF(s.x(), 0), QPointF(s.x(), self.height()))
        box = 6
        g.drawRect(QRectF(s.x() - box, s.y() - box, 2 * box, 2 * box))
        if self.osnap_hit:
            kind, p = self.osnap_hit
            sp = self.to_screen(p)
            pen = QtGui.QPen(QtGui.QColor(THEME["snap"]))
            pen.setWidthF(1.8)
            pen.setCosmetic(True)
            g.setPen(pen)
            r = 6
            if kind in ("end", "ins"):
                g.drawRect(QRectF(sp.x() - r, sp.y() - r, 2 * r, 2 * r))
            elif kind == "mid":
                g.drawPolygon(QtGui.QPolygonF([sp + QPointF(0, -r),
                                               sp + QPointF(r, r),
                                               sp + QPointF(-r, r)]))
            elif kind in ("cen", "nod"):
                g.drawEllipse(sp, r, r)
            elif kind == "qua":
                g.drawPolygon(QtGui.QPolygonF([sp + QPointF(0, -r), sp + QPointF(r, 0),
                                               sp + QPointF(0, r), sp + QPointF(-r, 0)]))
            elif kind == "int":
                g.drawLine(sp + QPointF(-r, -r), sp + QPointF(r, r))
                g.drawLine(sp + QPointF(-r, r), sp + QPointF(r, -r))
            elif kind == "per":
                g.drawLine(sp + QPointF(-r, -r), sp + QPointF(-r, r))
                g.drawLine(sp + QPointF(-r, r), sp + QPointF(r, r))
                g.drawLine(sp + QPointF(0, r), sp + QPointF(0, 0))
            else:
                g.drawEllipse(sp, r - 2, r - 2)
            g.setPen(QtGui.QPen(QtGui.QColor(THEME["snap"])))
            g.drawText(sp + QPointF(10, -8), OSNAP_LABEL.get(kind, kind))
        # entrada dinámica: campos editables junto al cursor
        fields = self.dyn_overlay_fn() if (self.dyn_overlay_fn and self.pick_mode) else None
        if fields:
            self._draw_dyn_fields(g, s, fields)
        elif self.base_point is not None and self.pick_mode:
            w = self.resolve_point(self.mouse_screen)
            d = vdist(self.base_point, w)
            a = math.degrees(vangle(self.base_point, w))
            g.setPen(QtGui.QPen(QtGui.QColor(THEME["muted"])))
            g.drawText(s + QPointF(14, 20), f"{fmt(d, 3)}  <  {fmt(a, 2)}°")

    def _draw_dyn_fields(self, g, s: QPointF, fields):
        """Rótulo tipo AutoCAD: [Distancia: 12.5] [Ángulo: 30°]  (Tab cambia)."""
        f = QtGui.QFont(self.font())
        f.setPixelSize(12)
        g.setFont(f)
        fm = QtGui.QFontMetricsF(f)
        x = s.x() + 18
        y = s.y() + 18
        h = fm.height() + 6
        for label, text, active, locked in fields:
            lab = label + ":"
            val = (text or " ") + ("  🔒" if locked else "")
            lw = fm.horizontalAdvance(lab) + 8
            vw = max(fm.horizontalAdvance(val) + 12, 54)
            box = QRectF(x, y, lw + vw, h)
            g.setPen(Qt.PenStyle.NoPen)
            g.setBrush(QtGui.QColor(20, 22, 28, 225))
            g.drawRoundedRect(box, 3, 3)
            vbox = QRectF(x + lw, y + 2, vw - 2, h - 4)
            g.setBrush(QtGui.QColor("#1f3b78") if active else QtGui.QColor(44, 46, 54))
            g.drawRect(vbox)
            g.setPen(QtGui.QColor(THEME["muted"]))
            g.drawText(QRectF(x + 4, y, lw, h),
                       int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), lab)
            g.setPen(QtGui.QColor("#ffffff" if active else
                                  ("#ffd54f" if locked else THEME["text"])))
            g.drawText(vbox.adjusted(5, 0, 0, 0),
                       int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), val)
            if active:
                pen = QtGui.QPen(QtGui.QColor("#4d7cfe"))
                pen.setCosmetic(True)
                g.setPen(pen)
                g.setBrush(Qt.BrushStyle.NoBrush)
                g.drawRect(vbox)
            x += lw + vw + 6
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.setPen(QtGui.QColor(THEME["muted"]))
        f.setPixelSize(10)
        g.setFont(f)
        g.drawText(QPointF(s.x() + 18, y + h + 12), "Tab: fijar y pasar al siguiente · Enter: aceptar")


# =========================================================================== #
#  5. MARCO DE COMANDOS
# =========================================================================== #
class Cancel(Exception):
    """Aborta el comando en curso."""


class Prompt:
    """Solicitud de entrada emitida por un comando (generador)."""

    def __init__(self, text: str, mode: str = "point", base: Optional[Vec] = None,
                 preview: Optional[Callable[[Vec], List[Entity]]] = None,
                 keywords: Optional[Dict[str, str]] = None, default: Any = None,
                 numeric: bool = False, dyn: Optional[str] = None):
        self.text = text
        self.mode = mode          # point | text | number | angle | select | keyword
        self.base = base
        self.preview = preview
        self.keywords = {k.upper(): v for k, v in (keywords or {}).items()}
        self.default = default
        self.numeric = numeric   # en modo punto, un número suelto se devuelve tal cual
        # Campos de entrada dinámica: "polar" (distancia/ángulo), "xy",
        # "wh" (ancho/alto) o "ang" (sólo ángulo). Por omisión se deduce.
        if dyn is None and mode == "point":
            low = text.lower()
            picks = ("objeto", "selecciona", "designa", "lado", "línea", "linea",
                     "entidad", "elige", "contorno", "borde", "texto a")
            if numeric:
                dyn = "ang"
            elif base is not None:
                dyn = "polar"
            elif not any(w in low for w in picks):
                dyn = "xy"
        self.dyn = dyn or ""


class Ctx:
    """Contexto que reciben los comandos."""

    def __init__(self, win):
        self.win = win
        self.name = ""
        self._touched = False

    @property
    def doc(self) -> Document:
        return self.win.doc

    @property
    def view(self) -> Canvas:
        return self.win.view

    def log(self, msg: str, level: str = "info"):
        self.win.log(msg, level)

    def touch(self):
        if not self._touched:
            self.doc.push_undo(self.name)
            self._touched = True

    def add(self, e: Entity) -> Entity:
        self.touch()
        if e.layer == "0" and self.doc.current_layer != "0":
            e.layer = self.doc.current_layer
        self.doc.apply_current(e)
        return self.doc.add(e)

    def remove(self, ents: List[Entity]):
        self.touch()
        self.doc.remove(ents)

    def sel(self) -> List[Entity]:
        return [e for e in self.doc.selection() if self.doc.is_editable(e)]

    def pick_entity(self, p: Vec, tol_px: float = 9.0) -> Optional[Entity]:
        tol = self.view.px(tol_px)
        best, bd = None, 1e18
        for e in reversed(self.doc.visible_entities()):
            if not self.doc.is_editable(e):
                continue
            d = e.dist_to(p)
            if d <= tol and d < bd:
                best, bd = e, d
        return best


def sel_or_prompt(ctx: Ctx, msg: str = "Selecciona objetos"):
    """Devuelve la selección actual o la solicita. Uso: `yield from`."""
    s = ctx.sel()
    if s:
        return s
    s = yield Prompt(msg + " <Enter=aceptar>", "select")
    return [e for e in (s or []) if ctx.doc.is_editable(e)]


# =========================================================================== #
#  6. COMANDOS — creación
# =========================================================================== #
def cmd_line(ctx: Ctx):
    p1 = yield Prompt("Punto inicial", "point")
    if p1 is None:
        return
    first = p1
    n = 0
    while True:
        prev = p1
        p = yield Prompt("Siguiente punto [C=cerrar/U=deshacer] <Enter=fin>",
                         "point", base=prev,
                         keywords={"C": "close", "U": "undo"},
                         preview=lambda cur, a=prev: [Line(a, cur)])
        if p is None:
            break
        if p == "close":
            if n >= 1:
                ctx.add(Line(prev, first))
            break
        if p == "undo":
            if ctx.doc.entities:
                ctx.remove([ctx.doc.entities[-1]])
                n -= 1
            continue
        ctx.add(Line(prev, p))
        n += 1
        p1 = p


def cmd_polyline(ctx: Ctx):
    p = yield Prompt("Primer punto", "point")
    if p is None:
        return
    pts = [p]
    while True:
        prev = pts[-1]
        p = yield Prompt("Siguiente punto [C=cerrar] <Enter=fin>", "point", base=prev,
                         keywords={"C": "close"},
                         preview=lambda cur, a=list(pts): [Polyline(a + [cur])])
        if p is None or p == "close":
            closed = (p == "close")
            if len(pts) >= 2:
                ctx.add(Polyline(pts, closed))
            return
        pts.append(p)


def cmd_rectangle(ctx: Ctx):
    p1 = yield Prompt("Primera esquina", "point")
    if p1 is None:
        return
    p2 = yield Prompt("Esquina opuesta", "point", base=p1, dyn="wh",
                      preview=lambda cur: [Polyline(_rect_pts(p1, cur), True)])
    if p2 is None:
        return
    ctx.add(Polyline(_rect_pts(p1, p2), True))


def _rect_pts(a: Vec, b: Vec) -> List[Vec]:
    return [(a[0], a[1]), (b[0], a[1]), (b[0], b[1]), (a[0], b[1])]


def _ngon(c: Vec, p: Vec, n: int, inscribed: bool = True) -> List[Vec]:
    r = vdist(c, p)
    a0 = vangle(c, p)
    if not inscribed:
        r = r / math.cos(math.pi / n)
    return [(c[0] + r * math.cos(a0 + 2 * math.pi * i / n),
             c[1] + r * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def cmd_polygon(ctx: Ctx):
    n = yield Prompt("Número de lados", "number", default=6)
    n = int(max(3, min(int(n or 6), 256)))
    c = yield Prompt("Centro", "point")
    if c is None:
        return
    mode = yield Prompt("Inscrito o circunscrito [I/C] <I>", "keyword",
                        keywords={"I": "I", "C": "C"}, default="I")
    ins = (mode or "I").upper() != "C"
    p = yield Prompt("Punto del radio", "point", base=c,
                     preview=lambda cur: [Polyline(_ngon(c, cur, n, ins), True)])
    if p is None:
        return
    ctx.add(Polyline(_ngon(c, p, n, ins), True))


def cmd_circle(ctx: Ctx):
    c = yield Prompt("Centro [2P/3P] ", "point", keywords={"2P": "2p", "3P": "3p"})
    if c is None:
        return
    if c == "2p":
        a = yield Prompt("Primer punto del diámetro", "point")
        b = yield Prompt("Segundo punto del diámetro", "point", base=a,
                         preview=lambda cur: [Circle(vlerp(a, cur, .5),
                                                     vdist(a, cur) / 2)])
        if a is None or b is None:
            return
        ctx.add(Circle(vlerp(a, b, .5), vdist(a, b) / 2))
        return
    if c == "3p":
        a = yield Prompt("Primer punto", "point")
        b = yield Prompt("Segundo punto", "point")
        d = yield Prompt("Tercer punto", "point")
        cc = circumcircle(a, b, d)
        if cc is None:
            ctx.log("Puntos colineales: no hay circunferencia.", "warn")
            return
        ctx.add(Circle(cc[0], cc[1]))
        return
    r = yield Prompt("Radio o punto [D=diámetro]", "point", base=c,
                     keywords={"D": "dia"},
                     preview=lambda cur: [Circle(c, vdist(c, cur))])
    if r is None:
        return
    if r == "dia":
        d = yield Prompt("Diámetro", "number")
        if not d:
            return
        ctx.add(Circle(c, abs(float(d)) / 2))
        return
    ctx.add(Circle(c, vdist(c, r)))


def circumcircle(a: Vec, b: Vec, c: Vec):
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    if abs(d) < 1e-12:
        return None
    ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) +
          (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) +
          (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
    uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) +
          (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) +
          (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d
    return ((ux, uy), vdist((ux, uy), a))


def cmd_arc(ctx: Ctx):
    mode = yield Prompt("Arco: centro o [3P=tres puntos]", "point",
                        keywords={"3P": "3p"})
    if mode is None:
        return
    if mode == "3p":
        a = yield Prompt("Punto inicial", "point")
        b = yield Prompt("Punto intermedio", "point")
        c = yield Prompt("Punto final", "point")
        cc = circumcircle(a, b, c)
        if cc is None:
            ctx.add(Line(a, c))
            return
        cen, r = cc
        a0, am, a1 = (vangle(cen, a), vangle(cen, b), vangle(cen, c))
        if not ang_in_arc(am, a0, a1):
            a0, a1 = a1, a0
        ctx.add(Arc(cen, r, a0, a1))
        return
    cen = mode
    a = yield Prompt("Punto inicial", "point", base=cen)
    if a is None:
        return
    r = vdist(cen, a)
    a0 = vangle(cen, a)
    b = yield Prompt("Punto final (sentido antihorario)", "point", base=cen,
                     preview=lambda cur: [Arc(cen, r, a0, vangle(cen, cur))])
    if b is None:
        return
    ctx.add(Arc(cen, r, a0, vangle(cen, b)))


def cmd_ellipse(ctx: Ctx):
    c = yield Prompt("Centro", "point")
    if c is None:
        return
    a = yield Prompt("Extremo del eje mayor", "point", base=c,
                     preview=lambda cur: [Ellipse(c, vdist(c, cur),
                                                  vdist(c, cur) / 2, vangle(c, cur))])
    if a is None:
        return
    rx = vdist(c, a)
    ang = vangle(c, a)
    b = yield Prompt("Semieje menor (punto o distancia)", "point", base=c,
                     preview=lambda cur: [Ellipse(c, rx, max(_perp_dist(cur, c, ang),
                                                             1e-3), ang)])
    if b is None:
        return
    ctx.add(Ellipse(c, rx, max(_perp_dist(b, c, ang), 1e-3), ang))


def _perp_dist(p: Vec, c: Vec, ang: float) -> float:
    n = (-math.sin(ang), math.cos(ang))
    return abs(vdot(vsub(p, c), n))


def cmd_point(ctx: Ctx):
    while True:
        p = yield Prompt("Ubicación del punto <Enter=fin>", "point")
        if p is None:
            return
        ctx.add(PointEnt(p))


def cmd_text(ctx: Ctx):
    p = yield Prompt("Punto de inserción", "point")
    if p is None:
        return
    h = yield Prompt("Altura", "number", default=ctx.win.text_height)
    h = float(h or ctx.win.text_height)
    ctx.win.text_height = h
    a = yield Prompt("Rotación (grados)", "number", default=0)
    s = yield Prompt("Texto", "text")
    if not s:
        return
    ctx.add(TextEnt(p, s, h, math.radians(float(a or 0))))


def cmd_edit_text(ctx: Ctx):
    p = yield Prompt("Selecciona el texto a editar", "point")
    if p is None:
        return
    e = ctx.pick_entity(p)
    if not isinstance(e, (TextEnt, Leader, Dimension)):
        ctx.log("No es un texto.", "warn")
        return
    cur = e.text or ""
    s = yield Prompt(f"Nuevo texto <{cur}>", "text", default=cur)
    ctx.touch()
    e.text = s if s else cur


def cmd_leader(ctx: Ctx):
    p = yield Prompt("Punto de la flecha", "point")
    if p is None:
        return
    pts = [p]
    while True:
        prev = pts[-1]
        q = yield Prompt("Siguiente vértice <Enter=texto>", "point", base=prev,
                         preview=lambda cur, a=list(pts): [Leader(a + [cur])])
        if q is None:
            break
        pts.append(q)
    if len(pts) < 2:
        pts.append(vadd(p, (ctx.win.text_height * 4, ctx.win.text_height * 2)))
    s = yield Prompt("Texto", "text")
    ctx.add(Leader(pts, s or "", ctx.win.text_height))


def cmd_spline(ctx: Ctx):
    p = yield Prompt("Primer punto de control", "point")
    if p is None:
        return
    pts = [p]
    while True:
        prev = pts[-1]
        q = yield Prompt("Siguiente punto <Enter=fin>", "point", base=prev,
                         preview=lambda cur, a=list(pts):
                         [Polyline(catmull_rom(a + [cur]))])
        if q is None:
            break
        pts.append(q)
    if len(pts) >= 2:
        ctx.add(Polyline(catmull_rom(pts)))


def cmd_hatch(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx, "Selecciona contornos cerrados")
    polys = [(e, e.polygon()) for e in sel]
    polys = [(e, p) for e, p in polys if p]
    if not polys:
        ctx.log("Se requiere al menos un contorno cerrado.", "warn")
        return
    ang = yield Prompt("Ángulo del achurado (grados)", "number", default=45)
    sp = yield Prompt("Separación", "number", default=2.0)
    solid = yield Prompt("¿Sólido? [S/N] <N>", "keyword",
                         keywords={"S": "S", "N": "N"}, default="N")
    for e, p in polys:
        h = Hatch(p, math.radians(float(ang or 45)), abs(float(sp or 2)) or 1.0,
                  (solid or "N").upper() == "S", layer=e.layer)
        ctx.add(h)
    ctx.doc.clear_selection()


# =========================================================================== #
#  7. COMANDOS — edición
# =========================================================================== #
def cmd_move(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if not sel:
        return
    a = yield Prompt("Punto base", "point")
    if a is None:
        return
    b = yield Prompt("Punto destino", "point", base=a,
                     preview=lambda cur: _ghost(sel, lambda e: e.translate(vsub(cur, a))))
    if b is None:
        return
    ctx.touch()
    for e in sel:
        e.translate(vsub(b, a))


def _ghost(ents: List[Entity], fn: Callable[[Entity], None]) -> List[Entity]:
    out = []
    for e in ents:
        c = copy.deepcopy(e)
        c.selected = False
        fn(c)
        out.append(c)
    return out


def cmd_copy(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if not sel:
        return
    a = yield Prompt("Punto base", "point")
    if a is None:
        return
    while True:
        b = yield Prompt("Punto destino <Enter=fin>", "point", base=a,
                         preview=lambda cur: _ghost(sel,
                                                    lambda e: e.translate(vsub(cur, a))))
        if b is None:
            return
        d = vsub(b, a)
        for e in sel:
            c = e.clone()
            c.translate(d)
            ctx.add(c)


def cmd_rotate(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if not sel:
        return
    c = yield Prompt("Centro de rotación", "point")
    if c is None:
        return
    a = yield Prompt("Ángulo (grados) o punto [C=copiar]", "point", base=c,
                     keywords={"C": "copy"}, numeric=True,
                     preview=lambda cur: _ghost(sel, lambda e: e.rotate(c, vangle(c, cur))))
    copy_mode = False
    if a == "copy":
        copy_mode = True
        a = yield Prompt("Ángulo (grados) o punto", "point", base=c, numeric=True,
                         preview=lambda cur: _ghost(sel,
                                                    lambda e: e.rotate(c, vangle(c, cur))))
    if a is None:
        return
    ang = math.radians(a) if isinstance(a, (int, float)) else vangle(c, a)
    ctx.touch()
    for e in sel:
        t = e.clone() if copy_mode else e
        t.rotate(c, ang)
        if copy_mode:
            ctx.add(t)


def cmd_scale(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if not sel:
        return
    c = yield Prompt("Punto base", "point")
    if c is None:
        return
    f = yield Prompt("Factor de escala", "number", default=1.0)
    f = float(f or 1.0)
    if abs(f) < 1e-9:
        return
    ctx.touch()
    for e in sel:
        e.scale(c, f)


def cmd_mirror(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if not sel:
        return
    p1 = yield Prompt("Primer punto del eje", "point")
    if p1 is None:
        return
    p2 = yield Prompt("Segundo punto del eje", "point", base=p1,
                      preview=lambda cur: _ghost(sel, lambda e: e.mirror(p1, cur)))
    if p2 is None:
        return
    keep = yield Prompt("¿Borrar originales? [S/N] <N>", "keyword",
                        keywords={"S": "S", "N": "N"}, default="N")
    ctx.touch()
    for e in sel:
        c = e.clone()
        c.mirror(p1, p2)
        ctx.add(c)
    if (keep or "N").upper() == "S":
        ctx.remove(sel)


def _offset_entity(e: Entity, d: float, side: Vec) -> Optional[Entity]:
    """Desplaza `e` una distancia `d` hacia el lado del punto `side`."""
    if isinstance(e, Line):
        n = vperp(vnorm(vsub(e.p2, e.p1)))
        s = 1.0 if vdot(vsub(side, e.p1), n) >= 0 else -1.0
        off = vmul(n, d * s)
        return Line(vadd(e.p1, off), vadd(e.p2, off), **_attrs(e))
    if isinstance(e, Circle):
        s = 1.0 if vdist(side, e.center) > e.radius else -1.0
        r = e.radius + d * s
        return Circle(e.center, r, **_attrs(e)) if r > 1e-9 else None
    if isinstance(e, Arc):
        s = 1.0 if vdist(side, e.center) > e.radius else -1.0
        r = e.radius + d * s
        return Arc(e.center, r, e.a0, e.a1, **_attrs(e)) \
            if r > 1e-9 else None
    if isinstance(e, Polyline):
        pts = e.points
        i = min(range(len(e.primitives())),
                key=lambda k: dist_point_seg(side, e.primitives()[k][1],
                                             e.primitives()[k][2]))
        pr = e.primitives()[i]
        n = vperp(vnorm(vsub(pr[2], pr[1])))
        s = 1.0 if vdot(vsub(side, pr[1]), n) >= 0 else -1.0
        return Polyline(offset_polyline(pts, d * s, e.closed), e.closed,
                        **_attrs(e))
    if isinstance(e, Ellipse):
        s = 1.0 if vdist(side, e.center) > (e.rx + e.ry) / 2 else -1.0
        return Ellipse(e.center, max(e.rx + d * s, 1e-6), max(e.ry + d * s, 1e-6),
                       e.angle, **_attrs(e))
    return None


def cmd_offset(ctx: Ctx):
    d = yield Prompt("Distancia de desfase", "number", default=ctx.win.offset_dist)
    d = abs(float(d or ctx.win.offset_dist))
    if d < 1e-9:
        return
    ctx.win.offset_dist = d
    while True:
        p = yield Prompt("Objeto a desfasar <Enter=fin>", "point")
        if p is None:
            return
        e = ctx.pick_entity(p)
        if e is None:
            ctx.log("No se encontró ningún objeto ahí.", "warn")
            continue
        q = yield Prompt("Lado del desfase", "point",
                         preview=lambda cur, ee=e: [x for x in
                                                    [_offset_entity(ee, d, cur)] if x])
        if q is None:
            return
        new = _offset_entity(e, d, q)
        if new is None:
            ctx.log("Ese objeto no admite desfase.", "warn")
            continue
        ctx.add(new)


def cmd_array(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if not sel:
        return
    mode = yield Prompt("Matriz [R=rectangular/P=polar] <R>", "keyword",
                        keywords={"R": "R", "P": "P"}, default="R")
    if (mode or "R").upper() == "P":
        c = yield Prompt("Centro de la matriz", "point")
        if c is None:
            return
        n = int(float((yield Prompt("Número de copias", "number", default=6)) or 6))
        total = float((yield Prompt("Ángulo total (grados)", "number",
                                    default=360)) or 360)
        rot = yield Prompt("¿Girar los objetos? [S/N] <S>", "keyword",
                           keywords={"S": "S", "N": "N"}, default="S")
        ctx.touch()
        step = math.radians(total) / (n if abs(total - 360) < 1e-6 else max(n - 1, 1))
        for i in range(1, n):
            for e in sel:
                c2 = e.clone()
                if (rot or "S").upper() == "S":
                    c2.rotate(c, step * i)
                else:
                    bb = e.bbox()
                    ctr = ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)
                    new_ctr = vrot(ctr, c, step * i)
                    c2.translate(vsub(new_ctr, ctr))
                ctx.add(c2)
        return
    rows = int(float((yield Prompt("Filas", "number", default=2)) or 2))
    cols = int(float((yield Prompt("Columnas", "number", default=2)) or 2))
    dy = float((yield Prompt("Distancia entre filas", "number", default=10)) or 10)
    dx = float((yield Prompt("Distancia entre columnas", "number", default=10)) or 10)
    ctx.touch()
    for i in range(rows):
        for j in range(cols):
            if i == 0 and j == 0:
                continue
            for e in sel:
                c2 = e.clone()
                c2.translate((j * dx, i * dy))
                ctx.add(c2)


def _trim_entity(e: Entity, ints: List[Vec], pick: Vec) -> Optional[List[Entity]]:
    """Recorta `e` con los puntos de intersección dados; None si no aplica."""
    if isinstance(e, Line):
        d = vsub(e.p2, e.p1)
        l2 = vdot(d, d)
        if l2 < 1e-12:
            return None
        cuts = {}
        for p in ints:
            t = vdot(vsub(p, e.p1), d) / l2
            if 1e-6 < t < 1 - 1e-6:
                cuts[round(t, 9)] = p          # se conserva el punto exacto
        if not cuts:
            return None
        tp = max(0.0, min(1.0, vdot(vsub(pick, e.p1), d) / l2))
        ts = sorted(cuts)
        bounds = [(0.0, e.p1)] + [(t, cuts[t]) for t in ts] + [(1.0, e.p2)]
        out = []
        for i in range(len(bounds) - 1):
            (ta, pa), (tb, pb) = bounds[i], bounds[i + 1]
            if ta <= tp <= tb:
                continue
            if tb - ta > 1e-9:
                out.append(Line(pa, pb, **_attrs(e)))
        return out
    if isinstance(e, (Circle, Arc)):
        c = e.center
        r = e.radius
        a0 = 0.0 if isinstance(e, Circle) else e.a0
        span = 2 * math.pi if isinstance(e, Circle) else \
            (norm_ang(e.a1 - e.a0) or 2 * math.pi)
        angs = sorted({round(norm_ang(math.atan2(p[1] - c[1], p[0] - c[0]) - a0), 9)
                       for p in ints
                       if norm_ang(math.atan2(p[1] - c[1], p[0] - c[0]) - a0) <
                       span - 1e-9})
        angs = [a for a in angs if a > 1e-9]
        if not angs:
            return None
        ap = norm_ang(math.atan2(pick[1] - c[1], pick[0] - c[0]) - a0)
        if isinstance(e, Circle):
            bounds = angs + [angs[0] + 2 * math.pi]
            for i in range(len(bounds) - 1):
                if bounds[i] <= ap <= bounds[i + 1]:
                    return [Arc(c, r, a0 + bounds[i + 1], a0 + bounds[i] + 2 * math.pi,
                                **_attrs(e))]
            return [Arc(c, r, a0 + bounds[-1], a0 + bounds[0] + 2 * math.pi,
                        **_attrs(e))]
        bounds = [0.0] + angs + [span]
        out = []
        for i in range(len(bounds) - 1):
            a, b = bounds[i], bounds[i + 1]
            if a <= ap <= b:
                continue
            if b - a > 1e-9:
                out.append(Arc(c, r, a0 + a, a0 + b, **_attrs(e)))
        return out
    if isinstance(e, Polyline):
        segs = e.explode()
        i = min(range(len(segs)), key=lambda k: segs[k].dist_to(pick))
        tgt = segs[i]
        res = _trim_entity(tgt, ints, pick)
        if res is None:
            return None
        return [s for j, s in enumerate(segs) if j != i] + res
    return None


def cmd_trim(ctx: Ctx):
    cutters = yield from sel_or_prompt(ctx, "Aristas de corte")
    if not cutters:
        return
    ctx.doc.clear_selection()
    while True:
        p = yield Prompt("Objeto a recortar <Enter=fin>", "point")
        if p is None:
            return
        tgt = ctx.pick_entity(p)
        if tgt is None:
            continue
        ints = []
        for c in cutters:
            if c is tgt:
                continue
            for pr in tgt.primitives():
                for qr in c.primitives():
                    ints += prim_int(pr, qr)
        res = _trim_entity(tgt, ints, p)
        if res is None:
            ctx.log("No hay intersecciones válidas para recortar.", "warn")
            continue
        ctx.remove([tgt])
        for r in res:
            ctx.add(r)


def cmd_extend(ctx: Ctx):
    bounds = yield from sel_or_prompt(ctx, "Aristas de contorno")
    if not bounds:
        return
    ctx.doc.clear_selection()
    while True:
        p = yield Prompt("Objeto a alargar (cerca del extremo) <Enter=fin>", "point")
        if p is None:
            return
        e = ctx.pick_entity(p)
        if not isinstance(e, Line):
            ctx.log("Sólo se pueden alargar líneas.", "warn")
            continue
        near_p1 = vdist(p, e.p1) < vdist(p, e.p2)
        end = e.p1 if near_p1 else e.p2
        other = e.p2 if near_p1 else e.p1
        u = vnorm(vsub(end, other))
        best, bd = None, 1e18
        for b in bounds:
            if b is e:
                continue
            for qr in b.primitives():
                for ip in prim_int(("seg", other, end), qr, inf_p=True):
                    t = vdot(vsub(ip, other), u)
                    if t > vdist(other, end) + 1e-9 and t < bd:
                        bd, best = t, ip
        if best is None:
            ctx.log("No hay contorno al que alargar.", "warn")
            continue
        ctx.touch()
        if near_p1:
            e.p1 = best
        else:
            e.p2 = best


def _fillet_pair(l1: Line, p1: Vec, l2: Line, p2: Vec, r: float, chamfer=None):
    ip = int_line_line(l1.p1, l1.p2, l2.p1, l2.p2, inf1=True, inf2=True)
    if not ip:
        return None
    P = ip[0]
    u1 = vnorm(vsub(closest_on_seg(p1, l1.p1, l1.p2), P))
    u2 = vnorm(vsub(closest_on_seg(p2, l2.p1, l2.p2), P))
    if vlen(u1) < .5 or vlen(u2) < .5:
        return None
    th = math.acos(max(-1.0, min(1.0, vdot(u1, u2))))
    if th < 1e-6 or abs(th - math.pi) < 1e-6:
        return None
    if chamfer:
        d1, d2 = chamfer
        T1 = vadd(P, vmul(u1, d1))
        T2 = vadd(P, vmul(u2, d2))
        extra = Line(T1, T2, layer=l1.layer)
    else:
        t = r / math.tan(th / 2)
        T1 = vadd(P, vmul(u1, t))
        T2 = vadd(P, vmul(u2, t))
        bis = vnorm(vadd(u1, u2))
        C = vadd(P, vmul(bis, r / math.sin(th / 2)))
        a1 = vangle(C, T1)
        a2 = vangle(C, T2)
        if norm_ang(a2 - a1) > math.pi:
            a1, a2 = a2, a1
        extra = Arc(C, r, a1, a2, layer=l1.layer) if r > 1e-9 else None
    k1 = l1.p1 if vdot(vsub(l1.p1, P), u1) > vdot(vsub(l1.p2, P), u1) else l1.p2
    k2 = l2.p1 if vdot(vsub(l2.p1, P), u2) > vdot(vsub(l2.p2, P), u2) else l2.p2
    n1 = Line(k1, T1, **_attrs(l1))
    n2 = Line(k2, T2, **_attrs(l2))
    return [x for x in (n1, n2, extra) if x is not None]


def cmd_fillet(ctx: Ctx):
    r = yield Prompt("Radio de empalme", "number", default=ctx.win.fillet_radius)
    r = abs(float(r if r is not None else ctx.win.fillet_radius))
    ctx.win.fillet_radius = r
    while True:
        p1 = yield Prompt("Primera línea <Enter=fin>", "point")
        if p1 is None:
            return
        e1 = ctx.pick_entity(p1)
        p2 = yield Prompt("Segunda línea", "point")
        if p2 is None:
            return
        e2 = ctx.pick_entity(p2)
        if not isinstance(e1, Line) or not isinstance(e2, Line) or e1 is e2:
            ctx.log("El empalme requiere dos líneas distintas.", "warn")
            continue
        res = _fillet_pair(e1, p1, e2, p2, r)
        if not res:
            ctx.log("No se pudo empalmar (¿paralelas?).", "warn")
            continue
        ctx.remove([e1, e2])
        for x in res:
            ctx.add(x)


def cmd_chamfer(ctx: Ctx):
    d1 = float((yield Prompt("Primera distancia", "number", default=5)) or 5)
    d2 = float((yield Prompt("Segunda distancia", "number", default=d1)) or d1)
    while True:
        p1 = yield Prompt("Primera línea <Enter=fin>", "point")
        if p1 is None:
            return
        e1 = ctx.pick_entity(p1)
        p2 = yield Prompt("Segunda línea", "point")
        if p2 is None:
            return
        e2 = ctx.pick_entity(p2)
        if not isinstance(e1, Line) or not isinstance(e2, Line) or e1 is e2:
            ctx.log("El chaflán requiere dos líneas distintas.", "warn")
            continue
        res = _fillet_pair(e1, p1, e2, p2, 0.0, chamfer=(abs(d1), abs(d2)))
        if not res:
            ctx.log("No se pudo achaflanar.", "warn")
            continue
        ctx.remove([e1, e2])
        for x in res:
            ctx.add(x)


def cmd_break(ctx: Ctx):
    p = yield Prompt("Objeto a partir", "point")
    if p is None:
        return
    e = ctx.pick_entity(p)
    if e is None:
        return
    a = yield Prompt("Primer punto de ruptura", "point")
    b = yield Prompt("Segundo punto de ruptura", "point")
    if a is None or b is None:
        return
    res = _trim_entity(e, [a, b], vlerp(a, b, 0.5))
    if res is None:
        ctx.log("Ese objeto no se puede partir.", "warn")
        return
    ctx.remove([e])
    for r in res:
        ctx.add(r)


def cmd_join(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx, "Objetos a unir")
    segs = []
    for e in sel:
        if isinstance(e, Line):
            segs.append([e.p1, e.p2])
        elif isinstance(e, Polyline):
            segs.append(list(e.points))
    if len(segs) < 2:
        ctx.log("Selecciona al menos dos líneas o polilíneas.", "warn")
        return
    tol = ctx.view.px(6)
    chain = segs.pop(0)
    changed = True
    while changed and segs:
        changed = False
        for i, s in enumerate(segs):
            if vdist(chain[-1], s[0]) <= tol:
                chain += s[1:]
            elif vdist(chain[-1], s[-1]) <= tol:
                chain += list(reversed(s))[1:]
            elif vdist(chain[0], s[-1]) <= tol:
                chain = s[:-1] + chain
            elif vdist(chain[0], s[0]) <= tol:
                chain = list(reversed(s))[:-1] + chain
            else:
                continue
            segs.pop(i)
            changed = True
            break
    closed = vdist(chain[0], chain[-1]) <= tol and len(chain) > 2
    if closed:
        chain = chain[:-1]
    ctx.remove(sel)
    ctx.add(Polyline(chain, closed))
    if segs:
        ctx.log(f"{len(segs)} objeto(s) no conectados quedaron fuera.", "warn")


def cmd_explode(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if not sel:
        return
    n = 0
    for e in sel:
        parts = e.explode()
        if parts:
            ctx.remove([e])
            for p in parts:
                ctx.add(p)
            n += 1
    ctx.log(f"{n} objeto(s) descompuestos.")


def _flatten(e: Entity) -> List[Vec]:
    pts: List[Vec] = []
    for pr in e.primitives():
        seq = [pr[1], pr[2]] if pr[0] == "seg" else arc_points(pr[1], pr[2], pr[3], pr[4])
        if pts and vdist(pts[-1], seq[0]) < 1e-9:
            pts += seq[1:]
        else:
            pts += seq
    return pts


def _points_along(pts: List[Vec], step: float) -> List[Vec]:
    out = []
    acc = 0.0
    nxt = step
    for i in range(len(pts) - 1):
        seg = vdist(pts[i], pts[i + 1])
        while acc + seg >= nxt - 1e-12 and seg > 1e-12:
            t = (nxt - acc) / seg
            out.append(vlerp(pts[i], pts[i + 1], t))
            nxt += step
        acc += seg
    return out


def cmd_divide(ctx: Ctx):
    p = yield Prompt("Objeto a dividir", "point")
    if p is None:
        return
    e = ctx.pick_entity(p)
    if e is None:
        return
    n = int(float((yield Prompt("Número de partes", "number", default=4)) or 4))
    pts = _flatten(e)
    L = sum(vdist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    if n < 2 or L < 1e-9:
        return
    for q in _points_along(pts, L / n)[:n - 1]:
        ctx.add(PointEnt(q))


def cmd_measure(ctx: Ctx):
    p = yield Prompt("Objeto a graduar", "point")
    if p is None:
        return
    e = ctx.pick_entity(p)
    if e is None:
        return
    d = float((yield Prompt("Longitud del segmento", "number", default=10)) or 10)
    if d <= 0:
        return
    for q in _points_along(_flatten(e), d):
        ctx.add(PointEnt(q))


def cmd_lengthen(ctx: Ctx):
    p = yield Prompt("Línea a modificar (cerca del extremo)", "point")
    if p is None:
        return
    e = ctx.pick_entity(p)
    if not isinstance(e, Line):
        ctx.log("Sólo aplica a líneas.", "warn")
        return
    d = float((yield Prompt("Incremento (negativo = acortar)", "number",
                            default=10)) or 10)
    ctx.touch()
    if vdist(p, e.p1) < vdist(p, e.p2):
        e.p1 = vadd(e.p1, vmul(vnorm(vsub(e.p1, e.p2)), d))
    else:
        e.p2 = vadd(e.p2, vmul(vnorm(vsub(e.p2, e.p1)), d))


def cmd_align(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if not sel:
        return
    s1 = yield Prompt("Primer punto de origen", "point")
    d1 = yield Prompt("Primer punto de destino", "point")
    s2 = yield Prompt("Segundo punto de origen", "point")
    d2 = yield Prompt("Segundo punto de destino", "point")
    if None in (s1, d1, s2, d2):
        return
    sc = yield Prompt("¿Escalar a la distancia destino? [S/N] <N>", "keyword",
                      keywords={"S": "S", "N": "N"}, default="N")
    ang = vangle(s1, s2)
    ang2 = vangle(d1, d2)
    f = (vdist(d1, d2) / vdist(s1, s2)) if (sc or "N").upper() == "S" and \
        vdist(s1, s2) > 1e-9 else 1.0
    ctx.touch()
    for e in sel:
        e.translate(vsub(d1, s1))
        e.rotate(d1, ang2 - ang)
        if abs(f - 1.0) > 1e-9:
            e.scale(d1, f)


def cmd_delete(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if sel:
        ctx.remove(sel)
        ctx.log(f"{len(sel)} objeto(s) eliminados.")


def cmd_group(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    if len(sel) < 2:
        ctx.log("Selecciona al menos dos objetos.", "warn")
        return
    name = yield Prompt("Nombre del grupo", "text", default=f"G{len(ctx.doc.groups)+1}")
    gid = (max(ctx.doc.groups) + 1) if ctx.doc.groups else 1
    ctx.touch()
    ctx.doc.groups[gid] = name or f"G{gid}"
    for e in sel:
        e.group = gid
    ctx.log(f"Grupo '{ctx.doc.groups[gid]}' creado con {len(sel)} objetos.")


def cmd_ungroup(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx)
    ctx.touch()
    for e in sel:
        e.group = None
    ctx.log("Grupo deshecho.")


def cmd_block(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx, "Objetos del bloque")
    if not sel:
        return
    name = yield Prompt("Nombre del bloque", "text")
    if not name:
        return
    base = yield Prompt("Punto base", "point")
    if base is None:
        return
    ctx.touch()
    defn = []
    for e in sel:
        c = copy.deepcopy(e)
        c.selected = False
        c.translate(vmul(base, -1))
        defn.append(c)
    ctx.doc.blocks[name] = defn
    ctx.remove(sel)
    ctx.add(BlockRef(name, base))
    ctx.log(f"Bloque '{name}' definido con {len(defn)} objetos.")


def cmd_insert(ctx: Ctx):
    if not ctx.doc.blocks:
        ctx.log("No hay bloques definidos (usa B para crear uno).", "warn")
        return
    names = ", ".join(ctx.doc.blocks)
    name = yield Prompt(f"Bloque [{names}]", "text", default=list(ctx.doc.blocks)[0])
    name = name or list(ctx.doc.blocks)[0]
    if name not in ctx.doc.blocks:
        ctx.log(f"No existe el bloque '{name}'.", "warn")
        return
    sc = float((yield Prompt("Escala", "number", default=1.0)) or 1.0)
    rot = float((yield Prompt("Rotación (grados)", "number", default=0)) or 0)
    while True:
        p = yield Prompt("Punto de inserción <Enter=fin>", "point",
                         preview=lambda cur: [BlockRef(name, cur, sc,
                                                       math.radians(rot))])
        if p is None:
            return
        ctx.add(BlockRef(name, p, sc, math.radians(rot)))


def cmd_purge(ctx: Ctx):
    used = {e.layer for e in ctx.doc.entities}
    used_blocks = {e.name for e in ctx.doc.entities if isinstance(e, BlockRef)}
    dead_l = [n for n in ctx.doc.layers
              if n not in used and n != ctx.doc.current_layer and n != "0"]
    dead_b = [n for n in ctx.doc.blocks if n not in used_blocks]
    if not dead_l and not dead_b:
        ctx.log("No hay nada que purgar.")
        return
    ctx.touch()
    for n in dead_l:
        del ctx.doc.layers[n]
    for n in dead_b:
        del ctx.doc.blocks[n]
    ctx.log(f"Purgadas {len(dead_l)} capas y {len(dead_b)} bloques.")
    ctx.win.refresh_panels()


# =========================================================================== #
#  8. COMANDOS — booleanas, análisis y cotas
# =========================================================================== #
def _sh_polys(ents):
    out = []
    for e in ents:
        p = e.polygon()
        if p and len(p) >= 3:
            try:
                sp = ShPolygon(p)
                if not sp.is_valid:
                    sp = sp.buffer(0)
                if not sp.is_empty:
                    out.append((e, sp))
            except Exception:
                pass
    return out


def _emit_shapely(ctx: Ctx, geom, layer: str):
    geoms = []
    if geom is None or geom.is_empty:
        return 0
    if isinstance(geom, ShMultiPolygon):
        geoms = list(geom.geoms)
    elif isinstance(geom, ShPolygon):
        geoms = [geom]
    else:
        geoms = [g for g in getattr(geom, "geoms", []) if isinstance(g, ShPolygon)]
    n = 0
    for g in geoms:
        pts = [(x, y) for x, y in list(g.exterior.coords)[:-1]]
        ctx.add(Polyline(pts, True, layer=layer))
        n += 1
        for ring in g.interiors:
            hp = [(x, y) for x, y in list(ring.coords)[:-1]]
            ctx.add(Polyline(hp, True, layer=layer))
            n += 1
    return n


def _boolean(ctx: Ctx, op: str, msg: str):
    if not HAS_SHAPELY:
        ctx.log("Las booleanas requieren shapely:  pip install shapely", "error")
        return
    sel = yield from sel_or_prompt(ctx, msg)
    pairs = _sh_polys(sel)
    if len(pairs) < 2:
        ctx.log("Se necesitan al menos dos regiones cerradas válidas.", "warn")
        return
    layer = pairs[0][0].layer
    res = pairs[0][1]
    try:
        if op == "union":
            res = unary_union([p for _, p in pairs])
        elif op == "difference":
            for _, p in pairs[1:]:
                res = res.difference(p)
        else:
            for _, p in pairs[1:]:
                res = res.intersection(p)
    except Exception as ex:
        ctx.log(f"Error en la operación booleana: {ex}", "error")
        return
    ctx.remove([e for e, _ in pairs])
    n = _emit_shapely(ctx, res, layer)
    ctx.log(f"Resultado: {n} contorno(s).")


def cmd_union(ctx):
    yield from _boolean(ctx, "union", "Regiones a unir")


def cmd_difference(ctx):
    yield from _boolean(ctx, "difference",
                        "Región base primero, luego las que se restan")


def cmd_intersection(ctx):
    yield from _boolean(ctx, "intersection", "Regiones a intersectar")


def cmd_area(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx, "Regiones cerradas a medir")
    total = 0.0
    perim = 0.0
    for e in sel:
        total += e.area()
        perim += e.length()
    ctx.log(f"Área total = {fmt(total, 4)} {ctx.doc.units}²   "
            f"Perímetro = {fmt(perim, 4)} {ctx.doc.units}")


def cmd_distance(ctx: Ctx):
    a = yield Prompt("Primer punto", "point")
    if a is None:
        return
    b = yield Prompt("Segundo punto", "point", base=a,
                     preview=lambda cur: [Line(a, cur)])
    if b is None:
        return
    d = vdist(a, b)
    ctx.log(f"Distancia = {fmt(d, 4)}   ΔX = {fmt(b[0]-a[0], 4)}   "
            f"ΔY = {fmt(b[1]-a[1], 4)}   Ángulo = {fmt(math.degrees(vangle(a, b)), 3)}°")


def cmd_id(ctx: Ctx):
    p = yield Prompt("Punto a identificar", "point")
    if p is None:
        return
    ctx.log(f"X = {fmt(p[0], 4)}   Y = {fmt(p[1], 4)}")


def cmd_list(ctx: Ctx):
    sel = ctx.sel()
    if not sel:
        ctx.log(f"Documento: {len(ctx.doc.entities)} entidades · "
                f"{len(ctx.doc.layers)} capas · {len(ctx.doc.blocks)} bloques · "
                f"unidades {ctx.doc.units}")
        for k in sorted({e.kind for e in ctx.doc.entities}):
            ctx.log(f"   {k}: {sum(1 for e in ctx.doc.entities if e.kind == k)}")
        return
    for e in sel[:40]:
        bb = e.bbox()
        ctx.log(f"{e.kind} #{e.id} capa='{e.layer}' long={fmt(e.length(), 3)} "
                f"área={fmt(e.area(), 3)} bbox=({fmt(bb[0],2)},{fmt(bb[1],2)})-"
                f"({fmt(bb[2],2)},{fmt(bb[3],2)})")
    if len(sel) > 40:
        ctx.log(f"… y {len(sel)-40} más.")


SAFE_MATH = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}


def cmd_calc(ctx: Ctx):
    s = yield Prompt("Expresión (sin(pi/4), 12*3.5, hypot(3,4)…)", "text")
    if not s:
        return
    try:
        val = eval(s, {"__builtins__": {}}, dict(SAFE_MATH, abs=abs, round=round,
                                                 min=min, max=max, sum=sum))
        ctx.log(f"{s} = {val}")
    except Exception as ex:
        ctx.log(f"Error de cálculo: {ex}", "error")


def _dim_common(ctx: Ctx, dtype: str):
    p1 = yield Prompt("Primer punto de origen", "point")
    if p1 is None:
        return
    p2 = yield Prompt("Segundo punto de origen", "point", base=p1)
    if p2 is None:
        return
    pos = yield Prompt("Posición de la línea de cota", "point", base=p2,
                       preview=lambda cur: [Dimension(dtype, p1, p2, cur,
                                                      height=ctx.win.text_height)])
    if pos is None:
        return
    ctx.add(Dimension(dtype, p1, p2, pos, height=ctx.win.text_height))


def cmd_dim_linear(ctx: Ctx):
    p1 = yield Prompt("Primer punto de origen", "point")
    if p1 is None:
        return
    p2 = yield Prompt("Segundo punto de origen", "point", base=p1)
    if p2 is None:
        return

    def dt(cur):
        return "horizontal" if abs(cur[1] - (p1[1] + p2[1]) / 2) >= \
            abs(cur[0] - (p1[0] + p2[0]) / 2) else "vertical"
    pos = yield Prompt("Posición de la línea de cota", "point", base=p2,
                       preview=lambda cur: [Dimension(dt(cur), p1, p2, cur,
                                                      height=ctx.win.text_height)])
    if pos is None:
        return
    ctx.add(Dimension(dt(pos), p1, p2, pos, height=ctx.win.text_height))


def cmd_dim_aligned(ctx):
    yield from _dim_common(ctx, "aligned")


def _dim_circular(ctx: Ctx, dtype: str):
    p = yield Prompt("Selecciona círculo o arco", "point")
    if p is None:
        return
    e = ctx.pick_entity(p)
    if not isinstance(e, (Circle, Arc)):
        ctx.log("Selecciona un círculo o un arco.", "warn")
        return
    on = vadd(e.center, vmul(vnorm(vsub(p, e.center)) or (1.0, 0.0), e.radius))
    pos = yield Prompt("Posición del texto", "point", base=on,
                       preview=lambda cur: [Dimension(dtype, e.center, on, cur,
                                                      height=ctx.win.text_height)])
    if pos is None:
        return
    ctx.add(Dimension(dtype, e.center, on, pos, height=ctx.win.text_height))


def cmd_dim_radius(ctx):
    yield from _dim_circular(ctx, "radius")


def cmd_dim_diameter(ctx):
    yield from _dim_circular(ctx, "diameter")


def cmd_dim_angular(ctx: Ctx):
    v = yield Prompt("Vértice del ángulo", "point")
    a = yield Prompt("Primer punto", "point", base=v)
    b = yield Prompt("Segundo punto", "point", base=v)
    if None in (v, a, b):
        return
    pos = yield Prompt("Radio de la línea de cota", "point", base=v,
                       preview=lambda cur: [Dimension("angular", v, a, cur, p3=b,
                                                      height=ctx.win.text_height)])
    if pos is None:
        return
    ctx.add(Dimension("angular", v, a, pos, p3=b, height=ctx.win.text_height))


# =========================================================================== #
#  9. COMANDOS — vista, documento y sistema
# =========================================================================== #
def cmd_zoom(ctx: Ctx):
    s = yield Prompt("Factor o [E=extensión/V=ventana/P=previo/S=selección]",
                     "text", keywords={"E": "E", "V": "V", "P": "P", "S": "S"})
    s = (s or "E").strip().upper()
    if s == "E":
        ctx.view.zoom_extents()
    elif s == "P":
        ctx.view.prev_view()
    elif s == "S":
        ctx.view.zoom_extents(ctx.sel() or None)
    elif s == "V":
        a = yield Prompt("Primera esquina de la ventana", "point")
        b = yield Prompt("Esquina opuesta", "point", base=a)
        if a and b:
            ctx.view.zoom_box(min(a[0], b[0]), min(a[1], b[1]),
                              max(a[0], b[0]), max(a[1], b[1]))
    else:
        try:
            f = float(s)
        except ValueError:
            ctx.log("Factor no válido.", "warn")
            return
        ctx.view.zoom_at(QPointF(ctx.view.width() / 2, ctx.view.height() / 2), f)


def cmd_zoom_extents(ctx: Ctx):
    ctx.view.zoom_extents()


def cmd_zoom_selected(ctx: Ctx):
    ctx.view.zoom_extents(ctx.sel() or None)


def cmd_zoom_window(ctx: Ctx):
    a = yield Prompt("Primera esquina de la ventana", "point")
    b = yield Prompt("Esquina opuesta", "point", base=a)
    if a and b:
        ctx.view.zoom_box(min(a[0], b[0]), min(a[1], b[1]),
                          max(a[0], b[0]), max(a[1], b[1]))


def cmd_zoom_prev(ctx: Ctx):
    ctx.view.prev_view()


def cmd_pan(ctx: Ctx):
    a = yield Prompt("Punto base del encuadre", "point")
    b = yield Prompt("Punto destino", "point", base=a)
    if a and b:
        d = vsub(b, a)
        ctx.view.pan += QPointF(d[0] * ctx.view.scale, -d[1] * ctx.view.scale)
        ctx.view.update()


def cmd_toggle_snap(ctx: Ctx):
    ctx.view.snap_on = not ctx.view.snap_on
    ctx.win.refresh_status()
    ctx.log(f"Snap de rejilla: {'ON' if ctx.view.snap_on else 'OFF'}")


def cmd_toggle_osnap(ctx: Ctx):
    ctx.view.osnap_on = not ctx.view.osnap_on
    ctx.win.refresh_status()
    ctx.log(f"Referencia a objetos: {'ON' if ctx.view.osnap_on else 'OFF'}")


def cmd_toggle_grid(ctx: Ctx):
    ctx.view.show_grid = not ctx.view.show_grid
    ctx.view.update()
    ctx.win.refresh_status()


def cmd_toggle_ortho(ctx: Ctx):
    ctx.view.ortho = not ctx.view.ortho
    if ctx.view.ortho:
        ctx.view.polar = False
    ctx.win.refresh_status()
    ctx.log(f"Orto: {'ON' if ctx.view.ortho else 'OFF'}")


def cmd_toggle_polar(ctx: Ctx):
    ctx.view.polar = not ctx.view.polar
    if ctx.view.polar:
        ctx.view.ortho = False
    ctx.win.refresh_status()
    ctx.log(f"Polar: {'ON' if ctx.view.polar else 'OFF'} "
            f"(paso {fmt(ctx.view.polar_step,1)}°)")


def cmd_grid_options(ctx: Ctx):
    g = yield Prompt("Tamaño de rejilla", "number", default=ctx.view.grid)
    ctx.view.grid = max(float(g or ctx.view.grid), 1e-6)
    ctx.view.update()
    ctx.log(f"Rejilla = {fmt(ctx.view.grid)}")


def cmd_units(ctx: Ctx):
    u = yield Prompt("Unidades [mm/cm/m/in/ft]", "text", default=ctx.doc.units)
    ctx.doc.units = (u or ctx.doc.units).strip()
    ctx.win.refresh_status()


def cmd_layer(ctx: Ctx):
    ctx.win.show_layer_dialog()


def cmd_properties(ctx: Ctx):
    ctx.win.props_dock.setVisible(True)
    ctx.win.props_dock.raise_()


def cmd_undo(ctx: Ctx):
    label = ctx.doc.undo()
    ctx.win.after_state_change()
    ctx.log(f"Deshecho: {label}" if label else "Nada que deshacer.")


def cmd_redo(ctx: Ctx):
    label = ctx.doc.redo()
    ctx.win.after_state_change()
    ctx.log(f"Rehecho: {label}" if label else "Nada que rehacer.")


def cmd_new(ctx: Ctx):
    ctx.win.file_new()


def cmd_open(ctx: Ctx):
    ctx.win.file_open()


def cmd_save(ctx: Ctx):
    ctx.win.file_save()


def cmd_saveas(ctx: Ctx):
    ctx.win.file_save_as()


def cmd_export_dxf(ctx: Ctx):
    ctx.win.file_export_dxf()


def cmd_export_svg(ctx: Ctx):
    ctx.win.file_export_svg()


def cmd_import(ctx: Ctx):
    ctx.win.file_import_dxf()


def cmd_import_dwg(ctx: Ctx):
    ctx.win.file_import_dwg()


def cmd_export_dwg(ctx: Ctx):
    ctx.win.file_export_dwg()


def cmd_script(ctx: Ctx):
    ctx.win.run_script_file()


def cmd_record(ctx: Ctx):
    ctx.win.toggle_recording()


def cmd_python(ctx: Ctx):
    ctx.win.py_dock.setVisible(not ctx.win.py_dock.isVisible())
    if ctx.win.py_dock.isVisible():
        ctx.win.py_input.setFocus()


def cmd_help(ctx: Ctx):
    ctx.win.show_help()


def cmd_options(ctx: Ctx):
    v = ctx.view
    ctx.log(f"Snap={'ON' if v.snap_on else 'OFF'} · OSnap={'ON' if v.osnap_on else 'OFF'}"
            f" · Orto={'ON' if v.ortho else 'OFF'} · Polar={'ON' if v.polar else 'OFF'}"
            f" · Rejilla={fmt(v.grid)} · Zoom={fmt(v.scale, 3)} px/u"
            f" · Capa='{ctx.doc.current_layer}'")


def cmd_select_all(ctx: Ctx):
    ctx.doc.select_all()
    ctx.win.after_selection()


def cmd_regen(ctx: Ctx):
    ctx.view.update()


# --------------------------------------------------------------------------- #
#  Comandos 5.0: impresión, propiedades, capas
# --------------------------------------------------------------------------- #
def cmd_plot(ctx: Ctx):
    """Impresora virtual (PDF/SVG/PNG). La ventana se puede designar en el dibujo."""
    win = ctx.win
    s = win.plot_settings
    while True:
        dlg = PlotDialog(win, s)
        r = dlg.exec()
        if r == PlotDialog.PICK_WINDOW:
            a = yield Prompt("Primera esquina del área a imprimir", "point", dyn="")
            if a is None:
                continue
            b = yield Prompt("Esquina opuesta", "point", base=a, dyn="wh",
                             preview=lambda cur: [Polyline(_rect_pts(a, cur), True)])
            if b is None:
                continue
            s.window = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
            s.area = "window"
            continue
        if r != QtWidgets.QDialog.DialogCode.Accepted:
            return
        break
    ext = {"pdf": "PDF (*.pdf)", "svg": "SVG (*.svg)", "png": "PNG (*.png)"}[s.fmt]
    base = os.path.splitext(os.path.basename(ctx.doc.filename or "lamina"))[0]
    start = os.path.join(os.path.dirname(ctx.doc.filename) if ctx.doc.filename
                         else os.path.expanduser("~/Desktop"), f"{base}.{s.fmt}")
    path, _ = QtWidgets.QFileDialog.getSaveFileName(win, "Guardar lámina", start, ext)
    if not path:
        return
    if not path.lower().endswith("." + s.fmt):
        path += "." + s.fmt
    ents = plot_entities(ctx.doc, s, ctx.doc.selection())
    lay = PlotLayout(ctx.doc, s, plot_world_box(ctx.doc, s, ents, win.view_world_box()))
    QtWidgets.QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    try:
        write_plot(path, ctx.doc, s, lay, ents)
    finally:
        QtWidgets.QApplication.restoreOverrideCursor()
    size = os.path.getsize(path) / 1024
    ctx.log(f"Lámina {lay.pw:.0f}×{lay.ph:.0f} mm, escala {lay.scale_label()}, "
            f"{len(ents)} objetos → {path} ({size:.0f} KB)")
    if lay.overflow:
        ctx.log("Parte del dibujo quedó fuera del papel a esta escala.", "warn")
    if s.open_after:
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))


def _parse_lw(txt: str) -> Optional[float]:
    t = (txt or "").strip().lower().replace("mm", "").replace(",", ".")
    if t in ("p", "porcapa", "bylayer", "capa"):
        return LW_BYLAYER
    try:
        v = float(t)
    except ValueError:
        return None
    return min(LINEWEIGHTS, key=lambda x: abs(x - v))


def cmd_lineweight(ctx: Ctx):
    sel = ctx.sel()
    cur = lw_label(ctx.doc.current_lineweight)
    who = f"{len(sel)} objeto(s) seleccionados" if sel else "objetos nuevos"
    v = yield Prompt(f"Grosor en mm para {who} (0.00–2.11) o P=PorCapa <{cur}>", "text",
                     default="")
    if not v:
        return
    lw = _parse_lw(v)
    if lw is None:
        ctx.log("Grosor no válido. Ejemplos: 0.35 · 0.5 · P", "warn")
        return
    ctx.win.apply_general("lineweight", lw)
    if not ctx.view.show_lwt:
        ctx.log("Los grosores no se muestran en pantalla: actívalos con LWT o el botón "
                "GROSOR.")


def cmd_toggle_lwt(ctx: Ctx):
    ctx.view.show_lwt = not ctx.view.show_lwt
    ctx.view.update()
    ctx.win.refresh_status()
    ctx.log(f"Mostrar grosores: {'ON' if ctx.view.show_lwt else 'OFF'}")


def cmd_toggle_dyn(ctx: Ctx):
    ctx.win.dyn_on = not ctx.win.dyn_on
    ctx.win.refresh_status()
    ctx.view.refresh_overlay()
    ctx.log(f"Entrada dinámica: {'ON' if ctx.win.dyn_on else 'OFF'}")


def cmd_color(ctx: Ctx):
    sel = ctx.sel()
    k = yield Prompt("Color: [P=PorCapa] o Enter para elegir en la paleta", "keyword",
                     keywords={"P": "P"}, default="")
    if (k or "").upper() == "P":
        ctx.win.apply_general("color", None)
        return
    start = (sel[0].color if sel else ctx.doc.current_color) or "#ffffff"
    c = QtWidgets.QColorDialog.getColor(QtGui.QColor(start), ctx.win, "Color")
    if c.isValid():
        ctx.win.apply_general("color", c.name())


def cmd_linetype(ctx: Ctx):
    opts = {"P": LT_BYLAYER, "C": "Continuous", "T": "Dashed", "PU": "Dotted",
            "TP": "DashDot", "O": "Hidden", "E": "Center", "F": "Phantom"}
    k = yield Prompt("Tipo de línea [P=PorCapa/C=continua/T=trazos/PU=puntos/"
                     "TP=trazo-punto/O=oculta/E=eje/F=fantasma]", "keyword",
                     keywords=opts, default="")
    if k in opts.values():
        ctx.win.apply_general("linetype", k)


def cmd_clayer(ctx: Ctx):
    names = ", ".join(list(ctx.doc.layers)[:12])
    n = yield Prompt(f"Nombre de la capa actual (se crea si no existe) [{names}]", "text",
                     default=ctx.doc.current_layer)
    n = (n or "").strip()
    if not n:
        return
    if n not in ctx.doc.layers:
        # coincidencia sin distinguir mayúsculas
        match = [k for k in ctx.doc.layers if k.lower() == n.lower()]
        if match:
            n = match[0]
        else:
            ctx.doc.push_undo("nueva capa")
            ctx.doc.add_layer(n)
            ctx.log(f"Capa '{n}' creada.")
    ctx.win.set_current_layer(n)


def _pick_layer_of(ctx: Ctx, msg: str):
    sel = ctx.sel()
    if sel:
        return sel[0]
    p = yield Prompt(msg, "point", dyn="")
    if p is None:
        return None
    tol = ctx.view.px(9)
    best, bd = None, 1e18
    for e in ctx.view.entities_near(p, tol):      # también capas bloqueadas
        d = e.dist_to(p)
        if d <= tol and d < bd:
            best, bd = e, d
    if best is None:
        ctx.log("No hay ningún objeto ahí.", "warn")
    return best


def cmd_laymcur(ctx: Ctx):
    e = yield from _pick_layer_of(ctx, "Designa un objeto cuya capa será la actual")
    if e is not None:
        ctx.win.set_current_layer(e.layer)


def cmd_laycur(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx, "Objetos a pasar a la capa actual")
    if sel:
        ctx.doc.clear_selection()
        for e in sel:
            e.selected = True
        ctx.win.move_selection_to_layer(ctx.doc.current_layer)


def cmd_laymove(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx, "Objetos a mover de capa")
    if not sel:
        return
    n = yield Prompt("Capa de destino (se crea si no existe)", "text",
                     default=ctx.doc.current_layer)
    n = (n or "").strip()
    if n:
        ctx.doc.clear_selection()
        for e in sel:
            e.selected = True
        ctx.win.move_selection_to_layer(n)


def cmd_layiso(ctx: Ctx):
    sel = yield from sel_or_prompt(ctx, "Objetos cuyas capas se aíslan")
    if sel:
        ctx.win.isolate_layers(sorted({e.layer for e in sel}))
        ctx.doc.clear_selection()


def cmd_layuniso(ctx: Ctx):
    ctx.win.unisolate_layers()


def cmd_layoff(ctx: Ctx):
    while True:
        e = yield from _pick_layer_of(ctx, "Objeto cuya capa se apaga <Enter=fin>")
        if e is None:
            return
        ctx.doc.layers[e.layer].visible = False
        ctx.doc.clear_selection()
        ctx.log(f"Capa '{e.layer}' apagada.")
        ctx.win.after_layers_changed()


def cmd_layon(ctx: Ctx):
    for lay in ctx.doc.layers.values():
        lay.visible = True
    ctx.win._iso_state = None
    ctx.win.after_layers_changed()
    ctx.log("Todas las capas encendidas.")


def cmd_laylck(ctx: Ctx):
    e = yield from _pick_layer_of(ctx, "Objeto cuya capa se bloquea")
    if e is not None:
        ctx.doc.layers[e.layer].locked = True
        ctx.doc.clear_selection()
        ctx.log(f"Capa '{e.layer}' bloqueada.")
        ctx.win.after_layers_changed()


def cmd_layulk(ctx: Ctx):
    e = yield from _pick_layer_of(ctx, "Objeto cuya capa se desbloquea")
    if e is not None:
        ctx.doc.layers[e.layer].locked = False
        ctx.log(f"Capa '{e.layer}' desbloqueada.")
        ctx.win.after_layers_changed()


def cmd_matchprop(ctx: Ctx):
    p = yield Prompt("Objeto de origen", "point", dyn="")
    if p is None:
        return
    src = ctx.pick_entity(p)
    if src is None:
        ctx.log("No hay ningún objeto ahí.", "warn")
        return
    ctx.log(f"Origen: capa {src.layer} · {src.color or 'PorCapa'} · "
            f"{LT_LABEL.get(src.linetype, src.linetype)} · {lw_label(src.lineweight)}")
    n = 0
    while True:
        q = yield Prompt("Objeto de destino <Enter=fin>", "point", dyn="")
        if q is None:
            break
        dst = ctx.pick_entity(q)
        if dst is None or dst is src:
            continue
        ctx.touch()
        dst.layer, dst.color = src.layer, src.color
        dst.linetype, dst.lineweight = src.linetype, src.lineweight
        if isinstance(dst, (TextEnt, Dimension, Leader)) and hasattr(src, "height"):
            dst.height = src.height
        n += 1
        ctx.view.update()
    ctx.log(f"Propiedades igualadas en {n} objeto(s).")


# =========================================================================== #
#  10. REGISTRO DE COMANDOS Y ALIAS
# =========================================================================== #
COMMANDS: Dict[str, Callable] = {
    # creación
    "Line": cmd_line, "Polyline": cmd_polyline, "Rectangle": cmd_rectangle,
    "Polygon": cmd_polygon, "Circle": cmd_circle, "Arc": cmd_arc,
    "Ellipse": cmd_ellipse, "Point": cmd_point, "Text": cmd_text,
    "Leader": cmd_leader, "InterpCrv": cmd_spline, "Hatch": cmd_hatch,
    # edición
    "Move": cmd_move, "Copy": cmd_copy, "Rotate": cmd_rotate, "Scale": cmd_scale,
    "Mirror": cmd_mirror, "Offset": cmd_offset, "Array": cmd_array,
    "Trim": cmd_trim, "Extend": cmd_extend, "Fillet": cmd_fillet,
    "Chamfer": cmd_chamfer, "Split": cmd_break, "Join": cmd_join,
    "Explode": cmd_explode, "Divide": cmd_divide, "Measure": cmd_measure,
    "Lengthen": cmd_lengthen, "Align": cmd_align, "Delete": cmd_delete,
    "EditText": cmd_edit_text, "Group": cmd_group, "Ungroup": cmd_ungroup,
    "Block": cmd_block, "Insert": cmd_insert, "Purge": cmd_purge,
    # booleanas
    "BooleanUnion": cmd_union, "BooleanDifference": cmd_difference,
    "BooleanIntersection": cmd_intersection, "CurveBoolean": cmd_union,
    # análisis
    "Area": cmd_area, "Distance": cmd_distance, "What": cmd_list,
    "Calc": cmd_calc, "Id": cmd_id,
    # cotas
    "Dim": cmd_dim_linear, "DimAligned": cmd_dim_aligned,
    "DimRadius": cmd_dim_radius, "DimDiameter": cmd_dim_diameter,
    "DimAngle": cmd_dim_angular, "Dimensions": cmd_dim_linear,
    # vista
    "Zoom": cmd_zoom, "ZoomExtents": cmd_zoom_extents,
    "ZoomAllExtents": cmd_zoom_extents, "ZoomSelected": cmd_zoom_selected,
    "ZoomAllSelected": cmd_zoom_selected, "ZoomWindow": cmd_zoom_window,
    "ZoomPrevious": cmd_zoom_prev, "Pan": cmd_pan,
    "ToggleSnap": cmd_toggle_snap, "ToggleOSnap": cmd_toggle_osnap,
    "ToggleGrid": cmd_toggle_grid, "ToggleOrtho": cmd_toggle_ortho,
    "TogglePolar": cmd_toggle_polar, "GridOptions": cmd_grid_options,
    "Regen": cmd_regen, "SelectAll": cmd_select_all,
    # documento y sistema
    "Layer": cmd_layer, "Properties": cmd_properties,
    "PropertiesPage": cmd_properties, "Units": cmd_units,
    "Undo": cmd_undo, "Redo": cmd_redo, "New": cmd_new, "Open": cmd_open,
    "Save": cmd_save, "SaveAs": cmd_saveas, "ExportDXF": cmd_export_dxf,
    "ExportSVG": cmd_export_svg, "Import": cmd_import,
    "ImportDWG": cmd_import_dwg, "ExportDWG": cmd_export_dwg,
    "ReadCommandFile": cmd_script, "RecordScript": cmd_record,
    "PythonConsole": cmd_python, "Help": cmd_help, "Options": cmd_options,
}

# Diccionario de alias (AutoCAD Aliases for Rhino) -> comando canónico
ALIAS_MAP: Dict[str, str] = {
    "Z": "Zoom", "ZE": "ZoomExtents", "ZEA": "ZoomAllExtents",
    "ZS": "ZoomSelected", "ZSA": "ZoomAllSelected", "ZW": "ZoomWindow",
    "ZP": "ZoomPrevious", "S": "ToggleSnap", "O": "Offset", "P": "Pan",
    "M": "Move", "U": "Undo", "RE": "Redo", "PON": "Point", "POFF": "Regen",
    "C": "Circle", "W": "ExportDXF", "3A": "Array", "3P": "Polyline",
    "A": "Arc", "AA": "Area", "AL": "Align", "AR": "Array", "B": "Block",
    "BH": "Hatch", "BO": "CurveBoolean", "BR": "Split", "CH": "Properties",
    "CHA": "Chamfer", "CO": "Copy", "COL": "PropertiesPage", "CP": "Copy",
    "D": "Dimensions", "DAL": "DimAligned", "DAN": "DimAngle",
    "DDI": "DimDiameter", "DI": "Distance", "DIV": "Divide", "DLI": "Dim",
    "DRA": "DimRadius", "DS": "Options", "DST": "Dimensions", "DT": "Text",
    "DXFIN": "Import", "DXFOUT": "ExportDXF", "E": "Delete", "ED": "EditText",
    "DWG": "ImportDWG", "DWGIN": "ImportDWG", "DWGOUT": "ExportDWG",
    "EL": "Ellipse", "EX": "Extend", "EXP": "ExportDXF", "F": "Fillet",
    "G": "Group", "UG": "Ungroup", "H": "Hatch", "HE": "Properties",
    "I": "Insert", "IMP": "Import", "IN": "BooleanIntersection", "J": "Join",
    "L": "Line", "LA": "Layer", "LE": "Leader", "LEN": "Lengthen",
    "LI": "What", "LS": "What", "LT": "Layer", "LTS": "Layer",
    "LTYPE": "Layer", "MA": "Properties", "ME": "Measure", "MI": "Mirror",
    "MO": "Properties", "MT": "Text", "OP": "Options", "ORTHO": "ToggleOrtho",
    "OS": "ToggleOSnap", "PE": "Properties", "PL": "Polyline", "PO": "Point",
    "POL": "Polygon", "PR": "PropertiesPage", "PROPS": "PropertiesPage",
    "PU": "Purge", "QC": "Calc", "REC": "Rectangle", "REG": "Hatch",
    "RO": "Rotate", "SC": "Scale", "SCR": "ReadCommandFile", "SE": "Options",
    "SET": "Options", "SN": "GridOptions", "SP": "Split", "SPL": "InterpCrv",
    "SPLINE": "InterpCrv", "SPLIT": "Split", "SU": "BooleanDifference",
    "T": "Text", "TR": "Trim", "UN": "Units", "UNI": "BooleanUnion",
    "X": "Explode", "ID": "Id", "F8": "ToggleOrtho", "F9": "ToggleSnap",
    "PY": "PythonConsole", "REC0": "RecordScript", "GRID": "ToggleGrid",
    "POLAR": "TogglePolar", "SVG": "ExportSVG", "SA": "SelectAll",
    "?": "Help", "HELP": "Help", "NEW": "New", "OPEN": "Open", "SAVE": "Save",
    "SAVEAS": "SaveAs",
}

COMMANDS.update({
    "Plot": cmd_plot, "LineWeight": cmd_lineweight, "ToggleLWT": cmd_toggle_lwt,
    "ToggleDyn": cmd_toggle_dyn, "Color": cmd_color, "Linetype": cmd_linetype,
    "CLayer": cmd_clayer, "LayMCur": cmd_laymcur, "LayCur": cmd_laycur,
    "LayMove": cmd_laymove, "LayIso": cmd_layiso, "LayUniso": cmd_layuniso,
    "LayOff": cmd_layoff, "LayOn": cmd_layon, "LayLck": cmd_laylck,
    "LayUlk": cmd_layulk, "MatchProp": cmd_matchprop,
})
ALIAS_MAP.update({
    "PLOT": "Plot", "PRINT": "Plot", "IMPRIMIR": "Plot", "PDF": "Plot",
    "LW": "LineWeight", "LWEIGHT": "LineWeight", "GROSOR": "LineWeight",
    "LWT": "ToggleLWT", "LWDISPLAY": "ToggleLWT", "DYN": "ToggleDyn",
    "DYNMODE": "ToggleDyn", "F12": "ToggleDyn",
    "COL": "Color", "COLOR": "Color", "LT": "Linetype", "LTYPE": "Linetype",
    "LINETYPE": "Linetype", "-LA": "CLayer", "CLAYER": "CLayer", "CAPA": "CLayer",
    "LAYMCUR": "LayMCur", "LAYCUR": "LayCur", "LAYMOVE": "LayMove",
    "LAYISO": "LayIso", "LAYUNISO": "LayUniso", "LAYOFF": "LayOff",
    "LAYON": "LayOn", "LAYLCK": "LayLck", "LAYULK": "LayUlk",
    "MA": "MatchProp", "MATCHPROP": "MatchProp", "PAINTER": "MatchProp",
})

#: Se pueden ejecutar en medio de otro comando sin interrumpirlo.
TRANSPARENT_COMMANDS = {
    "ToggleSnap", "ToggleOSnap", "ToggleGrid", "ToggleOrtho", "TogglePolar",
    "ToggleLWT", "ToggleDyn", "ZoomExtents", "ZoomAllExtents", "ZoomPrevious",
    "Regen", "Help", "Layer", "Properties", "PropertiesPage", "PythonConsole",
    "Options",
}

# Alias reconocidos por el archivo original pero sin equivalente 2D:
LEGACY_ALIASES = {
    "3DO": "RotateView", "3F": "Plane", "AP": "Plugins", "EXT": "ExtrudeCrv",
    "HI": "Make2D", "IAD": "BackgroundBitmap", "IAT": "BackgroundPlace",
    "LO": "Viewports", "MS": "Viewports", "MV": "Viewports", "PS": "Viewports",
    "REV": "Revolve", "RPR": "RenderOptions", "RR": "Render", "SEC": "Section",
    "SHA": "Shade", "SL": "Section", "SO": "3DFace", "SPE": "PointsOn",
    "TI": "Viewports", "TO": "Toolbar", "TOR": "Torus", "UC": "NamedCPlane",
    "V": "NamedView", "VP": "PlaceCameraTarget", "XA": "WorksessionAttach",
    "XR": "Worksession", "ORBIT": "RotateView", "WB": "ExportWithOrigin",
    "VPORTS": "ReadViewportsFromFile", "PRCLOSE": "PropertiesClose",
}


# =========================================================================== #
#  11. PANELES
# =========================================================================== #
class ColorButton(QtWidgets.QToolButton):
    """Botón de color con opción PorCapa (None)."""

    colorPicked = Signal(object)

    def __init__(self, parent=None, allow_bylayer: bool = True):
        super().__init__(parent)
        self._color: Optional[str] = None
        self.allow_bylayer = allow_bylayer
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        m = QtWidgets.QMenu(self)
        if allow_bylayer:
            m.addAction("PorCapa", lambda: self._pick(None))
            m.addSeparator()
        for name, hexc in [("Rojo", "#ff3b30"), ("Amarillo", "#ffd60a"),
                           ("Verde", "#34c759"), ("Cian", "#32ade6"),
                           ("Azul", "#0a84ff"), ("Magenta", "#bf5af2"),
                           ("Blanco/Negro", "#ffffff"), ("Gris", "#8e8e93"),
                           ("Naranjo", "#ff9f0a")]:
            pm = QtGui.QPixmap(14, 14)
            pm.fill(QtGui.QColor(hexc))
            m.addAction(QtGui.QIcon(pm), name, lambda h=hexc: self._pick(h))
        m.addSeparator()
        m.addAction("Otro color…", self._custom)
        self.setMenu(m)
        self.set_color(None)

    def _custom(self):
        c = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._color or "#ffffff"),
                                            self, "Color")
        if c.isValid():
            self._pick(c.name())

    def _pick(self, c):
        self.set_color(c)
        self.colorPicked.emit(c)

    def set_color(self, c: Optional[str], bylayer_hint: Optional[str] = None):
        self._color = c
        pm = QtGui.QPixmap(16, 16)
        pm.fill(QtGui.QColor(c or bylayer_hint or "#777777"))
        if c is None:
            p = QtGui.QPainter(pm)
            p.setPen(QtGui.QColor("#000000"))
            p.drawLine(0, 15, 15, 0)
            p.end()
        self.setIcon(QtGui.QIcon(pm))
        self.setText("PorCapa" if c is None else c.upper())

    def color(self) -> Optional[str]:
        return self._color


_ICON_CACHE: Dict[Tuple[str, Any], "QtGui.QIcon"] = {}


def make_lw_combo(allow_bylayer: bool = True) -> QtWidgets.QComboBox:
    cb = QtWidgets.QComboBox()
    if allow_bylayer:
        cb.addItem("PorCapa", LW_BYLAYER)
    for lw in LINEWEIGHTS:
        ic = _ICON_CACHE.get(("lw", lw))
        if ic is not None:
            cb.addItem(ic, f"{lw:.2f} mm", lw)
            continue
        pm = QtGui.QPixmap(46, 14)
        pm.fill(Qt.GlobalColor.transparent)
        p = QtGui.QPainter(pm)
        pen = QtGui.QPen(QtGui.QColor("#e6e6e6"))
        pen.setWidthF(max(1.0, min(lw * 4.0, 10.0)))
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.setPen(pen)
        p.drawLine(2, 7, 44, 7)
        p.end()
        _ICON_CACHE[("lw", lw)] = QtGui.QIcon(pm)
        cb.addItem(_ICON_CACHE[("lw", lw)], f"{lw:.2f} mm", lw)
    cb.setIconSize(QtCore.QSize(46, 14))
    return cb


def make_lt_combo(allow_bylayer: bool = True) -> QtWidgets.QComboBox:
    cb = QtWidgets.QComboBox()
    names = ([LT_BYLAYER] if allow_bylayer else []) + list(LINETYPES)
    for n in names:
        ic = _ICON_CACHE.get(("lt", n))
        if ic is not None:
            cb.addItem(ic, LT_LABEL.get(n, n), n)
            continue
        pm = QtGui.QPixmap(46, 14)
        pm.fill(Qt.GlobalColor.transparent)
        p = QtGui.QPainter(pm)
        pen = QtGui.QPen(QtGui.QColor("#e6e6e6"))
        pen.setWidthF(1.4)
        pat = LINETYPES.get(n, [])
        if pat:
            pen.setDashPattern([max(v * 1.2 / 1.4, 0.4) for v in pat])
        p.setPen(pen)
        p.drawLine(2, 7, 44, 7)
        p.end()
        _ICON_CACHE[("lt", n)] = QtGui.QIcon(pm)
        cb.addItem(_ICON_CACHE[("lt", n)], LT_LABEL.get(n, n), n)
    cb.setIconSize(QtCore.QSize(46, 14))
    return cb


def _combo_select(cb: QtWidgets.QComboBox, value):
    for i in range(cb.count()):
        d = cb.itemData(i)
        if (isinstance(d, float) and isinstance(value, (int, float))
                and abs(d - float(value)) < 1e-6) or d == value:
            cb.setCurrentIndex(i)
            return
    cb.setCurrentIndex(-1)


class LayerPanel(QtWidgets.QWidget):
    """Administrador de capas: visibilidad, bloqueo, impresión, color, tipo y grosor."""

    COLS = ["V", "B", "I", "Capa", "Color", "Tipo de línea", "Grosor", "Obj."]

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.filter = QtWidgets.QLineEdit()
        self.filter.setPlaceholderText("Filtrar capas…")
        self.filter.textChanged.connect(lambda _: self.refresh())
        self.table = QtWidgets.QTableWidget(0, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(24)
        hh = self.table.horizontalHeader()
        hh.setStretchLastSection(False)
        for c, w in enumerate([24, 24, 26, 120, 40, 104, 76, 44]):
            self.table.setColumnWidth(c, w)
        hh.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeaderItem(0).setToolTip("Visible (encender/apagar)")
        self.table.horizontalHeaderItem(1).setToolTip("Bloqueada")
        self.table.horizontalHeaderItem(2).setToolTip("Se imprime")
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.cellClicked.connect(self._cell_clicked)
        self.table.cellDoubleClicked.connect(self._cell_dblclicked)
        self.table.itemChanged.connect(self._item_changed)

        def btn(text, tip, slot):
            b = QtWidgets.QPushButton(text)
            b.setToolTip(tip)
            b.clicked.connect(slot)
            return b

        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(btn("Nueva", "Crear una capa nueva y hacerla actual", self.new_layer))
        row1.addWidget(btn("Actual", "Hacer actual la capa marcada", self.set_current))
        row1.addWidget(btn("Borrar", "Borrar la capa marcada", self.del_layer))
        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(btn("Mover selección ⇢", "Pasar los objetos seleccionados a la "
                           "capa marcada", self.move_selection))
        row2.addWidget(btn("Aislar", "Apagar todas las demás capas", self.isolate))
        row2.addWidget(btn("Todas", "Encender y desbloquear todas", self.all_on))

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.addWidget(self.filter)
        lay.addWidget(self.table)
        lay.addLayout(row1)
        lay.addLayout(row2)
        self._loading = False
        self._names: List[str] = []
        make_lw_combo().deleteLater()           # genera los iconos de muestra
        make_lt_combo().deleteLater()
        self.setMinimumWidth(400)
        self.refresh()

    # ------------------------------------------------------------------ #
    def refresh(self):
        self._loading = True
        doc = self.win.doc
        counts: Dict[str, int] = {}
        for e in doc.entities:
            counts[e.layer] = counts.get(e.layer, 0) + 1
        flt = self.filter.text().strip().lower()
        self._names = [n for n in doc.layers if flt in n.lower()]
        self.table.setRowCount(len(self._names))
        for r, name in enumerate(self._names):
            lay = doc.layers[name]
            for c, (on, sym_on, sym_off) in enumerate(
                    [(lay.visible, "●", "○"), (lay.locked, "🔒", "·"), (lay.plot, "🖨", "✕")]):
                it = QtWidgets.QTableWidgetItem(sym_on if on else sym_off)
                it.setFlags(Qt.ItemFlag.ItemIsEnabled)
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c == 0:
                    it.setForeground(QtGui.QColor("#ffd54f" if on else "#666"))
                self.table.setItem(r, c, it)
            n = QtWidgets.QTableWidgetItem(("▶ " if name == doc.current_layer else "") + name)
            if name == doc.current_layer:
                f = n.font()
                f.setBold(True)
                n.setFont(f)
            n.setToolTip("Doble clic: hacer actual · F2/escribir: renombrar")
            self.table.setItem(r, 3, n)
            c = QtWidgets.QTableWidgetItem("")
            c.setBackground(QtGui.QColor(lay.color))
            c.setFlags(Qt.ItemFlag.ItemIsEnabled)
            c.setToolTip("Doble clic: cambiar color")
            self.table.setItem(r, 4, c)
            lt = QtWidgets.QTableWidgetItem(LT_LABEL.get(lay.linetype, lay.linetype))
            lt.setIcon(_ICON_CACHE.get(("lt", lay.linetype)) or QtGui.QIcon())
            lt.setFlags(Qt.ItemFlag.ItemIsEnabled)
            lt.setToolTip("Clic: cambiar tipo de línea")
            self.table.setItem(r, 5, lt)
            lw = QtWidgets.QTableWidgetItem(f"{lay.lineweight:.2f}")
            lw.setIcon(_ICON_CACHE.get(("lw", lay.lineweight)) or QtGui.QIcon())
            lw.setFlags(Qt.ItemFlag.ItemIsEnabled)
            lw.setToolTip("Clic: cambiar grosor")
            self.table.setItem(r, 6, lw)
            k = QtWidgets.QTableWidgetItem(str(counts.get(name, 0)))
            k.setFlags(Qt.ItemFlag.ItemIsEnabled)
            k.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 7, k)
        self._loading = False

    def _layer_at(self, row) -> Optional[Layer]:
        if 0 <= row < len(self._names):
            return self.win.doc.layers.get(self._names[row])
        return None

    def _set_attr(self, name: str, attr: str, value):
        if self._loading or value is None:
            return
        lay = self.win.doc.layers.get(name)
        if lay is None or getattr(lay, attr) == value:
            return
        self.win.doc.push_undo("propiedades de capa")
        setattr(lay, attr, value)
        self.win.after_layers_changed(refresh_table=False)

    def _cell_clicked(self, row, col):
        lay = self._layer_at(row)
        if not lay:
            return
        if col == 0:
            lay.visible = not lay.visible
            if not lay.visible and lay.name == self.win.doc.current_layer:
                self.win.log("Apagaste la capa actual: lo que dibujes no se verá.", "warn")
        elif col == 1:
            lay.locked = not lay.locked
        elif col == 2:
            lay.plot = not lay.plot
        elif col in (5, 6):
            self._popup_attr(lay, "linetype" if col == 5 else "lineweight", row, col)
            return
        else:
            return
        self.win.doc.modified = True
        self.win.after_layers_changed()

    def _popup_attr(self, lay: Layer, attr: str, row: int, col: int):
        m = QtWidgets.QMenu(self)
        if attr == "linetype":
            for n in LINETYPES:
                a = m.addAction(_ICON_CACHE.get(("lt", n)) or QtGui.QIcon(),
                                LT_LABEL.get(n, n))
                a.setData(n)
                a.setCheckable(True)
                a.setChecked(n == lay.linetype)
        else:
            for v in LINEWEIGHTS:
                a = m.addAction(_ICON_CACHE.get(("lw", v)) or QtGui.QIcon(), f"{v:.2f} mm")
                a.setData(v)
                a.setCheckable(True)
                a.setChecked(abs(v - lay.lineweight) < 1e-6)
        rect = self.table.visualItemRect(self.table.item(row, col))
        a = m.exec(self.table.viewport().mapToGlobal(rect.bottomLeft()))
        if a is not None:
            self._set_attr(lay.name, attr, a.data())
            self.refresh()

    def _cell_dblclicked(self, row, col):
        lay = self._layer_at(row)
        if not lay:
            return
        if col == 4:
            c = QtWidgets.QColorDialog.getColor(QtGui.QColor(lay.color), self,
                                                f"Color de la capa {lay.name}")
            if c.isValid():
                self.win.doc.push_undo("color de capa")
                lay.color = c.name()
                self.win.after_layers_changed()
        elif col == 3:
            self.win.set_current_layer(lay.name)

    def _item_changed(self, item):
        if self._loading or item.column() != 3:
            return
        lay = self._layer_at(item.row())
        new = item.text().replace("▶ ", "").strip()
        if not lay or not new or new == lay.name:
            self.refresh()
            return
        self.win.rename_layer(lay.name, new)

    def new_layer(self):
        doc = self.win.doc
        i = 1
        while f"Capa{i}" in doc.layers:
            i += 1
        name, ok = QtWidgets.QInputDialog.getText(self, "Nueva capa", "Nombre:",
                                                  text=f"Capa{i}")
        name = (name or "").strip()
        if ok and name:
            if name in doc.layers:
                self.win.log(f"La capa '{name}' ya existe.", "warn")
                return
            doc.push_undo("nueva capa")
            doc.add_layer(name)
            self.win.set_current_layer(name)

    def set_current(self):
        lay = self._layer_at(self.table.currentRow())
        if lay:
            self.win.set_current_layer(lay.name)

    def move_selection(self):
        lay = self._layer_at(self.table.currentRow())
        if lay:
            self.win.move_selection_to_layer(lay.name)
        else:
            self.win.log("Marca primero una capa en la tabla.", "warn")

    def isolate(self):
        lay = self._layer_at(self.table.currentRow())
        if lay:
            self.win.isolate_layers([lay.name])

    def all_on(self):
        for lay in self.win.doc.layers.values():
            lay.visible = True
            lay.locked = False
        self.win.after_layers_changed()

    def del_layer(self):
        lay = self._layer_at(self.table.currentRow())
        if not lay or lay.name == "0":
            self.win.log("La capa 0 no se puede borrar.", "warn")
            return
        used = sum(1 for e in self.win.doc.entities if e.layer == lay.name)
        if used and QtWidgets.QMessageBox.question(
                self, "Borrar capa",
                f"La capa '{lay.name}' contiene {used} objeto(s). ¿Borrar todo?") != \
                QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self.win.doc.push_undo("borrar capa")
        self.win.doc.remove([e for e in self.win.doc.entities if e.layer == lay.name])
        del self.win.doc.layers[lay.name]
        if self.win.doc.current_layer == lay.name:
            self.win.doc.current_layer = "0" if "0" in self.win.doc.layers \
                else list(self.win.doc.layers)[0]
        self.win.after_layers_changed()


class PropertiesPanel(QtWidgets.QWidget):
    def __init__(self, win):
        super().__init__()
        self.win = win
        self.header = QtWidgets.QLabel("Sin selección")
        self.header.setWordWrap(True)
        self.layer_box = QtWidgets.QComboBox()
        self.layer_box.currentTextChanged.connect(self._layer_changed)
        self.color_btn = ColorButton()
        self.color_btn.colorPicked.connect(lambda c: self.win.apply_general("color", c))
        self.lt_box = make_lt_combo()
        self.lt_box.activated.connect(
            lambda _i: self.win.apply_general("linetype", self.lt_box.currentData()))
        self.lw_box = make_lw_combo()
        self.lw_box.activated.connect(
            lambda _i: self.win.apply_general("lineweight", self.lw_box.currentData()))
        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Propiedad", "Valor"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemChanged.connect(self._changed)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.addWidget(self.header)
        form = QtWidgets.QFormLayout()
        form.setContentsMargins(0, 2, 0, 2)
        form.addRow("Capa:", self.layer_box)
        form.addRow("Color:", self.color_btn)
        form.addRow("Tipo línea:", self.lt_box)
        form.addRow("Grosor:", self.lw_box)
        lay.addLayout(form)
        lay.addWidget(self.table)
        self._loading = False
        self._keys: List[str] = []

    @staticmethod
    def _common(sel, attr):
        vals = {getattr(e, attr) for e in sel}
        return vals.pop() if len(vals) == 1 else "*varios*"

    def refresh(self):
        self._loading = True
        doc = self.win.doc
        sel = doc.selection()
        self.layer_box.clear()
        self.layer_box.addItems(list(doc.layers))
        self.table.setRowCount(0)
        self._keys = []
        if not sel:
            self.header.setText(
                f"Sin selección · {len(doc.entities)} entidades · "
                f"capa actual <b>{doc.current_layer}</b><br>"
                "<span style='color:#9a9aa2'>Color, tipo y grosor definen las "
                "propiedades de los objetos nuevos.</span>")
            self.layer_box.setCurrentText(doc.current_layer)
            self.color_btn.set_color(doc.current_color,
                                     doc.layers[doc.current_layer].color)
            _combo_select(self.lt_box, doc.current_linetype)
            _combo_select(self.lw_box, doc.current_lineweight)
            self._loading = False
            return
        layer = self._common(sel, "layer")
        color = self._common(sel, "color")
        lt = self._common(sel, "linetype")
        lw = self._common(sel, "lineweight")
        if layer == "*varios*":
            self.layer_box.insertItem(0, "*varios*")
        self.layer_box.setCurrentText(layer)
        self.color_btn.set_color(None if color == "*varios*" else color,
                                 doc.layer_of(sel[0]).color)
        if color == "*varios*":
            self.color_btn.setText("*varios*")
        _combo_select(self.lt_box, lt if lt != "*varios*" else None)
        _combo_select(self.lw_box, lw if lw != "*varios*" else None)
        if len(sel) > 1:
            kinds = {}
            for e in sel:
                kinds[e.kind] = kinds.get(e.kind, 0) + 1
            self.header.setText(f"<b>{len(sel)}</b> objetos: " +
                                ", ".join(f"{k}×{v}" for k, v in kinds.items()))
            self._loading = False
            return
        e = sel[0]
        self.header.setText(f"<b>{e.kind}</b> #{e.id} · grosor efectivo "
                            f"{doc.lineweight_of(e):.2f} mm")
        props = e.props()
        self.table.setRowCount(len(props))
        for r, (k, label, val) in enumerate(props):
            it = QtWidgets.QTableWidgetItem(label)
            it.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(r, 0, it)
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(val))
            self._keys.append(k)
        self._loading = False

    def _changed(self, item):
        if self._loading or item.column() != 1:
            return
        sel = self.win.doc.selection()
        if len(sel) != 1:
            return
        key = self._keys[item.row()] if item.row() < len(self._keys) else None
        if not key:
            return
        self.win.doc.push_undo("propiedades")
        if not sel[0].set_prop(key, item.text()):
            self.win.log("Valor no válido.", "warn")
        self.win.view.update()
        self.refresh()

    def _layer_changed(self, name):
        if self._loading or not name or name == "*varios*":
            return
        if self.win.doc.selection():
            self.win.move_selection_to_layer(name)
        else:
            self.win.set_current_layer(name)


class PropertyBar(QtWidgets.QToolBar):
    """Barra de propiedades: capa, color, tipo y grosor (como en AutoCAD)."""

    def __init__(self, win):
        super().__init__("Propiedades", win)
        self.setObjectName("tb_propiedades")
        self.win = win
        self.setMovable(False)
        self._loading = False
        self.addWidget(QtWidgets.QLabel(" Capa "))
        self.layer_box = QtWidgets.QComboBox()
        self.layer_box.setMinimumWidth(170)
        self.layer_box.setToolTip("Capa actual · con objetos seleccionados, los mueve "
                                  "a la capa elegida")
        self.layer_box.activated.connect(self._layer_activated)
        self.addWidget(self.layer_box)
        b = QtWidgets.QToolButton()
        b.setText("⇡ Capa del objeto")
        b.setToolTip("Hacer actual la capa del objeto seleccionado (LAYMCUR)")
        b.clicked.connect(lambda: self.win.execute("LAYMCUR", True))
        self.addWidget(b)
        self.addSeparator()
        self.addWidget(QtWidgets.QLabel(" Color "))
        self.color_btn = ColorButton()
        self.color_btn.colorPicked.connect(lambda c: self.win.apply_general("color", c))
        self.addWidget(self.color_btn)
        self.addWidget(QtWidgets.QLabel("  Tipo "))
        self.lt_box = make_lt_combo()
        self.lt_box.activated.connect(
            lambda _i: self.win.apply_general("linetype", self.lt_box.currentData()))
        self.addWidget(self.lt_box)
        self.addWidget(QtWidgets.QLabel("  Grosor "))
        self.lw_box = make_lw_combo()
        self.lw_box.setMinimumWidth(130)
        self.lw_box.activated.connect(
            lambda _i: self.win.apply_general("lineweight", self.lw_box.currentData()))
        self.addWidget(self.lw_box)

    def refresh(self):
        self._loading = True
        doc = self.win.doc
        self.layer_box.clear()
        for name, lay in doc.layers.items():
            pm = QtGui.QPixmap(12, 12)
            pm.fill(QtGui.QColor(lay.color))
            label = name + ("" if lay.visible else "  (apagada)") + \
                ("  🔒" if lay.locked else "")
            self.layer_box.addItem(QtGui.QIcon(pm), label, name)
        sel = doc.selection()
        if sel:
            layers = {e.layer for e in sel}
            target = layers.pop() if len(layers) == 1 else None
            cols = {e.color for e in sel}
            lts = {e.linetype for e in sel}
            lws = {e.lineweight for e in sel}
            self.color_btn.set_color(cols.pop() if len(cols) == 1 else None,
                                     doc.layer_of(sel[0]).color)
            _combo_select(self.lt_box, lts.pop() if len(lts) == 1 else None)
            _combo_select(self.lw_box, lws.pop() if len(lws) == 1 else None)
        else:
            target = doc.current_layer
            self.color_btn.set_color(doc.current_color, doc.layers[doc.current_layer].color)
            _combo_select(self.lt_box, doc.current_linetype)
            _combo_select(self.lw_box, doc.current_lineweight)
        _combo_select(self.layer_box, target)
        self._loading = False

    def _layer_activated(self, _i):
        if self._loading:
            return
        name = self.layer_box.currentData()
        if not name:
            return
        if self.win.doc.selection():
            self.win.move_selection_to_layer(name)
        else:
            self.win.set_current_layer(name)


# =========================================================================== #
#  11b. IMPRESIÓN — impresora PDF vectorial virtual
# =========================================================================== #
#: Formatos de papel (ancho, alto) en mm, en vertical.
PAPER_SIZES: Dict[str, Optional[Tuple[float, float]]] = {
    "ISO A4": (210.0, 297.0), "ISO A3": (297.0, 420.0), "ISO A2": (420.0, 594.0),
    "ISO A1": (594.0, 841.0), "ISO A0": (841.0, 1189.0),
    "ISO B3": (353.0, 500.0), "ISO B2": (500.0, 707.0),
    "Carta (Letter)": (215.9, 279.4), "Oficio (Legal)": (215.9, 355.6),
    "Tabloide (11×17)": (279.4, 431.8), "ARCH C (18×24)": (457.2, 609.6),
    "ARCH D (24×36)": (609.6, 914.4), "Personalizado": None,
}
#: milímetros reales por unidad de dibujo
UNIT_MM = {"mm": 1.0, "cm": 10.0, "m": 1000.0, "in": 25.4, "ft": 304.8}
STANDARD_SCALES = ["Ajustar al papel", "1:1", "1:2", "1:5", "1:10", "1:20", "1:25",
                   "1:50", "1:75", "1:100", "1:125", "1:200", "1:250", "1:500",
                   "1:1000", "1:2000", "1:5000", "2:1", "5:1", "10:1"]
PLOT_STYLES = {"mono": "Monocromo (negro)", "gray": "Escala de grises",
               "color": "Color (claros → negro)"}
PLOT_AREAS = {"extents": "Extensión del dibujo", "display": "Pantalla actual",
              "window": "Ventana designada", "selection": "Objetos seleccionados"}


class PlotSettings:
    """Configuración de trazado; se recuerda durante la sesión."""

    def __init__(self):
        self.fmt = "pdf"                 # pdf | svg | png
        self.dpi = 300                   # sólo PNG
        self.paper = "ISO A3"
        self.custom = (420.0, 297.0)
        self.landscape = True
        self.area = "extents"
        self.window: Optional[Tuple[float, float, float, float]] = None
        self.scale = "Ajustar al papel"
        self.center = True
        self.offset = (0.0, 0.0)
        self.margin = 10.0
        self.style = "mono"
        self.lineweights = True
        self.scale_lw = False
        self.min_lw = 0.05
        self.ltscale = 1.0
        self.frame = True
        self.titleblock = True
        self.scalebar = True
        self.north = False
        self.project = ""
        self.title = ""
        self.author = ""
        self.company = "Centro Producción del Espacio · UDLA"
        self.sheet = "1/1"
        self.date = ""
        self.open_after = True

    def page_mm(self) -> Tuple[float, float]:
        wh = PAPER_SIZES.get(self.paper) or self.custom
        w, h = min(wh), max(wh)
        return (h, w) if self.landscape else (w, h)

    def ratio(self) -> Optional[float]:
        """Milímetros de papel por milímetro real; None = ajustar."""
        s = (self.scale or "").strip()
        if not s or s.lower().startswith("ajustar"):
            return None
        m = re.match(r"^\s*([\d.,]+)\s*[:/]\s*([\d.,]+)\s*$", s)
        if not m:
            return None
        a = float(m.group(1).replace(",", "."))
        b = float(m.group(2).replace(",", "."))
        return a / b if a > 0 and b > 0 else None


class PlotLayout:
    """Geometría de la lámina: zonas en mm de papel (origen arriba-izquierda)."""

    TB_H = 30.0          # alto del cajetín
    GAP = 4.0

    def __init__(self, doc: "Document", s: PlotSettings,
                 world: Tuple[float, float, float, float]):
        self.doc = doc
        self.s = s
        self.pw, self.ph = s.page_mm()
        m = s.margin
        self.inner = (m, m, self.pw - 2 * m, self.ph - 2 * m)          # x, y, w, h
        ix, iy, iw, ih = self.inner
        if s.titleblock:
            self.tb = (ix, iy + ih - self.TB_H, iw, self.TB_H)
            self.area = (ix + self.GAP, iy + self.GAP, iw - 2 * self.GAP,
                         ih - self.TB_H - 2 * self.GAP)
        else:
            self.tb = None
            self.area = (ix + self.GAP, iy + self.GAP, iw - 2 * self.GAP, ih - 2 * self.GAP)
        x0, y0, x1, y1 = world
        if x1 - x0 < 1e-9:
            x0, x1 = x0 - 1, x1 + 1
        if y1 - y0 < 1e-9:
            y0, y1 = y0 - 1, y1 + 1
        self.world = (x0, y0, x1, y1)
        ww, wh = x1 - x0, y1 - y0
        ax, ay, aw, ah = self.area
        unit = UNIT_MM.get(doc.units, 1.0)
        r = s.ratio()
        if r is None:
            self.k = min(aw / ww, ah / wh)              # mm de papel por unidad
            self.fitted = True
        else:
            self.k = unit * r
            self.fitted = False
        self.real_ratio = unit / self.k                   # 1 : real_ratio
        dw, dh = ww * self.k, wh * self.k
        if s.center:
            ox = ax + (aw - dw) / 2
            oy = ay + (ah + dh) / 2
        else:
            ox = ax
            oy = ay + ah
        self.ox = ox + s.offset[0]                        # papel de x0 (mm)
        self.oy = oy - s.offset[1]                        # papel de y0 (mm)
        self.overflow = (not self.fitted) and (dw > aw + 0.5 or dh > ah + 0.5)

    def scale_label(self) -> str:
        r = self.real_ratio
        if r >= 1:
            txt = f"1:{r:.6g}" if abs(r - round(r)) < 1e-6 else f"1:{r:.1f}"
        else:
            inv = 1 / r
            txt = f"{inv:.6g}:1" if abs(inv - round(inv)) < 1e-6 else f"{inv:.2f}:1"
        return ("≈ " + txt + " (ajustada)") if self.fitted else txt


class PlotView:
    """Imita la interfaz de transformación del lienzo para dibujar en papel."""

    plotting = True

    def __init__(self, lay: PlotLayout, dpmm: float, origin: QPointF = QPointF(0, 0)):
        self.lay = lay
        self.dpmm = dpmm
        self.scale = lay.k * dpmm                 # píxeles de dispositivo por unidad
        self.origin = origin
        self.marker = 0.8 * dpmm
        self._wx0, self._wy0 = lay.world[0], lay.world[1]

    def to_screen(self, p: Vec) -> QPointF:
        return QPointF(self.origin.x() + (self.lay.ox + (p[0] - self._wx0) * self.lay.k)
                       * self.dpmm,
                       self.origin.y() + (self.lay.oy - (p[1] - self._wy0) * self.lay.k)
                       * self.dpmm)

    def px(self, n: float) -> float:
        return n / self.scale

    def draw_arc(self, g, c, r, a0, a1):
        Canvas.draw_arc(self, g, c, r, a0, a1)

    def draw_arrow(self, g, tail, tip, color, size=None):
        Canvas.draw_arrow(self, g, tail, tip, color, size or 2.2 * self.dpmm)


def _plot_color(hexc: str, style: str) -> QtGui.QColor:
    c = QtGui.QColor(hexc)
    lum = 0.2126 * c.redF() + 0.7152 * c.greenF() + 0.0722 * c.blueF()
    if style == "mono":
        return QtGui.QColor("#000000")
    if style == "gray":
        if lum > 0.82:
            return QtGui.QColor("#000000")
        v = int(lum * 200)
        return QtGui.QColor(v, v, v)
    if lum > 0.82:                       # blanco / gris claro sobre papel blanco
        return QtGui.QColor("#000000")
    return c


def plot_entities(doc: "Document", s: PlotSettings,
                  selection: Optional[List[Entity]] = None) -> List[Entity]:
    out = []
    for e in (selection if s.area == "selection" and selection else doc.entities):
        lay = doc.layers.get(e.layer)
        if lay is not None and (not lay.visible or not lay.plot):
            continue
        out.append(e)
    return out


def plot_world_box(doc: "Document", s: PlotSettings, ents: List[Entity],
                   display: Optional[Tuple[float, float, float, float]] = None):
    if s.area == "window" and s.window:
        return s.window
    if s.area == "display" and display:
        return display
    bb = doc.bbox(ents) if ents else None
    return bb or (0.0, 0.0, 100.0, 100.0)


def _nice_length(target: float) -> float:
    if target <= 0:
        return 1.0
    e = 10 ** math.floor(math.log10(target))
    for m in (1, 2, 2.5, 5, 10):
        if m * e >= target * 0.75:
            return m * e
    return 10 * e


def render_plot(g: QtGui.QPainter, doc: "Document", s: PlotSettings, lay: PlotLayout,
                ents: List[Entity], dpmm: float, origin: QPointF = QPointF(0, 0)):
    """Dibuja la lámina completa en `g` (PDF, SVG, PNG o vista previa)."""
    view = PlotView(lay, dpmm, origin)

    def R(x, y, w, h) -> QRectF:
        return QRectF(origin.x() + x * dpmm, origin.y() + y * dpmm, w * dpmm, h * dpmm)

    def P(x, y) -> QPointF:
        return QPointF(origin.x() + x * dpmm, origin.y() + y * dpmm)

    def pen_mm(width_mm: float, color="#000000") -> QtGui.QPen:
        p = QtGui.QPen(QtGui.QColor(color))
        p.setWidthF(max(width_mm * dpmm, 0.01))
        p.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return p

    g.save()
    g.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
    g.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing, True)
    g.fillRect(R(0, 0, lay.pw, lay.ph), QtGui.QColor("#ffffff"))

    # --- dibujo ---------------------------------------------------------- #
    g.save()
    ax, ay, aw, ah = lay.area
    g.setClipRect(R(ax, ay, aw, ah))
    unit = UNIT_MM.get(doc.units, 1.0)
    lw_factor = (lay.k / unit) if s.scale_lw else 1.0
    wx0, wy0, wx1, wy1 = lay.world
    for e in ents:
        try:
            bx0, by0, bx1, by1 = e.bbox()
            if bx1 < wx0 or bx0 > wx1 or by1 < wy0 or by0 > wy1:
                continue
            lw = doc.lineweight_of(e) if s.lineweights else s.min_lw
            lw = max(lw * lw_factor, s.min_lw)
            pen = QtGui.QPen(_plot_color(doc.color_of(e), s.style))
            w = max(lw * dpmm, 0.01)
            pen.setWidthF(w)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            pat = LINETYPES.get(doc.linetype_of(e), [])
            if pat:
                pen.setCapStyle(Qt.PenCapStyle.FlatCap)
                pen.setStyle(Qt.PenStyle.CustomDashLine)
                pen.setDashPattern([max(v * s.ltscale * dpmm / w, 0.05) for v in pat])
            e.draw(g, view, pen)
        except Exception:
            traceback.print_exc()
    g.restore()

    # --- marco ------------------------------------------------------------- #
    ix, iy, iw, ih = lay.inner
    if s.frame:
        g.setPen(pen_mm(0.5))
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.drawRect(R(ix, iy, iw, ih))
        if s.margin > 6:
            g.setPen(pen_mm(0.13))
            g.drawRect(R(ix - 3, iy - 3, iw + 6, ih + 6))

    # --- escala gráfica ------------------------------------------------------ #
    if s.scalebar:
        target_mm = min(60.0, aw * 0.25)
        real = _nice_length(target_mm / lay.k)          # unidades de dibujo
        L = real * lay.k
        x = ax + 3
        y = ay + ah - 6
        seg = L / 4
        g.setPen(pen_mm(0.18))
        for i in range(4):
            g.setBrush(QtGui.QColor("#000000") if i % 2 == 0 else QtGui.QColor("#ffffff"))
            g.drawRect(R(x + i * seg, y, seg, 1.6))
        f = QtGui.QFont("Helvetica")
        f.setPixelSize(max(1, int(2.2 * dpmm)))
        g.setFont(f)
        g.setPen(QtGui.QColor("#000000"))
        g.drawText(P(x - 0.6, y - 1.0), "0")
        g.drawText(P(x + L - 2, y - 1.0), f"{fmt(real, 3)} {doc.units}")
        g.setBrush(Qt.BrushStyle.NoBrush)

    if s.north:
        cx, cy = ax + aw - 10, ay + 12
        path = QtGui.QPainterPath(P(cx, cy - 7))
        path.lineTo(P(cx + 3.5, cy + 5))
        path.lineTo(P(cx, cy + 2.5))
        path.closeSubpath()
        g.setPen(pen_mm(0.25))
        g.setBrush(QtGui.QColor("#000000"))
        g.drawPath(path)
        g.setBrush(Qt.BrushStyle.NoBrush)
        path2 = QtGui.QPainterPath(P(cx, cy - 7))
        path2.lineTo(P(cx - 3.5, cy + 5))
        path2.lineTo(P(cx, cy + 2.5))
        g.drawPath(path2)
        f = QtGui.QFont("Helvetica")
        f.setPixelSize(max(1, int(3.2 * dpmm)))
        f.setBold(True)
        g.setFont(f)
        g.setPen(QtGui.QColor("#000000"))
        g.drawText(R(cx - 5, cy - 13, 10, 5), int(Qt.AlignmentFlag.AlignCenter), "N")

    # --- cajetín ---------------------------------------------------------- #
    if lay.tb:
        tx, ty, tw, th = lay.tb
        g.setPen(pen_mm(0.5))
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.drawRect(R(tx, ty, tw, th))
        import datetime as _dt
        date = s.date or _dt.date.today().strftime("%d-%m-%Y")
        cells = [
            ("PROYECTO", s.project or "—", 0.30),
            ("LÁMINA", s.title or (os.path.splitext(os.path.basename(doc.filename))[0]
                                    if doc.filename else "Sin título"), 0.26),
            ("ESCALA", lay.scale_label(), 0.13),
            ("FECHA", date, 0.10),
            ("DIBUJÓ", s.author or "—", 0.11),
            ("N°", s.sheet or "1/1", 0.10),
        ]
        x = tx
        fl = QtGui.QFont("Helvetica")
        fl.setPixelSize(max(1, int(2.0 * dpmm)))
        fv = QtGui.QFont("Helvetica")
        fv.setBold(True)
        for i, (lab, val, frac) in enumerate(cells):
            w = tw * frac
            if i:
                g.setPen(pen_mm(0.25))
                g.drawLine(P(x, ty), P(x, ty + th))
            g.setPen(QtGui.QColor("#000000"))
            g.setFont(fl)
            g.drawText(R(x + 2, ty + 1.5, w - 4, 4),
                       int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop), lab)
            size = 5.0 if i < 2 else 3.6
            fv.setPixelSize(max(1, int(size * dpmm)))
            fm = QtGui.QFontMetricsF(fv)
            while fm.horizontalAdvance(val) > (w - 4) * dpmm and size > 1.8:
                size -= 0.3
                fv.setPixelSize(max(1, int(size * dpmm)))
                fm = QtGui.QFontMetricsF(fv)
            g.setFont(fv)
            g.drawText(R(x + 2, ty + 6, w - 4, th - 12),
                       int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter |
                           Qt.TextFlag.TextWordWrap), val)
            x += w
        # pie: empresa y programa
        g.setPen(pen_mm(0.18))
        g.drawLine(P(tx, ty + th - 6), P(tx + tw * 0.56, ty + th - 6))
        fl.setPixelSize(max(1, int(2.2 * dpmm)))
        g.setFont(fl)
        g.setPen(QtGui.QColor("#333333"))
        g.drawText(R(tx + 2, ty + th - 6, tw * 0.56 - 4, 6),
                   int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                   f"{s.company}   ·   {APP_NAME} {APP_VERSION}   ·   unidades: {doc.units}")
    g.restore()


def write_plot(path: str, doc: "Document", s: PlotSettings, lay: PlotLayout,
               ents: List[Entity]) -> str:
    """Genera el archivo final. Devuelve la ruta escrita."""
    pw, ph = lay.pw, lay.ph
    fmt_ = s.fmt
    if fmt_ == "pdf":
        wr = QtGui.QPdfWriter(path)
        ps = QtGui.QPageSize(QSizeF(min(pw, ph), max(pw, ph)),
                             QtGui.QPageSize.Unit.Millimeter, s.paper,
                             QtGui.QPageSize.SizeMatchPolicy.ExactMatch)
        orient = QtGui.QPageLayout.Orientation.Landscape if pw > ph else \
            QtGui.QPageLayout.Orientation.Portrait
        wr.setPageLayout(QtGui.QPageLayout(ps, orient, QtCore.QMarginsF(0, 0, 0, 0),
                                           QtGui.QPageLayout.Unit.Millimeter))
        wr.setResolution(1200)
        wr.setTitle(s.title or (os.path.basename(doc.filename) if doc.filename
                                else "VectorCAD"))
        wr.setCreator(f"{APP_NAME} {APP_VERSION}")
        try:
            wr.setPdfVersion(QtGui.QPagedPaintDevice.PdfVersion.PdfVersion_1_6)
        except Exception:
            pass
        g = QtGui.QPainter(wr)
        dpmm = wr.resolution() / 25.4
        render_plot(g, doc, s, lay, ents, dpmm)
        g.end()
        return path
    if fmt_ == "svg":
        from PySide6.QtSvg import QSvgGenerator
        gen = QSvgGenerator()
        gen.setFileName(path)
        dpmm = 96 / 25.4
        gen.setResolution(96)
        gen.setSize(QtCore.QSize(int(pw * dpmm), int(ph * dpmm)))
        gen.setViewBox(QRectF(0, 0, pw * dpmm, ph * dpmm))
        gen.setTitle(s.title or "VectorCAD")
        gen.setDescription(f"{APP_NAME} {APP_VERSION}")
        g = QtGui.QPainter(gen)
        render_plot(g, doc, s, lay, ents, dpmm)
        g.end()
        return path
    dpmm = s.dpi / 25.4
    img = QtGui.QImage(int(pw * dpmm), int(ph * dpmm), QtGui.QImage.Format.Format_RGB32)
    img.setDotsPerMeterX(int(s.dpi / 0.0254))
    img.setDotsPerMeterY(int(s.dpi / 0.0254))
    img.fill(QtGui.QColor("#ffffff"))
    g = QtGui.QPainter(img)
    render_plot(g, doc, s, lay, ents, dpmm)
    g.end()
    img.save(path, "PNG")
    return path


class PlotPreview(QtWidgets.QWidget):
    """Vista previa de la lámina tal como se imprimirá."""

    def __init__(self, dlg):
        super().__init__()
        self.dlg = dlg
        self.setMinimumSize(460, 360)

    def paintEvent(self, ev):
        g = QtGui.QPainter(self)
        g.fillRect(self.rect(), QtGui.QColor("#2a2c33"))
        try:
            lay, ents = self.dlg.layout_now()
        except Exception as ex:
            g.setPen(QtGui.QColor("#ff8a80"))
            g.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter), str(ex))
            return
        pad = 18
        dpmm = min((self.width() - 2 * pad) / lay.pw, (self.height() - 2 * pad) / lay.ph)
        ox = (self.width() - lay.pw * dpmm) / 2
        oy = (self.height() - lay.ph * dpmm) / 2
        g.fillRect(QRectF(ox + 5, oy + 5, lay.pw * dpmm, lay.ph * dpmm),
                   QtGui.QColor(0, 0, 0, 110))
        render_plot(g, self.dlg.doc, self.dlg.settings, lay, ents, dpmm, QPointF(ox, oy))
        # zona imprimible y aviso de desborde
        pen = QtGui.QPen(QtGui.QColor("#4d7cfe"))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        g.setPen(pen)
        ax, ay, aw, ah = lay.area
        g.drawRect(QRectF(ox + ax * dpmm, oy + ay * dpmm, aw * dpmm, ah * dpmm))
        if lay.overflow:
            g.setPen(QtGui.QColor("#ff5252"))
            g.drawText(QPointF(ox + 6, oy + lay.ph * dpmm + 14),
                       "⚠ El dibujo no cabe en el papel a esta escala.")


class PlotDialog(QtWidgets.QDialog):
    """Impresora virtual: PDF vectorial, SVG o PNG con cajetín y escala."""

    PICK_WINDOW = 2

    def __init__(self, win, settings: PlotSettings):
        super().__init__(win)
        self.win = win
        self.doc = win.doc
        self.settings = settings
        self.setWindowTitle("Imprimir / Trazar — impresora PDF vectorial")
        self.resize(1180, 760)
        s = settings
        self._display_box = win.view_world_box()

        form_w = QtWidgets.QWidget()
        form = QtWidgets.QVBoxLayout(form_w)
        form.setContentsMargins(6, 6, 6, 6)

        def group(title):
            gb = QtWidgets.QGroupBox(title)
            fl = QtWidgets.QFormLayout(gb)
            fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            form.addWidget(gb)
            return fl

        # salida
        fl = group("Impresora")
        self.fmt = QtWidgets.QComboBox()
        for k, v in [("pdf", "VectorCAD PDF (vectorial)"), ("svg", "VectorCAD SVG (vectorial)"),
                     ("png", "VectorCAD PNG (ráster)")]:
            self.fmt.addItem(v, k)
        _combo_select(self.fmt, s.fmt)
        self.dpi = QtWidgets.QSpinBox()
        self.dpi.setRange(72, 1200)
        self.dpi.setSingleStep(50)
        self.dpi.setValue(s.dpi)
        self.dpi.setSuffix(" ppp")
        fl.addRow("Formato:", self.fmt)
        fl.addRow("Resolución PNG:", self.dpi)

        # papel
        fl = group("Papel")
        self.paper = QtWidgets.QComboBox()
        self.paper.addItems(list(PAPER_SIZES))
        self.paper.setCurrentText(s.paper)
        self.cw = QtWidgets.QDoubleSpinBox()
        self.ch = QtWidgets.QDoubleSpinBox()
        for sp, v in ((self.cw, s.custom[0]), (self.ch, s.custom[1])):
            sp.setRange(20, 5000)
            sp.setDecimals(1)
            sp.setSuffix(" mm")
            sp.setValue(v)
        crow = QtWidgets.QHBoxLayout()
        crow.addWidget(self.cw)
        crow.addWidget(QtWidgets.QLabel("×"))
        crow.addWidget(self.ch)
        self.orient = QtWidgets.QComboBox()
        self.orient.addItems(["Horizontal", "Vertical"])
        self.orient.setCurrentIndex(0 if s.landscape else 1)
        self.margin = QtWidgets.QDoubleSpinBox()
        self.margin.setRange(0, 60)
        self.margin.setSuffix(" mm")
        self.margin.setValue(s.margin)
        fl.addRow("Tamaño:", self.paper)
        fl.addRow("Personalizado:", crow)
        fl.addRow("Orientación:", self.orient)
        fl.addRow("Margen:", self.margin)

        # área y escala
        fl = group("Área y escala")
        self.area = QtWidgets.QComboBox()
        for k, v in PLOT_AREAS.items():
            self.area.addItem(v, k)
        _combo_select(self.area, s.area)
        self.pick_btn = QtWidgets.QPushButton("Designar ventana en el dibujo <")
        self.pick_btn.clicked.connect(lambda: self.done(self.PICK_WINDOW))
        self.scale = QtWidgets.QComboBox()
        self.scale.setEditable(True)
        self.scale.addItems(STANDARD_SCALES)
        self.scale.setCurrentText(s.scale)
        self.scale.setToolTip("Escribe cualquier escala, p. ej. 1:75 o 1:333")
        self.center = QtWidgets.QCheckBox("Centrar en el papel")
        self.center.setChecked(s.center)
        self.offx = QtWidgets.QDoubleSpinBox()
        self.offy = QtWidgets.QDoubleSpinBox()
        for sp, v in ((self.offx, s.offset[0]), (self.offy, s.offset[1])):
            sp.setRange(-2000, 2000)
            sp.setSuffix(" mm")
            sp.setValue(v)
        orow = QtWidgets.QHBoxLayout()
        orow.addWidget(self.offx)
        orow.addWidget(self.offy)
        self.scale_info = QtWidgets.QLabel("")
        self.scale_info.setWordWrap(True)
        self.scale_info.setStyleSheet("color:#9a9aa2;")
        fl.addRow("Qué imprimir:", self.area)
        fl.addRow("", self.pick_btn)
        fl.addRow("Escala:", self.scale)
        fl.addRow("", self.center)
        fl.addRow("Desfase X / Y:", orow)
        fl.addRow("", self.scale_info)

        # estilo
        fl = group("Estilo de trazado")
        self.style = QtWidgets.QComboBox()
        for k, v in PLOT_STYLES.items():
            self.style.addItem(v, k)
        _combo_select(self.style, s.style)
        self.lws = QtWidgets.QCheckBox("Imprimir grosores de línea")
        self.lws.setChecked(s.lineweights)
        self.scale_lw = QtWidgets.QCheckBox("Escalar grosores con la escala")
        self.scale_lw.setChecked(s.scale_lw)
        self.min_lw = QtWidgets.QDoubleSpinBox()
        self.min_lw.setRange(0.0, 1.0)
        self.min_lw.setDecimals(2)
        self.min_lw.setSingleStep(0.01)
        self.min_lw.setSuffix(" mm")
        self.min_lw.setValue(s.min_lw)
        self.ltscale = QtWidgets.QDoubleSpinBox()
        self.ltscale.setRange(0.05, 100)
        self.ltscale.setDecimals(2)
        self.ltscale.setValue(s.ltscale)
        fl.addRow("Plumillas:", self.style)
        fl.addRow("", self.lws)
        fl.addRow("", self.scale_lw)
        fl.addRow("Grosor mínimo:", self.min_lw)
        fl.addRow("Escala tipo línea:", self.ltscale)

        # lámina
        fl = group("Lámina y cajetín")
        self.frame = QtWidgets.QCheckBox("Marco")
        self.frame.setChecked(s.frame)
        self.tb = QtWidgets.QCheckBox("Cajetín")
        self.tb.setChecked(s.titleblock)
        self.sbar = QtWidgets.QCheckBox("Escala gráfica")
        self.sbar.setChecked(s.scalebar)
        self.north = QtWidgets.QCheckBox("Norte")
        self.north.setChecked(s.north)
        crow2 = QtWidgets.QHBoxLayout()
        for w in (self.frame, self.tb, self.sbar, self.north):
            crow2.addWidget(w)
        fl.addRow(crow2)
        self.f_project = QtWidgets.QLineEdit(s.project)
        self.f_title = QtWidgets.QLineEdit(s.title)
        self.f_author = QtWidgets.QLineEdit(s.author)
        self.f_company = QtWidgets.QLineEdit(s.company)
        self.f_sheet = QtWidgets.QLineEdit(s.sheet)
        self.f_date = QtWidgets.QLineEdit(s.date)
        self.f_date.setPlaceholderText("hoy")
        fl.addRow("Proyecto:", self.f_project)
        fl.addRow("Lámina:", self.f_title)
        fl.addRow("Dibujó:", self.f_author)
        fl.addRow("Institución:", self.f_company)
        fl.addRow("N° lámina:", self.f_sheet)
        fl.addRow("Fecha:", self.f_date)

        self.open_after = QtWidgets.QCheckBox("Abrir el archivo al terminar")
        self.open_after.setChecked(s.open_after)
        form.addWidget(self.open_after)
        form.addStretch(1)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(form_w)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(410)

        self.preview = PlotPreview(self)
        split = QtWidgets.QSplitter()
        split.addWidget(scroll)
        split.addWidget(self.preview)
        split.setStretchFactor(1, 1)

        bb = QtWidgets.QDialogButtonBox()
        self.ok_btn = bb.addButton("Imprimir…", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        bb.addButton("Cancelar", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(split, 1)
        lay.addWidget(bb)

        for w in (self.fmt, self.paper, self.orient, self.area, self.style, self.scale):
            w.currentIndexChanged.connect(self._changed)
        self.scale.editTextChanged.connect(self._changed)
        for w in (self.dpi, self.cw, self.ch, self.margin, self.offx, self.offy,
                  self.min_lw, self.ltscale):
            w.valueChanged.connect(self._changed)
        for w in (self.center, self.lws, self.scale_lw, self.frame, self.tb, self.sbar,
                  self.north, self.open_after):
            w.toggled.connect(self._changed)
        for w in (self.f_project, self.f_title, self.f_author, self.f_company,
                  self.f_sheet, self.f_date):
            w.textChanged.connect(self._changed)
        self._changed()

    def _changed(self, *_):
        s = self.settings
        s.fmt = self.fmt.currentData() or "pdf"
        s.dpi = self.dpi.value()
        s.paper = self.paper.currentText()
        s.custom = (self.cw.value(), self.ch.value())
        s.landscape = self.orient.currentIndex() == 0
        s.margin = self.margin.value()
        s.area = self.area.currentData() or "extents"
        s.scale = self.scale.currentText()
        s.center = self.center.isChecked()
        s.offset = (self.offx.value(), self.offy.value())
        s.style = self.style.currentData() or "mono"
        s.lineweights = self.lws.isChecked()
        s.scale_lw = self.scale_lw.isChecked()
        s.min_lw = self.min_lw.value()
        s.ltscale = self.ltscale.value()
        s.frame = self.frame.isChecked()
        s.titleblock = self.tb.isChecked()
        s.scalebar = self.sbar.isChecked()
        s.north = self.north.isChecked()
        s.project = self.f_project.text()
        s.title = self.f_title.text()
        s.author = self.f_author.text()
        s.company = self.f_company.text()
        s.sheet = self.f_sheet.text()
        s.date = self.f_date.text()
        s.open_after = self.open_after.isChecked()
        custom = s.paper == "Personalizado"
        self.cw.setEnabled(custom)
        self.ch.setEnabled(custom)
        self.dpi.setEnabled(s.fmt == "png")
        self.offx.setEnabled(not s.center)
        self.offy.setEnabled(not s.center)
        self.pick_btn.setEnabled(True)
        try:
            lay, ents = self.layout_now()
            pw, ph = lay.pw, lay.ph
            txt = (f"Papel {pw:.0f}×{ph:.0f} mm · escala {lay.scale_label()} · "
                   f"{len(ents)} objetos")
            if s.area == "window" and not s.window:
                txt += " · ⚠ falta designar la ventana"
            self.scale_info.setText(txt)
        except Exception as ex:
            self.scale_info.setText(str(ex))
        self.preview.update()

    def layout_now(self) -> Tuple[PlotLayout, List[Entity]]:
        s = self.settings
        ents = plot_entities(self.doc, s, self.doc.selection())
        world = plot_world_box(self.doc, s, ents, self._display_box)
        return PlotLayout(self.doc, s, world), ents


# =========================================================================== #
#  12. VENTANA PRINCIPAL E INTÉRPRETE
# =========================================================================== #
_INVALID = object()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.doc = Document()
        self.view = Canvas(self.doc)
        self.setCentralWidget(self.view)

        # parámetros persistentes de sesión
        self.text_height = 2.5
        self.offset_dist = 5.0
        self.fillet_radius = 2.0

        # estado del intérprete
        self.ctx: Optional[Ctx] = None
        self.gen = None
        self.prompt: Optional[Prompt] = None
        self.last_cmd: Optional[str] = None
        self.history: List[str] = []
        self.hist_pos = 0
        self.script_queue: List[str] = []
        self.recording: Optional[List[str]] = None

        # entrada dinámica (DIN): valores fijados con Tab y campo activo
        self.dyn_on = True
        self.dyn_locks: Dict[str, float] = {}
        self.dyn_idx = 0
        self._num_pick: Optional[Vec] = None          # 1er punto al medir una distancia
        self._iso_state: Optional[Dict[str, bool]] = None
        self.plot_settings = PlotSettings()
        self.settings = QtCore.QSettings("CEPRODEP", os.environ.get("VECTORCAD_SETTINGS", "VectorCAD"))
        self._import_thread = None

        self._build_docks()
        self._build_menu()
        self._build_toolbar()
        self._build_status()
        self._load_settings()

        self.view.pointPicked.connect(self._on_point)
        self.view.mouseMoved.connect(self._on_move)
        self.view.selectionChanged.connect(self.after_selection)
        self.view.zoomChanged.connect(self.refresh_status)
        self.cmd_input.textChanged.connect(lambda _t: self.view.refresh_overlay())
        self.setAcceptDrops(True)
        icon = app_icon()
        if icon is not None:
            self.setWindowIcon(icon)

        self.update_title()
        self.refresh_panels()
        self.log(f"{APP_NAME} {APP_VERSION} — {QT_LIB} · "
                 f"shapely {'ON' if HAS_SHAPELY else 'off'} · "
                 f"ezdxf {'ON' if HAS_EZDXF else 'off'} · DWG: {dwg_converter_name()}")
        self.log("Escribe un alias (L, C, REC, PL, M, TR, F, UNI…) y pulsa Enter. "
                 "'?' muestra la lista completa. Ctrl+P imprime a PDF.")
        self.log("Entrada dinámica: durante un comando escribe la distancia y pulsa Tab "
                 "para fijarla y pasar al ángulo; Enter acepta. F12 la activa/desactiva.")
        self.log("Rueda = zoom · botón central o Mayús+arrastrar = encuadre · "
                 "clic derecho o Esc = cancelar · Enter en vacío = repetir comando.")
        self.cmd_input.setFocus()

    # ------------------------------------------------------------------ UI --
    def _build_docks(self):
        # panel lateral
        self.layer_panel = LayerPanel(self)
        self.props_panel = PropertiesPanel(self)
        self.layer_dock = QtWidgets.QDockWidget("Capas", self)
        self.layer_dock.setObjectName("dock_capas")
        self.layer_dock.setWidget(self.layer_panel)
        self.props_dock = QtWidgets.QDockWidget("Propiedades", self)
        self.props_dock.setObjectName("dock_props")
        self.props_dock.setWidget(self.props_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.props_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layer_dock)

        # consola de comandos
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        v.setContentsMargins(4, 2, 4, 4)
        v.setSpacing(3)
        self.history_view = QtWidgets.QPlainTextEdit()
        self.history_view.setReadOnly(True)
        self.history_view.setMaximumHeight(150)
        self.history_view.setStyleSheet(
            "background:#0b0b0d;color:#9fe;font-family:Menlo,Monaco,monospace;font-size:12px;")
        row = QtWidgets.QHBoxLayout()
        self.prompt_label = QtWidgets.QLabel("Comando:")
        self.prompt_label.setStyleSheet("color:#ffd54f;font-family:Menlo,Monaco,monospace;")
        self.cmd_input = QtWidgets.QLineEdit()
        self.cmd_input.setStyleSheet("font-family:Menlo,Monaco,monospace;")
        self.cmd_input.setPlaceholderText("alias + Enter  (?, L, C, REC, M, TR, UNI…)")
        self.cmd_input.returnPressed.connect(self._on_input)
        self.cmd_input.installEventFilter(self)
        row.addWidget(self.prompt_label)
        row.addWidget(self.cmd_input, 1)
        v.addWidget(self.history_view)
        v.addLayout(row)
        self.cmd_dock = QtWidgets.QDockWidget("Intérprete de comandos", self)
        self.cmd_dock.setObjectName("dock_cmd")
        self.cmd_dock.setWidget(w)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.cmd_dock)

        # consola Python
        pw = QtWidgets.QWidget()
        pv = QtWidgets.QVBoxLayout(pw)
        pv.setContentsMargins(4, 2, 4, 4)
        self.py_out = QtWidgets.QPlainTextEdit()
        self.py_out.setReadOnly(True)
        self.py_out.setStyleSheet(
            "background:#0b0b0d;color:#b39ddb;font-family:Menlo,Monaco,monospace;font-size:12px;")
        self.py_input = QtWidgets.QLineEdit()
        self.py_input.setPlaceholderText(
            ">>> add(Circle((0,0), 10))   ·   for i in range(5): add(Line((0,i),(10,i)))")
        self.py_input.setStyleSheet("font-family:Menlo,Monaco,monospace;")
        self.py_input.returnPressed.connect(self._on_python)
        pv.addWidget(self.py_out)
        pv.addWidget(self.py_input)
        self.py_dock = QtWidgets.QDockWidget("Consola Python (automatización)", self)
        self.py_dock.setObjectName("dock_py")
        self.py_dock.setWidget(pw)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.py_dock)
        self.py_dock.setVisible(False)

    def _act(self, menu, text, slot, shortcut=None):
        a = QtGui.QAction(text, self)
        if shortcut:
            a.setShortcut(shortcut)
        a.triggered.connect(slot)
        menu.addAction(a)
        return a

    def _alias_action(self, menu, text, alias, shortcut=None):
        return self._act(menu, text, lambda _=False, al=alias: self.execute(al, True), shortcut)

    def _build_menu(self):
        mb = self.menuBar()
        m = mb.addMenu("&Archivo")
        self._alias_action(m, "Nuevo", "NEW", "Ctrl+N")
        self._alias_action(m, "Abrir…", "OPEN", "Ctrl+O")
        self._alias_action(m, "Guardar", "SAVE", "Ctrl+S")
        self._alias_action(m, "Guardar como…", "SAVEAS", "Ctrl+Shift+S")
        m.addSeparator()
        self._alias_action(m, "Importar DXF/DWG…", "DXFIN", "Ctrl+I")
        self._alias_action(m, "Exportar DXF…", "DXFOUT")
        self._alias_action(m, "Exportar DWG…", "DWGOUT")
        self._alias_action(m, "Exportar SVG…", "SVG")
        m.addSeparator()
        self._alias_action(m, "Imprimir / Trazar a PDF…", "PLOT", "Ctrl+P")
        m.addSeparator()
        self.recent_menu = m.addMenu("Archivos recientes")
        self.recent_menu.aboutToShow.connect(self._fill_recent)
        m.addSeparator()
        self._alias_action(m, "Ejecutar script (.scr)…", "SCR")
        self._act(m, "Grabar/detener script", self.toggle_recording)
        m.addSeparator()
        self._act(m, "Salir", self.close, "Ctrl+Q")

        m = mb.addMenu("&Edición")
        self._alias_action(m, "Deshacer", "U", "Ctrl+Z")
        self._alias_action(m, "Rehacer", "RE", "Ctrl+Y")
        m.addSeparator()
        self._alias_action(m, "Seleccionar todo", "SA", "Ctrl+A")
        self._alias_action(m, "Borrar", "E")
        self._alias_action(m, "Propiedades", "PR")

        m = mb.addMenu("&Dibujar")
        for label, al in [("Línea", "L"), ("Polilínea", "PL"), ("Rectángulo", "REC"),
                          ("Polígono", "POL"), ("Círculo", "C"), ("Arco", "A"),
                          ("Elipse", "EL"), ("Spline", "SPL"), ("Punto", "PO"),
                          ("Texto", "T"), ("Directriz", "LE"), ("Achurado", "H")]:
            self._alias_action(m, label, al)

        m = mb.addMenu("&Modificar")
        for label, al in [("Mover", "M"), ("Copiar", "CO"), ("Rotar", "RO"),
                          ("Escalar", "SC"), ("Simetría", "MI"), ("Desfase", "O"),
                          ("Matriz", "AR"), ("Recortar", "TR"), ("Alargar", "EX"),
                          ("Empalme", "F"), ("Chaflán", "CHA"), ("Partir", "BR"),
                          ("Unir", "J"), ("Descomponer", "X"), ("Dividir", "DIV"),
                          ("Graduar", "ME"), ("Alinear", "AL"), ("Agrupar", "G"),
                          ("Desagrupar", "UG"), ("Bloque", "B"), ("Insertar", "I"),
                          ("Purgar", "PU")]:
            self._alias_action(m, label, al)

        m = mb.addMenu("&Booleanas")
        self._alias_action(m, "Unión (UNI)", "UNI")
        self._alias_action(m, "Diferencia (SU)", "SU")
        self._alias_action(m, "Intersección (IN)", "IN")

        m = mb.addMenu("&Acotar")
        for label, al in [("Cota lineal", "DLI"), ("Cota alineada", "DAL"),
                          ("Radio", "DRA"), ("Diámetro", "DDI"),
                          ("Angular", "DAN")]:
            self._alias_action(m, label, al)

        m = mb.addMenu("&Ver")
        self._alias_action(m, "Zoom extensión", "ZE", "Ctrl+E")
        self._alias_action(m, "Zoom ventana", "ZW")
        self._alias_action(m, "Zoom previo", "ZP")
        self._alias_action(m, "Encuadre", "P")
        m.addSeparator()
        self._alias_action(m, "Rejilla ON/OFF", "GRID", "F7")
        self._alias_action(m, "Snap ON/OFF", "S", "F9")
        self._alias_action(m, "Orto ON/OFF", "ORTHO", "F8")
        self._alias_action(m, "Polar ON/OFF", "POLAR", "F10")
        self._alias_action(m, "Referencia a objetos ON/OFF", "OS", "F3")
        self._alias_action(m, "Mostrar grosores de línea ON/OFF", "LWT")
        self._alias_action(m, "Entrada dinámica ON/OFF", "DYN", "F12")
        self._alias_action(m, "Tamaño de rejilla…", "SN")
        m.addSeparator()
        m.addAction(self.layer_dock.toggleViewAction())
        m.addAction(self.props_dock.toggleViewAction())
        m.addAction(self.cmd_dock.toggleViewAction())
        m.addAction(self.py_dock.toggleViewAction())

        m = mb.addMenu("&Formato")
        self._alias_action(m, "Administrador de capas", "LA")
        self._alias_action(m, "Capa actual por nombre…", "CLAYER")
        m.addSeparator()
        self._alias_action(m, "Color actual / de la selección…", "COLOR")
        self._alias_action(m, "Tipo de línea…", "LT")
        self._alias_action(m, "Grosor de línea…", "LW")
        self._alias_action(m, "Igualar propiedades", "MA")
        m.addSeparator()
        self._alias_action(m, "Unidades…", "UN")

        m = mb.addMenu("&Capas")
        for label, al in [("Hacer actual la capa del objeto", "LAYMCUR"),
                          ("Cambiar selección a la capa actual", "LAYCUR"),
                          ("Aislar capas de la selección", "LAYISO"),
                          ("Desaislar", "LAYUNISO"),
                          ("Apagar capa del objeto", "LAYOFF"),
                          ("Encender todas las capas", "LAYON"),
                          ("Bloquear capa del objeto", "LAYLCK"),
                          ("Desbloquear capa del objeto", "LAYULK"),
                          ("Mover selección a capa…", "LAYMOVE")]:
            self._alias_action(m, label, al)

        m = mb.addMenu("&Herramientas")
        for label, al in [("Distancia", "DI"), ("Área", "AA"), ("Listar", "LI"),
                          ("Calculadora", "QC"), ("Coordenadas", "ID"),
                          ("Unidades", "UN"), ("Capas", "LA"),
                          ("Consola Python", "PY"), ("Estado", "OP")]:
            self._alias_action(m, label, al)

        m = mb.addMenu("A&yuda")
        self._alias_action(m, "Diccionario de comandos", "?", "F1")
        self._act(m, "Acerca de", self.show_about)

    def _build_toolbar(self):
        tb = self.addToolBar("Dibujo")
        tb.setObjectName("tb_dibujo")
        tb.setMovable(False)
        groups = [
            [("Línea", "L"), ("Polilínea", "PL"), ("Rect", "REC"), ("Círculo", "C"),
             ("Arco", "A"), ("Elipse", "EL"), ("Texto", "T"), ("Achurado", "H")],
            [("Mover", "M"), ("Copiar", "CO"), ("Rotar", "RO"), ("Escala", "SC"),
             ("Simetría", "MI"), ("Offset", "O"), ("Matriz", "AR")],
            [("Recortar", "TR"), ("Alargar", "EX"), ("Empalme", "F"),
             ("Chaflán", "CHA"), ("Unir", "J"), ("Explotar", "X")],
            [("Unión", "UNI"), ("Diferencia", "SU"), ("Intersección", "IN")],
            [("Cota", "DLI"), ("Radio", "DRA")],
            [("Zoom Ext", "ZE"), ("Deshacer", "U"), ("Rehacer", "RE")],
            [("Imprimir PDF", "PLOT")],
        ]
        for i, grp in enumerate(groups):
            if i:
                tb.addSeparator()
            for label, al in grp:
                a = QtGui.QAction(label, self)
                a.setToolTip(f"{label}  ({al})")
                a.triggered.connect(lambda _=False, x=al: self.execute(x, True))
                tb.addAction(a)
        self.addToolBarBreak()
        self.prop_bar = PropertyBar(self)
        self.addToolBar(self.prop_bar)

    def _build_status(self):
        sb = self.statusBar()
        self.coord_label = QtWidgets.QLabel("X 0.000   Y 0.000")
        self.coord_label.setStyleSheet("font-family:Menlo,Monaco,monospace;")
        sb.addWidget(self.coord_label)
        self.zoom_label = QtWidgets.QLabel("")
        sb.addWidget(self.zoom_label)
        self.toggle_btns = {}
        tips = {"SNAP": "Forzar cursor a la rejilla (F9)", "REJILLA": "Rejilla (F7)",
                "ORTO": "Orto (F8)", "POLAR": "Rastreo polar (F10)",
                "REFENT": "Referencia a objetos (F3)",
                "DIN": "Entrada dinámica: distancia/ángulo con Tab (F12)",
                "GROSOR": "Mostrar grosores de línea (LWT)"}
        for key, alias in [("SNAP", "S"), ("REJILLA", "GRID"), ("ORTO", "ORTHO"),
                           ("POLAR", "POLAR"), ("REFENT", "OS"), ("DIN", "DYN"),
                           ("GROSOR", "LWT")]:
            b = QtWidgets.QToolButton()
            b.setText(key)
            b.setCheckable(True)
            b.setToolTip(tips.get(key, key))
            b.clicked.connect(lambda _=False, x=alias: self.execute(x, True))
            sb.addPermanentWidget(b)
            self.toggle_btns[key] = b
        self.layer_label = QtWidgets.QLabel("")
        sb.addPermanentWidget(self.layer_label)
        self.refresh_status()

    # ------------------------------------------------------- utilidades --
    def log(self, msg: str, level: str = "info"):
        pre = {"info": "", "warn": "⚠ ", "error": "✖ ", "cmd": "» "}.get(level, "")
        self.history_view.appendPlainText(pre + str(msg))
        self.history_view.verticalScrollBar().setValue(
            self.history_view.verticalScrollBar().maximum())

    def update_title(self):
        name = os.path.basename(self.doc.filename) if self.doc.filename else "sin título"
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION} — {name}"
                            f"{'*' if self.doc.modified else ''}")

    def refresh_status(self):
        v = self.view
        self.zoom_label.setText(f"   zoom {fmt(v.scale, 3)} px/u   "
                                f"rejilla {fmt(v.grid)}")
        for key, state in [("SNAP", v.snap_on), ("REJILLA", v.show_grid),
                           ("ORTO", v.ortho), ("POLAR", v.polar),
                           ("REFENT", v.osnap_on), ("DIN", self.dyn_on),
                           ("GROSOR", v.show_lwt)]:
            self.toggle_btns[key].setChecked(state)
        d = self.doc
        self.layer_label.setText(
            f"  capa: {d.current_layer} · {lw_label(d.current_lineweight)} · "
            f"[{d.units}]  ")
        self.update_title()

    def refresh_panels(self):
        self.layer_panel.refresh()
        self.props_panel.refresh()
        self.prop_bar.refresh()
        self.refresh_status()

    # ------------------------------------------------- capas y propiedades --
    def after_layers_changed(self, refresh_table: bool = True):
        if refresh_table:
            self.layer_panel.refresh()
        self.props_panel.refresh()
        self.prop_bar.refresh()
        self.refresh_status()
        self.view.update()

    def set_current_layer(self, name: str):
        if name not in self.doc.layers:
            return
        lay = self.doc.layers[name]
        if not lay.visible:
            lay.visible = True
            self.log(f"La capa '{name}' estaba apagada: se encendió al hacerla actual.")
        self.doc.current_layer = name
        self.log(f"Capa actual: {name}")
        self.after_layers_changed()

    def move_selection_to_layer(self, name: str):
        sel = [e for e in self.doc.selection() if self.doc.is_editable(e)]
        if not sel:
            self.log("No hay objetos seleccionados (o están en capas bloqueadas).", "warn")
            return
        if name not in self.doc.layers:
            self.doc.add_layer(name)
        self.doc.push_undo("cambiar capa")
        for e in sel:
            e.layer = name
        self.log(f"{len(sel)} objeto(s) movidos a la capa '{name}'.")
        self.after_layers_changed()

    def rename_layer(self, old: str, new: str):
        doc = self.doc
        if new in doc.layers or old not in doc.layers:
            self.log(f"No se puede renombrar: '{new}' ya existe.", "warn")
            self.layer_panel.refresh()
            return
        doc.push_undo("renombrar capa")
        lay = doc.layers[old]
        lay.name = new
        doc.layers = {(new if k == old else k): v for k, v in doc.layers.items()}
        for e in doc.entities:
            if e.layer == old:
                e.layer = new
        if doc.current_layer == old:
            doc.current_layer = new
        self.after_layers_changed()

    def isolate_layers(self, names: List[str]):
        doc = self.doc
        if self._iso_state is None:
            self._iso_state = {n: l.visible for n, l in doc.layers.items()}
        for n, lay in doc.layers.items():
            lay.visible = n in names
        if doc.current_layer not in names:
            doc.current_layer = names[0]
        self.log(f"Capas aisladas: {', '.join(names)}  (LAYUNISO para restaurar)")
        self.after_layers_changed()

    def unisolate_layers(self):
        if self._iso_state is None:
            self.log("No hay capas aisladas.")
            return
        for n, vis in self._iso_state.items():
            if n in self.doc.layers:
                self.doc.layers[n].visible = vis
        self._iso_state = None
        self.log("Estado de capas restaurado.")
        self.after_layers_changed()

    def apply_general(self, attr: str, value):
        """Color / tipo / grosor: a la selección si la hay, si no al dibujo actual."""
        if value is None and attr != "color":
            return
        sel = [e for e in self.doc.selection() if self.doc.is_editable(e)]
        if sel:
            self.doc.push_undo("propiedades")
            for e in sel:
                setattr(e, attr, value)
            self.log(f"{len(sel)} objeto(s): {attr} = "
                     f"{lw_label(value) if attr == 'lineweight' else (value or 'PorCapa')}")
        else:
            setattr(self.doc, "current_" + attr, value)
            self.log(f"Para objetos nuevos: {attr} = "
                     f"{lw_label(value) if attr == 'lineweight' else (value or 'PorCapa')}")
        self.after_layers_changed(refresh_table=False)

    def view_world_box(self) -> Tuple[float, float, float, float]:
        v = self.view
        a = v.to_world(QPointF(0, 0))
        b = v.to_world(QPointF(v.width(), v.height()))
        return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))

    # ------------------------------------------------- configuración ------ #
    def _load_settings(self):
        st = self.settings
        v = self.view

        def b(key, default):
            val = st.value(key, default)
            return val if isinstance(val, bool) else str(val).lower() in ("1", "true")

        try:
            v.show_grid = b("grid", v.show_grid)
            v.snap_on = b("snap", v.snap_on)
            v.osnap_on = b("osnap", v.osnap_on)
            v.ortho = b("ortho", v.ortho)
            v.polar = b("polar", v.polar)
            v.show_lwt = b("lwt", v.show_lwt)
            self.dyn_on = b("dyn", self.dyn_on)
            v.grid = float(st.value("grid_size", v.grid))
            geo = st.value("geometry")
            if geo is not None:
                self.restoreGeometry(geo)
            else:
                self.resize(1440, 900)
            stt = st.value("state")
            if stt is not None:
                self.restoreState(stt, 50)
            ps = self.plot_settings
            ps.author = str(st.value("plot/author", ps.author))
            ps.company = str(st.value("plot/company", ps.company))
            ps.paper = str(st.value("plot/paper", ps.paper))
            ps.style = str(st.value("plot/style", ps.style))
        except Exception:
            self.resize(1440, 900)

    def _save_settings(self):
        st = self.settings
        v = self.view
        for key, val in [("grid", v.show_grid), ("snap", v.snap_on), ("osnap", v.osnap_on),
                         ("ortho", v.ortho), ("polar", v.polar), ("lwt", v.show_lwt),
                         ("dyn", self.dyn_on), ("grid_size", v.grid)]:
            st.setValue(key, val)
        st.setValue("geometry", self.saveGeometry())
        st.setValue("state", self.saveState(50))
        ps = self.plot_settings
        st.setValue("plot/author", ps.author)
        st.setValue("plot/company", ps.company)
        st.setValue("plot/paper", ps.paper)
        st.setValue("plot/style", ps.style)

    def add_recent(self, path: str):
        path = os.path.abspath(path)
        rec = [p for p in (self.settings.value("recent") or []) if p != path]
        if isinstance(rec, str):
            rec = [rec]
        rec.insert(0, path)
        self.settings.setValue("recent", rec[:12])

    def _fill_recent(self):
        self.recent_menu.clear()
        rec = self.settings.value("recent") or []
        if isinstance(rec, str):
            rec = [rec]
        for p in rec:
            if os.path.exists(p):
                self.recent_menu.addAction(os.path.basename(p) + "   —   " +
                                           os.path.dirname(p),
                                           lambda x=p: self.open_file(x))
        if not self.recent_menu.actions():
            a = self.recent_menu.addAction("(vacío)")
            a.setEnabled(False)

    def open_file(self, path: str):
        if not self._confirm_discard():
            return
        open_path(self, path)

    def dragEnterEvent(self, ev):
        if ev.mimeData().hasUrls():
            ev.acceptProposedAction()

    def dropEvent(self, ev):
        for url in ev.mimeData().urls():
            p = url.toLocalFile()
            if p.lower().endswith((".dxf", ".dwg")):
                self.import_drawing(p)
            elif p.lower().endswith((".vcad", ".json")):
                self.open_file(p)
            break

    def after_state_change(self):
        self.refresh_panels()
        self.view.update()

    def after_selection(self):
        self.props_panel.refresh()
        self.prop_bar.refresh()
        n = len(self.doc.selection())
        if n and self.gen is None:
            self.statusBar().showMessage(f"{n} objeto(s) seleccionados", 2500)

    # ------------------------------------------- entrada dinámica (DIN) -- #
    DYN_FIELDS = {"polar": [("dist", "Distancia"), ("ang", "Ángulo")],
                  "xy": [("x", "X"), ("y", "Y")],
                  "wh": [("w", "Ancho"), ("h", "Alto")],
                  "ang": [("ang", "Ángulo")]}

    def _dyn_fields(self) -> List[Tuple[str, str]]:
        p = self.prompt
        if not (self.dyn_on and self.gen is not None and p is not None and
                p.mode == "point" and p.dyn):
            return []
        if p.dyn in ("polar", "wh", "ang") and p.base is None:
            return []
        return self.DYN_FIELDS.get(p.dyn, [])

    def _dyn_reset(self):
        self.dyn_locks = {}
        self.dyn_idx = 0

    def _dyn_typed(self) -> Optional[float]:
        return eval_number(self.cmd_input.text())

    def _dyn_values(self) -> Dict[str, float]:
        vals = dict(self.dyn_locks)
        fields = self._dyn_fields()
        if fields:
            v = self._dyn_typed()
            if v is not None:
                vals[fields[min(self.dyn_idx, len(fields) - 1)][0]] = v
        return vals

    def _dyn_compute(self, p: Prompt, vals: Dict[str, float], cur: Vec) -> Vec:
        b = p.base
        if p.dyn == "polar" and b is not None:
            d, a = vals.get("dist"), vals.get("ang")
            if a is not None:
                ar = math.radians(a)
                u = (math.cos(ar), math.sin(ar))
                if d is None:
                    d = vdot(vsub(cur, b), u)
            else:
                u = vnorm(vsub(cur, b))
                if vlen(u) < 0.5:
                    u = (1.0, 0.0)
                if d is None:
                    return cur
            return vadd(b, vmul(u, d))
        if p.dyn == "ang" and b is not None:
            a = vals.get("ang")
            if a is None:
                return cur
            L = max(vdist(b, cur), self.view.px(80))
            ar = math.radians(a)
            return vadd(b, (L * math.cos(ar), L * math.sin(ar)))
        if p.dyn == "wh" and b is not None:
            dx, dy = cur[0] - b[0], cur[1] - b[1]
            w, h = vals.get("w"), vals.get("h")
            if w is not None:
                dx = w if w < 0 else math.copysign(w, dx if abs(dx) > 1e-12 else 1.0)
            if h is not None:
                dy = h if h < 0 else math.copysign(h, dy if abs(dy) > 1e-12 else 1.0)
            return (b[0] + dx, b[1] + dy)
        if p.dyn == "xy":
            return (vals.get("x", cur[0]), vals.get("y", cur[1]))
        return cur

    def _dyn_constraint(self, w: Vec) -> Vec:
        if not self._dyn_fields():
            return w
        vals = self._dyn_values()
        return self._dyn_compute(self.prompt, vals, w) if vals else w

    def _dyn_overlay(self) -> List[Tuple[str, str, bool, bool]]:
        fields = self._dyn_fields()
        if not fields:
            return []
        p = self.prompt
        pt = self.view.resolve_point(self.view.mouse_screen)
        b = p.base
        live: Dict[str, float] = {}
        if b is not None:
            live["dist"] = vdist(b, pt)
            live["ang"] = math.degrees(vangle(b, pt)) % 360
            live["w"] = abs(pt[0] - b[0])
            live["h"] = abs(pt[1] - b[1])
        live["x"], live["y"] = pt
        typed = self.cmd_input.text().strip()
        out = []
        for i, (key, label) in enumerate(fields):
            active = i == self.dyn_idx
            locked = key in self.dyn_locks
            if active and typed:
                txt = typed
            elif locked:
                txt = fmt(self.dyn_locks[key], 4)
            else:
                txt = fmt(live.get(key, 0.0), 3)
            if key == "ang" and not (active and typed):
                txt += "°"
            out.append((label, txt, active, locked))
        return out

    def _dyn_tab(self, backwards: bool = False) -> bool:
        fields = self._dyn_fields()
        if not fields:
            return False
        raw = self.cmd_input.text().strip()
        key = fields[self.dyn_idx][0]
        if raw:
            v = eval_number(raw)
            if v is None:
                self.log(f"'{raw}' no es un número válido para {fields[self.dyn_idx][1]}.",
                         "warn")
                return True
            self.dyn_locks[key] = v
            self.cmd_input.clear()
        n = len(fields)
        self.dyn_idx = (self.dyn_idx + (-1 if backwards else 1)) % n
        self.view.refresh_overlay()
        return True

    def _dyn_commit(self, raw: str):
        """Enter con DIN activo. Devuelve el valor a enviar o _INVALID si no aplica."""
        fields = self._dyn_fields()
        if not fields:
            return _INVALID
        v = eval_number(raw) if raw else None
        if raw and v is None:
            return _INVALID                       # coordenadas, @, <, palabras clave…
        vals = dict(self.dyn_locks)
        if v is not None:
            vals[fields[self.dyn_idx][0]] = v
        if not vals:
            return _INVALID
        p = self.prompt
        if p.numeric and p.dyn == "ang" and "ang" in vals:
            return vals["ang"]
        cur = self.view.free_point(self.view.mouse_screen)
        return self._dyn_compute(p, vals, cur)

    @staticmethod
    def _is_measure_prompt(p: Prompt) -> bool:
        low = p.text.lower()
        return p.mode == "number" and any(w in low for w in (
            "distancia", "radio", "altura", "separación", "longitud", "diámetro",
            "desfase", "tamaño", "ancho", "alto", "espaciado", "delta"))

    # ------------------------------------------------- intérprete ------- #
    def execute(self, text: str, from_ui: bool = False):
        """Ejecuta un alias o nombre canónico de comando.

        `from_ui` indica que viene de un menú o botón: si hay otro comando en
        curso se cancela (salvo los transparentes, que no lo interrumpen).
        """
        raw = (text or "").strip()
        if not raw:
            return
        first = raw.lstrip("_").lstrip("'").split()[0]
        canonical = ALIAS_MAP.get(first.upper(), first)
        if canonical not in COMMANDS:
            for k in COMMANDS:
                if k.lower() == first.lower():
                    canonical = k
                    break
        if self.gen is not None:
            if canonical in TRANSPARENT_COMMANDS:
                # se ejecuta sin interrumpir el comando en curso (como 'ZOOM)
                try:
                    COMMANDS[canonical](Ctx(self))
                except Exception as ex:
                    self.log(f"Error en {canonical}: {ex}", "error")
                self.refresh_status()
                self.view.update()
                if self.prompt is not None:
                    self._apply_prompt(self.prompt, keep_dyn=True)
                return
            if canonical in COMMANDS and from_ui:
                self._end_command("Cancelado.")       # elegido en un menú/barra
            else:
                self._feed(raw)
                return
        if canonical not in COMMANDS:
            if first.upper() in LEGACY_ALIASES:
                self.log(f"[{first.upper()}] → '{LEGACY_ALIASES[first.upper()]}' "
                         f"pertenece al entorno 3D y no aplica en 2D.", "warn")
            else:
                self.log(f"Comando desconocido: '{text}'. Escribe ? para la lista.",
                         "warn")
            return
        if self.recording is not None:
            self.recording.append(first.upper())
        self.log(f"{canonical}", "cmd")
        self.history.append(first)
        self.hist_pos = len(self.history)
        self.last_cmd = first
        self.ctx = Ctx(self)
        self.ctx.name = canonical
        try:
            res = COMMANDS[canonical](self.ctx)
        except Cancel:
            self._end_command("Cancelado.")
            return
        except Exception as ex:
            traceback.print_exc()
            self.log(f"Error en {canonical}: {ex}", "error")
            self._end_command()
            return
        if inspect.isgenerator(res):
            self.gen = res
            self._advance(None, first=True)
        else:
            self._end_command()

    def _advance(self, value, first: bool = False):
        while True:
            try:
                p = next(self.gen) if first else self.gen.send(value)
            except StopIteration:
                self._end_command()
                return
            except Cancel:
                self._end_command("Cancelado.")
                return
            except Exception as ex:
                traceback.print_exc()
                self.log(f"Error: {ex}", "error")
                self._end_command()
                return
            first = False
            self.prompt = p
            self._apply_prompt(p)
            if self.script_queue and p.mode != "select":
                token = self.script_queue.pop(0)
                value = self._parse_input(token, p)
                if value is _INVALID:
                    self.log(f"Script: entrada no válida '{token}'.", "warn")
                    self._end_command()
                    return
                continue
            return

    def _apply_prompt(self, p: Prompt, keep_dyn: bool = False):
        if not keep_dyn:
            self._dyn_reset()
            self._num_pick = None
        measure = self._is_measure_prompt(p)
        self.view.pick_mode = (p.mode == "point") or measure
        self.view.select_mode = (p.mode == "select")
        self.view.base_point = p.base if p.mode == "point" else self._num_pick
        self.view.preview_fn = p.preview
        self.view.constraint_fn = self._dyn_constraint
        self.view.dyn_overlay_fn = self._dyn_overlay
        txt = p.text
        if measure:
            txt += (" (o designa el segundo punto)" if self._num_pick
                    else " (o mide con dos clics)")
        if p.default is not None and "<" not in txt:
            txt += f" <{p.default}>"
        self.prompt_label.setText(txt + ":")
        if p.mode == "point":
            ph = ("escribe la distancia y Tab para fijarla · clic · x,y · @dx,dy · @d<áng"
                  if self._dyn_fields() else "clic en el lienzo · x,y · @dx,dy · @d<áng")
        elif p.mode == "select":
            ph = "selecciona objetos y pulsa Enter"
        elif p.mode == "number":
            ph = "número o expresión (p. ej. 1200/2)"
        else:
            ph = ""
        self.cmd_input.setPlaceholderText(ph)
        self.cmd_input.setFocus()
        self.view.update()

    def _end_command(self, msg: Optional[str] = None):
        if self.gen is not None:
            try:
                self.gen.close()
            except Exception:
                pass
        self.gen = None
        self.ctx = None
        self.prompt = None
        self.view.pick_mode = False
        self.view.select_mode = False
        self.view.base_point = None
        self.view.preview_fn = None
        self.view.constraint_fn = None
        self._dyn_reset()
        self._num_pick = None
        self.prompt_label.setText("Comando:")
        self.cmd_input.setPlaceholderText("alias + Enter  (?, L, C, REC, M, TR, UNI…)")
        if msg:
            self.log(msg)
        self.after_state_change()
        self._pump_script()

    def cancel_command(self):
        if self.gen is not None:
            self._end_command("Cancelado.")
        else:
            self.doc.clear_selection()
            self.after_selection()
            self.view.update()

    def _pump_script(self):
        guard = 0
        while self.script_queue and self.gen is None and guard < 5000:
            guard += 1
            line = self.script_queue.pop(0).strip()
            if not line or line.startswith(";") or line.startswith("#"):
                continue
            self.execute(line)

    # --- entrada de usuario ---------------------------------------------- #
    def _on_input(self):
        txt = self.cmd_input.text()
        self.cmd_input.clear()
        raw = txt.strip()
        if self.gen is None:
            if not raw:
                if self.last_cmd:
                    self.execute(self.last_cmd)
                return
            self.execute(raw)
            return
        self._feed(raw)

    def _feed(self, raw: str):
        p = self.prompt
        if p is None:
            return
        if self.recording is not None:
            self.recording.append(raw)
        if p.mode == "select":
            if raw.upper() in ("T", "TODO", "ALL"):
                self.doc.select_all()
                self.view.update()
                return
            self._advance([e for e in self.doc.selection()
                           if self.doc.is_editable(e)])
            return
        if p.mode == "point" and not (raw and p.keywords and raw.upper() in p.keywords):
            val = self._dyn_commit(raw)
            if val is not _INVALID:
                if isinstance(val, tuple):
                    self.log(f"  → {fmt(val[0], 4)}, {fmt(val[1], 4)}")
                self._advance(val)
                return
        val = self._parse_input(raw, p)
        if val is _INVALID:
            self.log("Entrada no válida. Formatos: x,y · @dx,dy · @dist<áng · número",
                     "warn")
            return
        self._advance(val)

    def _parse_input(self, raw: str, p: Prompt):
        raw = (raw or "").strip()
        if raw and p.keywords:
            k = raw.upper()
            if k in p.keywords:
                return p.keywords[k]
        if not raw:
            if p.mode in ("number",):
                return p.default
            if p.mode in ("text", "keyword"):
                return p.default if p.default is not None else ""
            return None                      # punto: Enter = terminar
        if p.mode in ("text", "keyword"):
            return raw
        if p.mode in ("number", "angle"):
            v = eval_number(raw.replace(",", ".") if raw.count(",") == 1 and
                            "." not in raw else raw)
            return _INVALID if v is None else v
        # modo punto
        base = p.base if p.base is not None else self.view.base_point
        cur = self.view.free_point(self.view.mouse_screen) if self.view.width() else \
            self.view.mouse_world
        return parse_point(raw, base, cur, p.numeric)

    def _on_point(self, w):
        p = self.prompt
        if self.gen is None or p is None:
            return
        if p.mode == "point":
            self._advance(w)
        elif self._is_measure_prompt(p):
            # distancia por dos puntos (p. ej. desfase, radio de empalme…)
            if self._num_pick is None:
                self._num_pick = w
                self._apply_prompt(p, keep_dyn=True)
                self.view.base_point = w
            else:
                d = vdist(self._num_pick, w)
                self.log(f"  distancia medida = {fmt(d, 4)}")
                self._num_pick = None
                self._advance(d)

    def _on_move(self, w):
        self.coord_label.setText(f"X {w[0]:>10.3f}   Y {w[1]:>10.3f}")

    def eventFilter(self, obj, ev):
        if obj is self.cmd_input and ev.type() == QtCore.QEvent.Type.KeyPress:
            k = ev.key()
            if k == Qt.Key.Key_Escape:
                self.cancel_command()
                return True
            if k in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                if self.gen is None:
                    self._complete_alias()
                else:
                    self._dyn_tab(backwards=(k == Qt.Key.Key_Backtab or bool(
                        ev.modifiers() & Qt.KeyboardModifier.ShiftModifier)))
                return True
            if k == Qt.Key.Key_Space and self.gen is not None and \
                    self.prompt is not None and self.prompt.mode == "point" and \
                    self._dyn_fields() and eval_number(self.cmd_input.text()) is not None:
                self._on_input()                     # Espacio = Enter, como en AutoCAD
                return True
            if k == Qt.Key.Key_Up and self.history:
                self.hist_pos = max(0, self.hist_pos - 1)
                self.cmd_input.setText(self.history[self.hist_pos])
                return True
            if k == Qt.Key.Key_Down and self.history:
                self.hist_pos = min(len(self.history), self.hist_pos + 1)
                self.cmd_input.setText(self.history[self.hist_pos]
                                       if self.hist_pos < len(self.history) else "")
                return True
            if k == Qt.Key.Key_Space and not self.cmd_input.text() and self.gen is None:
                if self.last_cmd:
                    self.execute(self.last_cmd)
                return True
            if k == Qt.Key.Key_Space and self.gen is None and self.cmd_input.text().strip():
                self._on_input()                     # Espacio confirma el alias
                return True
        return super().eventFilter(obj, ev)

    def _complete_alias(self):
        """Tab sin comando activo: autocompleta alias o nombre de comando."""
        t = self.cmd_input.text().strip()
        if not t:
            return
        names = sorted({*ALIAS_MAP, *COMMANDS}, key=len)
        hits = [n for n in names if n.upper().startswith(t.upper())]
        if not hits:
            return
        if len(hits) == 1:
            self.cmd_input.setText(hits[0])
        else:
            self.log("  " + " · ".join(hits[:24]))

    def keyPressEvent(self, ev):
        k = ev.key()
        if k == Qt.Key.Key_Escape:
            self.cancel_command()
        elif k == Qt.Key.Key_Delete and self.gen is None:
            sel = [e for e in self.doc.selection() if self.doc.is_editable(e)]
            if sel:
                self.doc.push_undo("borrar")
                self.doc.remove(sel)
                self.after_state_change()
        elif k == Qt.Key.Key_F3:
            self.execute("OS")
        elif k == Qt.Key.Key_F7:
            self.execute("GRID")
        elif k == Qt.Key.Key_F8:
            self.execute("ORTHO")
        elif k == Qt.Key.Key_F9:
            self.execute("S")
        elif k == Qt.Key.Key_F10:
            self.execute("POLAR")
        else:
            super().keyPressEvent(ev)

    # --- consola Python ---------------------------------------------------- #
    def _py_namespace(self) -> dict:
        ns = {n: ENTITY_TYPES[n] for n in ENTITY_TYPES}
        ns.update({c.__name__: c for c in (Line, Polyline, Circle, Arc, Ellipse,
                                           PointEnt, TextEnt, Leader, Hatch,
                                           Dimension, BlockRef)})
        ns.update(doc=self.doc, view=self.view, win=self, math=math,
                  add=lambda e: self.doc.add(e),
                  remove=lambda es: self.doc.remove(es),
                  redraw=lambda: (self.view.update(), self.refresh_panels()),
                  zoom_extents=lambda: self.view.zoom_extents(),
                  run=lambda s: self.execute(s))
        return ns

    def _on_python(self):
        src = self.py_input.text()
        self.py_input.clear()
        if not src.strip():
            return
        self.py_out.appendPlainText(">>> " + src)
        ns = self._py_namespace()
        self.doc.push_undo("consola Python")
        try:
            try:
                val = eval(src, ns)
                if val is not None:
                    self.py_out.appendPlainText(repr(val))
            except SyntaxError:
                exec(src, ns)
        except Exception as ex:
            self.py_out.appendPlainText(f"{type(ex).__name__}: {ex}")
        self.view.update()
        self.refresh_panels()

    # --- scripts ------------------------------------------------------------ #
    def run_script_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Ejecutar script", "", "Scripts (*.scr *.txt);;Todos (*)")
        if not path:
            return
        self.run_script_text(open(path, encoding="utf-8").read())

    def run_script_text(self, text: str):
        """Ejecuta un script. Una línea vacía equivale a Enter (termina o acepta
        el valor por omisión), como en los .scr de AutoCAD."""
        lines = [l.strip() for l in text.splitlines()]
        while lines and not lines[-1]:
            lines.pop()
        self.script_queue = [l for l in lines if not l.startswith((";", "#"))]
        n = sum(1 for l in self.script_queue if l)
        self.log(f"Ejecutando script con {n} instrucciones…")
        self._pump_script()

    def toggle_recording(self):
        if self.recording is None:
            self.recording = []
            self.log("● Grabando script… (vuelve a activar para guardar)")
            return
        lines = self.recording
        self.recording = None
        if not lines:
            self.log("Grabación vacía.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Guardar script", "macro.scr", "Scripts (*.scr)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            self.log(f"Script guardado ({len(lines)} líneas): {path}")

    # --- archivos ------------------------------------------------------------ #
    def _confirm_discard(self) -> bool:
        if not self.doc.modified:
            return True
        r = QtWidgets.QMessageBox.question(
            self, "Cambios sin guardar", "¿Descartar los cambios actuales?",
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No)
        return r == QtWidgets.QMessageBox.StandardButton.Yes

    def file_new(self):
        if not self._confirm_discard():
            return
        self.set_document(Document())
        self.view.zoom_extents()
        self.log("Documento nuevo.")

    def file_open(self):
        if not self._confirm_discard():
            return
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Abrir dibujo", "",
            "Dibujos (*.vcad *.json *.dxf *.dwg);;VectorCAD (*.vcad *.json);;"
            "DXF (*.dxf);;DWG (*.dwg);;Todos (*)")
        if not path:
            return
        open_path(self, path)

    def load_vcad(self, path: str) -> bool:
        try:
            doc = Document()
            with open(path, encoding="utf-8") as f:
                doc.load_json(f.read())
            doc.filename = path
            self.set_document(doc)
            self.view.zoom_extents()
            self.add_recent(path)
            self.log(f"Abierto: {path} ({len(self.doc.entities)} entidades)")
            return True
        except Exception as ex:
            self.log(f"No se pudo abrir: {ex}", "error")
            return False

    def set_document(self, doc: "Document"):
        if self.gen is not None:
            self._end_command()
        self.doc = doc
        self.view.doc = doc
        self._iso_state = None
        self.after_state_change()

    def file_save(self):
        if not self.doc.filename:
            return self.file_save_as()
        try:
            with open(self.doc.filename, "w", encoding="utf-8") as f:
                f.write(self.doc.to_json())
            self.doc.modified = False
            self.update_title()
            self.add_recent(self.doc.filename)
            self.log(f"Guardado: {self.doc.filename}")
        except Exception as ex:
            self.log(f"No se pudo guardar: {ex}", "error")

    def file_save_as(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Guardar como", "dibujo.vcad", "VectorCAD (*.vcad);;JSON (*.json)")
        if not path:
            return
        self.doc.filename = path
        self.file_save()

    def file_export_dxf(self):
        if not HAS_EZDXF:
            self.log("Instala ezdxf para exportar DXF:  pip install ezdxf", "error")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Exportar DXF", "dibujo.dxf", "DXF (*.dxf)")
        if not path:
            return
        try:
            self.doc.export_dxf(path)
            self.log(f"DXF exportado: {path}")
        except Exception as ex:
            self.log(f"Error al exportar: {ex}", "error")

    def file_export_svg(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Exportar SVG", "dibujo.svg", "SVG (*.svg)")
        if not path:
            return
        try:
            self.doc.export_svg(path)
            self.log(f"SVG exportado: {path}")
        except Exception as ex:
            self.log(f"Error al exportar: {ex}", "error")

    def file_import_dxf(self):
        if not HAS_EZDXF:
            self.log("Instala ezdxf para importar DXF:  pip install ezdxf", "error")
            return
        has_dwg = find_dwg_converter() is not None
        flt = ("Dibujos (*.dxf *.dwg);;DXF (*.dxf);;DWG (*.dwg);;Todos (*)"
               if has_dwg else "DXF (*.dxf);;DWG (*.dwg);;Todos (*)")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar dibujo", "", flt)
        if not path:
            return
        self.import_drawing(path)

    def file_import_dwg(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Importar DWG", "", "DWG (*.dwg);;Todos (*)")
        if not path:
            return
        self.import_drawing(path)

    def import_drawing(self, path: str, new_doc: bool = False):
        """Importa DXF o DWG (el DWG pasa por conversor) sin congelar la interfaz.

        Con `new_doc` el resultado sustituye al documento actual (Abrir).
        """
        is_dwg = path.lower().endswith(".dwg")
        if is_dwg and find_dwg_converter(refresh=True) is None:
            self.log("No hay conversor DWG disponible.", "error")
            for line in dwg_install_hint().splitlines():
                self.log(line)
            return
        if self._import_thread is not None:
            self.log("Ya hay una importación en curso.", "warn")
            return
        name = os.path.basename(path)
        dlg = QtWidgets.QProgressDialog(f"Abriendo {name}…", None, 0, 0, self)
        dlg.setWindowTitle("Importar dibujo")
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setMinimumDuration(300)
        dlg.setCancelButton(None)
        th = ImportWorker(path)
        self._import_thread = th

        def on_progress(msg):
            dlg.setLabelText(f"{name}\n{msg}")
            self.log(msg)

        def on_ok(res):
            dlg.close()
            self._import_thread = None
            if new_doc:
                doc = Document()
                n = doc.merge_import(res)
                doc.modified = False
                doc._undo.clear()
                self.set_document(doc)
                self.add_recent(path)
            else:
                self.doc.push_undo("importar dibujo")
                n = self.doc.merge_import(res)
            self._zoom_import_extents()
            self.after_state_change()
            self.log(f"Importadas {n} entidades y {len(res.layers)} capas desde {name}"
                     + (f" (unidades: {res.units})" if res.units else ""))
            for note in res.notes:
                self.log(note, "warn")
            if res.skipped:
                total = sum(res.skipped.values())
                detalle = ", ".join(f"{k}×{v}" for k, v in
                                    sorted(res.skipped.items(), key=lambda kv: -kv[1])[:6])
                self.log(f"{total} entidades no traducibles omitidas: {detalle}", "warn")

        def on_fail(msg):
            dlg.close()
            self._import_thread = None
            for line in msg.splitlines():
                self.log(line, "error")
            QtWidgets.QMessageBox.warning(self, "No se pudo importar", msg[:900])

        th.progress.connect(on_progress)
        th.finished_ok.connect(on_ok)
        th.failed.connect(on_fail)
        th.start()

    def _zoom_import_extents(self):
        """Encuadra el dibujo importado ignorando entidades muy dispersas.

        Los archivos convertidos traen a veces inserciones degeneradas cuyas
        coordenadas son órdenes de magnitud mayores que el resto; encuadrar
        sobre ellas dejaría el dibujo real reducido a un punto.
        """
        ents = [e for e in self.doc.entities if e.bbox()]
        if len(ents) < 8:
            self.view.zoom_extents()
            return
        boxes = [e.bbox() for e in ents]
        cx = sorted((b[0] + b[2]) / 2 for b in boxes)
        cy = sorted((b[1] + b[3]) / 2 for b in boxes)
        mx, my = cx[len(cx) // 2], cy[len(cy) // 2]
        dist = sorted(max(abs((b[0] + b[2]) / 2 - mx), abs((b[1] + b[3]) / 2 - my))
                      for b in boxes)
        cut = dist[int(len(dist) * 0.98)] * 4 + 1e-9
        keep = [b for b in boxes
                if max(abs((b[0] + b[2]) / 2 - mx), abs((b[1] + b[3]) / 2 - my)) <= cut]
        if len(keep) == len(boxes) or not keep:
            self.view.zoom_extents()
            return
        bb = (min(b[0] for b in keep), min(b[1] for b in keep),
              max(b[2] for b in keep), max(b[3] for b in keep))
        self.view.zoom_box(bb[0], bb[1], bb[2], bb[3])
        self.log(f"{len(boxes) - len(keep)} entidades con coordenadas atípicas "
                 f"quedan fuera del encuadre inicial (usa Z para verlo todo).", "warn")

    def file_export_dwg(self):
        if find_dwg_converter() is None:
            self.log("No hay conversor DWG instalado.", "error")
            for line in dwg_install_hint().splitlines():
                self.log(line)
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Exportar DWG", "dibujo.dwg", "DWG (*.dwg)")
        if not path:
            return
        if not path.lower().endswith(".dwg"):
            path += ".dwg"
        try:
            QtWidgets.QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                self.doc.export_dwg(path)
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()
            self.log(f"DWG exportado: {path}  ({dwg_converter_name()})")
        except Exception as ex:
            for line in str(ex).splitlines():
                self.log(line, "error")

    # --- diálogos ------------------------------------------------------------ #
    def show_layer_dialog(self):
        self.layer_dock.setVisible(True)
        self.layer_dock.raise_()
        self.layer_panel.refresh()

    def show_help(self):
        rows = []
        inv: Dict[str, List[str]] = {}
        for al, canon in ALIAS_MAP.items():
            inv.setdefault(canon, []).append(al)
        for canon in sorted(inv):
            if canon in COMMANDS:
                rows.append((", ".join(sorted(inv[canon], key=len)), canon))
        html = ["<h3>Diccionario de comandos</h3>",
                "<table cellpadding=4><tr><th align=left>Alias</th>"
                "<th align=left>Comando</th></tr>"]
        for al, canon in rows:
            html.append(f"<tr><td><b>{al}</b></td><td>{canon}</td></tr>")
        html.append("</table>")
        html.append("<p><b>Entrada de puntos:</b> <code>x,y</code> absoluto · "
                    "<code>@dx,dy</code> relativo · <code>@dist&lt;áng</code> polar · "
                    "un número solo = distancia directa en la dirección del cursor.</p>")
        html.append("<p><b>Entrada dinámica (DIN, F12):</b> durante un comando escribe "
                    "la distancia y pulsa <b>Tab</b> para fijarla y pasar al ángulo "
                    "(o X→Y, Ancho→Alto en rectángulos); <b>Enter</b> o <b>Espacio</b> "
                    "acepta. Con un valor fijado, el cursor sólo elige la dirección. "
                    "Los campos aceptan expresiones: <code>1200/2</code>. "
                    "Las distancias numéricas (desfase, radio…) también se pueden "
                    "medir con dos clics.</p>")
        html.append("<p><b>Imprimir:</b> Ctrl+P o PLOT — PDF/SVG vectorial o PNG, papel "
                    "ISO/ANSI, escala 1:N, plumillas monocromo/gris/color, grosores, "
                    "cajetín y escala gráfica.</p>")
        html.append("<p><b>Teclas:</b> F3 refent · F7 rejilla · F8 orto · F9 snap · "
                    "F10 polar · F12 entrada dinámica · Esc cancelar · Supr borrar · "
                    "Enter repetir · Tab autocompleta alias.</p>")
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Ayuda de VectorCAD")
        dlg.resize(560, 640)
        br = QtWidgets.QTextBrowser()
        br.setHtml("".join(html))
        lay = QtWidgets.QVBoxLayout(dlg)
        lay.addWidget(br)
        dlg.exec()

    def show_about(self):
        QtWidgets.QMessageBox.about(
            self, f"Acerca de {APP_NAME}",
            f"<b>{APP_NAME} {APP_VERSION}</b><br>"
            "Sistema de dibujo 2D vectorial paramétrico en Python desarrollado por el Centro Producción del Espacio UDLA 2026.<br><br>"
            f"Lectura DWG: {dwg_converter_name()}<br>"
            f"Qt: {QT_LIB} · Shapely: {'sí' if HAS_SHAPELY else 'no'} · "
            f"ezdxf: {'sí' if HAS_EZDXF else 'no'}")

    def closeEvent(self, ev):
        if self._confirm_discard():
            self._save_settings()
            ev.accept()
        else:
            ev.ignore()


# --------------------------------------------------------------------------- #
#  Analizador de entrada de puntos
# --------------------------------------------------------------------------- #
_NUM_EXPR = re.compile(r"^[\d\s.+\-*/()]+$")


def eval_number(raw: str) -> Optional[float]:
    """Número o expresión aritmética simple ('1200/2', '3*0.15+2'). None si no lo es.

    La coma NO se acepta como decimal: en la línea de comandos separa X e Y.
    """
    s = (raw or "").strip().rstrip("°").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        pass
    if len(s) > 60 or "**" in s or not _NUM_EXPR.match(s):
        return None
    try:
        v = eval(s, {"__builtins__": {}}, {})
    except Exception:
        return None
    return float(v) if isinstance(v, (int, float)) and math.isfinite(v) else None


def app_icon() -> Optional["QtGui.QIcon"]:
    """Icono de la aplicación (instalado junto al programa)."""
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(SUPPORT_DIR, "VectorCAD.png"),
                 os.path.join(here, "VectorCAD.png"),
                 os.path.join(SUPPORT_DIR, "VectorCAD.icns"),
                 os.path.join(here, "VectorCAD.icns")):
        if os.path.isfile(cand):
            return QtGui.QIcon(cand)
    return None


class ImportWorker(QtCore.QThread):
    """Lee DXF/DWG en segundo plano para no congelar la interfaz."""

    progress = Signal(str)
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def run(self):
        try:
            res = read_drawing(self.path, self.progress.emit)
            self.finished_ok.emit(res)
        except Exception as ex:
            traceback.print_exc()
            self.failed.emit(str(ex))


def parse_point(raw: str, base: Optional[Vec], cursor: Vec, numeric: bool = False):
    """x,y | @dx,dy | dist<ang | @dist<ang | número (distancia directa)."""
    s = raw.replace(" ", "")
    rel = s.startswith("@")
    if rel:
        s = s[1:]
    b = base if base is not None else (0.0, 0.0)
    try:
        if "<" in s:
            ds, angs = s.split("<", 1)
            d = float(ds.replace(",", "."))
            a = math.radians(float(angs.replace(",", ".")))
            p = (d * math.cos(a), d * math.sin(a))
            return vadd(b, p) if rel else p
        if "," in s or ";" in s:
            parts = re.split(r"[;,]", s)
            if len(parts) != 2:
                return _INVALID
            x, y = float(parts[0]), float(parts[1])
            return vadd(b, (x, y)) if rel else (x, y)
        val = float(s)
        if numeric:
            return val
        if base is None:
            return _INVALID
        u = vnorm(vsub(cursor, b))
        if vlen(u) < 0.5:
            u = (1.0, 0.0)
        return vadd(b, vmul(u, val))
    except ValueError:
        return _INVALID


# =========================================================================== #
#  13. ARRANQUE
# =========================================================================== #
def apply_dark_palette(app: "QtWidgets.QApplication"):
    app.setStyle("Fusion")
    p = QtGui.QPalette()
    C = QtGui.QColor
    p.setColor(QtGui.QPalette.ColorRole.Window, C(THEME["panel"]))
    p.setColor(QtGui.QPalette.ColorRole.WindowText, C(THEME["text"]))
    p.setColor(QtGui.QPalette.ColorRole.Base, C(THEME["panel_alt"]))
    p.setColor(QtGui.QPalette.ColorRole.AlternateBase, C(THEME["panel"]))
    p.setColor(QtGui.QPalette.ColorRole.Text, C(THEME["text"]))
    p.setColor(QtGui.QPalette.ColorRole.Button, C(THEME["panel_alt"]))
    p.setColor(QtGui.QPalette.ColorRole.ButtonText, C(THEME["text"]))
    p.setColor(QtGui.QPalette.ColorRole.Highlight, C("#3d5afe"))
    p.setColor(QtGui.QPalette.ColorRole.HighlightedText, C("#ffffff"))
    p.setColor(QtGui.QPalette.ColorRole.ToolTipBase, C(THEME["panel_alt"]))
    p.setColor(QtGui.QPalette.ColorRole.ToolTipText, C(THEME["text"]))
    app.setPalette(p)


def open_path(win, path: str) -> bool:
    """Abre un .vcad/.json o un .dxf/.dwg (como documento nuevo) en la ventana."""
    if not path or not os.path.exists(path):
        return False
    if path.lower().endswith((".dxf", ".dwg")):
        win.import_drawing(path, new_doc=True)
        return True
    return win.load_vcad(path)


class VectorCADApp(QtWidgets.QApplication):
    """QApplication que atiende QFileOpenEvent.

    En macOS el sistema no pasa la ruta por argv cuando se hace doble clic en un
    documento o se arrastra sobre el icono del .app: envía un FileOpen event.
    """

    def __init__(self, argv):
        super().__init__(argv)
        self.window = None
        self._pending: List[str] = []

    def attach(self, win) -> None:
        self.window = win
        for p in self._pending:
            open_path(win, p)
        self._pending = []

    def event(self, ev):  # noqa: D102
        if ev.type() == QtCore.QEvent.Type.FileOpen:
            path = ev.file()
            if self.window is not None:
                open_path(self.window, path)
            else:
                self._pending.append(path)
            return True
        return super().event(ev)


def main(argv: Optional[List[str]] = None):
    argv = list(argv if argv is not None else sys.argv)
    app = VectorCADApp(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName("CEPRODEP")
    apply_dark_palette(app)
    icon = app_icon()
    if icon is not None:
        app.setWindowIcon(icon)
    win = MainWindow()
    win.show()
    win.view.zoom_extents()
    app.attach(win)
    for arg in argv[1:]:
        if not arg.startswith("-") and os.path.exists(arg):
            open_path(win, arg)
            break
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
