#!/bin/bash
# ---------------------------------------------------------------------------
#  VectorCAD 5.0 — instalador para macOS
#
#  Crea un entorno virtual aislado, instala las dependencias, compila el
#  lector DWG (LibreDWG) desde el código fuente oficial de GNU si no hay otro
#  conversor, genera el icono y deja VectorCAD.app en ~/Applications más un
#  comando `vectorcad` en la terminal.
#
#  Uso:  doble clic sobre este archivo, o bien
#        bash install_macos.command [--no-dwg]
#
#  Desinstalar:  bash install_macos.command --uninstall
# ---------------------------------------------------------------------------
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUPPORT="$HOME/Library/Application Support/VectorCAD"
VENV="$SUPPORT/venv"
APPS="$HOME/Applications"
BUNDLE="$APPS/VectorCAD.app"
BIN="$HOME/.local/bin"
BUNDLE_ID="cl.ceprodep.vectorcad"
VERSION="5.0"
LIBREDWG_VERSION="0.13.4"
WANT_DWG=1
[[ " $* " == *" --no-dwg "* ]] && WANT_DWG=0

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!! \033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m!! \033[0m %s\n' "$*" >&2; exit 1; }

# Ejecuta un comando con límite de tiempo (macOS no trae `timeout`).
with_timeout() { local t="$1"; shift; perl -e 'alarm shift; exec @ARGV' "$t" "$@"; }

# --------------------------------------------------------------------------- #
#  Desinstalación
# --------------------------------------------------------------------------- #
if [[ "${1:-}" == "--uninstall" ]]; then
    say "Eliminando VectorCAD…"
    rm -rf "$BUNDLE" "$SUPPORT" "$BIN/vectorcad"
    say "Listo. Se eliminaron la app, el entorno, el lector DWG y el comando."
    exit 0
fi

[[ "$(uname -s)" == "Darwin" ]] || die "Este instalador es para macOS. En Linux/Windows: pip install PySide6 ezdxf shapely && python vectorcad.py"
[[ -f "$SRC_DIR/vectorcad.py" ]] || die "No encuentro vectorcad.py junto a este instalador."

# --------------------------------------------------------------------------- #
#  1. Intérprete de Python
# --------------------------------------------------------------------------- #
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3; do
    p="$(command -v "$c" 2>/dev/null || true)"
    [[ -z "$p" ]] && continue
    if "$p" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 9) else 1)' 2>/dev/null; then
        PY="$p"; break
    fi
done
[[ -n "$PY" ]] || die "Necesitas Python 3.9 o superior. Instálalo con:  brew install python@3.12   (o desde python.org)"
say "Python: $PY  ($("$PY" -V 2>&1))"

# --------------------------------------------------------------------------- #
#  2. Entorno virtual y dependencias
# --------------------------------------------------------------------------- #
mkdir -p "$SUPPORT"
if [[ ! -x "$VENV/bin/python" ]]; then
    say "Creando entorno virtual en $VENV"
    "$PY" -m venv "$VENV"
fi
say "Instalando dependencias (PySide6, ezdxf, shapely)…"
"$VENV/bin/python" -m pip install --upgrade pip wheel >/dev/null
"$VENV/bin/python" -m pip install --upgrade "PySide6>=6.5" ezdxf shapely

# --------------------------------------------------------------------------- #
#  3. Copiar la aplicación (con `cat`, que obliga a iCloud a descargar)
# --------------------------------------------------------------------------- #
say "Copiando archivos…"
for f in vectorcad.py make_icon.py ejemplo.scr; do
    if [[ -f "$SRC_DIR/$f" ]]; then
        cat "$SRC_DIR/$f" > "$SUPPORT/$f.tmp" && mv "$SUPPORT/$f.tmp" "$SUPPORT/$f"
    fi
done

ICNS=""
if [[ -f "$SUPPORT/make_icon.py" ]]; then
    say "Generando icono…"
    if with_timeout 90 env QT_QPA_PLATFORM=offscreen "$VENV/bin/python" \
            "$SUPPORT/make_icon.py" "$SUPPORT" >/dev/null 2>&1 \
       && [[ -f "$SUPPORT/VectorCAD.icns" ]]; then
        ICNS="$SUPPORT/VectorCAD.icns"
    elif [[ -f "$SRC_DIR/VectorCAD.icns" ]]; then
        cp "$SRC_DIR/VectorCAD.icns" "$SUPPORT/VectorCAD.icns"
        ICNS="$SUPPORT/VectorCAD.icns"
    else
        warn "No se pudo generar el icono; se usará el genérico."
    fi
fi

# --------------------------------------------------------------------------- #
#  4. Lector DWG
#     Preferencia: ODA File Converter > LibreDWG integrado > LibreDWG del sistema.
#     Si no hay ninguno, se compila LibreDWG desde ftp.gnu.org (sin Homebrew).
# --------------------------------------------------------------------------- #
DWG_DIR="$SUPPORT/libredwg/bin"
have_dwg() {
    [[ -x /Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter ]] && return 0
    [[ -x "$DWG_DIR/dwg2dxf" ]] && return 0
    command -v dwg2dxf >/dev/null 2>&1 && return 0
    [[ -x /opt/homebrew/bin/dwg2dxf || -x /usr/local/bin/dwg2dxf ]] && return 0
    return 1
}

build_libredwg() {
    if ! xcode-select -p >/dev/null 2>&1 || ! command -v cc >/dev/null 2>&1; then
        warn "Falta el compilador. Instálalo con:  xcode-select --install   y vuelve a ejecutar."
        return 1
    fi
    local work
    work="$(mktemp -d /tmp/vcad_libredwg.XXXXXX)"   # ruta sin espacios (libtool)
    say "Descargando LibreDWG $LIBREDWG_VERSION (GNU)…"
    curl -fsSL "https://ftp.gnu.org/gnu/libredwg/libredwg-$LIBREDWG_VERSION.tar.gz" \
        -o "$work/libredwg.tar.gz" || { warn "No se pudo descargar LibreDWG."; return 1; }
    tar -xzf "$work/libredwg.tar.gz" -C "$work"
    # configure exige pkg-config aunque no use paquetes opcionales: sustituto mínimo.
    mkdir -p "$work/shim"
    cat > "$work/shim/pkg-config" <<'SHIM'
#!/bin/sh
case "$1" in --version) echo 0.29.2; exit 0;; --atleast-pkgconfig-version) exit 0;; esac
exit 1
SHIM
    chmod +x "$work/shim/pkg-config"
    say "Compilando LibreDWG (puede tardar 5–10 minutos)…"
    (
        cd "$work/libredwg-$LIBREDWG_VERSION"
        export PATH="$work/shim:$PATH"
        ./configure --prefix="$work/inst" --disable-bindings --disable-shared \
            --enable-static --disable-docs --disable-werror >"$work/configure.log" 2>&1
        make -j"$(sysctl -n hw.ncpu 2>/dev/null || echo 4)" >"$work/make.log" 2>&1
    ) || { warn "La compilación de LibreDWG falló (registro en $work)."; return 1; }
    mkdir -p "$DWG_DIR"
    for prog in dwg2dxf dwgread dxf2dwg; do
        cp "$work/libredwg-$LIBREDWG_VERSION/programs/$prog" "$DWG_DIR/$prog"
    done
    rm -rf "$work"
    say "LibreDWG integrado en $DWG_DIR"
}

if have_dwg; then
    say "Lector DWG disponible."
elif [[ $WANT_DWG -eq 1 ]]; then
    build_libredwg || warn "VectorCAD funcionará igual, pero sin abrir DWG (DXF sí)."
else
    warn "Sin lector DWG (--no-dwg)."
fi

# --------------------------------------------------------------------------- #
#  5. Construir el bundle .app
# --------------------------------------------------------------------------- #
say "Creando $BUNDLE"
mkdir -p "$APPS"
rm -rf "$BUNDLE"
mkdir -p "$BUNDLE/Contents/MacOS" "$BUNDLE/Contents/Resources"
[[ -n "$ICNS" ]] && cp "$ICNS" "$BUNDLE/Contents/Resources/VectorCAD.icns"

cat > "$BUNDLE/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>VectorCAD</string>
    <key>CFBundleDisplayName</key><string>VectorCAD</string>
    <key>CFBundleExecutable</key><string>VectorCAD</string>
    <key>CFBundleIdentifier</key><string>$BUNDLE_ID</string>
    <key>CFBundleIconFile</key><string>VectorCAD</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleShortVersionString</key><string>$VERSION</string>
    <key>CFBundleVersion</key><string>$VERSION</string>
    <key>LSMinimumSystemVersion</key><string>11.0</string>
    <key>NSHighResolutionCapable</key><true/>
    <key>NSHumanReadableCopyright</key><string>Centro Producción del Espacio · UDLA 2026</string>
    <key>LSApplicationCategoryType</key><string>public.app-category.graphics-design</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key><string>Dibujo VectorCAD</string>
            <key>CFBundleTypeRole</key><string>Editor</string>
            <key>LSHandlerRank</key><string>Owner</string>
            <key>CFBundleTypeIconFile</key><string>VectorCAD</string>
            <key>CFBundleTypeExtensions</key><array><string>vcad</string></array>
        </dict>
        <dict>
            <key>CFBundleTypeName</key><string>Dibujo DXF</string>
            <key>CFBundleTypeRole</key><string>Editor</string>
            <key>LSHandlerRank</key><string>Alternate</string>
            <key>CFBundleTypeExtensions</key><array><string>dxf</string></array>
        </dict>
        <dict>
            <key>CFBundleTypeName</key><string>Dibujo DWG</string>
            <key>CFBundleTypeRole</key><string>Viewer</string>
            <key>LSHandlerRank</key><string>Alternate</string>
            <key>CFBundleTypeExtensions</key><array><string>dwg</string></array>
        </dict>
    </array>
</dict>
</plist>
PLIST

cat > "$BUNDLE/Contents/MacOS/VectorCAD" <<'LAUNCH'
#!/bin/bash
SUPPORT="$HOME/Library/Application Support/VectorCAD"
LOG="$SUPPORT/vectorcad.log"
if [[ ! -x "$SUPPORT/venv/bin/python" ]]; then
    osascript -e 'display alert "VectorCAD" message "Falta el entorno de Python. Vuelve a ejecutar install_macos.command."'
    exit 1
fi
# el registro se recorta para que no crezca sin límite
if [[ -f "$LOG" ]] && [[ $(stat -f%z "$LOG") -gt 2000000 ]]; then
    tail -c 500000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
exec "$SUPPORT/venv/bin/python" "$SUPPORT/vectorcad.py" "$@" >>"$LOG" 2>&1
LAUNCH
chmod +x "$BUNDLE/Contents/MacOS/VectorCAD"

# Firma ad-hoc: evita avisos de Gatekeeper en Apple Silicon.
codesign --force --sign - "$BUNDLE" >/dev/null 2>&1 || warn "No se pudo firmar el bundle (no es crítico)."
xattr -dr com.apple.quarantine "$BUNDLE" 2>/dev/null || true

# Registrar en LaunchServices (Spotlight, «Abrir con») y refrescar el icono.
LSREG="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
[[ -x "$LSREG" ]] && "$LSREG" -f "$BUNDLE" >/dev/null 2>&1 || true
touch "$BUNDLE"

# --------------------------------------------------------------------------- #
#  6. Comando de terminal
# --------------------------------------------------------------------------- #
mkdir -p "$BIN"
cat > "$BIN/vectorcad" <<'CLI'
#!/bin/bash
SUPPORT="$HOME/Library/Application Support/VectorCAD"
exec "$SUPPORT/venv/bin/python" "$SUPPORT/vectorcad.py" "$@"
CLI
chmod +x "$BIN/vectorcad"

# --------------------------------------------------------------------------- #
#  7. Verificación
# --------------------------------------------------------------------------- #
say "Verificando…"
QT_QPA_PLATFORM=offscreen "$VENV/bin/python" -c "
import sys
sys.path.insert(0, '$SUPPORT')
import vectorcad as vc
print('    VectorCAD %s — %d comandos, %d alias, DXF=%s, booleanas=%s, DWG=%s'
      % (vc.APP_VERSION, len(vc.COMMANDS), len(vc.ALIAS_MAP), vc.HAS_EZDXF,
         vc.HAS_SHAPELY, vc.dwg_converter_name()))
" || die "La verificación falló; revisa el error anterior."

echo
say "Instalación terminada."
echo "   App:      $BUNDLE   (arrástrala al Dock si quieres)"
echo "   Terminal: vectorcad archivo.vcad|archivo.dxf|archivo.dwg"
case ":$PATH:" in
    *":$BIN:"*) ;;
    *) echo "   Añade el comando al PATH:  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc" ;;
esac
echo "   Registro de errores: $SUPPORT/vectorcad.log"
echo
