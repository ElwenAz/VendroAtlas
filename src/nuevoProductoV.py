import flet as ft
from invSis import agregar_producto_a_lista

# FUNC CERRAR VENTANA
def cerrar_ventana(page):
    page.overlay.clear()
    page.update()

# FUNC CREAR VENTANA
def mostrar_ventana_n_producto(e, page, id_lista, actualizar_callback):
    page.overlay.clear()
    page.update()
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

    def agregar_producto_action(e):
        nombre = nombre_producto.value.strip()
        tipo = dropdown_tipo.value
        if not nombre or not tipo:
            print("Faltan datos")
            return

        if agregar_producto_a_lista(nombre, tipo, id_lista):
            print("Producto agregado correctamente")
            cerrar_ventana(page)
            actualizar_callback()
        else:
            print("Error al agregar el producto")


    # DROPDOWN DE CALIDAD/TIPO
    dropdown_tipo = ft.Dropdown(
        label="FRUTA/VERDURA",
        options=[
            ft.dropdown.Option("Fruta"),
            ft.dropdown.Option("Verdura"),
        ],
        value="Primera",
        width=300,
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        color="black",
        border_radius=ft.border_radius.all(15),
    )

    nombre_producto = ft.TextField(
                            label="NUEVO PRODUCTO",
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
                    content=ft.Text("NUEVO PRODUCTO", size=20, weight=ft.FontWeight.BOLD, color="black"),
                    bgcolor="#FAEDE2",
                    border_radius=10,
                    padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                    alignment=ft.alignment.center_left,
                ),

                # DIVIDER CON LA PALABRA "VENTA"
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                        ft.Text("NUEVO PRODUCTO", size=14, color="gray"),
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),

                # TEXTFIELD DE NOMBRE
                nombre_producto,

                # DROPDOWN DE TIPO
                dropdown_tipo,
                
                
                # BOTONES DE ACCION
                ft.Row(
                    [
                        ft.ElevatedButton("Cancelar", icon=ft.Icons.CLOSE, on_click=lambda _: cerrar_ventana(page)),
                        ft.ElevatedButton("Continuar", icon=ft.Icons.ADD, on_click=agregar_producto_action),
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