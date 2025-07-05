import flet as ft
from datetime import datetime, timedelta
from invSis import Inventario, Lista, Producto, Compra, Venta
from listaGui import lista_detalle
import invDueno
from ventaV import mostrar_ventana_venta
from compraV import mostrar_ventana_compra
from db_connection import create_connection, close_connection
from Grafica import main as grafica_main
from personal import main as personal_main

# CARGAR INV DE BASE DE DATOS
def cargar_inventarios():
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return []

    try:
        query = "SELECT id_inventario AS id, nombre FROM inventarios"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        inventarios = cursor.fetchall()
        return inventarios
    except Exception as ex:
        print(f"Error al cargar inventarios: {ex}")
        return []
    finally:
        close_connection(connection)

inventarios = cargar_inventarios()

# CARGAR LISTAS DE BASE DE DATOS
def cargar_listas_por_inventario(id_inventario):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return []

    try:
        query = """
            SELECT id_lista AS id, nombre_lista AS nombre, ultima_modificacion
            FROM listas
            WHERE id_inventario = %s
            ORDER BY ultima_modificacion DESC
        """
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (id_inventario,))
        listas = cursor.fetchall()
        return listas
    except Exception as ex:
        print(f"Error al cargar listas: {ex}")
        return []
    finally:
        close_connection(connection)

# CARGAR LISTA DE DESPERDICIO
def cargar_lista_desperdicio(id_inventario):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return None

    try:
        query = """
            SELECT id_lista AS id, nombre_lista AS nombre, ultima_modificacion
            FROM listas
            WHERE id_inventario = %s AND LOWER(nombre_lista) = 'desperdicio'
            LIMIT 1
        """
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (id_inventario,))
        lista = cursor.fetchone()
        return lista
    except Exception as ex:
        print(f"Error al cargar la lista de desperdicio: {ex}")
        return None
    finally:
        close_connection(connection)

# CREAR PRIMER INV POR DEFECTO
def crear_inventario_por_defecto():
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos para crear un inventario por defecto.")
        return
    try:
        query = "INSERT INTO inventarios (nombre) VALUES (%s)"
        cursor = connection.cursor()
        cursor.execute(query, ("Inventario 1",))
        connection.commit()
        id_inventario = cursor.lastrowid

        query_lista = "INSERT INTO listas (nombre_lista, id_inventario, ultima_modificacion) VALUES (%s, %s, NOW())"
        cursor.execute(query_lista, ("Desperdicio", id_inventario))
        connection.commit()

        print("Inventario por defecto y su lista de desperdicio creados exitosamente.")
    except Exception as ex:
        print(f"Error al crear el inventario por defecto: {ex}")
    finally:
        close_connection(connection)


def main(page: ft.Page, pLogin, usuario_logeado):
    page.views.clear()
    # CONFIG PRINCIPAL
    page.title = "VendorAtlas"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # ACTUALIZAR LISTAS SIN CAMBIAR DROPDOWN
    def actualizar_inventarios_y_listas():
        nonlocal inventarios, inventario_seleccionado
        inventarios = cargar_inventarios()
        inventario_seleccionado = obtener_inventario_mas_reciente(inventarios)
        dropdown.options = [
            ft.dropdown.Option(inv["nombre"])
            for inv in sorted(
                inventarios,
                key=lambda inv: max(
                    (lista["ultima_modificacion"] for lista in cargar_listas_por_inventario(inv["id"]) if lista["nombre"].lower() != "desperdicio"),
                    default=datetime.min
                ),
                reverse=True
            )[:3]
        ]
        dropdown.value = inventario_seleccionado["nombre"]
        dropdown.update()
        cargar_listas()
        page.update()

    # OBTENER EL INVENTARIO CON LA LISTA MÁS RECIENTE
    def obtener_inventario_mas_reciente(inventarios):
        inventarios_ordenados = sorted(
            inventarios,
            key=lambda inv: max(
                (lista["ultima_modificacion"] for lista in cargar_listas_por_inventario(inv["id"]) if lista["nombre"].lower() != "desperdicio"),
                default=datetime.min
            ),
            reverse=True
        )
        return inventarios_ordenados[0] if inventarios_ordenados else None

    # OBTENER EL INVENTARIO CON LA LISTA MÁS RECIENTE
    inventarios = cargar_inventarios()
    if not inventarios:
        print("No hay inventarios disponibles.")
        crear_inventario_por_defecto()
        inventarios = cargar_inventarios()

    inventario_seleccionado = obtener_inventario_mas_reciente(inventarios)
    listas = cargar_listas_por_inventario(inventario_seleccionado["id"])

    # FUNC PARA ACTUALIZAR LISTAS AL SELECCIONAR INVENTARIO
    def actualizar_listas(e):
        nonlocal inventario_seleccionado
        inventario_seleccionado = next(
            (inv for inv in inventarios if inv["nombre"] == dropdown.value), None
        )
        cargar_listas()

    # FUNCION PARA CARGAR LISTAS EN LA INTERFAZ
    def cargar_listas():
        lista_column.controls.clear()

        listas = cargar_listas_por_inventario(inventario_seleccionado["id"])
        if not listas:
            print(f"No hay listas disponibles para el inventario {inventario_seleccionado['nombre']}.")
            page.update()
            return

        listas_filtradas = [
            lista for lista in listas
            if lista["nombre"].lower() != "desperdicio" and not lista["nombre"].lower().startswith("desperdicio de ")
        ]

        for lista in listas_filtradas[:3]:

            lista_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(lista["nombre"], weight=ft.FontWeight.BOLD, color="black"),
                            ft.Text(
                                f"Última modificación: {lista['ultima_modificacion']}",
                                size=10,
                                color="black",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor="#D3E4CD" if lista == listas[0] else "#F0F0EF",
                    border=ft.border.all(2, "black") if lista == listas[0] else None,
                    padding=5,
                    border_radius=ft.border_radius.all(5),
                    margin=ft.Margin(bottom=3, top=0, left=0, right=0),
                    on_click=lambda e, l=lista: lista_detalle(page, l, actualizar_inventarios_y_listas),
                    on_hover=lambda e, l=lista: (
                        setattr(
                            e.control,
                            "bgcolor",
                            ft.Colors.BLUE_GREY_200 if e.data == "true" else (
                                "#D3E4CD" if l == listas[0] else "#F0F0EF"
                            )
                        ),
                        e.control.update()
                    ),
                )
            )

        # AGREGAR LA LISTA DE DESPERDICIO GENERAL AL FINAL
        lista_desperdicio = cargar_lista_desperdicio(inventario_seleccionado["id"])
        if lista_desperdicio:
            lista_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(lista_desperdicio["nombre"], weight=ft.FontWeight.BOLD, color="black"),
                            ft.Text(
                                f"Última modificación: {lista_desperdicio['ultima_modificacion']}",
                                size=10,
                                color="black",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor="#E5C6DB",
                    padding=5,
                    border_radius=ft.border_radius.all(5),
                    margin=ft.Margin(bottom=3, top=20, left=0, right=0),
                    on_click=lambda e, l=lista_desperdicio: lista_detalle(page, l, lambda: regresar_a_dueno_gui(page)),
                    on_hover=lambda e, l=lista_desperdicio: (
                        setattr(
                            e.control,
                            "bgcolor",
                            ft.Colors.RED_200 if e.data == "true" else "#E5C6DB"
                        ),
                        e.control.update()
                    ),
                )
            )

        page.update()

    # DROPDOWN PARA SELECCIONAR EL INVENTARIO
    dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option(inv["nombre"])
            for inv in sorted(
                inventarios,
                key=lambda inv: max(
                    (lista["ultima_modificacion"] for lista in cargar_listas_por_inventario(inv["id"]) if lista["nombre"].lower() != "desperdicio"),
                    default=datetime.min
                ),
                reverse=True
            )[:3]
        ],
        value=inventario_seleccionado["nombre"],
        width=page.width * 0.8,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        color="black",
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        on_change=actualizar_listas,
    )

    # CONTENEDOR DE LAS LISTAS
    lista_column = ft.Column(spacing=5)

    def cerrarSesion():
        pLogin()

    cerrar_sesion_btn = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.LOGOUT,
            on_click=lambda _: cerrarSesion(),
        ),
        bgcolor="#EAEBE8",
        border_radius=ft.border_radius.all(5),
        padding=5,
        margin=ft.Margin(left=10,right=0, bottom=0, top=0),
    )

    # BANNER
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
                content=ft.Row(
                    [cerrar_sesion_btn],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center_left,
                expand=True,
            ),
            ft.Container(
                bgcolor=ft.Colors.with_opacity(0.9, "#426B1F"),
                alignment=ft.alignment.center,
                expand=True,
                height=85,
                margin=ft.margin.only(left=page.width * 0.75, right=0, top=0, bottom=0),
                content= ft.Row(
                    [
                        ft.Image(
                            src="src/assets/banner/logo.png",
                            fit=ft.ImageFit.COVER,
                            #width=20,
                            #height=20,
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
        ]),
        bgcolor="blue", 
        margin= ft.Margin(bottom=15, left=0, right=0, top=0),
        height=85,
        alignment=ft.alignment.center,
        expand=True,
    )

    # RECTANGULOS TITULO LISTAS
    rec_listas = ft.Container(
        bgcolor = "#FBE0D0",
        height = 35,
        width = page.width * 0.90,
        border_radius = ft.border_radius.all(7),
        padding= ft.padding.only(left=10, right=10, top=0, bottom=0),
        margin= ft.Margin(bottom=0, left=0, right=0, top=0),
        alignment = ft.alignment.center,
        content= ft.Row(
            [ft.Text("LISTAS", size=20, weight=ft.FontWeight.BOLD, color="black")],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # BOTON DE COMPRA
    btn_compra = ft.Container(
        content=ft.Row(
            [
                ft.Image(
                    src="src/assets/btnIcons/addBtn.png",
                    width=20,
                    height=20,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Text("Compra", size=13, weight=ft.FontWeight.BOLD, color="black"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#E6E6E6",
        border_radius=ft.border_radius.all(5),
        padding=5,
        width=150,
        height=35,
        on_click=lambda e: mostrar_ventana_compra(
            e,
            page,
            sorted(
                inventarios,
                key=lambda inv: max(
                    (lista["ultima_modificacion"] for lista in cargar_listas_por_inventario(inv["id"]) if lista["nombre"].lower() != "desperdicio"),
                    default=datetime.min
                ),
                reverse=True
            )[:3],
            usuario_logeado,
            actualizar_inventarios_y_listas
        ),
        on_hover=lambda e: (
            setattr(e.control, "bgcolor", "#CCCCCC" if e.data == "true" else "#E6E6E6"),
            e.control.update(),
        ),
    )

    # BOTON DE VENTA
    btn_venta = ft.Container(
        content=ft.Row(
            [
                ft.Image(
                    src="src/assets/btnIcons/addBtn.png",
                    width=20,
                    height=20,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Text("Venta", size=13, weight=ft.FontWeight.BOLD, color="black"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#E6E6E6",
        border_radius=ft.border_radius.all(5),
        padding=5,
        width=150,
        height=35,
        on_click=lambda e: mostrar_ventana_venta(
            e,
            page,
            sorted(
                inventarios,
                key=lambda inv: max(
                    (lista["ultima_modificacion"] for lista in cargar_listas_por_inventario(inv["id"]) if lista["nombre"].lower() != "desperdicio"),
                    default=datetime.min
                ),
                reverse=True
            )[:3],
            actualizar_inventarios_y_listas,
            usuario_logeado
        ),
        on_hover=lambda e: (
            setattr(e.control, "bgcolor", "#CCCCCC" if e.data == "true" else "#E6E6E6"),
            e.control.update(),
        ),
    )


    filas_cv = ft.Row(
        [
            btn_compra,
            btn_venta,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=page.width * 0.90 * 0.45,
    )

        # RECTANGULOS TITULO ACCIONES
    rec_acciones = ft.Container(
        bgcolor = "#FBE0D0",
        height = 35,
        width = page.width * 0.90,
        border_radius = ft.border_radius.all(7),
        padding= ft.padding.only(left=10, right=10, top=0, bottom=0),
        margin= ft.Margin(bottom=10, left=0, right=0, top=20),
        alignment = ft.alignment.center,
        content= ft.Row(
            [ft.Text("ACCIONES", size=20, weight=ft.FontWeight.BOLD, color="black")],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # BOTON DE INVENTARIOS
    btn_inv = ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src="src/assets/btnIcons/invBtn.png",
                    width=55,
                    height=55,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Text("Inventarios", size=15, weight=ft.FontWeight.BOLD, color="black"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#A1D476",
        border_radius=ft.border_radius.all(5),
        padding=10,
        width=135,
        height=135,
        on_click=lambda _: invDueno.main(page, lambda: regresar_a_dueno_gui(page), inventarios, usuario_logeado),
        on_hover=lambda e: (
            setattr(e.control, "bgcolor", "#88B85E" if e.data == "true" else "#A1D476"),
            e.control.update(),
        ),
    )

    """FUNCION REGRESO"""
    # FUNCIÓN PARA REGRESAR A DUENOGUI
    def regresar_a_dueno_gui(page: ft.Page):
        # Limpiar las vistas acumuladas
        while len(page.views) > 1:
            page.views.pop()

        main(page, pLogin, usuario_logeado)
    """FUNCION REGRESO"""

    # BOTON DE PERSONAL
    btn_personal = ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src="src/assets/btnIcons/personalBtn.png",
                    width=55,
                    height=55,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Text("Personal", size=15, weight=ft.FontWeight.BOLD, color="black"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#E6E6E6",
        border_radius=ft.border_radius.all(5),
        padding=10,
        width=135,
        height=135,
        on_click=lambda _: personal_main(page, lambda: regresar_a_dueno_gui(page), usuario_logeado),
        on_hover=lambda e: (
            setattr(e.control, "bgcolor", "#CCCCCC" if e.data == "true" else "#E6E6E6"),
            e.control.update(),
        ),
    )

    # BOTON DE GANACIAS
    btn_ganancias = ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src="src/assets/btnIcons/gananciasBtn.png",
                    width=55,
                    height=55,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Text("Ganancias", size=15, weight=ft.FontWeight.BOLD, color="black"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#A1D476",
        border_radius=ft.border_radius.all(5),
        padding=10,
        width=135,
        height=135,
        on_click=lambda _: grafica_main(page, lambda: regresar_a_dueno_gui(page)),
        on_hover=lambda e: (
            setattr(e.control, "bgcolor", "#88B85E" if e.data == "true" else "#A1D476"),
            e.control.update(),
        ),
    )

    # BOTON DE CONECCIONES
    btn_conecciones = ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src="src/assets/btnIcons/coneccionesBtn.png",
                    width=55,
                    height=55,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Text("Conecciones", size=15, weight=ft.FontWeight.BOLD, color="black"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#E6E6E6",
        border_radius=ft.border_radius.all(5),
        padding=10,
        width=135,
        height=135,
        on_click=lambda _: print("conecciones"),
        on_hover=lambda e: (
            setattr(e.control, "bgcolor", "#CCCCCC" if e.data == "true" else "#E6E6E6"),
            e.control.update(),
        ),
    )

    # FILAS DE BOTONES
    filas_btn = ft.Row(
        [
            btn_inv,
            btn_personal,
            btn_ganancias,
            btn_conecciones
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=page.width * 0.90 * 0.10,
    )

    # CUADRO DE LISTAS
    cuadro_listas = ft.Container(
        bgcolor="#FFFFFF",
        #height=300,
        padding=ft.padding.only(left=10, right=10, top=5, bottom=10),
        margin=ft.Margin(bottom=8, left=0, right=0, top=0),
        width=page.width * 0.85,
        border_radius=ft.border_radius.only(bottom_left=7, bottom_right=7, top_left=0, top_right=0),
        alignment=ft.alignment.center,
        content=ft.Column(
            [
                # DROPDOWN
                ft.Row(
                    [dropdown],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                # lINEA DIVISORA
                ft.Divider(color="black", thickness=2, height=10),

                 # LISTAS
                 lista_column,
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.START,
        ),
    )


    # CUADRO DE CONTENIDO PRINCIPAL
    cuadro_main = ft.Container(
        bgcolor="#FAFAF5",
        border=ft.border.all(2, ft.Colors.BLUE_GREY_100),
        padding=ft.padding.only(left=15, right=15, top=25, bottom=10),
        alignment=ft.alignment.center,
        border_radius=ft.border_radius.all(10),
        height=page.height - banner.height,
        width=page.width * 0.90,

        content=ft.Column(
            [
                rec_listas,
                cuadro_listas,

                filas_cv,

                rec_acciones,
                filas_btn,
            ],
            spacing=0,
            alignment= ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # MANEJADOR DE RUTAS
    def route_change(event):
        route = event.route
        if route.startswith("/detalle/"):
            lista_nombre = route.split("/detalle/")[1]
            # Buscar la lista correspondiente al nombre
            listas = cargar_listas_por_inventario(inventario_seleccionado["id"])
            lista_seleccionada = next(
                (lista for lista in listas if lista["nombre"] == lista_nombre),
                None
            )
            if lista_seleccionada:
                lista_detalle(page, lista_seleccionada)
            else:
                print(f"Error: No se encontró la lista con el nombre '{lista_nombre}'")
        elif route == "/":
            # LIMPIAR VISTAS ACUMULADAS
            while len(page.views) > 1:
                page.views.pop()
            page.views.clear()

            cargar_listas()

            page.views.append(
                ft.View(
                    "/",
                    [banner, cuadro_main],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.MainAxisAlignment.START,
                    padding=0,
                )
            )
        page.update()

    page.on_route_change = route_change

    # AGREGAR VISTA PRINCIPAL
    page.views.append(
        ft.View(
            "/",
            [banner, cuadro_main],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.START,
            padding=0,
        )
    )

    # CARGAR LISTAS
    cargar_listas()
