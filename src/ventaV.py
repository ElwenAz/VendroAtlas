import flet as ft
from invSis import registrar_venta_bd, obtener_stock_producto_lista, cargar_productos_por_lista, cargar_listas_por_inventario, obtener_stock_producto_lista

# FUNC VALIDAR ENTRADA DE SOLO NUMEROS Y UN SOLO PUNTO DECIMAL
def validar_numeros(e):
    valor = e.control.value
    # Permitir solo dígitos y un único punto decimal
    if not valor.replace('.', '', 1).isdigit() or valor.count('.') > 1:
        # Filtrar caracteres no válidos y limitar a un solo punto decimal
        e.control.value = ''.join(c for c in valor if c.isdigit() or c == '.')
        if e.control.value.count('.') > 1:
            e.control.value = e.control.value.replace('.', '', e.control.value.count('.') - 1)
        e.control.update()

# FUNC CERRAR VENTANA
def cerrar_ventana(page):
    page.overlay.clear()
    page.update()

# FUNC CREAR VENTANA
def mostrar_ventana_venta(e, page, inventarios, actualizar_callback=None, usuario_logeado=None):
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

    def registrar_venta_action(e):
        inventario_nombre = dropdown_inventarios.value
        producto_nombre = dropdown_productos.value
        calidad = dropdown_calidad.value
        kilos = textfield_kilos.value
        precio_unitario = textfield_precio.value

        if not inventario_nombre or not producto_nombre or not calidad or not kilos or not precio_unitario:
            print("Por favor, completa todos los campos.")
            return

        try:
            kg = float(kilos)
            precio = float(precio_unitario)
        except ValueError:
            print("Kilos o precio inválidos.")
            return

        inventario = next((inv for inv in inventarios if inv["nombre"] == inventario_nombre), None)
        if not inventario:
            print("Inventario no encontrado.")
            return

        listas = cargar_listas_por_inventario(inventario["id"])
        lista_reciente = max(
            [lista for lista in listas if lista["nombre"].lower() != "desperdicio"],
            key=lambda lista: lista["ultima_modificacion"],
            default=None,
        )
        if not lista_reciente:
            print("No hay lista reciente.")
            return

        productos = cargar_productos_por_lista(lista_reciente["id"])
        producto = next((p for p in productos if p["nombre"] == producto_nombre), None)
        if not producto:
            print("Producto no encontrado.")
            return

        stock_disponible = obtener_stock_producto_lista(lista_reciente["id"], producto["id_producto"], calidad)
        if stock_disponible <= 0:
            mensaje_error.value = "No hay stock disponible para este producto y calidad."
            mensaje_error.update()
            return
        if kg <= 0:
            mensaje_error.value = "Debes ingresar una cantidad mayor a 0 kg."
            mensaje_error.update()
            return
        if kg > stock_disponible:
            mensaje_error.value = f"No puedes vender más de lo disponible ({stock_disponible} kg)."
            mensaje_error.update()
            return

        exito = registrar_venta_bd(lista_reciente["id"], producto["id_producto"], calidad, kg, precio, usuario_logeado["nombre"])
        if exito:
            print("Venta registrada correctamente.")
            cerrar_ventana(page)
            if actualizar_callback:
                actualizar_callback()
        else:
            mensaje_error.value = "Error al registrar la venta."
            mensaje_error.update()

    # MENSAJE ERROR
    mensaje_error = ft.Text("", color="red", size=14)

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

    # FUNC PARA ACTUALIZAR LOS PRODUCTOS SEGÚN EL INVENTARIO SELECCIONADO
    def actualizar_productos(e):
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

    # CONTENIDO DE LA VENTANA
    ventana_contenido = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("VENTA DE PRODUCTO", size=20, weight=ft.FontWeight.BOLD, color="black"),
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
                        ft.Text("VENTA", size=14, color="gray"),
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                
                # DROPDOWN DE INVENTARIOS
                dropdown_inventarios,

                # DROPDOWN DE CALIDAD/TIPO
                dropdown_calidad,
                
                # DROPDOWN DE PRODUCTOS
                dropdown_productos,
                
                # KILOS Y PRECIO/KILO
                ft.Row(
                    [
                        textfield_kilos,
                        textfield_precio,
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                # MENSAJE DE ERROR
                mensaje_error,
                
                # BOTONES DE ACCION
                ft.Row(
                    [
                        ft.ElevatedButton("Cancelar", icon=ft.Icons.CLOSE, on_click=lambda _: cerrar_ventana(page)),
                        ft.ElevatedButton("Continuar", icon=ft.Icons.ADD, on_click=registrar_venta_action),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=400,
        height=420,
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

    # ACTUALIZAR LOS PRODUCTOS INICIALMENTE (después de agregar el dropdown a la página)
    actualizar_productos(None)