import flet as ft
from db_connection import create_connection, close_connection

# CREAR INV EN BDD
def crear_inventario(nombre_inventario):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False

    try:
        # CREAR INVENTARIO
        query = """
            INSERT INTO inventarios (nombre, fecha_creacion)
            VALUES (%s, NOW())
        """
        cursor = connection.cursor()
        cursor.execute(query, (nombre_inventario,))
        connection.commit()
        id_inventario = cursor.lastrowid

        query_lista = """
            INSERT INTO listas (nombre_lista, id_inventario, ultima_modificacion)
            VALUES ('Desperdicio', %s, NOW())
        """
        cursor.execute(query_lista, (id_inventario,))
        connection.commit()

        print(f"Inventario '{nombre_inventario}' y lista 'Desperdicio' creados exitosamente.")
        return True
    except Exception as ex:
        print(f"Error al crear el inventario: {ex}")
        return False
    finally:
        close_connection(connection)

# FUNC CERRAR VENTANA
def cerrar_ventana(page):
    page.overlay.clear()
    page.update()

# FUNC CREAR VENTANA
def mostrar_ventana_n_inv(e, page, actualizar_callback):
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

    # FUNC PARA CREAR EL INVENTARIO
    def crear_inventario_action(e):
        if not nombre_inv.value.strip():
            print("El nombre del inventario no puede estar vacío.")
            return

        btn_continuar.disabled = True
        btn_continuar.update()

        if crear_inventario(nombre_inv.value.strip()):
            print(f"Inventario '{nombre_inv.value.strip()}' creado exitosamente.")
            cerrar_ventana(page)
            actualizar_callback()
        else:
            print("Error al crear el inventario.")

        btn_continuar.disabled = False
        btn_continuar.update()

    # FUNC HABILITAR BTN
    def habilitar_btn():
        btn_continuar.disabled = False
        btn_continuar.update()

    # BOTON DE CONTINUAR
    btn_continuar = ft.ElevatedButton(
            "Continuar",
            icon=ft.Icons.ADD,
            on_click=crear_inventario_action,
        )

    # TEXTFIELD DE NOMBRE
    nombre_inv = ft.TextField(
        label="NUEVA INVENTARIO",
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
                    content=ft.Text("NUEVO INVENTARIO", size=20, weight=ft.FontWeight.BOLD, color="black"),
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
                        ft.Text("INVENTARIO", size=14, color="gray"),
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),

                # TEXTFIELD DE NOMBRE
                nombre_inv,
                
                # BOTONES DE ACCION
                ft.Row(
                    [
                        ft.ElevatedButton("Cancelar", icon=ft.Icons.CLOSE, on_click=lambda _: cerrar_ventana(page)),
                        btn_continuar,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=400,
        height=230,
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