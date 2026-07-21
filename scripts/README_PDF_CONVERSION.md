# PDF to Markdown Conversion Scripts

## Scripts Included

### 1. `convert_pdf_to_md.py`
Convierte todos los PDFs de `/papers/pdf` a archivos Markdown en `/papers/markdown`.

**Características:**
- Extrae texto completo de cada página
- Detecta y convierte tablas a Markdown
- Agrega metadatos (autor, año, título) en YAML frontmatter
- Genera archivos con nombre base idéntico al PDF

## Requirements

```bash
pip install pdfplumber
```

## Uso

```bash
# Navegar al directorio de scripts
cd scripts/

# Ejecutar el script
python3 convert_pdf_to_md.py
```

### Output

Los archivos Markdown se crearán en `/papers/markdown/` con la siguiente estructura:

```
markdown/
├── ACE_2020_Recuperacion_de_plusvalia.md
├── ACE_2023_Subsidios.md
├── AUS_2019_Precios_auge_campamentos.md
└── ... (todos los PDFs convertidos)
```

### Formato de los archivos Markdown

Cada archivo Markdown tiene:

```markdown
---
author: ACE
year: 2020
title: Recuperacion de plusvalia
source: ACE_2020_Recuperacion_de_plusvalia.pdf
---

# Recuperacion de plusvalia

**Author:** ACE
**Year:** 2020
**Source:** ACE_2020_Recuperacion_de_plusvalia.pdf

---

## Content

### Page 1

[Contenido del PDF...]

### Tables on Page 3

| Column 1 | Column 2 |
|----------|----------|
| ...      | ...      |
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pdfplumber'"

Instala la dependencia:
```bash
pip install pdfplumber
```

### PDFs con problemas de extracción

Algunos PDFs escaneados o con fuentes especiales pueden no extraer texto adecuadamente.

## Performance

- Aproximadamente 2-5 segundos por PDF (varía según tamaño)
- Para 64 PDFs: ~5-10 minutos
- Consume ~200-500MB de memoria
