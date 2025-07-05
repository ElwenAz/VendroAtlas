import flet as ft
from invAsign import inventarios_view
from listVendedores import VendedoresView
from db_connection import create_connection, close_connection

# Compatibilidad con versiones antiguas de Flet
if not hasattr(ft, 'colors'):
    ft.colors = ft.Colors
if not hasattr(ft, 'icons'):
    ft.icons = ft.Icons

def main(page: ft.Page, regresar_callback, usuario_logeado):
    def obtener_vendedores():
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT nombre, 
                (SELECT descripcion FROM tipos_usuario WHERE id_tipo_usuario = usuarios.id_tipo_usuario) AS rol,
                DATE_FORMAT(fecha_creacion, '%d/%m/%Y') AS fecha_creacion,
                ultima_actividad,
                id_inventario
            FROM usuarios
            """
        )
        vendedores = cursor.fetchall()
        close_connection(connection)
        return vendedores
    
    def obtener_nombre_inventario(id_inventario):
        if not id_inventario or id_inventario == "-" or id_inventario is None:
            return "No asignado"
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT nombre FROM inventarios WHERE id_inventario = %s", (id_inventario,))
        inv = cursor.fetchone()
        close_connection(connection)
        return inv["nombre"] if inv else "No asignado"

    def obtener_primer_usuario():
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT nombre, 
                DATE_FORMAT(fecha_creacion, '%d/%m/%Y') AS fecha_creacion,
                ultima_actividad,
                id_inventario,
                (SELECT descripcion FROM tipos_usuario WHERE id_tipo_usuario = usuarios.id_tipo_usuario) AS rol
            FROM usuarios
            ORDER BY fecha_creacion ASC
            LIMIT 1
            """
        )
        user = cursor.fetchone()
        close_connection(connection)
        return user

    page.title = "VendorAtlas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.views.clear()

    def route_change(e):
        if page.route == "/inventarios":
            page.views.clear()
            page.views.append(inventarios_view(page, lambda: page.go("/plantilla")))
        elif page.route == "/plantilla":
            page.views.clear()
            page.views.append(main_view())
        elif page.route == "/vendedores":
            page.views.clear()
            usuario_actual = {
                "nombre": "SIMON EL SUGAR",
                "rol": "Administrador"
            }
            vendedores_view = VendedoresView(page, usuario_actual)
            page.views.append(vendedores_view())
        page.update()

    page.on_route_change = route_change

    def crear_banner():
        regresar_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda _: regresar_callback(),
            ),
            bgcolor=ft.colors.with_opacity(0.9, "#EAEBE8"),
            border_radius=ft.border_radius.all(5),
            padding=5,
            margin=ft.margin.only(left=10, right=0, bottom=0, top=0),
        )

        return ft.Container(
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
                        content=ft.Row(
                            [regresar_btn],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center_left,
                        expand=True,
                    ),
                    ft.Container(
                        bgcolor=ft.colors.with_opacity(0.9, "#426B1F"),
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
            margin=ft.margin.only(bottom=15),
            height=85,
            alignment=ft.alignment.center,
            expand=True,
        )

    def main_view():
        # Mostrar por defecto el usuario logeado si existe
        if usuario_logeado:
            user = {
                "nombre": usuario_logeado["nombre"],
                "fecha_creacion": usuario_logeado.get("fecha_creacion", "-"),
                "ultima_actividad": usuario_logeado.get("ultima_actividad", "-"),
                "id_inventario": usuario_logeado.get("id_inventario", "-"),
                "rol": usuario_logeado.get("rol", "-")
            }
        else:
            user = obtener_primer_usuario()
            if not user:
                user = {
                    "nombre": "Sin usuarios",
                    "fecha_creacion": "-",
                    "ultima_actividad": "-",
                    "id_inventario": "-",
                    "rol": "-"
                }

        nombre_usuario = user["nombre"]
        fecha_creacion = f"Creado: {user['fecha_creacion']}"
        ultima_actividad = f"Última actividad: {user['ultima_actividad'] or 'Sin actividad'}"
        inventario_nombre = obtener_nombre_inventario(user["id_inventario"])
        inventario_asignado = f"Inventario {inventario_nombre}"
        rol_usuario = user["rol"]

        perfil_nombre = ft.Text(
            nombre_usuario,
            size=32,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.BLUE_800
        )
        perfil_fecha = ft.Text(fecha_creacion, size=14, color=ft.colors.GREY_600)
        perfil_ultima = ft.Text(ultima_actividad, size=14, color=ft.colors.GREY_600)
        perfil_inventario = ft.Text(inventario_asignado, size=16)
        perfil_rol = ft.Text(rol_usuario, size=16)

        # Inicializa el historial con el usuario logeado o el primero
        columnas_historial = ["Fecha", "Tipo", "Producto", "Kilos", "Precio/kg", "Total", "Calidad"]
        def obtener_historial_usuario(nombre_usuario):
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT fecha, tipo, producto, cantidad_kg, precio_kg, total, calidad FROM (
                    SELECT 
                        c.fecha_compra AS fecha,
                        'Compra' AS tipo,
                        p.nombre AS producto,
                        c.cantidad_kg,
                        c.precio_kg,
                        c.total,
                        c.calidad
                    FROM compras c
                    JOIN productos p ON c.id_producto = p.id_producto
                    WHERE c.nombre_usuario = %s AND c.nombre_usuario != 'TRANSFERENCIA'
                    UNION ALL
                    SELECT 
                        v.fecha_venta AS fecha,
                        'Venta' AS tipo,
                        p.nombre AS producto,
                        v.cantidad_kg,
                        v.precio_kg,
                        v.total,
                        v.calidad
                    FROM ventas v
                    JOIN productos p ON v.id_producto = p.id_producto
                    WHERE v.nombre_usuario = %s
                ) AS historial
                ORDER BY fecha DESC
            """, (nombre_usuario, nombre_usuario))
            historial = cursor.fetchall()
            close_connection(connection)
            return historial

        # Crea la tabla de historial como objeto para poder actualizar sus filas
        historial = obtener_historial_usuario(nombre_usuario)
        filas_historial = []
        if historial:
            for h in historial:
                filas_historial.append([
                    h["fecha"].strftime("%d/%m/%Y") if hasattr(h["fecha"], "strftime") else str(h["fecha"]),
                    h["tipo"],
                    h["producto"],
                    f"{h['cantidad_kg']:.2f}",
                    f"${h['precio_kg']:.2f}",
                    f"${h['total']:.2f}",
                    h["calidad"]
                ])
        else:
            filas_historial.append(["-", "-", "-", "-", "-", "-", "-"])

        tabla_historial = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD)) for col in columnas_historial],
            rows=[
                ft.DataRow([ft.DataCell(ft.Text(item)) for item in fila])
                for fila in filas_historial
            ],
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
        )

        vendedores_bd = obtener_vendedores()

        def actualizar_perfil(nombre):
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT nombre, DATE_FORMAT(fecha_creacion, '%d/%m/%Y') AS fecha_creacion, ultima_actividad, id_inventario, (SELECT descripcion FROM tipos_usuario WHERE id_tipo_usuario = usuarios.id_tipo_usuario) AS rol FROM usuarios WHERE nombre = %s",
                (nombre,)
            )
            user = cursor.fetchone()
            close_connection(connection)
            if user:
                perfil_nombre.value = user["nombre"]
                perfil_fecha.value = f"Creado: {user['fecha_creacion']}"
                perfil_ultima.value = f"Última actividad: {user['ultima_actividad'] or 'Sin actividad'}"
                inventario_nombre = obtener_nombre_inventario(user["id_inventario"])
                perfil_inventario.value = f"{inventario_nombre}"
                perfil_rol.value = user["rol"]

                # Actualiza el historial del usuario seleccionado
                historial = obtener_historial_usuario(nombre)
                filas = []
                ultima_fecha = "-"
                if historial:
                    fechas = [h["fecha"] for h in historial if h["fecha"]]
                    if fechas:
                        from datetime import datetime
                        try:
                            fechas_dt = [datetime.strptime(f, "%Y-%m-%d %H:%M:%S") if isinstance(f, str) else f for f in fechas]
                            ultima_fecha = max(fechas_dt).strftime("%d/%m/%Y")
                        except Exception:
                            ultima_fecha = str(max(fechas))
                    for h in historial:
                        filas.append([
                            h["fecha"].strftime("%d/%m/%Y") if hasattr(h["fecha"], "strftime") else str(h["fecha"]),
                            h["tipo"],
                            h["producto"],
                            f"{h['cantidad_kg']:.2f}",
                            f"${h['precio_kg']:.2f}",
                            f"${h['total']:.2f}",
                            h["calidad"]
                        ])
                else:
                    filas.append(["-", "-", "-", "-", "-", "-", "-"])
                tabla_historial.rows = [
                    ft.DataRow([ft.DataCell(ft.Text(item)) for item in fila])
                    for fila in filas
                ]
                perfil_ultima.value = f"Última actividad: {ultima_fecha}"
                page.update()

        def fila_vendedor(v):
            subrayado = ft.Ref[ft.Text]()
            def on_hover(e):
                subrayado.current.style = ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE if e.data == "true" else None)
                page.update()
            return ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.GestureDetector(
                            content=ft.Text(
                                v["nombre"],
                                ref=subrayado,
                                color=ft.colors.BLUE_800
                            ),
                            on_tap=lambda e: actualizar_perfil(v["nombre"]),
                            on_hover=on_hover,
                            mouse_cursor="pointer",
                        )
                    ),
                    ft.DataCell(ft.Text(v["rol"]))
                ]
            )

        filas_vendedores = [fila_vendedor(v) for v in vendedores_bd if v["nombre"] != "TRANSFERENCIA"]

        tabla_historial_container = ft.Row(
            [tabla_historial],
            scroll=ft.ScrollMode.AUTO,
            width=700  # Ajusta el ancho según lo que necesites
        )

        seccion_vendedores = ft.Column(
            [
                ft.Text("LISTA DE VENDEDORES", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800),
                ft.Divider(height=10),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Rol", weight=ft.FontWeight.BOLD)),
                    ],
                    rows=filas_vendedores,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=10,
                    vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
                    horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
                ),
            ],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        seccion_perfil = ft.Column(
            [
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="INVENTARIOS",
                            icon=ft.icons.INVENTORY,
                            width=200,
                            height=50,
                            on_click=lambda e: page.go("/inventarios")
                        ),
                        ft.ElevatedButton(
                            text="VENDEDORES",
                            icon=ft.icons.PEOPLE,
                            width=200,
                            height=50,
                            on_click=lambda e: page.go("/vendedores")
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                ft.Divider(height=30, color=ft.colors.GREY_300),
                perfil_nombre,
                ft.Column(
                    [
                        perfil_fecha,
                        perfil_ultima,
                    ],
                    spacing=5,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Divider(height=20, color=ft.colors.GREY_300),
                ft.Row(
                    [
                        ft.Text("Inventario asignado:", size=16, weight=ft.FontWeight.BOLD),
                        perfil_inventario,
                    ],
                    spacing=10
                ),
                ft.Row(
                    [
                        ft.Text("Rol:", size=16, weight=ft.FontWeight.BOLD),
                        perfil_rol,
                    ],
                    spacing=10
                ),
                ft.Divider(height=30, color=ft.colors.GREY_300),
                tabla_historial_container
            ],
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        contenedor_principal = ft.Row(
            [
                ft.Container(
                    seccion_perfil,
                    padding=20,
                    expand=3,
                    border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.GREY_300))
                ),
                ft.Container(
                    seccion_vendedores,
                    padding=20,
                    expand=2
                )
            ],
            expand=True
        )

        cuadro_main = ft.Container(
            bgcolor="#FAFAF5",
            border=ft.border.all(2, ft.colors.BLUE_GREY_100),
            padding=ft.padding.only(left=15, right=15, top=25, bottom=10),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.all(10),
            height=page.height - 100,
            width=page.width * 0.90,
            content=contenedor_principal
        )

        return ft.View(
            "/plantilla",
            [crear_banner(), cuadro_main],
            bgcolor="#FAFAF5",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.START,
            padding=0,
        )
    
    page.views.append(main_view())
    page.update()