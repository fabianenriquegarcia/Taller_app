import os
from datetime import datetime

def generar_reporte_txt(hardware_dict, log_lines):
    """Genera un archivo de reporte técnico en formato .txt con el diagnóstico y la actividad."""
    try:
        # Creamos una carpeta 'Reportes' si no existe
        carpeta_reportes = "Reportes"
        if not os.path.exists(carpeta_reportes):
            os.makedirs(carpeta_reportes)

        # Nombre de archivo basado en fecha y hora actual
        timestamp_archivo = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = os.path.join(carpeta_reportes, f"Reporte_TallerPC_{timestamp_archivo}.txt")

        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("====================================================\n")
            f.write("          INFORME TÉCNICO DE MANTENIMIENTO          \n")
            f.write("                     TALLER PC                      \n")
            f.write("====================================================\n")
            f.write(f"Fecha y Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("Técnico / Responsable: Fabián Enrique García\n")
            f.write("Ubicación: La Calera, Córdoba, Argentina\n")
            f.write("----------------------------------------------------\n\n")

            f.write("[ 1. INFORMACIÓN DE HARDWARE DEL EQUIPO ]\n")
            for clave, valor in hardware_dict.items():
                f.write(f" - {clave}: {valor}\n")
            
            f.write("\n[ 2. REGISTRO DE ACTIVIDAD Y PROCESOS ]\n")
            for linea in log_lines:
                f.write(f"{linea}\n")

            f.write("\n====================================================\n")
            f.write("  Fin del informe - Taller PC Mantenimiento Profesional\n")
            f.write("====================================================\n")

        return True, nombre_archivo
    except Exception as e:
        return False, str(e)