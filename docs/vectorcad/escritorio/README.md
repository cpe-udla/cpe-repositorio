# VectorCAD 5.0

Sistema de dibujo 2D vectorial paramétrico en Python: lienzo cartesiano infinito,
intérprete de comandos con el diccionario de alias AutoCAD/Rhino, motor geométrico
propio y consola Python embebida para automatización.

```bash
pip install PySide6            # obligatoria (GUI)
pip install ezdxf shapely      # opcionales (DXF y booleanas)
python vectorcad.py            # o: python vectorcad.py dibujo.vcad | plano.dxf
```

Archivo único, ~8.000 líneas, sin dependencias obligatorias más allá de Qt.

## Novedades 5.0

- **Entrada dinámica (DIN, F12)**: durante un comando escribe la distancia y pulsa
  **Tab** para fijarla y pasar al ángulo (X→Y en el primer punto, Ancho→Alto en
  rectángulos); **Enter** o **Espacio** acepta. Con un valor fijado, el cursor sólo
  elige la dirección. Los campos aceptan expresiones (`1200/2`). Las distancias que
  pide un comando (desfase, radio…) también se pueden medir con dos clics.
- **Grosores de línea** reales (0.00–2.11 mm, PorCapa), visibles en pantalla con
  `LWT`/botón GROSOR, en capas, propiedades, DXF y PDF. Comandos `LW`, `COLOR`, `LT`.
- **Capas**: barra de propiedades (capa · color · tipo · grosor) que fija los valores
  actuales o cambia la selección; administrador con encender, bloquear, imprimir,
  color, tipo, grosor y conteo; `LAYMCUR`, `LAYCUR`, `LAYMOVE`, `LAYISO`/`LAYUNISO`,
  `LAYOFF`/`LAYON`, `LAYLCK`/`LAYULK`, `-LA`, igualar propiedades (`MA`).
- **Impresora virtual** (`PLOT`, Ctrl+P): PDF y SVG vectoriales o PNG; papel ISO/ANSI
  o personalizado; extensión, pantalla, ventana o selección; escala 1:N o ajustada;
  plumillas monocromo/gris/color; grosores; cajetín, marco, escala gráfica y norte;
  vista previa en vivo.
- **DWG** con LibreDWG compilado e integrado por el instalador (sin Homebrew), lectura
  DXF tolerante a errores, en segundo plano, conservando colores, tipos, grosores,
  textos MTEXT y alineaciones.
- **Rendimiento**: caché de dibujo, recorte por vista e índice espacial; planos de
  15.000 entidades se mueven con fluidez.
- Archivos recientes, arrastrar y soltar, preferencias persistentes, autocompletar
  alias con Tab, comandos transparentes y nuevo icono.

## Instalación

**macOS** — `bash install_macos.command` deja un `VectorCAD.app` en `~/Applications`
y el comando `vectorcad` en la terminal, con un entorno virtual aislado. Para una
app autónoma distribuible: `bash build_macos.sh --dmg`. Detalles, notarización y
resolución de problemas en [INSTALL_MACOS.md](INSTALL_MACOS.md).

**Como paquete** — `pipx install .` (o `pip install ".[full]"` dentro de un
entorno virtual) instala el comando `vectorcad` en Linux, macOS y Windows.

**Sin instalar** — `pip install PySide6 ezdxf shapely && python vectorcad.py`.

## Formatos

| Formato | Leer | Escribir | Requiere |
|---|---|---|---|
| `.vcad` / JSON | sí | sí | nada |
| DXF | sí | sí (R2010) | `ezdxf` |
| DWG | sí | sí | `ezdxf` + conversor externo |
| SVG | — | sí | nada |

DWG es un formato binario propietario sin especificación pública, así que se lee
delegando en un conversor externo que produce un DXF temporal:

- **LibreDWG** (libre): `brew install libredwg`, o `apt install libredwg-tools`.
- **ODA File Converter** (gratuito con registro, mayor fidelidad):
  [opendesign.com](https://www.opendesign.com/guestfiles/oda_file_converter).
  Se prefiere si está instalado.

Se detectan solos en las rutas habituales, incluido `/opt/homebrew/bin`, que no
está en el PATH de las apps lanzadas desde el Finder. Para forzar una ruta:
`export VECTORCAD_DWG_CONVERTER=/ruta/al/dwg2dxf`.

Comandos: `DWG`/`DWGIN` importar, `DWGOUT` exportar; `Ctrl+I` acepta ambos
formatos y el diálogo *Abrir* también. Probado contra los archivos de referencia
de LibreDWG en versiones DWG R2000 a 2018.

La importación traduce líneas, polilíneas, arcos, círculos, elipses, splines,
puntos, textos, achurados, sólidos 2D, caras 3D, líneas infinitas (acotadas) y
bloques anidados; las cotas y directrices se explotan a su geometría. Lo que no
tiene equivalente 2D —regiones, sólidos 3D, wipeouts, luces— se omite y se
informa en la línea de comandos, con el recuento por tipo.

## Arquitectura

| Capa | Implementación |
|---|---|
| Modelo geométrico | Python puro (tuplas `(x, y)`), independiente de Qt: permite `deepcopy`, JSON y pruebas sin GUI |
| Primitivas normalizadas | Toda entidad expone `("seg", a, b)` / `("arc", c, r, a0, a1)` → intersección, distancia, recorte y selección se resuelven con dos rutinas genéricas |
| Motor booleano | Shapely (`unary_union`, `difference`, `intersection`), con agujeros convertidos a polilíneas |
| GUI | PySide6 (fallback a PyQt6): lienzo `QPainter`, docks acoplables, menús, barra de estado |
| Intérprete | Comandos como generadores; cada `yield Prompt(...)` es un paso de entrada (punto, texto, número, palabra clave, selección) |
| E/S | `.vcad`/JSON nativo, DXF R2010 (ezdxf, ida y vuelta), SVG |

## Entrada de puntos

`x,y` absoluto · `@dx,dy` relativo · `@dist<áng` polar relativo · `dist<áng` polar absoluto ·
un número solo = distancia directa en la dirección del cursor · clic en el lienzo.

## Comandos implementados (88 canónicos, 120 alias)

- **Dibujo**: `L` `PL` `REC` `POL` `C` (centro/2P/3P) `A` (centro o 3P) `EL` `SPL` `PO` `T` `LE` `H`
- **Edición**: `M` `CO` `RO` `SC` `MI` `O` `AR` (rectangular/polar) `TR` `EX` `F` `CHA` `BR` `J` `X` `DIV` `ME` `LEN` `AL` `E` `ED` `G` `UG` `B` `I` `PU`
- **Booleanas**: `UNI` `SU` `IN`
- **Análisis**: `AA` `DI` `LI` `QC` `ID`
- **Cotas**: `DLI` `DAL` `DRA` `DDI` `DAN`
- **Vista**: `Z` `ZE` `ZW` `ZP` `ZS` `P` `S` `OS` `GRID` `ORTHO` `POLAR` `SN`
- **Sistema**: `LA` `PR` `UN` `U` `RE` `SA` `DXFIN` `DXFOUT` `DWGIN` `DWGOUT` `SVG` `SCR` `PY` `?`

Teclas: `F3` refent · `F7` rejilla · `F8` orto · `F9` snap · `F10` polar · `Esc` cancelar ·
`Supr` borrar · `Enter`/`Espacio` en vacío repite el último comando · `↑`/`↓` historial.

## Automatización

1. **Scripts `.scr`** — `SCR` ejecuta un archivo de texto donde cada línea es un alias o
   una entrada del comando activo (ver `ejemplo.scr`). El menú Archivo permite además
   **grabar** la sesión y guardarla como macro.
2. **Consola Python** (`PY`) — acceso directo al documento con el espacio de nombres
   precargado:
   ```python
   for i in range(12):
       add(Circle((i*15, 0), 5 + i))
   redraw(); zoom_extents()
   ```

## Qué cambia respecto a la propuesta base

**Errores corregidos**: `QSizeF` y `typing` sin importar; ángulos de arco invertidos en
`drawArc`; comandos sin `yield` que reventaban el intérprete; `zoom_at` con doble
corrección de encuadre; modo de selección inexistente (los clics se interpretaban como
puntos); imposibilidad de teclear coordenadas; `redo` incompleto; visibilidad y bloqueo
de capas ignorados en dibujo y selección.

**Añadidos sustantivos**: referencia a objetos con nueve modos (extremo, medio, centro,
cuadrante, intersección real, perpendicular, nodo, inserción, cercano) con marcadores
diferenciados; orto y polar; previsualización elástica en todos los comandos de creación
y transformación; selección por ventana/captura con realimentación visual y pinzamientos;
`TR`, `EX`, `F`, `CHA`, `BR`, `J`, `X`, `AR`, `DIV`, `ME`, `AL`, `POL`, `SPL`, `H`, bloques,
grupos y cotas (antes marcadores de "no implementado"); deshacer/rehacer por instantáneas
del documento; panel de propiedades editable; gestor de capas con color, visibilidad,
bloqueo y renombrado; importación DXF además de exportación; exportación SVG; scripts y
consola Python.

## Limitaciones conocidas

- `TR` sobre polilíneas las descompone en líneas (el segmento recortado se conserva como línea suelta).
- `EX` opera sobre líneas; `F` y `CHA` requieren dos líneas.
- Las booleanas necesitan Shapely; sin ella el comando avisa en vez de degradar el resultado.
- Sin espacio papel, layouts ni impresión: el destino de plotteo es DXF o SVG.
