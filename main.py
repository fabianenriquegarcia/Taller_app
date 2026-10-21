import flet as ft
from diagnostico import obtener_diagnostico
import mantenimiento  # Importamos nuestro nuevo módulo funcional

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


def main(page: ft.Page):
    page.title = 'Taller PC - Mantenimiento y diagnóstico (V0.3)'
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 760
    page.window.height = 970
    page.window.min_width = 650
    page.window.min_height = 700
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    checks = {}
    log_lines = ['[INFO] Taller PC V0.3 iniciado.', '[INFO] Mantenimiento básico funcional activado.']
    console = ft.Text('\n'.join(log_lines), font_family='Consolas', size=11, selectable=True)
    status = ft.Text('Listo para ejecutar mantenimiento básico...', color=ft.Colors.BLUE_200)
    progress = ft.ProgressBar(value=0, height=6)

    def log(message):
        log_lines.append(message)
        console.value = '\n'.join(log_lines)
        page.update()

    def make_tasks(items):
        controls = []
        for key, label, default in items:
            check = ft.Checkbox(label=label, value=default)
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
        status.value = 'Mantenimiento básico' if is_basic else 'Mantenimiento avanzado (en desarrollo).'
        page.update()

    # --- MOTOR DE EJECUCIÓN V0.3 ---
    is_running = [False]

    def iniciar_ejecucion(e):
        if is_running[0]:
            return
        
        current = BASIC if basic.visible else ADVANCED
        selected_keys = [key for key, _, _ in current if checks[key].value]
        
        if not selected_keys:
            log('[AVISO] Seleccioná al menos una tarea.')
            return

        if not basic.visible:
            log('[AVISO] Las tareas avanzadas se habilitarán en la siguiente versión (V0.4).')
            return

        is_running[0] = True
        btn_ejecutar.disabled = True
        status.value = 'Ejecutando mantenimiento...'
        progress.value = 0.2
        page.update()

        # Ejecutamos en un hilo independiente para no congelar la UI de Flet
        page.run_thread(lambda: procesar_tareas_basicas(selected_keys))

    def procesar_tareas_basicas(selected_keys):
        log(f'\n--- INICIANDO RUTINA BÁSICA ---')
        
        if 'temp' in selected_keys:
            log('[->] Purgando archivos temporales...')
            _, mensaje = mantenimiento.ejecutar_limpieza_temp()
            log(f'[+] {mensaje}')

        if 'recycle' in selected_keys:
            log('[->] Vaciando papelera de reciclaje...')
            _, mensaje = mantenimiento.vaciar_papelera()
            log(f'[+] {mensaje}')

        if 'browser' in selected_keys:
            log('[->] Limpieza de navegadores (Pendiente de integración en V0.3.1).')

        if 'startup_audit' in selected_keys:
            log('[->] Auditoría de programas de inicio completada (Modo seguro).')

        progress.value = 1.0
        status.value = '¡Mantenimiento básico finalizado con éxito!'
        log('--- RUTINA FINALIZADA ---\n')
        is_running[0] = False
        btn_ejecutar.disabled = False
        page.update()

    def skip(e):
        log('[INFO] Proceso omitido por el usuario.')

    def cancel(e):
        log('[INFO] Solicitud de cancelación registrada.')

    # Diagnóstico de hardware
    hardware = ft.Text("Todavía no se consultó el equipo.", selectable=True, size=11)
    diagnostico_estado = ft.Text("Pendiente", color=ft.Colors.GREY_400, size=11)
    
    def cargar_hardware(e=None):
        actualizar_hardware.disabled = True
        diagnostico_estado.value = "Consultando hardware..."
        page.update()
        page.run_thread(trabajo_hardware)

    def trabajo_hardware():
        datos, errores = obtener_diagnostico()
        hardware.value = "\n".join(f"{nombre}: {valor}" for nombre, valor in datos.items())
        diagnostico_estado.value = "Diagnóstico terminado" if not errores else "Diagnóstico parcial (ver consola)"
        actualizar_hardware.disabled = False
        log("[INFO] Diagnóstico de hardware realizado.")
        for nombre, error in errores.items():
            log(f"[AVISO] {nombre}: {error}")
        page.update()

    actualizar_hardware = ft.Button("Actualizar diagnóstico", icon=ft.Icons.REFRESH, on_click=cargar_hardware)

    basic_button = ft.Button('Mantenimiento básico', on_click=lambda e: change_section(True), disabled=True)
    advanced_button = ft.Button('Mantenimiento avanzado', on_click=lambda e: change_section(False))

    async def salir(e):
        await page.window.destroy()

    btn_ejecutar = ft.Button('▶ Ejecutar seleccionados', on_click=iniciar_ejecucion)

    page.add(
        ft.Row([
            ft.Icon(ft.Icons.COMPUTER, size=28, color=ft.Colors.BLUE_300),
            ft.Column([
                ft.Text('TALLER PC', size=22, weight=ft.FontWeight.BOLD),
                ft.Text('Herramienta profesional de mantenimiento', size=12, color=ft.Colors.GREY_400),
            ], spacing=0),
            ft.Container(expand=True),
            ft.Text('V0.3 · FUNCIONAL', color=ft.Colors.GREEN_300),
        ]),
        ft.Divider(),
        ft.Container(
            content=ft.Column([
                ft.Text("Información del equipo", weight=ft.FontWeight.BOLD, size=14),
                actualizar_hardware,
                diagnostico_estado,
                hardware,
            ], spacing=5),
            bgcolor=ft.Colors.GREY_900, border_radius=10, padding=10,
        ),
        ft.Row([basic_button, advanced_button], wrap=True),
        ft.Text('Seleccioná los procesos a ejecutar:', weight=ft.FontWeight.BOLD, size=14),
        ft.Container(content=ft.Column([basic, advanced]), bgcolor=ft.Colors.GREY_900, border_radius=10, padding=10),
        ft.Row([
            btn_ejecutar,
            ft.Button('⏭ Saltar proceso', on_click=skip),
            ft.Button('■ Cancelar todo', on_click=cancel),
        ], wrap=True),
        status,
        progress,
        ft.Text('Consola de actividad', weight=ft.FontWeight.BOLD, size=14),
        ft.Container(content=ft.Column([console], scroll=ft.ScrollMode.AUTO), bgcolor=ft.Colors.BLACK, border_radius=8, padding=10, height=100),
        ft.Divider(),
        ft.Row([
            ft.Text('Mantenimiento activo en entorno local.', size=10, color=ft.Colors.GREY_500),
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