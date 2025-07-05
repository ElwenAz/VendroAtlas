import flet as ft
from datetime import datetime
from db_connection import create_connection, close_connection
import uuid

class VendedoresView:
    def __init__(self, page: ft.Page, usuario_actual: dict):
        self.page = page
        self.usuario_actual = usuario_actual
        self.vendedores = self.obtener_vendedores_bd()
        self.build_view()

        self.page.dialog = None

    def obtener_vendedores_bd(self):
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT correo, nombre, 
                (SELECT descripcion FROM tipos_usuario WHERE id_tipo_usuario = usuarios.id_tipo_usuario) AS rol,
                DATE_FORMAT(fecha_creacion, '%d/%m/%Y') AS fecha
            FROM usuarios
            """
        )
        vendedores = cursor.fetchall()
        close_connection(connection)
        return vendedores

    def crear_banner(self):
        btn_regresar = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda _: self.page.go("/plantilla"),
            ),
            bgcolor="#EAEBE8",
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
                        width=self.page.width,
                        height=85,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [btn_regresar],
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
                        margin=ft.margin.only(left=self.page.width * 0.75, right=0, top=0, bottom=0),
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

    def build_view(self):
        # Componentes UI
        self.nombre_field = ft.TextField(label="Nombre completo", width=300)
        self.rol_dropdown = ft.Dropdown(
            label="Rol",
            options=[
                ft.dropdown.Option("Dueno"),
                ft.dropdown.Option("Vendedor"),
            ],
            width=300
        )
        self.contrasena_field = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True)
        
        # Tabla de vendedores desde la base de datos
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Rol", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha de registro", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text(""))  # Columna vacía para acciones
            ],
            rows=self._generar_filas()
        )

        # Contenido principal
        contenido = ft.Column(
            [
                ft.Row([
                    ft.Column([
                        ft.Text("Registrar nuevo vendedor:", size=18, weight=ft.FontWeight.BOLD),
                        self.nombre_field,
                        self.rol_dropdown,
                        self.contrasena_field,
                        ft.ElevatedButton(
                            "Guardar registro",
                            icon=ft.icons.SAVE,
                            on_click=self.agregar_vendedor,
                            bgcolor=ft.colors.GREEN_400,
                            color=ft.colors.WHITE
                        )
                    ], spacing=15),
                    ft.VerticalDivider(),
                    ft.Container(
                        content=ft.ListView([self.tabla], height=400),
                        expand=True
                    )
                ], spacing=30, expand=True)
            ],
            spacing=20,
            expand=True
        )

        # Cuadro principal
        cuadro_main = ft.Container(
            bgcolor="#FAFAF5",
            border=ft.border.all(2, ft.colors.BLUE_GREY_100),
            padding=ft.padding.only(left=15, right=15, top=25, bottom=10),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.all(10),
            height=self.page.height - 100,
            width=self.page.width * 0.90,
            content=contenido
        )

        # Vista completa
        self.view = ft.View(
            "/vendedores",
            [
                self.crear_banner(),
                cuadro_main
            ],
            bgcolor="#FAFAF5",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.START,
            padding=0,
        )

    def _generar_filas(self):
        rows = []
        for v in self.vendedores:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(v["nombre"])),
                    ft.DataCell(ft.Text(v["rol"])),
                    ft.DataCell(ft.Text(v["fecha"])),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.icons.DELETE_FOREVER,
                            icon_color=ft.colors.RED_700,
                            on_click=lambda e, v=v: self.eliminar_vendedor(v),  # Directo
                            tooltip="Eliminar este vendedor"
                        )
                    )
                ]
            ))
        return rows

    def agregar_vendedor(self, e):
        if not self.nombre_field.value or not self.rol_dropdown.value or not self.contrasena_field.value:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Complete todos los campos requeridos"),
                bgcolor=ft.colors.RED_400
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Determinar el id_tipo_usuario según el rol
        rol = self.rol_dropdown.value.lower()
        id_tipo_usuario = 1 if rol == "dueno" else 2

        # Generar correo aleatorio para cumplir con la restricción de la base de datos
        correo_aleatorio = f"{uuid.uuid4().hex[:12]}@fake.com"

        connection = create_connection()
        if not connection:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("No se pudo conectar a la base de datos"),
                bgcolor=ft.colors.RED_400
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO usuarios (correo, nombre, contrasena, id_tipo_usuario, fecha_creacion)
                VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (
                correo_aleatorio,
                self.nombre_field.value,
                self.contrasena_field.value,
                id_tipo_usuario
            ))
            connection.commit()
            # Recargar la lista desde la base de datos
            self.vendedores = self.obtener_vendedores_bd()
            self.tabla.rows = self._generar_filas()
            self.nombre_field.value = ""
            self.rol_dropdown.value = ""
            self.contrasena_field.value = ""
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Vendedor registrado!"),
                bgcolor=ft.colors.GREEN_400
            )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Error al registrar: {ex}"),
                bgcolor=ft.colors.RED_400
            )
        finally:
            close_connection(connection)
            self.page.snack_bar.open = True
            self.page.update()

    def eliminar_vendedor(self, vendedor):
        print("Eliminando directamente:", vendedor)  # Depuración
        connection = create_connection()
        if not connection:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("No se pudo conectar a la base de datos"),
                bgcolor=ft.colors.RED_400
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            cursor = connection.cursor()
            print("Eliminando compras y ventas de:", vendedor["nombre"])  # Depuración
            cursor.execute("DELETE FROM compras WHERE nombre_usuario = %s", (vendedor["nombre"],))
            cursor.execute("DELETE FROM ventas WHERE nombre_usuario = %s", (vendedor["nombre"],))
            print("Eliminando usuario:", vendedor["nombre"])  # Depuración
            cursor.execute("DELETE FROM usuarios WHERE nombre = %s", (vendedor["nombre"],))
            connection.commit()
            self.vendedores = self.obtener_vendedores_bd()
            self.tabla.rows = self._generar_filas()
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Vendedor {vendedor['nombre']} eliminado"),
                bgcolor=ft.colors.ORANGE_400
            )
        except Exception as ex:
            print("Error al eliminar:", ex)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Error al eliminar: {ex}"),
                bgcolor=ft.colors.RED_400
            )
        finally:
            close_connection(connection)
            self.page.snack_bar.open = True
            self.page.update()

    def __call__(self):
        return self.view