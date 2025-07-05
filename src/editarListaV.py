import flet as ft
from invSis import cargar_listas_por_inventario, actualizar_nombre_lista

def cerrar_ventana(page):
    page.overlay.clear()
    page.update()

def mostrar_ventana_e_lista(e, page, id_inventario, actualizar_callback):
    page.overlay.clear()
    page.update()
    ventana_x = 250
    ventana_y = 150

    # Cargar todas las listas del inventario
    listas = cargar_listas_por_inventario(id_inventario)

    # Dropdown de listas
    dropdown_listas = ft.Dropdown(
        label="SELECCIONA LISTA",
        options=[ft.dropdown.Option(l["nombre"]) for l in listas],
        width=300,
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        color="black",
        border_radius=ft.border_radius.all(15),
    )

    nombre_lista = ft.TextField(
        label="NUEVO NOMBRE",
        bgcolor="#F0F0EF",
        border_color="#F0F0EF",
        border_radius=ft.border_radius.all(15),
    )

    def mover_ventana(event):
        nonlocal ventana_x, ventana_y
        ventana_x += event.delta_x
        ventana_y += event.delta_y
        ventana_movable.left = ventana_x
        ventana_movable.top = ventana_y
        page.update()

    def editar_lista_action(e):
        nombre_sel = dropdown_listas.value
        nuevo_nombre = nombre_lista.value.strip()
        if not nombre_sel or not nuevo_nombre:
            return
        lista = next((l for l in listas if l["nombre"] == nombre_sel), None)
        if not lista:
            return
        id_lista = lista["id"]
        exito = actualizar_nombre_lista(id_lista, nuevo_nombre)
        if exito:
            cerrar_ventana(page)
            if actualizar_callback:
                actualizar_callback()

    ventana_contenido = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("EDITAR LISTA", size=20, weight=ft.FontWeight.BOLD, color="black"),
                    bgcolor="#FAEDE2",
                    border_radius=10,
                    padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                    alignment=ft.alignment.center_left,
                ),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                        ft.Text("EDITAR LISTA", size=14, color="gray"),
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                dropdown_listas,
                nombre_lista,
                ft.Row(
                    [
                        ft.ElevatedButton("Cancelar", icon=ft.Icons.CLOSE, on_click=lambda _: cerrar_ventana(page)),
                        ft.ElevatedButton("Continuar", icon=ft.Icons.ADD, on_click=editar_lista_action),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=400,
        height=300,
        bgcolor="#FFD5BD",
        border_radius=10,
        border=ft.border.all(2, "black"),
        padding=20,
    )

    ventana_movable = ft.GestureDetector(
        content=ventana_contenido,
        on_pan_update=mover_ventana,
        left=ventana_x,
        top=ventana_y,
    )

    ventana_stack = ft.Stack(
        controls=[ventana_movable],
        width=page.width,
        height=page.height,
    )

    page.overlay.append(ventana_stack)
    page.update()