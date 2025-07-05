import flet as ft
from db_connection import create_connection, close_connection

def obtener_inventarios():
    connection = create_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_inventario, nombre, fecha_creacion FROM inventarios")
        inventarios = cursor.fetchall()
        return inventarios
    finally:
        close_connection(connection)

def obtener_vendedores():
    connection = create_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT nombre, id_inventario FROM usuarios WHERE id_tipo_usuario = 2")
        vendedores = cursor.fetchall()
        return vendedores
    finally:
        close_connection(connection)

def asignar_inventario_a_vendedor(nombre_vendedor, id_inventario):
    connection = create_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE usuarios SET id_inventario = %s WHERE nombre = %s",
            (id_inventario, nombre_vendedor)
        )
        connection.commit()
        return True
    finally:
        close_connection(connection)

def inventarios_view(page, regresar_callback):
    inventarios = obtener_inventarios()
    vendedores = obtener_vendedores()

    # Diccionario para los dropdowns (nombre actual asignado por inventario)
    asignaciones = {inv["id_inventario"]: None for inv in inventarios}
    for v in vendedores:
        if v["id_inventario"]:
            asignaciones[v["id_inventario"]] = v["nombre"]

    def on_asignar(e, id_inventario, dropdown):
        nombre_vendedor = dropdown.value
        if not nombre_vendedor:
            return
        if asignar_inventario_a_vendedor(nombre_vendedor, id_inventario):
            ft.SnackBar(ft.Text(f"Inventario asignado a {nombre_vendedor}")).open = True
            # Actualiza la vista
            page.views.clear()
            page.views.append(inventarios_view(page, regresar_callback))
            page.update()

    # Tabla de inventarios
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Fecha Creación")),
            ft.DataColumn(ft.Text("Asignar a vendedor")),
            ft.DataColumn(ft.Text("Acción")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(inv["id_inventario"]))),
                    ft.DataCell(ft.Text(inv["nombre"])),
                    ft.DataCell(ft.Text(inv["fecha_creacion"].strftime("%d/%m/%Y") if hasattr(inv["fecha_creacion"], "strftime") else str(inv["fecha_creacion"]))),
                    # --- AQUÍ: crea el dropdown como variable local
                    ft.DataCell(
                        dropdown := ft.Dropdown(
                            options=[ft.dropdown.Option(v["nombre"]) for v in vendedores],
                            value=asignaciones.get(inv["id_inventario"]),
                            width=180,
                        )
                    ),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Asignar",
                            icon=ft.icons.PERSON_ADD,
                            on_click=lambda e, inv_id=inv["id_inventario"], dd=dropdown: on_asignar(e, inv_id, dd)
                        )
                    ),
                ]
            )
            for inv in inventarios
        ]
    )

    banner = ft.Container(
        content=ft.Stack(
            [
                ft.Image(
                    src="src/assets/banner/bgBanner.png",
                    fit=ft.ImageFit.COVER,
                    width=page.width,
                    height=85,
                    expand=True,
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,  # Ícono de flecha hacia la izquierda
                        on_click=lambda _: regresar_callback(),  # Llama al callback para regresar
                    ),
                    bgcolor="#EAEBE8",
                    border_radius=ft.border_radius.all(5),
                    padding=5,
                    margin=ft.Margin(left=10, right=0, bottom=0, top=0),
                ),
                ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.9, "#426B1F"),
                    alignment=ft.alignment.center,
                    expand=True,
                    height=85,
                    margin=ft.margin.only(left=page.width * 0.75, right=0, top=0, bottom=0),
                    content=ft.Row(
                        [
                            ft.Image(
                                src="src/assets/banner/logo.png",
                                fit=ft.ImageFit.COVER,
                            ),
                            ft.Text(
                                "VendorAtlas",
                                color="#35172C",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                font_family="Neuton",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),
            ]
        ),
        bgcolor="transparent",
        margin=ft.Margin(bottom=15, left=0, right=0, top=0),
        height=85,
        alignment=ft.alignment.center,
        expand=True,
    )

    cuadro_main = ft.Container(
        bgcolor="#FAFAF5",
        border=ft.border.all(2, ft.colors.BLUE_GREY_100),
        padding=ft.padding.only(left=15, right=15, top=25, bottom=10),
        alignment=ft.alignment.center,
        border_radius=ft.border_radius.all(10),
        height=page.height - banner.height,
        width=page.width * 0.90,
        content=ft.Column([
            ft.Text("ASIGNACIÓN DE INVENTARIOS", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            tabla
        ])
    )

    return ft.View(
        "/inventarios",
        [banner, cuadro_main],
        bgcolor="#FAFAF5",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.START,
        padding=0,
    )