"""
Runner unificado — Suite de regresión ABBE
Ejecuta todos los diagnósticos de bloques 2.2–2.6 y genera artefacto de salida.

Uso:
    python3 run_all.py              # solo offline (no requiere servidor)
    python3 run_all.py --runtime    # offline + runtime (requiere servidor en :7862)
    python3 run_all.py --block 2.5  # solo un bloque específico

Artefacto de salida: regression_report.md
"""
import subprocess
import sys
import os
import argparse
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(SCRIPT_DIR, "regression_report.md")

# Inventario de scripts por bloque
SUITES = {
    "2.2": {
        "offline": ["diag_retrieval.py"],
        "runtime": [],
    },
    "2.3": {
        "offline": ["diag_routing.py"],
        "runtime": ["diag_adversarial.py", "diag_multiturn.py"],
    },
    "2.4": {
        "offline": [],
        "runtime": ["diag_runtime_24.py"],
    },
    "2.5": {
        "offline": ["diag_25_noresults.py"],
        "runtime": ["diag_25_runtime.py"],
    },
    "2.6": {
        "offline": [],
        "runtime": ["diag_26_historial.py", "diag_26_final.py"],
    },
}

def run_script(script_name):
    """Ejecuta un script y retorna (exit_code, stdout+stderr)."""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        return 1, f"[ERROR] Script no encontrado: {script_path}"

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=os.path.join(SCRIPT_DIR, ".."),  # Ejecutar desde ABBE/
        )
        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return 1, f"[TIMEOUT] {script_name} excedió 300s"
    except Exception as e:
        return 1, f"[ERROR] {e}"

def main():
    parser = argparse.ArgumentParser(description="Runner de regresión ABBE")
    parser.add_argument("--runtime", action="store_true", help="Incluir tests runtime (requiere servidor)")
    parser.add_argument("--block", type=str, help="Ejecutar solo un bloque (ej: 2.5)")
    args = parser.parse_args()

    blocks = [args.block] if args.block else sorted(SUITES.keys())
    include_runtime = args.runtime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = []
    report_lines.append(f"{'=' * 70}")
    report_lines.append(f"  ABBE Regression Report — {timestamp}")
    report_lines.append(f"  Mode: {'offline + runtime' if include_runtime else 'offline only'}")
    report_lines.append(f"  Blocks: {', '.join(blocks)}")
    report_lines.append(f"{'=' * 70}")

    total_scripts = 0
    total_passed = 0
    total_failed = 0
    summary = []

    for block in blocks:
        if block not in SUITES:
            print(f"[WARN] Bloque {block} no encontrado, skip")
            continue

        suite = SUITES[block]
        scripts = suite["offline"][:]
        if include_runtime:
            scripts += suite["runtime"]

        if not scripts:
            continue

        report_lines.append(f"\n{'─' * 70}")
        report_lines.append(f"  BLOQUE {block}")
        report_lines.append(f"{'─' * 70}")

        for script in scripts:
            total_scripts += 1
            tag = "[RUNTIME]" if script in suite["runtime"] else "[OFFLINE]"
            print(f"  Running {tag} {script}...", end=" ", flush=True)

            exit_code, output = run_script(script)
            status = "PASS" if exit_code == 0 else "FAIL"
            icon = "✓" if exit_code == 0 else "✗"

            if exit_code == 0:
                total_passed += 1
            else:
                total_failed += 1

            print(f"{icon} {status}")
            summary.append((block, script, status))

            report_lines.append(f"\n  {tag} {script} — {status}")
            report_lines.append(output)

    # Resumen
    report_lines.append(f"\n{'=' * 70}")
    report_lines.append(f"  RESUMEN")
    report_lines.append(f"{'=' * 70}")
    report_lines.append(f"  Total: {total_scripts} scripts")
    report_lines.append(f"  Passed: {total_passed}")
    report_lines.append(f"  Failed: {total_failed}")
    report_lines.append("")
    for block, script, status in summary:
        icon = "✓" if status == "PASS" else "✗"
        report_lines.append(f"  {icon} [{block}] {script}")
    report_lines.append(f"\n{'=' * 70}")

    # Escribir artefacto
    report = "\n".join(report_lines)
    with open(REPORT_PATH, "w") as f:
        f.write(report)

    # Imprimir resumen en consola
    print(f"\n{'=' * 70}")
    print(f"  Scripts: {total_scripts} | Passed: {total_passed} | Failed: {total_failed}")
    print(f"  Report: {REPORT_PATH}")
    print(f"{'=' * 70}")

    sys.exit(1 if total_failed > 0 else 0)

if __name__ == "__main__":
    main()
