"""Check the SAP HANA Cloud connection and show the last rows the app mirrored. Run from the project folder:
  HANA_HOST=... HANA_USER=... HANA_PASSWORD=... python3 tools_hana_check.py
(needs: pip install -r backend/requirements-sap.txt). Prints no password."""
import os, sys
from backend.app import hana_sink as H
if not H.enabled(): sys.exit("Set HANA_HOST, HANA_USER and HANA_PASSWORD first.")
try:
    conn = H._connect(); H._ensure_table(conn); cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {H.TABLE}"); print("Connected. Rows in", H.TABLE, ":", cur.fetchone()[0])
    cur.execute(f"SELECT TOP 5 CREATED_AT, AGENT, MODE, OUTPUT_SUMMARY FROM {H.TABLE} ORDER BY ID DESC")
    for r in cur.fetchall(): print(" ", *r)
except Exception as e: sys.exit(f"Could not connect: {e}")
