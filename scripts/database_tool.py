#!/usr/bin/env python3
"""
Aether Sovereign Database Management & Administrative Tool
Provides CLI management commands for Aether's 17 isolated SQLite databases:
- Integrity Verification (PRAGMA integrity_check)
- Online Hot Backup Engine (Atomic snapshot via SQLite Backup API)
- Defragmentation and Query Planner Optimization (VACUUM + ANALYZE)
- Granular Storage and B-Tree Space Allocation Auditing
- Data Export Pipeline (JSON & CSV dumps)
- Read-Only SQL Shell Inspector

Usage:
    python3 scripts/database_tool.py audit
    python3 scripts/database_tool.py integrity
    python3 scripts/database_tool.py optimize
    python3 scripts/database_tool.py backup --target /path/to/backup
    python3 scripts/database_tool.py export --db notes.db --table notes --format json
    python3 scripts/database_tool.py query --db calendar.db --sql "SELECT * FROM calendar_events"
"""

from __future__ import annotations
import argparse
import csv
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Ensure project root is in python path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.database_manager import db_manager


def cmd_audit(args: argparse.Namespace) -> int:
    """Print comprehensive database enclave audit report."""
    print("=" * 80)
    print("   AETHER ENCLAVE STORAGE AUDIT (17 ISOLATED SQLITE DATABASES)")
    print("=" * 80)
    audit = db_manager.get_storage_audit()
    print(f"Storage Root:        {audit.get('storage_path')}")
    print(f"Total Enclaves:      {audit.get('total_databases')} active SQLite databases")
    print(f"Total Data Storage:  {audit.get('total_data_size_mb', 0):.3f} MB")
    print(f"Total WAL Storage:   {audit.get('total_wal_size_mb', 0):.3f} MB")
    print(f"Combined Storage:    {audit.get('combined_storage_mb', 0):.3f} MB")
    print(f"Total Records:       {audit.get('total_records_stored', 0):,} rows indexed")
    print("-" * 85)
    print(f"{'Subsystem Enclave':<22} {'DB File':<18} {'Size (KB)':<10} {'WAL (KB)':<10} {'Pages':<8} {'Rows':<8} {'Frag'}")
    print("-" * 85)

    diagnostics = db_manager.get_all_databases_diagnostics()
    for diag in sorted(diagnostics, key=lambda d: d.get("name", "")):
        name = diag.get("name", "")
        db_file = name if name.endswith(".db") else f"{name}.db"
        size_kb = diag.get("file_size_kb", 0.0)
        wal_kb = diag.get("wal_size_kb", 0.0)
        pages = diag.get("page_count", 0)
        records = diag.get("total_records", 0)
        frag = diag.get("fragmentation_percent", 0.0)
        print(f"{name:<22} {db_file:<18} {size_kb:<10.1f} {wal_kb:<10.1f} {pages:<8} {records:<8} {frag:<5.1f}%")

    print("=" * 85)
    return 0


def cmd_integrity(args: argparse.Namespace) -> int:
    """Run PRAGMA integrity_check across all databases."""
    print("Executing PRAGMA integrity_check across all 17 database enclaves...")
    start = time.perf_counter()
    report = db_manager.verify_integrity_all_databases()
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    all_passed = report.get("all_healthy", False)
    databases = report.get("databases", {})

    print("-" * 65)
    print(f"{'Enclave Database':<25} {'Status':<15} {'Integrity'}")
    print("-" * 65)
    for db_name, res in sorted(databases.items()):
        status_str = res.get("status", "Unknown")
        msg = res.get("integrity", "")
        print(f"{db_name:<25} {status_str:<15} {msg}")

    print("-" * 65)
    print(f"Integrity Check Result: {'[ALL HEALTHY]' if all_passed else '[ERRORS DETECTED]'}")
    print(f"Verification Duration:  {elapsed_ms:.2f} ms")
    return 0 if all_passed else 1


def cmd_optimize(args: argparse.Namespace) -> int:
    """Run VACUUM and ANALYZE across all enclaves."""
    print("Running optimization (VACUUM defragmentation + ANALYZE statistics)...")
    start = time.perf_counter()
    report = db_manager.optimize_all_databases()
    elapsed = (time.perf_counter() - start) * 1000.0

    print(f"Optimization completed in {elapsed:.2f} ms.")
    print(f"Status summary: {len(report)} databases processed.")
    return 0


def cmd_backup(args: argparse.Namespace) -> int:
    """Atomic online backup of all 17 databases."""
    target_dir = args.target or os.path.join(WORKSPACE_ROOT, "data", "backups")
    os.makedirs(target_dir, exist_ok=True)
    print(f"Starting online hot backup to: {target_dir}")
    start = time.perf_counter()
    res = db_manager.backup_all_databases(backup_dir=target_dir)
    elapsed = (time.perf_counter() - start) * 1000.0

    print(f"Hot backup completed in {elapsed:.2f} ms.")
    print(f"Total backups saved: {res.get('databases_backed_up', len(res.get('manifest', [])))} databases")
    print(f"Total backup size:  {res.get('total_size_mb', 0.0):.3f} MB")
    print(f"Backup directory:   {res.get('backup_directory', target_dir)}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Export database table rows to JSON or CSV."""
    db_name = args.db
    table = args.table
    fmt = args.format.lower()
    output_path = args.output

    if not db_name.endswith(".db"):
        db_name = f"{db_name}.db"

    sql = f"SELECT * FROM {table}"
    try:
        rows = db_manager.execute_query(db_name, sql)
    except Exception as e:
        print(f"Export query failed: {e}", file=sys.stderr)
        return 1

    if fmt == "json":
        data_str = json.dumps(rows, indent=2, default=str)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as fp:
                fp.write(data_str)
            print(f"Successfully exported {len(rows)} records to {output_path}")
        else:
            print(data_str)
    elif fmt == "csv":
        if not rows:
            print("Table contains no rows.", file=sys.stderr)
            return 0
        fieldnames = list(rows[0].keys())
        out_stream = open(output_path, "w", newline="", encoding="utf-8") if output_path else sys.stdout
        try:
            writer = csv.DictWriter(out_stream, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        finally:
            if output_path:
                out_stream.close()
                print(f"Successfully exported {len(rows)} records to {output_path}")
    else:
        print(f"Unsupported format: {fmt}", file=sys.stderr)
        return 1

    return 0


def cmd_query(args: argparse.Namespace) -> int:
    """Execute a read-only query on a target database."""
    db_name = args.db
    sql = args.sql
    if not db_name.endswith(".db"):
        db_name = f"{db_name}.db"

    try:
        rows = db_manager.execute_query(db_name, sql)
        print(json.dumps(rows, indent=2, default=str))
        print(f"\n({len(rows)} rows returned)")
        return 0
    except Exception as e:
        print(f"Query error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aether Sovereign Database Administrative Management Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Management commands")

    # audit
    subparsers.add_parser("audit", help="Audit storage and allocation across all 17 databases")

    # integrity
    subparsers.add_parser("integrity", help="Run PRAGMA integrity_check across all 17 databases")

    # optimize
    subparsers.add_parser("optimize", help="Run VACUUM and ANALYZE across all databases")

    # backup
    backup_parser = subparsers.add_parser("backup", help="Create hot snapshot backup of databases")
    backup_parser.add_argument("--target", type=str, help="Destination directory for snapshots")

    # export
    export_parser = subparsers.add_parser("export", help="Export enclave table data to JSON or CSV")
    export_parser.add_argument("--db", type=str, required=True, help="Database name (e.g. notes.db)")
    export_parser.add_argument("--table", type=str, required=True, help="Table name to export")
    export_parser.add_argument("--format", type=str, choices=["json", "csv"], default="json", help="Export format")
    export_parser.add_argument("--output", type=str, help="Output destination filepath")

    # query
    query_parser = subparsers.add_parser("query", help="Execute read-only SQL query on target database")
    query_parser.add_argument("--db", type=str, required=True, help="Database name (e.g. calendar.db)")
    query_parser.add_argument("--sql", type=str, required=True, help="SQL query to execute")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "audit": cmd_audit,
        "integrity": cmd_integrity,
        "optimize": cmd_optimize,
        "backup": cmd_backup,
        "export": cmd_export,
        "query": cmd_query
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
