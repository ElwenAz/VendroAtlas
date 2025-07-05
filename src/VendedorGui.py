import flet as ft
from flet import MainAxisAlignment, CrossAxisAlignment, Colors
from invSis import cargar_listas_por_inventario, cargar_productos_por_lista
from invSis import cargar_lista_desperdicio_por_lista
from listaGui import lista_detalle

from nuevoProductoV import mostrar_ventana_n_producto
from compraV import mostrar_ventana_compra
from elprodV import mostrar_ventana_b_prod
from ventaV import mostrar_ventana_venta

def main(page: ft.Page, pLogin, usuario_logeado):
    page.title = "Panel de Vendedor"
    page.views.clear()
    page.theme_mode = ft.ThemeMode.LIGHT

    """FUNCION REGRESO"""
    # FUNCIÓN PARA REGRESAR A DUENOGUI
    def regresar_a_dueno_gui(page: ft.Page):
        # Limpiar las vistas acumuladas
        while len(page.views) > 1:
            page.views.pop()

        main(page, pLogin, usuario_logeado)
    """FUNCION REGRESO"""


    def panel_lista_vendedor(page, lista):
        productos = cargar_productos_por_lista(lista["id"])
        frutas = [p for p in productos if p["tipo"].lower() == "fruta"]
        verduras = [p for p in productos if p["tipo"].lower() == "verdura"]

        def paneles(productos):
            return [
                ft.ExpansionPanel(
                    header=ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(producto["nombre"], weight=ft.FontWeight.BOLD, color="black"),
                                    width=120,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        f"{sum([float(producto.get('kg_c1', 0) or 0), float(producto.get('kg_c2', 0) or 0), float(producto.get('kg_c3', 0) or 0)])} kg",
                                        size=12,
                                        color="black"
                                    ),
                                    bgcolor="#FFFFFF",
                                    border_radius=ft.border_radius.all(5),
                                    padding=ft.Padding(left=10, right=10, top=2, bottom=2),
                                    margin=ft.Margin(left=10, right=0, top=0, bottom=0),
                                    width=80,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Container(
                                    content=ft.Text("Días restantes", size=12, color="black"),
                                    bgcolor="#FFFFFF",
                                    border_radius=ft.border_radius.all(5),
                                    padding=ft.Padding(left=10, right=10, top=2, bottom=2),
                                    margin=ft.Margin(left=10, right=0, top=0, bottom=0),
                                    width=100,
                                    alignment=ft.alignment.center,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        alignment=ft.alignment.center_left,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text("C1", size=14, color="black"),
                                        width=120,
                                        padding=ft.Padding(left=20, right=0, top=0, bottom=0),
                                    ),
                                    ft.Container(
                                        content=ft.Text(f"{producto.get('kg_c1', '0')}kg", size=14, color="black"),
                                        bgcolor="#F5F5F5",
                                        border_radius=ft.border_radius.all(5),
                                        padding=ft.Padding(left=10, right=10, top=2, bottom=2),
                                        margin=ft.Margin(left=20, right=0, top=0, bottom=0),
                                        width=80,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(
                                        content=ft.Text(f"{producto.get('dias_c1', '0')}", size=14, color="black"),
                                        bgcolor="#F5F5F5",
                                        border_radius=ft.border_radius.all(5),
                                        padding=ft.Padding(left=10, right=10, top=2, bottom=2),
                                        margin=ft.Margin(left=10, right=55, top=0, bottom=0),
                                        width=100,
                                        alignment=ft.alignment.center,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(
                                content=ft.Divider(height=1, thickness=1, color=ft.Colors.BLACK26),
                                padding=ft.Padding(left=15, right=15, top=5, bottom=5),
                            ),
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text("C2", size=14, color="black"),
                                        width=120,
                                        padding=ft.Padding(left=20, right=0, top=0, bottom=0),
                                    ),
                                    ft.Container(
                                        content=ft.Text(f"{producto.get('kg_c2', '0')}kg", size=14, color="black"),
                                        bgcolor="#F5F5F5",
                                        border_radius=ft.border_radius.all(5),
                                        padding=ft.Padding(left=10, right=10, top=2, bottom=2),
                                        margin=ft.Margin(left=20, right=0, top=0, bottom=0),
                                        width=80,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(
                                        content=ft.Text(f"{producto.get('dias_c2', '0')}", size=14, color="black"),
                                        bgcolor="#F5F5F5",
                                        border_radius=ft.border_radius.all(5),
                                        padding=ft.Padding(left=10, right=10, top=2, bottom=2),
                                        margin=ft.Margin(left=10, right=55, top=0, bottom=0),
                                        width=100,
                                        alignment=ft.alignment.center,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(
                                content=ft.Divider(height=1, thickness=1, color=ft.Colors.BLACK26),
                                padding=ft.Padding(left=15, right=15, top=5, bottom=5),
                            ),
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text("C3", size=14, color="black"),
                                        width=120,
                                        padding=ft.Padding(left=20, right=0, top=0, bottom=7),
                                    ),
                                    ft.Container(
                                        content=ft.Text(f"{producto.get('kg_c3', '0')}kg", size=14, color="black"),
                                        bgcolor="#F5F5F5",
                                        border_radius=ft.border_radius.all(5),
                                        padding=ft.Padding(left=10, right=10, top=2, bottom=7),
                                        margin=ft.Margin(left=20, right=0, top=0, bottom=0),
                                        width=80,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(
                                        content=ft.Text(f"{producto.get('dias_c3', '0')}", size=14, color="black"),
                                        bgcolor="#F5F5F5",
                                        border_radius=ft.border_radius.all(5),
                                        padding=ft.Padding(left=10, right=10, top=2, bottom=7),
                                        margin=ft.Margin(left=10, right=55, top=0, bottom=0),
                                        width=100,
                                        alignment=ft.alignment.center,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=5,
                    ),
                    bgcolor="#F6F6F6"
                )
                for producto in productos
            ]

        frutas_panel = ft.ExpansionPanel(
            header=ft.Container(
                content=ft.Text("Frutas", size=16, weight=ft.FontWeight.BOLD, color="black"),
                alignment=ft.alignment.center_left,
                padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                height=40,
                bgcolor="#E0E8DE",
            ),
            content=ft.ExpansionPanelList(
                expand=True,
                controls=paneles(frutas)
            ),
            bgcolor="#E0E8DE",
        )
        verduras_panel = ft.ExpansionPanel(
            header=ft.Container(
                content=ft.Text("Verduras", size=16, weight=ft.FontWeight.BOLD, color="black"),
                alignment=ft.alignment.center_left,
                padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                height=40
            ),
            content=ft.ExpansionPanelList(
                expand=True,
                controls=paneles(verduras)
            ),
            bgcolor="#E0E8DE",
        )

        panel_general = ft.ExpansionPanelList(
            expand=True,
            controls=[frutas_panel, verduras_panel]
        )

        # --- DESPERDICIO ---
        desperdicio = cargar_lista_desperdicio_por_lista(lista["id"])
        desperdicio_control = None
        if desperdicio:
            def mostrar_desperdicio_lista(e):
                # Usa la misma interfaz que el dueño: lista_detalle
                page.views.append(
                    lista_detalle(
                        page,
                        desperdicio,
                        lambda: regresar_a_dueno_gui(page)
                    )
                )
                page.update()

            desperdicio_control = ft.Container(
                content=ft.Row(
                    [
                        ft.Text("Desperdicio", weight=ft.FontWeight.BOLD, color="black"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor="#E5C6DB",
                padding=5,
                border_radius=ft.border_radius.all(5),
                margin=ft.Margin(bottom=3, top=20, left=0, right=0),
                on_click=mostrar_desperdicio_lista,
                on_hover=lambda e: (
                    setattr(
                        e.control,
                        "bgcolor",
                        ft.Colors.RED_200 if e.data == "true" else "#E5C6DB"
                    ),
                    e.control.update()
                ),
            )

        paneles_finales = [panel_general]
        if desperdicio_control:
            paneles_finales.append(desperdicio_control)

        return ft.Container(
            content=ft.Column(paneles_finales, spacing=0, scroll=ft.ScrollMode.AUTO),
            expand=True,
            bgcolor=None,
            padding=0,
        )


    # BOTÓN CERRAR SESIÓN
    def cerrar_sesion():
        pLogin()

    cerrar_sesion_btn = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.LOGOUT,
            on_click=lambda _: cerrar_sesion(),
        ),
        bgcolor="#EAEBE8",
        border_radius=ft.border_radius.all(5),
        padding=5,
        margin=ft.Margin(left=10, right=0, bottom=0, top=0),
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

    acciones_grid = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.ADD, size=50, color="black"),
                                ft.Text("Nuevo\nProducto", size=17, weight=ft.FontWeight.BOLD, color="black", text_align=ft.TextAlign.CENTER),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        bgcolor="#A1D476",
                        on_hover=lambda e: (
                            setattr(e.control, "bgcolor", "#88B85E" if e.data == "true" else "#A1D476"),
                            e.control.update(),
                        ),
                        border_radius=ft.border_radius.all(14),
                        padding=20,
                        width=150,
                        height=160,
                        alignment=ft.alignment.center,
                        on_click=lambda e: mostrar_ventana_n_producto(
                            e, page, lista_mas_reciente["id"], lambda: main(page, pLogin, usuario_logeado)
                        ),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.SHOPPING_CART, size=50, color="black"),
                                ft.Text("Añadir\nCompra", size=17, weight=ft.FontWeight.BOLD, color="black", text_align=ft.TextAlign.CENTER),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        bgcolor="#E6E6E6",
                        on_hover=lambda e: (
                            setattr(e.control, "bgcolor", "#CCCCCC" if e.data == "true" else "#E6E6E6"),
                            e.control.update(),
                        ),
                        border_radius=ft.border_radius.all(14),
                        padding=20,
                        width=150,
                        height=160,
                        alignment=ft.alignment.center,
                        on_click=lambda e: mostrar_ventana_compra(
                            e, page, [{"id": usuario_logeado["id_inventario"], "nombre": "Mi inventario"}], usuario_logeado, lambda: main(page, pLogin, usuario_logeado)
                        ),
                    ),
                ],
                spacing=30,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.DELETE, size=50, color="black"),
                                ft.Text("Eliminar\nProducto", size=17, weight=ft.FontWeight.BOLD, color="black", text_align=ft.TextAlign.CENTER),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        bgcolor="#E6E6E6",
                        on_hover=lambda e: (
                            setattr(e.control, "bgcolor", "#CCCCCC" if e.data == "true" else "#E6E6E6"),
                            e.control.update(),
                        ),
                        border_radius=ft.border_radius.all(14),
                        padding=20,
                        width=150,
                        height=160,
                        alignment=ft.alignment.center,
                        on_click=lambda e: mostrar_ventana_b_prod(
                            page, lista_mas_reciente["id"], lambda: main(page, pLogin, usuario_logeado)
                        ),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.ATTACH_MONEY, size=50, color="black"),
                                ft.Text("Añadir\nVenta", size=17, weight=ft.FontWeight.BOLD, color="black", text_align=ft.TextAlign.CENTER),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        bgcolor="#A1D476",
                        on_hover=lambda e: (
                            setattr(e.control, "bgcolor", "#88B85E" if e.data == "true" else "#A1D476"),
                            e.control.update(),
                        ),
                        border_radius=ft.border_radius.all(14),
                        padding=20,
                        width=150,
                        height=160,
                        alignment=ft.alignment.center,
                        on_click=lambda e: mostrar_ventana_venta(
                            e, page, [{"id": usuario_logeado["id_inventario"], "nombre": "Mi inventario"}], lambda: main(page, pLogin, usuario_logeado), usuario_logeado
                        ),
                    ),
                ],
                spacing=30,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=30,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    acciones_titulo = ft.Container(
        ft.Text("ACCIONES", size=18, weight=ft.FontWeight.BOLD, color="black"),
        bgcolor="#FBE0D0",
        border_radius=ft.border_radius.all(7),
        padding=ft.padding.only(left=20, right=20, top=4, bottom=4),
        alignment=ft.alignment.top_left,
        width=400,
        margin=ft.margin.only(top=0, left=0, right=10, bottom=0),
    )

    acciones_card = ft.Container(
        content=ft.Column(
            [
                acciones_grid,
            ],
            spacing=30,
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
        bgcolor="white",
        border_radius=ft.border_radius.only(bottom_left=7, bottom_right=7, top_left=0, top_right=0),
        padding=ft.padding.only(left=10, right=10, top=25, bottom=25),
        margin=ft.margin.only(top=0, left=0, right=10, bottom=0),
        width=350,
        alignment=ft.alignment.top_center,
        #shadow=ft.BoxShadow(blur_radius=18, color="#e0e0e0", offset=ft.Offset(0, 4)),
    )

    inventario_titulo = ft.Container(
        ft.Text("INVENTARIO", size=18, weight=ft.FontWeight.BOLD, color="black"),
        bgcolor="#FBE0D0",
        border_radius=ft.border_radius.all(7),
        padding=ft.padding.only(left=20, right=20, top=4, bottom=4),
        alignment=ft.alignment.top_left,
        width=650,
        margin=ft.margin.only(top=0, left=0, right=10, bottom=0),
    )

    id_inventario = usuario_logeado.get("id_inventario")
    lista_mas_reciente = None
    if id_inventario:
        listas = cargar_listas_por_inventario(id_inventario)
        listas = [l for l in listas if not l["nombre"].lower().startswith("desperdicio")]
        if listas:
            listas.sort(key=lambda l: l["ultima_modificacion"], reverse=True)
            lista_mas_reciente = listas[0]

    inventario_card = ft.Container(
        content=panel_lista_vendedor(page, lista_mas_reciente) if lista_mas_reciente else ft.Text("No hay listas en tu inventario."),
        bgcolor="white",
        border_radius=ft.border_radius.only(bottom_left=7, bottom_right=7, top_left=0, top_right=0),
        padding=ft.padding.only(left=10, right=10, top=25, bottom=25),
        margin=ft.margin.only(top=0, left=0, right=10, bottom=0),
        width=600,
        alignment=ft.alignment.top_center,
    )

    # CUADRO PRINCIPAL VACÍO
    cuadro_main = ft.Container(
        bgcolor="#FAFAF5",
        border=ft.border.all(2, ft.Colors.BLUE_GREY_100),
        padding=ft.padding.only(left=15, right=15, top=25, bottom=10),
        alignment=ft.alignment.center,
        border_radius=ft.border_radius.all(10),
        height=page.height - banner.height,
        width=page.width * 0.90,
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            inventario_titulo,
                            inventario_card,
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    expand=3,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            acciones_titulo,
                            acciones_card,
                        ],
                        spacing=0,
                        alignment= ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    expand=2,
                ),
            ],
            expand=True,
        )
    )

    page.views.append(
        ft.View(
            "/vendedor",
            [banner, cuadro_main],
            bgcolor="#FAFAF5",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.START,
            padding=0,
        )
    )
    page.update()