import flet as ft
from DuenoGui import main as inicio_gui
from VendedorGui import main as vendedor_gui
from db_connection import create_connection, close_connection

clave_licencia = "12345"  # CLAVE/LICENCIA

def main(page: ft.Page):
    page.title = "VendorAtlas"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK

    # FUNCIÓN VERIFICAR SI EXISTE UN DUEÑO
    def existe_dueño():
        connection = create_connection()
        if not connection:
            print("No se pudo conectar a la base de datos.")
            return False
        try:
            query = "SELECT COUNT(*) AS total FROM usuarios WHERE id_tipo_usuario = 1"
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            return result["total"] > 0
        except Exception as ex:
            print(f"Error al verificar si existe un dueño: {ex}")
            return False
        finally:
            close_connection(connection)


    def obtener_contraseña_dueño():
        connection = create_connection()
        if not connection:
            print("No se pudo conectar a la base de datos.")
            return None
        try:
            query = "SELECT contrasena FROM usuarios WHERE es_cuenta_inicial = TRUE LIMIT 1"
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            return result["contrasena"] if result else None
        except Exception as ex:
            print(f"Error al obtener la contraseña del dueño: {ex}")
            return None
        finally:
            close_connection(connection)

    def mostrar_crear_cuenta_inicial():
        licencia = ft.TextField(label="Clave/Licencia", password=True, width=300, bgcolor="#426B1F", color="white", can_reveal_password=True)
        correo = ft.TextField(label="Correo", width=300, bgcolor="#426B1F", color="white")
        usuario = ft.TextField(label="Usuario", width=300, bgcolor="#426B1F", color="white")
        contraseña = ft.TextField(label="Contraseña", password=True, width=300, bgcolor="#426B1F", color="white", can_reveal_password=True)
        confirmar_contraseña = ft.TextField(label="Confirmar Contraseña", password=True, width=300, bgcolor="#426B1F", color="white", can_reveal_password=True)
        error_text = ft.Text("", color="red")

        def crear_cuenta_inicial(e):
            if contraseña.value != confirmar_contraseña.value:
                error_text.value = "Las contraseñas no coinciden"
            elif licencia.value == clave_licencia:
                connection = create_connection()
                if not connection:
                    print("No se pudo conectar a la base de datos.")
                    return
                try:
                    query = """
                        INSERT INTO usuarios (correo, nombre, contrasena, id_tipo_usuario, es_cuenta_inicial)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor = connection.cursor()
                    cursor.execute(query, (correo.value, usuario.value, contraseña.value, 1, True))
                    connection.commit()
                    mostrar_login()
                except Exception as ex:
                    print(f"Error al crear la cuenta inicial: {ex}")
                    error_text.value = "Error al crear la cuenta inicial"
                finally:
                    close_connection(connection)
            else:
                error_text.value = "Clave/licencia incorrecta"
            page.update()

        crear_button = ft.ElevatedButton(
            "Crear Cuenta", on_click=crear_cuenta_inicial, bgcolor="black", color="white"
        )

        # AGREGAR LA VISTA DE CREACIÓN DE CUENTA INICIAL
        page.views.clear()
        page.views.append(
            ft.View(
                "/crear_cuenta_inicial",
                [
                    ft.Container(
                        content=ft.Stack(
                            [
                                ft.Image(
                                    src="src/assets/login/bgLogin.png",
                                    fit=ft.ImageFit.COVER,
                                    width=10000,
                                    height=10000,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text(
                                                    "Crear Cuenta Inicial (Dueño)",
                                                    size=20,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="black",
                                                ),
                                                licencia,
                                                correo,
                                                usuario,
                                                contraseña,
                                                confirmar_contraseña,
                                                crear_button,
                                                error_text,
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        bgcolor="#D9D9D9",
                                        width=page.width * 0.5,
                                        height=page.height * 0.7,
                                        border_radius=15,
                                        padding=20,
                                        opacity=0.9,
                                    ),
                                    alignment=ft.alignment.center,
                                    expand=True,
                                ),
                            ]
                        ),
                        expand=True,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                padding=0,
            )
        )
        page.update()

    def mostrar_crear_nueva_cuenta():
        correo = ft.TextField(label="Correo", width=300, bgcolor="#426B1F", color="white")
        nombre = ft.TextField(label="Nombre", width=300, bgcolor="#426B1F", color="white")
        contraseña = ft.TextField(label="Contraseña", password=True, width=300, bgcolor="#426B1F", color="white", can_reveal_password=True)
        confirmar_contraseña = ft.TextField(label="Confirmar Contraseña", password=True, width=300, bgcolor="#426B1F", color="white", can_reveal_password=True)
        contraseña_dueño = ft.TextField(label="Contraseña del Dueño Inicial", password=True, width=300, bgcolor="#426B1F", color="white", can_reveal_password=True)
        tipo_cuenta = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(
                        value="dueño",
                        label="Dueño",
                        fill_color="black",
                        label_style=ft.TextStyle(color="black"),
                    ),
                    ft.Radio(
                        value="vendedor",
                        label="Vendedor",
                        fill_color="black",
                        label_style=ft.TextStyle(color="black"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        error_text = ft.Text("", color="red")

        def crear_cuenta(e):
            contraseña_dueño_inicial = obtener_contraseña_dueño()
            if contraseña.value != confirmar_contraseña.value:
                error_text.value = "Las contraseñas no coinciden"
            elif not contraseña_dueño_inicial:
                error_text.value = "No hay una cuenta de dueño inicial registrada"
            elif contraseña_dueño.value != contraseña_dueño_inicial:
                error_text.value = "Contraseña del dueño inicial incorrecta"
            else:
                connection = create_connection()
                if not connection:
                    print("No se pudo conectar a la base de datos.")
                    return
                try:
                    id_tipo_usuario = 1 if tipo_cuenta.value == "dueño" else 2
                    query = """
                        INSERT INTO usuarios (correo, nombre, contrasena, id_tipo_usuario, es_cuenta_inicial)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor = connection.cursor()
                    cursor.execute(query, (correo.value, nombre.value, contraseña.value, id_tipo_usuario, False))
                    connection.commit()
                    mostrar_login()
                except Exception as ex:
                    print(f"Error al crear la cuenta: {ex}")
                    error_text.value = "Error al crear la cuenta"
                finally:
                    close_connection(connection)
            page.update()

        crear_button = ft.ElevatedButton(
            "Crear Cuenta", on_click=crear_cuenta, bgcolor="black", color="white"
        )
        regresar_button = ft.ElevatedButton(
            "Regresar", on_click=lambda _: mostrar_login(), bgcolor="black", color="white"
        )

        page.views.clear()
        page.views.append(
            ft.View(
                "/crear_nueva_cuenta",
                [
                    ft.Container(
                        content=ft.Stack(
                            [
                                ft.Image(
                                    src="src/assets/login/bgLogin.png",
                                    fit=ft.ImageFit.COVER,
                                    width=10000,
                                    height=10000,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text(
                                                    "Crear Nueva Cuenta",
                                                    size=20,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="black",
                                                ),
                                                correo,
                                                nombre,
                                                contraseña,
                                                confirmar_contraseña,
                                                contraseña_dueño,
                                                tipo_cuenta,
                                                crear_button,
                                                error_text,
                                                regresar_button,
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        bgcolor="#D9D9D9",
                                        width=page.width * 0.5,
                                        height=page.height * 0.9,
                                        border_radius=15,
                                        padding=20,
                                        opacity=0.9,
                                    ),
                                    alignment=ft.alignment.center,
                                    expand=True,
                                ),
                            ]
                        ),
                        expand=True,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                padding=0,
            )
        )
        page.update()

    def mostrar_login():
        page.theme_mode = ft.ThemeMode.DARK  

        nombre = ft.TextField(label="Nombre", width=300, bgcolor="#426B1F", color="white")
        contraseña = ft.TextField(label="Contraseña", password=True, width=300, bgcolor="#426B1F", color="white", can_reveal_password=True)
        tipo_cuenta = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(
                        value="dueño",
                        label="Dueño",
                        fill_color="black",
                        label_style=ft.TextStyle(color="black"),
                    ),
                    ft.Radio(
                        value="vendedor",
                        label="Vendedor",
                        fill_color="black",
                        label_style=ft.TextStyle(color="black"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        error_text = ft.Text("", color="red")

        def login(e):
            connection = create_connection()
            if not connection:
                print("No se pudo conectar a la base de datos.")
                return
            try:
                # Cambia el query para buscar por nombre
                query = "SELECT * FROM usuarios WHERE nombre = %s AND contrasena = %s"
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (nombre.value, contraseña.value))
                result = cursor.fetchone()
                if result:
                    if tipo_cuenta.value == "dueño" and result["id_tipo_usuario"] == 1:
                        inicio_gui(page, mostrar_login, usuario_logeado=result)
                    elif tipo_cuenta.value == "vendedor" and result["id_tipo_usuario"] == 2:
                        vendedor_gui(page, mostrar_login, usuario_logeado=result)
                    else:
                        error_text.value = "Tipo de cuenta incorrecto"
                else:
                    error_text.value = "Usuario o contraseña incorrectos"
            except Exception as ex:
                print(f"Error al iniciar sesión: {ex}")
                error_text.value = "Error al iniciar sesión"
            finally:
                close_connection(connection)
            page.update()

        login_button = ft.ElevatedButton(
            "Iniciar Sesión", on_click=login, bgcolor="black", color="white"
        )

        page.views.clear()
        page.views.append(
            ft.View(
                "/login",
                [
                    ft.Container(
                        content=ft.Stack(
                            [
                                ft.Image(
                                    src="src/assets/login/bgLogin.png",
                                    fit=ft.ImageFit.COVER,
                                    width=10000,
                                    height=10000,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text(
                                                    "Inicio de Sesión",
                                                    size=20,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="black",
                                                ),
                                                nombre,
                                                contraseña,
                                                tipo_cuenta,
                                                login_button,
                                                error_text,
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        bgcolor="#D9D9D9",
                                        width=page.width * 0.5,
                                        height=page.height * 0.6,
                                        border_radius=15,
                                        padding=20,
                                        opacity=0.9,
                                    ),
                                    alignment=ft.alignment.center,
                                    expand=True,
                                ),
                            ]
                        ),
                        expand=True,
                    ),
                    
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                padding=0,
            )
        )
        page.update()

    # MOSTRAR PANTALLA INICIAL SEGÚN EXISTA UN DUEÑO
    if not existe_dueño():
        mostrar_crear_cuenta_inicial()
    else:
        mostrar_login()

ft.app(target=main)