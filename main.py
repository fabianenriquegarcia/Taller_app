import flet as ft

BASIC = [
    ('temp', 'Limpieza de archivos temporales', True),
    ('browser', 'Cookies e historial de navegadores', False),
    ('recycle', 'Vaciar papelera de reciclaje', False),
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
    page.title = 'Taller PC - Mantenimiento y diagnóstico'
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 760
    page.window.height = 850
    page.window.min_width = 650
    page.window.min_height = 650
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    checks = {}
    log_lines = ['[INFO] Taller PC V0.1 iniciado.', '[INFO] Modo demostración: no se ejecutarán tareas reales.']
    console = ft.Text('\n'.join(log_lines), font_family='Consolas', size=12, selectable=True)
    status = ft.Text('Esperando instrucciones...', color=ft.Colors.BLUE_200)
    progress = ft.ProgressBar(value=0, height=7)

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
        return ft.Column(controls, spacing=2)

    basic = make_tasks(BASIC)
    advanced = make_tasks(ADVANCED)
    advanced.visible = False

    def change_section(is_basic):
        basic.visible = is_basic
        advanced.visible = not is_basic
        basic_button.disabled = is_basic
        advanced_button.disabled = not is_basic
        status.value = 'Mantenimiento básico' if is_basic else 'Mantenimiento avanzado: algunas tareas requieren administrador.'
        page.update()

    def simulate(e):
        current = BASIC if basic.visible else ADVANCED
        selected = [label for key, label, _ in current if checks[key].value]
        if not selected:
            log('[AVISO] Seleccioná al menos una tarea.')
            return
        log('[DEMO] Tareas seleccionadas:')
        for label in selected:
            log(f'  - {label}')
        status.value = f'{len(selected)} tarea(s) preparadas. Sin cambios en Windows.'
        progress.value = 0
        page.update()

    def skip(e):
        log('[DEMO] Saltar estará disponible cuando conectemos el motor de tareas.')

    def cancel(e):
        log('[DEMO] No hay tareas reales en ejecución.')

    basic_button = ft.Button('Mantenimiento básico', on_click=lambda e: change_section(True), disabled=True)
    advanced_button = ft.Button('Mantenimiento avanzado', on_click=lambda e: change_section(False))

    page.add(
        ft.Row([
            ft.Icon(ft.Icons.COMPUTER, size=30, color=ft.Colors.BLUE_300),
            ft.Column([
                ft.Text('TALLER PC', size=24, weight=ft.FontWeight.BOLD),
                ft.Text('Herramienta profesional de mantenimiento', size=13, color=ft.Colors.GREY_400),
            ], spacing=0),
            ft.Container(expand=True),
            ft.Text('V0.1.2 · DEMO', color=ft.Colors.AMBER_300),
        ]),
        ft.Divider(),
        ft.Row([basic_button, advanced_button], wrap=True),
        ft.Text('Seleccioná los procesos a ejecutar:', weight=ft.FontWeight.BOLD, size=15),
        ft.Container(content=ft.Column([basic, advanced]), bgcolor=ft.Colors.GREY_900, border_radius=10, padding=14),
        ft.Row([
            ft.Button('▶ Ejecutar seleccionados', on_click=simulate),
            ft.Button('⏭ Saltar proceso', on_click=skip),
            ft.Button('■ Cancelar todo', on_click=cancel),
        ], wrap=True),
        status,
        progress,
        ft.Text('Consola de actividad', weight=ft.FontWeight.BOLD),
        ft.Container(content=ft.Column([console], scroll=ft.ScrollMode.AUTO), bgcolor=ft.Colors.BLACK, border_radius=8, padding=12, height=160),
        ft.Divider(),
        ft.Row([
            ft.Text('Prototipo seguro: ninguna tarea modifica el sistema.', size=11, color=ft.Colors.GREY_500),
            ft.Container(expand=True),
            ft.Column([
                ft.Text('Autor: Fabián Enrique García', size=11, color=ft.Colors.GREY_400),
                ft.Text('Creación: 10/2026', size=11, color=ft.Colors.GREY_500),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END),
            ft.Button('Salir', icon=ft.Icons.EXIT_TO_APP, on_click=lambda e: page.window.close()),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )


if __name__ == '__main__':
    ft.run(main)
