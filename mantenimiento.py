import os
import shutil
import subprocess

def ejecutar_limpieza_temp():
    temp_paths = [
        os.environ.get("TEMP", ""),
        os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")
    ]
    eliminados = 0
    for ruta in temp_paths:
        if ruta and os.path.exists(ruta):
            for item in os.listdir(ruta):
                item_path = os.path.join(ruta, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                        eliminados += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True) # ignore_errors salta lo que esté bloqueado al instante
                        eliminados += 1
                except Exception:
                    pass
    return True, f"Temporales purgados con éxito ({eliminados} elementos procesados)."

def vaciar_papelera():
    """Vacía la papelera de reciclaje de manera silenciosa mediante PowerShell."""
    try:
        subprocess.run(
            ["PowerShell.exe", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
            capture_output=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        return True, "Papelera de reciclaje vaciada correctamente."
    except Exception as e:
        return False, f"No se pudo vaciar la papelera: {e}"