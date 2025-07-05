import flet as ft
from datetime import datetime
from listaGui import lista_detalle  # Importar lista_detalle
from invSis import cargar_listas_por_inventario, cargar_inventarios
from nuevaListaV import mostrar_ventana_n_lista
from nuevoInvV import mostrar_ventana_n_inv
from invSis import cargar_lista_desperdicio
from editarListaV import mostrar_ventana_e_lista
from borrar_lista import mostrar_ventana_borrar_lista

def main(page: ft.Page, regresar_callback, inventarios, usuario_logeado):
    # EL INVENTARIO INICIAL
    inventario_seleccionado = None

    # FUNC PARA ACTUALIZAR LISTAS AL SELECCIONAR INVENTARIO
    def actualizar_listas(e):
        nonlocal inventario_seleccionado
        inventario_seleccionado = next(
            (inv for inv in inventarios if inv["nombre"] == dropdown.value), None
        )
        cargar_listas()

    # FUNCION PARA CARGAR TODAS LAS LISTAS EN LA INTERFAZ
    def cargar_listas():
        lista_column.controls.clear()

        # OBTENER LAS LISTAS DEL INVENTARIO SELECCIONADO DESDE LA BASE DE DATOS
        listas = cargar_listas_por_inventario(inventario_seleccionado["id"])
        if not listas:
            print(f"No hay listas disponibles para el inventario {inventario_seleccionado['nombre']}.")
            page.update()
            return

        # AGREGAR LAS LISTAS MÁS RECIENTES (EXCLUYENDO "DESPERDICIO" Y "DESPERDICIO DE ...")
        for lista in listas:
            nombre = lista["nombre"].lower()
            if nombre == "desperdicio" or nombre.startswith("desperdicio de "):
                continue 
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
                    on_click=lambda e, l=lista: abrir_lista_detalle(l),
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
                    on_click=lambda e, l=lista_desperdicio: abrir_lista_detalle(l),
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

    # FUNCION PARA ABRIR LA PANTALLA DE DETALLE DE UNA LISTA
        def abrir_lista_detalle(lista):
            # Llama a la función lista_detalle de listaGui.py
            lista_detalle(page, lista, cargar_listas)

    # FUNCIÓN PARA ACTUALIZAR EL DROPDOWN
    def actualizar_dropdown():
        nonlocal inventarios, inventario_seleccionado, menu_height
        inventarios = cargar_inventarios()
        if inventarios:
            nuevo_nombre = inventarios[-1]["nombre"]
            dropdown.options = [ft.dropdown.Option(inv["nombre"]) for inv in inventarios]
            dropdown.value = nuevo_nombre
            inventario_seleccionado = inventarios[-1]
        else:
            dropdown.options = []
            dropdown.value = None
            inventario_seleccionado = None

        ITEM_HEIGHT = 40
        MAX_MENU_HEIGHT = 250
        menu_height = min(len(inventarios) * ITEM_HEIGHT, MAX_MENU_HEIGHT)
        dropdown.menu_height = menu_height

        dropdown.update()
        cargar_listas()
        page.update()

    # DROPDOWN PARA SELECCIONAR EL INVENTARIO
    ITEM_HEIGHT = 40  # ALTURA POR OPCIÓN
    MAX_MENU_HEIGHT = 250  # ALTURA MÁXIMA

    menu_height = min(len(inventarios) * ITEM_HEIGHT, MAX_MENU_HEIGHT)

    dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(inv["nombre"]) for inv in inventarios],
        value=inventarios[0]["nombre"],
        width=page.width * 0.8,
        menu_height=menu_height,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        color="black",
        filled=True,
        fill_color="#F0F0EF",
        border_color="#F0F0EF",
        on_change=actualizar_listas,
    )

    # BOTÓN AL LADO DEL DROPDOWN
    btn_mas = ft.IconButton(
        icon=ft.Icons.ADD,
        bgcolor="#E6E6E6",
        icon_color="black",
        on_click=lambda e: mostrar_ventana_n_inv(None, page, actualizar_dropdown),
    )

    # ACTUALIZAR EL CONTENEDOR DEL DROPDOWN
    dropdown_row = ft.Row(
        [
            dropdown,
            btn_mas,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )

    # CONTENEDOR DE LAS LISTAS
    lista_column = ft.Column(spacing=5)

    # BOTÓN PARA REGRESAR A LA PANTALLA ANTERIOR
    regresar_btn = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda _: regresar_callback(),
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
                        [regresar_btn],
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
        bgcolor="blue",
        margin=ft.Margin(bottom=15, left=0, right=0, top=0),
        height=85,
        alignment=ft.alignment.center,
        expand=True,
    )

    # RECTÁNGULO DE TÍTULO LISTAS
    rec_listas = ft.Container(
        bgcolor="#FBE0D0",
        height=35,
        width=page.width * 0.90,
        border_radius=ft.border_radius.all(7),
        padding=ft.padding.only(left=10, right=10, top=0, bottom=0),
        margin=ft.Margin(bottom=0, left=0, right=0, top=0),
        alignment=ft.alignment.center,
        content=ft.Row(
            [ft.Text("LISTAS", size=20, weight=ft.FontWeight.BOLD, color="black")],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # CUADRO DE LISTAS
    cuadro_listas = ft.Container(
        bgcolor="#FFFFFF",
        padding=ft.padding.only(left=10, right=10, top=5, bottom=10),
        margin=ft.Margin(bottom=8, left=0, right=0, top=0),
        width=page.width * 0.85,
        border_radius=ft.border_radius.only(bottom_left=7, bottom_right=7, top_left=0, top_right=0),
        alignment=ft.alignment.center,
        content=ft.Column(
            [
                dropdown_row,
                ft.Divider(color="black", thickness=2, height=10),
                lista_column,
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

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
            [
                rec_listas,
                cuadro_listas,

                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Nuevo",
                            icon=ft.Icons.ADD,
                            bgcolor="#E6E6E6",
                            color="black",
                            on_click=lambda e: mostrar_ventana_n_lista(
                                None,
                                page,
                                inventario_seleccionado["id"],
                                cargar_listas,
                                usuario_logeado["nombre"]
                            ),
                        ),
                        ft.ElevatedButton(
                            text="Editar",
                            icon=ft.Icons.EDIT,
                            bgcolor="#E6E6E6",
                            color="black",
                            on_click=lambda e: mostrar_ventana_e_lista(
                                e, page, inventario_seleccionado["id"], cargar_listas
                            ),
                        ),
                        ft.ElevatedButton(
                            text="Eliminar",
                            icon=ft.Icons.DELETE,
                            bgcolor="#E6E6E6",
                            color="black",
                            on_click=lambda e: mostrar_ventana_borrar_lista(
                                e, page, inventario_seleccionado["id"], cargar_listas
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=50,
                ),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # AGREGAR VISTA PRINCIPAL
    page.views.append(
        ft.View(
            "/inventarios",
            [banner, cuadro_main],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.START,
            padding=0,
        )
    )

    # CARGAR LISTAS DE INVENTARIO INICIAL
    inventario_seleccionado = inventarios[0]
    cargar_listas()

    print(inventario_seleccionado)