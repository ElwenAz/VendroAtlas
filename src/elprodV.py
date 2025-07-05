import flet as ft
from db_connection import create_connection, close_connection
from invSis import cargar_productos_por_lista

# FUNC CERRAR VENTANA
def cerrar_ventana(page):
    page.overlay.clear()
    page.update()

# FUNC CREAR VENTANA
def mostrar_ventana_b_prod(page, id_lista, actualizar_callback):
    productos = cargar_productos_por_lista(id_lista)

    ventana_x = 250
    ventana_y = 150

    # FUNC MOVER VENTANA
    def mover_ventana(event):
        nonlocal ventana_x, ventana_y
        ventana_x += event.delta_x
        ventana_y += event.delta_y
        ventana_movable.left = ventana_x
        ventana_movable.top = ventana_y
        page.update()

    # BOTON DE CONTINUAR
    btn_continuar = ft.ElevatedButton(
            "Continuar",
            icon=ft.Icons.ADD,
        )

    # DROPDOWN PRODUCTOS
    dropdown_productos = ft.Dropdown(
        label="SELECCIONA PRODUCTO",
        options=[ft.dropdown.Option(p["nombre"]) for p in productos],
        width=300,
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        color="black",
        border_radius=ft.border_radius.all(15),
    )

    # FUNCIÓN PARA ELIMINAR EL PRODUCTO SELECCIONADO
    def eliminar_producto_action(e):
        nombre_prod = dropdown_productos.value
        if not nombre_prod:
            return
        producto = next((p for p in productos if p["nombre"] == nombre_prod), None)
        if not producto:
            return
        id_producto = producto["id_producto"]
        from invSis import eliminar_producto_global
        exito = eliminar_producto_global(id_producto)
        if exito:
            nuevos_productos = cargar_productos_por_lista(id_lista)
            dropdown_productos.options = [ft.dropdown.Option(p["nombre"]) for p in nuevos_productos]
            dropdown_productos.value = None
            dropdown_productos.update()
            cerrar_ventana(page)
            if actualizar_callback:
                actualizar_callback()

    # CONTENIDO DE LA VENTANA
    ventana_contenido = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("BORRAR PRODUCTO", size=20, weight=ft.FontWeight.BOLD, color="black"),
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
                        ft.Text("BORRAR PRODUCTO", size=14, color="gray"),
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),

                dropdown_productos,
                
                ft.Row(
                    [
                        ft.ElevatedButton("Cancelar", icon=ft.Icons.CLOSE, on_click=lambda _: cerrar_ventana(page)),
                        ft.ElevatedButton("Continuar", icon=ft.Icons.DELETE, on_click=eliminar_producto_action),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=400,
        height=230,
        bgcolor="#FFD5BD",
        border_radius=10,
        border=ft.border.all(2, "black"),
        padding=20,
    )

    # GESTURE DETECTOR PARA MOVER LA VENTANA
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

    # AGREGAR LA VENTANA A LA PÁGINA
    page.overlay.append(ventana_stack)
    page.update()