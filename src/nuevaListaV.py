import flet as ft
from invSis import cargar_listas_por_inventario, cargar_productos_por_lista
from db_connection import create_connection, close_connection

def crear_lista(nombre_lista, id_inventario, nombre_usuario):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        cursor = connection.cursor(dictionary=True)
        # BUSCAR LA LISTA ANTERIOR
        listas = cargar_listas_por_inventario(id_inventario)
        listas_no_desperdicio = [l for l in listas if not l["nombre"].lower().startswith("desperdicio")]
        lista_anterior = listas_no_desperdicio[0] if listas_no_desperdicio else None

        # CREAR LA NUEVA LISTA
        query = """
            INSERT INTO listas (nombre_lista, id_inventario, ultima_modificacion)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (nombre_lista, id_inventario))
        id_lista_nueva = cursor.lastrowid

        # VERIFICAR Q NO SEA DESPERDICIO
        if nombre_lista.lower() != "desperdicio" and lista_anterior:
            productos_ant = cargar_productos_por_lista(lista_anterior["id"])
            for prod in productos_ant:
                cursor.execute(
                    "INSERT INTO lista_productos (id_lista, id_producto, cantidad, kg_c1, kg_c2, kg_c3) VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        id_lista_nueva,
                        prod["id_producto"],
                        0,
                        prod.get("kg_c1", 0) or 0,
                        prod.get("kg_c2", 0) or 0,
                        prod.get("kg_c3", 0) or 0,
                    ),
                )

                for calidad, campo in [("1ra", "kg_c1"), ("2da", "kg_c2"), ("3ra", "kg_c3")]:
                    kg = prod.get(campo, 0) or 0
                    if kg > 0:
                        
                        cursor.execute(
                            "SELECT precio_kg, nombre_usuario FROM compras WHERE id_lista = %s AND id_producto = %s AND calidad = %s ORDER BY fecha_compra DESC LIMIT 1",
                            (lista_anterior["id"], prod["id_producto"], calidad)
                        )
                        row = cursor.fetchone()
                        precio_kg = row["precio_kg"] if row else 0
                        nombre_usuario_original = row["nombre_usuario"] if row else nombre_usuario
                        cursor.execute(
                            "INSERT INTO compras (id_lista, id_producto, calidad, cantidad_kg, precio_kg, nombre_usuario) VALUES (%s, %s, %s, %s, %s, %s)",
                            (id_lista_nueva, prod["id_producto"], calidad, kg, precio_kg, "TRANSFERENCIA")
                        )
                
                # PONER STOCK EN 0 EN LA LISTA ANTERIOR
                cursor.execute(
                    "UPDATE lista_productos SET kg_c1=0, kg_c2=0, kg_c3=0 WHERE id_lista=%s AND id_producto=%s",
                    (lista_anterior["id"], prod["id_producto"])
                )
        connection.commit()

        # SI NO ES DESPERDICIO, CREAR SU LISTA DE DESPERDICIO HIJA
        if nombre_lista.lower() != "desperdicio":
            query_desperdicio = """
                INSERT INTO listas (nombre_lista, id_inventario, id_lista_padre, ultima_modificacion)
                VALUES (%s, %s, %s, NOW())
            """
            nombre_desperdicio = f"Desperdicio de {nombre_lista}"
            cursor.execute(query_desperdicio, (nombre_desperdicio, id_inventario, id_lista_nueva))
            connection.commit()

        return True
    except Exception as ex:
        print(f"Error al crear la lista: {ex}")
        return False
    finally:
        close_connection(connection)

# FUNC CERRAR VENTANA
def cerrar_ventana(page):
    page.overlay.clear()
    page.update()

# FUNC CREAR VENTANA
def mostrar_ventana_n_lista(e, page, id_inventario, actualizar_callback, nombre_usuario):
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

    # FUNC PARA CREAR LA LISTA
    def crear_lista_action(e):
        if not nombre_lista.value.strip():
            print("El nombre de la lista no puede estar vacío.")
            return
        
        # INHABILITAR BOTON DE CONTINUAR PARA COULDOWN
        btn_continuar.disabled = True
        btn_continuar.update()

        # CREAR LA LISTA EN LA BASE DE DATOS
        if crear_lista(nombre_lista.value.strip(), id_inventario, nombre_usuario):
            print(f"Lista '{nombre_lista.value.strip()}' creada exitosamente.")
            cerrar_ventana(page) 
            actualizar_callback()
        else:
            print("Error al crear la lista.")

        # HABILITAR BOTON DESPUES DE 2SEG
        page.timer(2, lambda _: habilitar_btn())

    # FUNC HABILITAR BTN
    def habilitar_btn():
        btn_continuar.disabled = False
        btn_continuar.update()

    # BOTON DE CONTINUAR
    btn_continuar = ft.ElevatedButton(
            "Continuar",
            icon=ft.Icons.ADD,
            on_click=crear_lista_action,
        )

    nombre_lista = ft.TextField(
                            label="NUEVA LISTA",
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
                    content=ft.Text("NUEVA LISTA", size=20, weight=ft.FontWeight.BOLD, color="black"),
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
                        ft.Text("LISTA", size=14, color="gray"),
                        ft.Container(
                            content=ft.Divider(thickness=1, color="gray"),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),

                # TEXTFIELD DE NOMBRE
                nombre_lista,
                
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