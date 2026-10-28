import flet as ft
from diagnostico import obtener_diagnostico
import mantenimiento
import reportes
from datetime import datetime
import ctypes
import os

def es_administrador():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

BASIC = [
    ('temp', 'Limpieza de archivos temporales', True),
    ('browser', 'Cookies e historial de navegadores', False),
    ('recycle', 'Vaciar papelera de reciclaje', True),
    ('startup_audit', 'Auditoría de programas de inicio', True),
    ('defender', 'Actualizar firmas de Windows Defender', False),
]
ADVANCED = [
    ('update', 'Limpiar caché de Windows Update', False),
    ('startup', 'Optimizar programas de inicio', False),
    ('bloat', 'Remover bloatware', False),
    ('dism', 'Reparación de imagen del sistema (DISM)', False),
    ('sfc', 'Verificación de archivos del sistema (SFC)', False),
    ('disk', 'Escaneo de integridad del disco (CHKDSK)', False),
    ('ram', 'Diagnóstico de memoria RAM', False),
]

TAREAS = {
    'temp':     ('Purgando temporales',   mantenimiento.ejecutar_limpieza_temp),
    'recycle':  ('Vaciando papelera',     mantenimiento.vaciar_papelera),
    'defender': ('Actualizando Defender', mantenimiento.actualizar_defender),
    'dism':     ('Reparación DISM',       mantenimiento.ejecutar_dism),
    'sfc':      ('Verificación SFC',      mantenimiento.ejecutar_sfc),
    'disk':     ('Escaneo CHKDSK',        mantenimiento.ejecutar_chkdsk),
}
REQUIEREN_ADMIN = {'dism', 'sfc', 'disk'}

def main(page: ft.Page):
    # Actualizado a V1.0 Oficial
    page.title = 'Taller PC - Mantenimiento y diagnóstico (V1.0)'
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 780
    page.window.height = 910
    page.window.min_width = 650
    page.window.min_height = 700
    page.padding = 15
    page.scroll = None

    checks = {}
    admin_status = "Administrador" if es_administrador() else "Usuario estándar"
    log_lines = [
        '[INFO] Taller PC V1.0 iniciado.',
        f'[INFO] Nivel de privilegios: {admin_status}.',
        '[INFO] Aplicación lista para pruebas de campo.'
    ]
    
    console = ft.Text('\n'.join(log_lines), font_family='Consolas', size=11, selectable=True)
    status = ft.Text('Listo para ejecutar tareas y generar reportes...', color=ft.Colors.BLUE_200)
    progress = ft.ProgressBar(value=0, height=6)

    datos_hardware_actuales = {}

    def log(message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_lines.append(f'[{timestamp}] {message}')
        console.value = '\n'.join(log_lines)
        page.update()

    def make_tasks(items):
        controls = []
        for key, label, default in items:
            implementado = key in TAREAS
            check = ft.Checkbox(
                label=label if implementado else f'{label} (próximamente)',
                value=default and implementado,
                disabled=not implementado,
            )
            checks[key] = check
            controls.append(check)
        return ft.Column(controls, spacing=1)

    basic = make_tasks(BASIC)
    advanced = make_tasks(ADVANCED)
    advanced.visible = False

    def change_section(is_basic):
        basic.visible = is_basic
        advanced.visible = not is_basic
        basic_button.disabled = is_basic
        advanced_button.disabled = not is_basic
        status.value = 'Mantenimiento básico' if is_basic else 'Mantenimiento avanzado (requiere permisos de Admin).'
        page.update()

    is_running = [False]

    def iniciar_ejecucion(e):
        if is_running[0]:
            return
        
        current = BASIC if basic.visible else ADVANCED
        selected_keys = [key for key, _, _ in current if checks[key].value]
        
        if not selected_keys:
            log('[AVISO] Seleccioná al menos una tarea.')
            return

        is_running[0] = True
        btn_ejecutar.disabled = True
        status.value = 'Ejecutando mantenimiento en segundo plano...'
        progress.value = 0.1
        page.update()

        page.run_thread(lambda: procesar_tareas(selected_keys, es_basico=basic.visible))

    def procesar_tareas(selected_keys, es_basico):
        tipo = "BÁSICA" if es_basico else "AVANZADA"
        log(f'=== INICIANDO RUTINA {tipo} ({len(selected_keys)} TAREAS) ===')
        ok = fallo = omitidas = 0
        try:
            for i, key in enumerate(selected_keys, 1):
                if key not in TAREAS:
                    log(f'[~] "{key}" no está implementado, se omite.')
                    omitidas += 1
                elif key in REQUIEREN_ADMIN and not es_administrador():
                    log(f'[!] "{key}" requiere administrador, se omite.')
                    omitidas += 1
                else:
                    titulo, funcion = TAREAS[key]
                    log(f'[INICIO] {titulo}...')
                    exito, mensaje = funcion()
                    log(f'[{"+" if exito else "!"}] {mensaje}')
                    if exito:
                        ok += 1
                    else:
                        fallo += 1
                progress.value = i / len(selected_keys)
                page.update()
            status.value = f'Terminado: {ok} OK, {fallo} con error, {omitidas} omitidas.'
            log(f'=== RUTINA {tipo} FINALIZADA: {status.value} ===')
        finally:
            is_running[0] = False
            btn_ejecutar.disabled = False
            page.update()

    def exportar_reporte(e):
        log('[INICIO] Generando informe técnico en texto...')
        exito, resultado = reportes.generar_reporte_txt(datos_hardware_actuales, log_lines)
        if exito:
            log(f'[+] Reporte guardado con éxito en: {resultado}')
            status.value = f'Reporte guardado: {os.path.basename(resultado)}'
        else:
            log(f'[!] Error al generar el reporte: {resultado}')
            status.value = 'Error al generar reporte.'
        page.update()

    def skip(e):
        log('[INFO] Proceso omitido por el usuario.')

    def cancel(e):
        log('[INFO] Solicitud de cancelación recibida.')

    hardware = ft.Text("Todavía no se consultó el equipo.", selectable=True, size=11)
    diagnostico_estado = ft.Text("Pendiente", color=ft.Colors.GREY_400, size=11)
    
    def cargar_hardware(e=None):
        actualizar_hardware.disabled = True
        diagnostico_estado.value = "Consultando hardware..."
        page.update()
        page.run_thread(trabajo_hardware)

    def trabajo_hardware():
        nonlocal datos_hardware_actuales
        datos, errores = obtener_diagnostico()
        datos_hardware_actuales = datos
        hardware.value = "\n".join(f"{nombre}: {valor}" for nombre, valor in datos.items())
        diagnostico_estado.value = "Diagnóstico terminado" if not errores else "Diagnóstico parcial"
        actualizar_hardware.disabled = False
        log("[INFO] Diagnóstico de hardware completado.")
        page.update()

    actualizar_hardware = ft.Button("Actualizar diagnóstico", icon=ft.Icons.REFRESH, on_click=cargar_hardware)

    basic_button = ft.Button('Mantenimiento básico', on_click=lambda e: change_section(True), disabled=True)
    advanced_button = ft.Button('Mantenimiento avanzado', on_click=lambda e: change_section(False))

    async def salir(e):
        await page.window.destroy()

    btn_ejecutar = ft.Button('▶ Ejecutar', on_click=iniciar_ejecucion)
    btn_reporte = ft.Button('📄 Reporte', icon=ft.Icons.DESCRIPTION, on_click=exportar_reporte, color=ft.Colors.GREEN_ACCENT_200)
    btn_saltar = ft.Button('⏭ Saltar', on_click=skip)
    btn_cancelar = ft.Button('■ Cancelar todo', on_click=cancel)

    page.add(
        ft.Row([
            ft.Icon(ft.Icons.COMPUTER, size=28, color=ft.Colors.BLUE_300),
            ft.Column([
                ft.Text('TALLER PC', size=22, weight=ft.FontWeight.BOLD),
                ft.Text('Herramienta profesional de mantenimiento', size=12, color=ft.Colors.GREY_400),
            ], spacing=0),
            ft.Container(expand=True),
            # Etiqueta visual actualizada a V1.0 RELEASE
            ft.Text('V1.0 · RELEASE', color=ft.Colors.CYAN_ACCENT_400),
        ]),
        ft.Divider(),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Información del equipo", weight=ft.FontWeight.BOLD, size=14),
                    ft.Container(expand=True),
                    actualizar_hardware,
                    diagnostico_estado,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Column([hardware], scroll=ft.ScrollMode.AUTO),
                    height=75,
                )
            ], spacing=3),
            bgcolor=ft.Colors.GREY_900, border_radius=10, padding=10,
        ),
        ft.Row([basic_button, advanced_button], wrap=True),
        ft.Text('Seleccioná los procesos a ejecutar:', weight=ft.FontWeight.BOLD, size=14),
        ft.Container(content=ft.Column([basic, advanced]), bgcolor=ft.Colors.GREY_900, border_radius=10, padding=10),
        ft.Row([
            btn_ejecutar,
            btn_reporte,
            btn_saltar,
            btn_cancelar,
        ], spacing=8),
        status,
        progress,
        ft.Text('Consola de actividad (Detallada)', weight=ft.FontWeight.BOLD, size=14),
        ft.Container(
            content=ft.Column([console], scroll=ft.ScrollMode.AUTO), 
            bgcolor=ft.Colors.BLACK, 
            border_radius=8, 
            padding=10, 
            height=120
        ),
        ft.Divider(),
        ft.Row([
            ft.Text(f'Modo: {admin_status}', size=10, color=ft.Colors.GREY_500),
            ft.Container(expand=True),
            ft.Column([
                ft.Text('Autor: Fabián Enrique García', size=10, color=ft.Colors.GREY_400),
                ft.Text('Creación: 10/2026', size=10, color=ft.Colors.GREY_500),
            ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.END),
            ft.Button('Salir', icon=ft.Icons.EXIT_TO_APP, on_click=salir),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )
    cargar_hardware()

if __name__ == '__main__':
    ft.run(main)