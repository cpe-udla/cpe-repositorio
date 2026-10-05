#!/bin/bash
# ---------------------------------------------------------------------------
#  VectorCAD — compilar una app autónoma para macOS (PyInstaller)
#
#  Produce dist/VectorCAD.app (no necesita Python en el Mac de destino) y,
#  opcionalmente, un DMG para distribuirla.
#
#  Uso:   bash build_macos.sh [--dmg] [--universal]
#
#  Nota: la app se compila para la arquitectura de esta máquina (arm64 en
#  Apple Silicon). --universal exige un Python universal2 (el de python.org).
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DMG=0
UNIVERSAL=0
for arg in "$@"; do
    case "$arg" in
        --dmg) DMG=1 ;;
        --universal) UNIVERSAL=1 ;;
        *) echo "Opción desconocida: $arg"; exit 1 ;;
    esac
done

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m!! \033[0m %s\n' "$*" >&2; exit 1; }

[[ "$(uname -s)" == "Darwin" ]] || die "PyInstaller no compila para macOS desde otro sistema: ejecútalo en el Mac."
[[ -f vectorcad.py ]] || die "Falta vectorcad.py en este directorio."

PY=""
for c in python3.12 python3.11 python3.13 python3; do
    p="$(command -v "$c" 2>/dev/null || true)"
    [[ -n "$p" ]] && PY="$p" && break
done
[[ -n "$PY" ]] || die "No encuentro Python 3."

VENV=".build-venv"
if [[ ! -x "$VENV/bin/python" ]]; then
    say "Creando entorno de compilación…"
    "$PY" -m venv "$VENV"
fi
say "Instalando PyInstaller y dependencias…"
"$VENV/bin/python" -m pip install --upgrade pip wheel >/dev/null
"$VENV/bin/python" -m pip install --upgrade pyinstaller "PySide6>=6.5" ezdxf shapely

say "Generando icono…"
"$VENV/bin/python" make_icon.py . || true

if [[ $UNIVERSAL -eq 1 ]]; then
    say "Modo universal2 (requiere un Python universal2 y wheels universales)"
    sed -i '' 's/target_arch=None/target_arch="universal2"/' VectorCAD.spec
fi

say "Compilando…"
rm -rf build dist
"$VENV/bin/pyinstaller" --noconfirm --clean VectorCAD.spec

[[ -d dist/VectorCAD.app ]] || die "La compilación no produjo dist/VectorCAD.app"

say "Firmando (ad-hoc) y limpiando cuarentena…"
codesign --force --deep --sign - dist/VectorCAD.app || true
xattr -cr dist/VectorCAD.app || true

SIZE=$(du -sh dist/VectorCAD.app | cut -f1)
say "Listo: dist/VectorCAD.app ($SIZE)"

if [[ $DMG -eq 1 ]]; then
    say "Creando DMG…"
    rm -f dist/VectorCAD-5.0.dmg
    STAGE=$(mktemp -d)
    cp -R dist/VectorCAD.app "$STAGE/"
    ln -s /Applications "$STAGE/Applications"
    hdiutil create -volname "VectorCAD 5.0" -srcfolder "$STAGE" \
        -ov -format UDZO dist/VectorCAD-5.0.dmg >/dev/null
    rm -rf "$STAGE"
    say "Listo: dist/VectorCAD-5.0.dmg"
fi

echo
echo "Instalar:  cp -R dist/VectorCAD.app /Applications/"
echo "Probar:    open dist/VectorCAD.app"
echo "Si macOS dice que la app está dañada (viene sin notarizar):"
echo "    xattr -dr com.apple.quarantine /Applications/VectorCAD.app"
