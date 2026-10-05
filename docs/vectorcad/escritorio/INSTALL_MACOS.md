# VectorCAD en macOS

Tres rutas, de menor a mayor esfuerzo. Si sólo quieres usarlo en tu Mac, la **A** basta.

| Ruta | Resultado | Requiere Python | Tiempo |
|---|---|---|---|
| **A. `install_macos.command`** | `VectorCAD.app` en `~/Applications` + comando `vectorcad` | Sí (3.9+) | ~2 min |
| **B. `build_macos.sh`** | `.app` autónomo (y `.dmg`), distribuible a otros Macs | Sólo para compilar | ~5 min |
| **C. `pip install .`** | Comando `vectorcad` en un entorno cualquiera | Sí | ~1 min |

---

## A. Instalación normal (recomendada)

Requiere Python 3.9 o superior. Si no lo tienes:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12
```

Después, en la carpeta que contiene `vectorcad.py`:

```bash
bash install_macos.command
```

(También funciona con doble clic desde el Finder. Si macOS se niega a abrirlo:
Ajustes del Sistema → Privacidad y seguridad → *Abrir igualmente*.)

El instalador:

1. crea un entorno virtual aislado en `~/Library/Application Support/VectorCAD/venv`
   —no toca tu Python del sistema ni tus otros proyectos—;
2. instala `PySide6`, `ezdxf` y `shapely`;
3. si no hay conversor DWG, descarga LibreDWG de ftp.gnu.org y lo compila en
   `~/Library/Application Support/VectorCAD/libredwg` (5–10 min, sólo la primera
   vez; requiere las Command Line Tools: `xcode-select --install`; se omite con
   `--no-dwg`);
4. genera el icono y construye `~/Applications/VectorCAD.app`, firmado ad-hoc y
   registrado en LaunchServices (aparece en Spotlight y en *Abrir con*);
5. asocia las extensiones `.vcad`, `.dxf` y `.dwg`;
6. deja el comando `vectorcad` en `~/.local/bin`.

Uso:

```bash
open -a VectorCAD                 # o desde el Launchpad / Dock
vectorcad plano.dxf               # desde la terminal
```

Si `vectorcad` no se encuentra, añade la carpeta al PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

Actualizar (tras editar `vectorcad.py`): vuelve a ejecutar el instalador.
Desinstalar: `bash install_macos.command --uninstall`.

**Advertencia**: como el ejecutable del bundle es un lanzador que llama al Python
del entorno virtual, macOS puede mostrar «Python» en algún diálogo del sistema.
Es cosmético. Si te molesta, usa la ruta B.

---

## B. App autónoma (para distribuir)

Compila un `.app` con el intérprete y Qt dentro: funciona en un Mac sin Python.

```bash
bash build_macos.sh          # dist/VectorCAD.app  (~250-400 MB)
bash build_macos.sh --dmg    # además dist/VectorCAD-5.0.dmg
```

La app se compila para la arquitectura de la máquina que compila. Un `.app`
hecho en Apple Silicon corre en Intel sólo si usas `--universal`, lo que exige
un Python universal2 (el instalador de python.org) y ruedas universales de
PySide6.

Como no está notarizada por Apple, en el Mac de destino:

```bash
xattr -dr com.apple.quarantine /Applications/VectorCAD.app
```

o bien clic derecho → *Abrir* la primera vez. Para repartirla sin fricción
necesitarías una cuenta de Apple Developer (99 USD/año) y firmar + notarizar:

```bash
codesign --deep --force --options runtime --sign "Developer ID Application: TU NOMBRE (TEAMID)" dist/VectorCAD.app
xcrun notarytool submit dist/VectorCAD-5.0.dmg --apple-id … --team-id … --password … --wait
xcrun stapler staple dist/VectorCAD-5.0.dmg
```

---

## C. Como paquete de Python

```bash
pipx install .          # aislado, deja el comando en el PATH
# o
pip install ".[full]"   # dentro de un entorno virtual tuyo
vectorcad
```

`pip install .` instala sólo PySide6; el extra `full` añade `ezdxf` (DXF) y
`shapely` (booleanas robustas).

---

## Importar DWG

DWG no se lee de forma nativa: hace falta un conversor, que VectorCAD localiza
solo. Desde la 5.0 el instalador de la ruta A **compila e integra LibreDWG** desde
el código fuente oficial de GNU, sin Homebrew (queda en
`~/Library/Application Support/VectorCAD/libredwg/bin`). La lectura corre en
segundo plano y usa el modo de recuperación de ezdxf; si el conversor entrega
todas las capas apagadas (ocurre con algunos DWG 2004–2007), se encienden y se
avisa en el historial. Alternativa con Homebrew:

```bash
brew install libredwg          # libre, rápido, sin interfaz
```

Para máxima fidelidad —planos comerciales complejos, DWG muy recientes— instala
además el **ODA File Converter** desde
[opendesign.com](https://www.opendesign.com/guestfiles/oda_file_converter)
(gratuito, pide registro). Si está presente, VectorCAD lo prefiere. Se busca en
`/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter`.

Para forzar una ruta concreta:

```bash
export VECTORCAD_DWG_CONVERTER="/ruta/al/dwg2dxf"
```

Si lanzas la app desde el Finder, esa variable no se hereda de tu `~/.zshrc`;
añádela al lanzador (`~/Applications/VectorCAD.app/Contents/MacOS/VectorCAD`) o
usa el comando `vectorcad` desde la terminal. En la app compilada con
PyInstaller (ruta B) el conversor sigue siendo externo: el `.app` es autónomo en
cuanto a Python y Qt, no en cuanto a DWG.

Comprobar qué conversor ve la aplicación:

```bash
"$HOME/Library/Application Support/VectorCAD/venv/bin/python" -c \
  "import sys; sys.path.insert(0,'$HOME/Library/Application Support/VectorCAD'); \
   import vectorcad as v; print(v.dwg_converter_name())"
```

---

## Notas de uso en macOS

- Los atajos con `Ctrl` de la documentación son `Cmd` en macOS: Qt hace la
  traducción automáticamente (`Cmd-Z` deshacer, `Cmd-S` guardar, etc.).
- `F3`, `F7`–`F10` requieren pulsar `fn` si tienes activada la fila de teclas
  multimedia, o desactivar esa opción en Ajustes → Teclado.
- Rueda del ratón / *pinch* del trackpad: zoom. Botón central o `Space`
  arrastrando: encuadre.
- Las trazas de error de la app lanzada desde el Finder quedan en
  `~/Library/Application Support/VectorCAD/vectorcad.log`.

## Si algo falla

| Síntoma | Causa habitual | Solución |
|---|---|---|
| «Necesitas Python 3.9 o superior» | sólo tienes el Python de las Command Line Tools | `brew install python@3.12` y reintenta |
| La app rebota en el Dock y se cierra | falta una dependencia | revisa `vectorcad.log`; reinstala con `bash install_macos.command` |
| `ModuleNotFoundError: PySide6` al usar `vectorcad` | el entorno se movió o borró | reinstala |
| Sin comandos DXF ni booleanas | `ezdxf`/`shapely` no se instalaron | `~/Library/Application\ Support/VectorCAD/venv/bin/pip install ezdxf shapely` |
| «VectorCAD está dañada» | cuarentena de Gatekeeper | `xattr -dr com.apple.quarantine /ruta/VectorCAD.app` |
| El icono no aparece | LaunchServices cacheó el genérico | `touch ~/Applications/VectorCAD.app` y reinicia el Finder |
