"""Lecturas de hardware. No modifica la configuración de Windows."""
import ctypes
import os
import platform
import shutil
import subprocess


def _powershell(command):
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, text=True, timeout=12,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Código {result.returncode}")
    return result.stdout.strip()


def obtener_diagnostico():
    """Devuelve (datos, errores); cada dato se consulta independientemente."""
    datos, errores = {}, {}
    consultas = {
        "Sistema": lambda: f"{platform.system()} {platform.release()} ({platform.machine()})",
        "Procesador": lambda: _powershell("(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)"),
        "Memoria RAM": lambda: f"{int(_powershell('(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory')) / 1024**3:.2f} GB",
        "Unidad del sistema": lambda: _disco(),
    }
    for nombre, consulta in consultas.items():
        try:
            datos[nombre] = consulta() or "No disponible"
        except Exception as exc:
            datos[nombre] = "No disponible"
            errores[nombre] = str(exc)
    return datos, errores


def _disco():
    unidad = os.environ.get("SystemDrive", "C:") + "\\"
    total, usado, libre = shutil.disk_usage(unidad)
    return f"{libre / 1024**3:.1f} GB libres / {total / 1024**3:.1f} GB totales"
