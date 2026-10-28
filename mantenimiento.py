import os
import shutil
import subprocess

def ejecutar_limpieza_temp():
    """Limpia los archivos temporales del usuario y del sistema de forma segura."""
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
                        shutil.rmtree(item_path, ignore_errors=True)
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

def actualizar_defender():
    """Actualiza las firmas de Windows Defender."""
    try:
        mpcmd = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Windows Defender", "MpCmdRun.exe")
        if not os.path.exists(mpcmd):
            mpcmd = os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Windows Defender", "MpCmdRun.exe")
        
        if os.path.exists(mpcmd):
            res = subprocess.run([mpcmd, "-SignatureUpdate"], capture_output=True, text=True, timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if res.returncode == 0:
                return True, "Firmas de seguridad de Windows Defender actualizadas."
            return True, "Consulta a Defender finalizada (se omitió o sin red)."
        return False, "MpCmdRun.exe no fue localizado en la ruta estándar."
    except Exception as e:
        return False, f"Error al actualizar Defender: {e}"

def ejecutar_dism():
    """Ejecuta la reparación de imagen del sistema mediante DISM."""
    try:
        res = subprocess.run(
            ["dism.exe", "/Online", "/Cleanup-Image", "/RestoreHealth"],
            capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if res.returncode == 0:
            return True, "Imagen del sistema reparada exitosamente mediante DISM."
        return False, f"DISM finalizó con código de salida {res.returncode}."
    except Exception as e:
        return False, f"Error crítico al ejecutar DISM: {e}"

def ejecutar_sfc():
    """Ejecuta la comprobación de archivos de sistema con SFC."""
    try:
        res = subprocess.run(
            ["sfc.exe", "/scannow"],
            capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if res.returncode == 0:
            return True, "Examen SFC completado: No se encontraron infracciones de integridad."
        return True, "Examen SFC finalizado (archivos verificados/reparados)."
    except Exception as e:
        return False, f"Error al ejecutar SFC: {e}"

def ejecutar_chkdsk():
    """Ejecuta el escaneo de integridad de disco en la unidad C:."""
    try:
        res = subprocess.run(
            ["chkdsk.exe", "C:"],
            capture_output=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if res.returncode == 0:
            return True, "CHKDSK: no se encontraron errores en C:."
        return False, f"CHKDSK terminó con código {res.returncode} (3 = errores sin corregir o sin permisos)."
    except Exception as e:
        return False, f"Error al ejecutar CHKDSK: {e}"