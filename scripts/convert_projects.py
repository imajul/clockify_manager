#!/usr/bin/env python3
"""
Convert projects.xlsx to docs/projects.json.

The Excel must have at least two columns:
  - One named "Name" or "Project" (project name)
  - One named "Client" or "Client Name" (client name)

Clockify's default project export uses "Name" and "Client".
"""

import json
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("Install openpyxl: pip install openpyxl")

XLSX_PATH = Path("projects.xlsx")
JSON_PATH = Path("docs/projects.json")

PROJECT_COLS = ["Name", "Project", "Project Name", "name", "project"]
CLIENT_COLS  = ["Client", "Client Name", "client", "client name"]


def find_col(headers, candidates):
    for c in candidates:
        if c in headers:
            return c
    return None


def main():
    if not XLSX_PATH.exists():
        sys.exit(f"Archivo no encontrado: {XLSX_PATH}")

    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        sys.exit("El archivo Excel está vacío.")

    headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    proj_col   = find_col(headers, PROJECT_COLS)
    client_col = find_col(headers, CLIENT_COLS)

    if not proj_col:
        sys.exit(f"No se encontró columna de proyecto. Columnas disponibles: {headers}")
    if not client_col:
        sys.exit(f"No se encontró columna de cliente. Columnas disponibles: {headers}")

    proj_idx   = headers.index(proj_col)
    client_idx = headers.index(client_col)

    entries = []
    seen = set()
    for row in rows[1:]:
        project = str(row[proj_idx]).strip() if row[proj_idx] is not None else ""
        client  = str(row[client_idx]).strip() if row[client_idx] is not None else ""
        if not project or not client:
            continue
        key = (project, client)
        if key in seen:
            continue
        seen.add(key)
        entries.append({"project": project, "client": client})

    entries.sort(key=lambda e: (e["project"], e["client"]))

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n")
    print(f"✓ {len(entries)} entradas escritas en {JSON_PATH}")


if __name__ == "__main__":
    main()
