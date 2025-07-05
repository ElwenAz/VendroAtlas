import flet as ft
from nuevoProductoV import mostrar_ventana_n_producto
from invSis import cargar_productos_por_lista
from elprodV import mostrar_ventana_b_prod
from editarV import mostrar_ventana_e_producto

def lista_detalle(page: ft.Page, lista, regresar_callback):
  
    # LISTA DE DESPERDICIO POR LISTA
    def mostrar_desperdicio_lista(page, lista, regresar_callback):
        from invSis import cargar_lista_desperdicio_por_lista
        desperdicio = cargar_lista_desperdicio_por_lista(lista["id"])
        if desperdicio:
            lista_detalle(page, desperdicio, lambda: lista_detalle(page, lista, regresar_callback))
        else:
            print("No hay desperdicio para esta lista.")

    productos = cargar_productos_por_lista(lista["id"])

    # BOTÓN PARA REGRESAR A LA PANTALLA ANTERIOR
    regresar_btn = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda _: (page.views.pop(), page.update()),
        ),
        bgcolor="#EAEBE8",
        border_radius=ft.border_radius.all(5),
        padding=5,
        margin=ft.Margin(left=10, right=0, bottom=0, top=0),
    )

    # SEPARAR PRODUCTOS EN FRUTAS/VERDURAS
    frutas = [p for p in productos if p["tipo"].lower() == "fruta"]
    verduras = [p for p in productos if p["tipo"].lower() == "verdura"]

    # EXPANSIONLIST DE FRUTAS
    frutas_productos_panels = [
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
        for producto in frutas
    ]

    # EXPANSIONLIST DE VERDURAS
    verduras_productos_panels = [
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
        for producto in verduras
    ]

    # EXPANSIONPANEL PRINCIPAL DE FRUTAS
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
            controls=frutas_productos_panels
        ),
        bgcolor="#E0E8DE",
    )

    # EXPANSIONPANEL PRINCIPAL DE VERDURAS
    verduras_panel = ft.ExpansionPanel(
        header=ft.Container(
            content=ft.Text("Verduras", size=16, weight=ft.FontWeight.BOLD, color="black"),
            alignment=ft.alignment.center_left,
            padding=ft.Padding(left=10, right=0, top=0, bottom=0),
            height=40
        ),
        content=ft.ExpansionPanelList(
            expand=True,
            controls=verduras_productos_panels
        ),
        bgcolor="#E0E8DE",
    )

    panel_general = ft.ExpansionPanelList(
        expand=True,
        controls=[frutas_panel, verduras_panel]
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
                        [regresar_btn],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center_left,
                    expand=True,
                ),
            ]
        ),
        bgcolor="blue",
        margin=ft.Margin(bottom=15, left=0, right=0, top=0),
        height=85,
        alignment=ft.alignment.center,
        expand=True,
    )

    controls_cm = [
        panel_general,
    ]

    scrollable_content = ft.Container(
        content=ft.ListView(
            controls=controls_cm,
            spacing=10,
            expand=True,
            padding=0,
            auto_scroll=False,
        ),
        expand=True,
        bgcolor=None,
    )

    main_controls = [
        ft.Text(f"Productos en la lista: {lista['nombre']}", size=20, weight=ft.FontWeight.BOLD),
        scrollable_content,
        ft.Container(
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
            on_click=lambda e: mostrar_desperdicio_lista(page, lista, regresar_callback),
            on_hover=lambda e: (
                setattr(
                    e.control,
                    "bgcolor",
                    ft.Colors.RED_200 if e.data == "true" else "#E5C6DB"
                ),
                e.control.update()
            ),
        ) if not lista["nombre"].lower().startswith("desperdicio") else None,
        ft.Row(
            [
                ft.ElevatedButton(
                    text="Nuevo producto",
                    icon=ft.Icons.ADD,
                    bgcolor="#E6E6E6",
                    color="black",
                    on_click=lambda e: mostrar_ventana_n_producto(
                        e, page, lista["id"], lambda: (
                            regresar_callback(),
                            lista_detalle(page, lista, regresar_callback)
                        )
                    ),
                ),
                ft.ElevatedButton(
                    text="Editar",
                    icon=ft.Icons.EDIT,
                    bgcolor="#E6E6E6",
                    color="black",
                    on_click=lambda e: mostrar_ventana_e_producto(
                        e, page, lista["id"], lambda: lista_detalle(page, lista, regresar_callback)
                    ),
                ),
                ft.ElevatedButton(
                    text="Eliminar producto",
                    icon=ft.Icons.DELETE,
                    bgcolor="#E6E6E6",
                    color="black",
                    on_click=lambda e: mostrar_ventana_b_prod(
                        page,
                        lista["id"],  # id de la lista actual
                        lambda: lista_detalle(page, lista, regresar_callback)  # recarga el detalle
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=50,
        ),
    ]

    # FILTRAR CONTROLES NULOS PARA EVITAR ERRORES
    main_controls = [c for c in main_controls if c is not None]


    # CUADRO PRINCIPAL
    cuadro_main = ft.Container(
        bgcolor="#FAFAF5",
        border=ft.border.all(2, ft.Colors.BLUE_GREY_100),
        padding=ft.padding.only(left=15, right=15, top=25, bottom=10),
        alignment=ft.alignment.center,
        border_radius=ft.border_radius.all(10),
        height=page.height - banner.height,
        width=page.width * 0.90,
        content=ft.Column(
            main_controls,
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # CERRAR DETALLES DE LISTA
    detalle_view = ft.View(
        f"/detalle/{lista['nombre']}",
        [
            banner,
            cuadro_main,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.START,
        padding=0,
    )

    # AGREGAR VISTA A LA PÁGINA
    if page.views and page.views[-1].route.startswith("/detalle/"):
        page.views.pop()
    page.views.append(detalle_view)
    page.update()