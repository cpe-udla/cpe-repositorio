#!/usr/bin/env python3
"""
Script para convertir PDFs a Markdown
Usa pdfplumber para extraer texto y contenido estructurado
"""

import os
import re
from pathlib import Path
from typing import Tuple
import pdfplumber

def parse_filename(filename: str) -> Tuple[str, str, str]:
    """Extrae autor, año y título del nombre del archivo renombrado"""
    filename_without_ext = filename.replace('.pdf', '')

    # Patrón: Autor_Año_Titulo
    pattern = r'^(.+?)_(\d{4})_(.+)$'
    match = re.match(pattern, filename_without_ext)

    if match:
        author = match.group(1).replace('_', ' ')
        year = match.group(2)
        title = match.group(3).replace('_', ' ')
        return author, year, title

    return "Unknown", "Unknown", filename_without_ext

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extrae texto de un PDF usando pdfplumber"""
    try:
        text_content = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extraer texto
                text = page.extract_text()
                if text:
                    text_content.append(f"### Page {page_num}\n\n{text}\n")

                # Intentar extraer tablas
                tables = page.extract_tables()
                if tables:
                    text_content.append(f"### Tables on Page {page_num}\n\n")
                    for table in tables:
                        # Convertir tabla a markdown
                        if table:
                            headers = table[0]
                            md_table = "| " + " | ".join(str(h) for h in headers) + " |\n"
                            md_table += "|" + "|".join(["---"] * len(headers)) + "|\n"

                            for row in table[1:]:
                                md_table += "| " + " | ".join(str(cell) if cell else "" for cell in row) + " |\n"

                            text_content.append(md_table + "\n")

        return "\n".join(text_content) if text_content else "No text content found in PDF."

    except Exception as e:
        return f"Error extracting text: {str(e)}"

def create_markdown_file(pdf_path: Path, md_dir: Path) -> bool:
    """Convierte un PDF a Markdown"""
    try:
        # Parse filename
        author, year, title = parse_filename(pdf_path.name)

        # Extract text
        print(f"Processing: {pdf_path.name}...", end=" ")
        text_content = extract_text_from_pdf(pdf_path)

        # Create markdown filename
        md_filename = pdf_path.stem + ".md"
        md_path = md_dir / md_filename

        # Create markdown content with frontmatter
        markdown_content = f"""---
author: {author}
year: {year}
title: {title}
source: {pdf_path.name}
---

# {title}

**Author:** {author}
**Year:** {year}
**Source:** {pdf_path.name}

---

## Content

{text_content}
"""

        # Write markdown file
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print("✓")
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    pdf_dir = Path('/Users/josefranciscovergara/Library/CloudStorage/GoogleDrive-franciscovergarap@gmail.com/Mi unidad/0-RESPALDOS/CPE/repositorio Github CPE/papers/pdf')
    md_dir = pdf_dir.parent / 'markdown'

    if not pdf_dir.exists():
        print(f"Error: {pdf_dir} does not exist")
        return

    # Create markdown directory
    md_dir.mkdir(exist_ok=True)
    print(f"Output directory: {md_dir}\n")

    # Get all PDF files
    pdf_files = sorted(pdf_dir.glob('*.pdf'))

    if not pdf_files:
        print("No PDF files found")
        return

    print(f"Found {len(pdf_files)} PDF files\n")
    print("Converting to Markdown...")
    print("-" * 60)

    successful = 0
    failed = 0

    for pdf_file in pdf_files:
        if create_markdown_file(pdf_file, md_dir):
            successful += 1
        else:
            failed += 1

    print("-" * 60)
    print(f"\n✓ Conversion complete!")
    print(f"  ├─ Successful: {successful}")
    print(f"  ├─ Failed: {failed}")
    print(f"  └─ Output: {md_dir}")

if __name__ == '__main__':
    main()
