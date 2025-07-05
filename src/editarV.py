import flet as ft
from invSis import actualizar_nombre_producto, cargar_productos_por_lista

# FUNC CERRAR VENTANA
def cerrar_ventana(page):
    page.overlay.clear()
    page.update()

# FUNC CREAR VENTANA
def mostrar_ventana_e_producto(e, page, id_lista, actualizar_callback):
    page.overlay.clear()
    page.update()
    ventana_x = 250
    ventana_y = 150

    productos = cargar_productos_por_lista(id_lista)

    # FUNC MOVER VENTANA
    def mover_ventana(event):
        nonlocal ventana_x, ventana_y
        ventana_x += event.delta_x
        ventana_y += event.delta_y
        ventana_movable.left = ventana_x
        ventana_movable.top = ventana_y
        page.update()

    def editar_producto_action(e):
        nombre_prod = dropdown_productos.value
        nuevo_nombre = nombre_producto.value.strip()
        if not nombre_prod or not nuevo_nombre:
            return
        producto = next((p for p in productos if p["nombre"] == nombre_prod), None)
        if not producto:
            return
        id_producto = producto["id_producto"]
        exito = actualizar_nombre_producto(id_producto, nuevo_nombre)
        if exito:
            cerrar_ventana(page)
            if actualizar_callback:
                actualizar_callback()


    # DROPDOWN DE CALIDAD/TIPO
    dropdown_productos = ft.Dropdown(
        label="SELECCIONA PRODUCTO",
        options=[ft.dropdown.Option(p["nombre"]) for p in productos],
        value="Primera",
        width=300,
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        color="black",
        border_radius=ft.border_radius.all(15),
    )

    nombre_producto = ft.TextField(
                            label="NUEVO NOMBRE",
                            bgcolor="#F0F0EF",
                            border_color="#F0F0EF",
                            border_radius=ft.border_radius.all(15),
    )

    # CONTENIDO DE LA VENTANA
    ventana_contenido = ft.Container(
        content=ft.Column(
            [
                # TITULO
                ft.Container(
                    content=ft.Text("EDITAR PRODUCTO", size=20, weight=ft.FontWeight.BOLD, color="black"),
                    bgcolor="#FAEDE2",
                    border_radius=10,
                    padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                    alignment=ft.alignment.center_left,
                ),

                # DIVIDER
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                        ft.Text("EDITAR PRODUCTO", size=14, color="gray"),
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),

                # DROPDOWN DE TIPO
                dropdown_productos,

                # TEXTFIELD DE NOMBRE
                nombre_producto,
                
                
                # BOTONES DE ACCION
                ft.Row(
                    [
                        ft.ElevatedButton("Cancelar", icon=ft.Icons.CLOSE, on_click=lambda _: cerrar_ventana(page)),
                        ft.ElevatedButton("Continuar", icon=ft.Icons.ADD, on_click=editar_producto_action),
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