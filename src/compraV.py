import flet as ft
from db_connection import create_connection, close_connection
from invSis import cargar_productos_por_lista, cargar_listas_por_inventario, sumar_kg_a_producto_lista, registrar_compra_bd

# FUNC VALIDAR ENTRADA DE SOLO NUMEROS Y UN SOLO PUNTO DECIMAL
def validar_numeros(e):
    valor = e.control.value
    if not valor.replace('.', '', 1).isdigit() or valor.count('.') > 1:
        e.control.value = ''.join(c for c in valor if c.isdigit() or c == '.')
        if e.control.value.count('.') > 1:
            e.control.value = e.control.value.replace('.', '', e.control.value.count('.') - 1)
        e.control.update()

# FUNC CERRAR VENTANA
def cerrar_ventana(page):
    page.overlay.clear()
    page.update()

# FUNC CREAR VENTANA
def mostrar_ventana_compra(e, page, inventarios, usuario_logeado, actualizar_callback=None):
    page.overlay.clear()
    page.update()

    productos = []

    ventana_x = 250
    ventana_y = 150

    def mover_ventana(event):
        nonlocal ventana_x, ventana_y
        ventana_x += event.delta_x
        ventana_y += event.delta_y
        ventana_movable.left = ventana_x
        ventana_movable.top = ventana_y
        page.update()

    # DROPDOWN DE PRODUCTOS
    dropdown_productos = ft.Dropdown(
        label="PRODUCTO",
        options=[],
        width=300,
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        color="black",
        border_radius=ft.border_radius.all(15),
    )

    # FUNC PARA ACTUALIZAR LOS PRODUCTOS SEGÚN EL INVENTARIO SELECCIONADO
    def actualizar_productos(e):
        nonlocal productos
        inventario_seleccionado = next(
            (inv for inv in inventarios if inv["nombre"] == dropdown_inventarios.value), None
        )
        if inventario_seleccionado:
            listas = cargar_listas_por_inventario(inventario_seleccionado["id"])
            lista_reciente = max(
                [lista for lista in listas if lista["nombre"].lower() != "desperdicio"],
                key=lambda lista: lista["ultima_modificacion"],
                default=None,
            )
            if lista_reciente:
                productos = cargar_productos_por_lista(lista_reciente["id"])
                dropdown_productos.options = [
                    ft.dropdown.Option(p["nombre"]) for p in productos
                ]
                dropdown_productos.value = dropdown_productos.options[0].key if dropdown_productos.options else None
                dropdown_productos.update()
            else:
                productos = []
                dropdown_productos.options = []
                dropdown_productos.value = None
                dropdown_productos.update()

    # DROPDOWN DE INVENTARIOS
    dropdown_inventarios = ft.Dropdown(
        label="INVENTARIO",
        options=[ft.dropdown.Option(inv["nombre"]) for inv in inventarios],
        value=inventarios[0]["nombre"] if inventarios else None,
        width=300,
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        color="black",
        border_radius=ft.border_radius.all(20),
        on_change=actualizar_productos,
    )

    # DROPDOWN DE CALIDAD/TIPO
    dropdown_calidad = ft.Dropdown(
        label="CALIDAD/TIPO",
        options=[
            ft.dropdown.Option("1ra"),
            ft.dropdown.Option("2da"),
            ft.dropdown.Option("3ra"),
        ],
        value="1ra",
        width=300,
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        color="black",
        border_radius=ft.border_radius.all(15),
    )

    # CAMPOS DE TEXTO PARA KILOS Y PRECIO/KILO
    textfield_kilos = ft.TextField(
        label="KILOS",
        width=140,
        bgcolor="#F0F0EF",
        border_color="#F0F0EF",
        border_radius=ft.border_radius.all(15),
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=validar_numeros,
    )
    textfield_precio = ft.TextField(
        label="PRECIO/KILO",
        width=140,
        bgcolor="#F0F0EF",
        border_color="#F0F0EF",
        border_radius=ft.border_radius.all(15),
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=validar_numeros,
    )

    # BOTON DE CONTINUAR
    continuar_btn = ft.ElevatedButton(
        "Continuar",
        icon=ft.Icons.ADD,
        on_click=None  # Se asigna después
    )

    # FUNC PARA REGISTRAR LA COMPRA
    def registrar_compra_action(e):
        # PARA DESACTIVAR BTN PARA EVITAR DUPLICACIONES
        continuar_btn.disabled = True
        continuar_btn.update()
        page.update()

        if not dropdown_inventarios.value or not dropdown_productos.value or not dropdown_calidad.value or not textfield_kilos.value or not textfield_precio.value:
            print("Por favor, completa todos los campos.")
            return

        inventario_seleccionado = next(
            (inv for inv in inventarios if inv["nombre"] == dropdown_inventarios.value), None
        )
        if not inventario_seleccionado:
            print("Inventario no encontrado.")
            return

        listas = cargar_listas_por_inventario(inventario_seleccionado["id"])
        lista_reciente = max(
            [lista for lista in listas if lista["nombre"].lower() != "desperdicio"],
            key=lambda lista: lista["ultima_modificacion"],
            default=None,
        )
        if not lista_reciente:
            print("No hay una lista reciente en el inventario seleccionado.")
            return

        producto_seleccionado = next(
            (p for p in productos if p["nombre"] == dropdown_productos.value), None
        )
        if not producto_seleccionado:
            print("Producto no encontrado.")
            return

        calidad = dropdown_calidad.value
        try:
            kg = float(textfield_kilos.value)
            precio_unitario = float(textfield_precio.value)
        except ValueError:
            print("Kilos o precio inválidos.")
            return

        exito_kg = sumar_kg_a_producto_lista(
            lista_reciente["id"],
            producto_seleccionado["id_producto"],
            calidad,
            kg
        )

        exito_compra = registrar_compra_bd(
            lista_reciente["id"],
            producto_seleccionado["id_producto"],
            calidad,
            kg,
            precio_unitario,
            usuario_logeado["nombre"]
        )

        if exito_kg and exito_compra:
            print(f"Compra registrada: {producto_seleccionado['nombre']}, {kg}kg, ${precio_unitario}/kg, {calidad}")
            cerrar_ventana(page)
            if actualizar_callback:
                actualizar_callback()
        else:
            print("Error al registrar la compra")

        # PARA DESACTIVAR BTN PARA EVITAR DUPLICACIONES
        def enable_btn():
            import time
            time.sleep(1)
            continuar_btn.disabled = False
            continuar_btn.update()
            page.update()
        page.run_task(enable_btn)

    continuar_btn.on_click = registrar_compra_action

    # CONTENIDO DE LA VENTANA
    ventana_contenido = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("COMPRA DE PRODUCTO", size=20, weight=ft.FontWeight.BOLD, color="black"),
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
                        ft.Text("COMPRA", size=14, color="gray"),
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                dropdown_inventarios,
                dropdown_productos,
                dropdown_calidad,
                ft.Row(
                    [
                        textfield_kilos,
                        textfield_precio,
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton("Cancelar", icon=ft.Icons.CLOSE, on_click=lambda _: cerrar_ventana(page)),
                        continuar_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=400,
        height=400,
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

    if inventarios:
        dropdown_inventarios.value = inventarios[0]["nombre"]
        actualizar_productos(None)