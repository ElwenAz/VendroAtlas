from datetime import datetime
from db_connection import create_connection, close_connection

class Producto:
    def __init__(self, nombre, tipo):
        self.nombre = nombre
        self.tipo = tipo

class Compra:
    def __init__(self, producto, cantidad_kg, precio_kg, calidad):
        self.producto = producto
        self.cantidad_kg = cantidad_kg
        self.precio_kg = precio_kg
        self.calidad = calidad

class Venta:
    def __init__(self, producto, calidad, cantidad_kg, precio_kg):
        self.producto = producto
        self.calidad = calidad
        self.cantidad_kg = cantidad_kg
        self.precio_kg = precio_kg

class Lista:
    def __init__(self, nombre):
        self.nombre = nombre 
        self.fecha_creacion = datetime.now()
        self.ultima_modificacion = datetime.now()
        self.compras = []
        self.ventas = []
        self.productos = []

    def cambiar_nombre(self, nuevo_nombre):
        """Cambiar el nombre de la lista."""
        self.nombre = nuevo_nombre
        self.ultima_modificacion = datetime.now()

    def registrar_compra(self, compra):
        self.compras.append(compra)
        self.ultima_modificacion = datetime.now()

    def registrar_venta(self, venta):
        self.ventas.append(venta)
        self.ultima_modificacion = datetime.now()

    def agregar_producto(self, producto):
        self.productos.append(producto)
        self.ultima_modificacion = datetime.now()

    def obtener_producto(self, nombre):
        for producto in self.productos:
            if producto.nombre == nombre:
                return producto
        return None

class Inventario:
    def __init__(self, nombre):
        self.nombre = nombre
        self.listas = []
        self.lista_desperdicio = self.crear_lista("Desperdicio")

    def cambiar_nombre(self, nuevo_nombre):
        """Permite cambiar el nombre del inventario."""
        self.nombre = nuevo_nombre

    def crear_lista(self, nombre):
        nueva_lista = Lista(nombre)
        self.listas.append(nueva_lista)
        return nueva_lista

    def obtener_lista_actual(self):
        if not self.listas:
            return self.crear_lista(f"Semana {len(self.listas) + 1}")
        return self.listas[-1]
    
    def obtener_listas_ordenadas(self):
        listas_ordenadas = sorted(self.listas, key=lambda lista: lista.ultima_modificacion, reverse=True)
        if self.lista_desperdicio in listas_ordenadas:
            listas_ordenadas.remove(self.lista_desperdicio)
        listas_ordenadas.append(self.lista_desperdicio)
        return listas_ordenadas
    
    
# CARGAR PRODUCTOS DE BASE DE DATOS
def cargar_productos_por_lista(id_lista):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return []

    try:
        query = """
            SELECT p.id_producto, p.nombre, p.tipo, p.descripcion, p.precio,
                   lp.kg_c1, lp.kg_c2, lp.kg_c3
            FROM lista_productos lp
            JOIN productos p ON lp.id_producto = p.id_producto
            WHERE lp.id_lista = %s
        """
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (id_lista,))
        productos = cursor.fetchall()
        return productos
    except Exception as ex:
        print(f"Error al cargar productos de la lista: {ex}")
        return []
    finally:
        close_connection(connection)

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

# CARGAR INV
def cargar_inventarios():
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return []

    try:
        query = "SELECT id_inventario as id, nombre FROM inventarios"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        inventarios = cursor.fetchall()
        return inventarios
    except Exception as ex:
        print(f"Error al cargar inventarios: {ex}")
        return []
    finally:
        close_connection(connection)

# CARGAR PRODUCTOS
def cargar_productos_por_lista(id_lista):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return []

    try:
        query = """
            SELECT p.id_producto, p.nombre, p.tipo, p.descripcion, p.precio,
                   lp.kg_c1, lp.kg_c2, lp.kg_c3
            FROM lista_productos lp
            JOIN productos p ON lp.id_producto = p.id_producto
            WHERE lp.id_lista = %s
        """
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (id_lista,))
        productos = cursor.fetchall()
        return productos
    except Exception as ex:
        print(f"Error al cargar productos de la lista: {ex}")
        return []
    finally:
        close_connection(connection)

# AGREGAR PRODUCTO A LA LISTA
def agregar_producto_a_lista(nombre, tipo, id_lista):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_producto FROM productos WHERE nombre = %s AND tipo = %s", (nombre, tipo))
        producto = cursor.fetchone()
        if not producto:
            cursor.execute(
                "INSERT INTO productos (nombre, tipo) VALUES (%s, %s)",
                (nombre, tipo)
            )
            connection.commit()
            id_producto = cursor.lastrowid
        else:
            id_producto = producto["id_producto"]

        cursor.execute(
            "INSERT INTO lista_productos (id_lista, id_producto, cantidad) VALUES (%s, %s, %s)",
            (id_lista, id_producto, 0)
        )
        connection.commit()

        # ACTUALIZAR FECHA DE ÚLTIMA MODIFICACIÓN DE LA LISTA
        cursor.execute(
            "UPDATE listas SET ultima_modificacion = NOW() WHERE id_lista = %s",
            (id_lista,)
        )
        connection.commit()

        return True
    except Exception as ex:
        print(f"Error al agregar producto a la lista: {ex}")
        return False
    finally:
        close_connection(connection)

# CARGAR DESPERDICIO DE CADA LISTA
def cargar_lista_desperdicio_por_lista(id_lista_padre):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return None
    try:
        query = """
            SELECT id_lista AS id, nombre_lista AS nombre, ultima_modificacion
            FROM listas
            WHERE id_lista_padre = %s AND LOWER(nombre_lista) LIKE 'desperdicio%%'
            LIMIT 1
        """
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (id_lista_padre,))
        return cursor.fetchone()
    except Exception as ex:
        print(f"Error al cargar desperdicio de la lista: {ex}")
        return None
    finally:
        close_connection(connection)

def cargar_lista_desperdicio(id_inventario):
    connection = create_connection()
    if not connection:
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
        return cursor.fetchone()
    except Exception as ex:
        print(f"Error al cargar desperdicio general: {ex}")
        return None
    finally:
        close_connection(connection)

# REGISTRAR KILOS COMPRADOS
def sumar_kg_a_producto_lista(id_lista, id_producto, calidad, kg):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        campo = None
        if calidad == "1ra":
            campo = "kg_c1"
        elif calidad == "2da":
            campo = "kg_c2"
        elif calidad == "3ra":
            campo = "kg_c3"
        else:
            print("Calidad inválida")
            return False

        query = f"""
            UPDATE lista_productos
            SET {campo} = {campo} + %s
            WHERE id_lista = %s AND id_producto = %s
        """
        cursor = connection.cursor()
        cursor.execute(query, (kg, id_lista, id_producto))
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al sumar kg por calidad: {ex}")
        return False
    finally:
        close_connection(connection)

# REGISTRAR COMPRA EN BDD PARA HISTORIAL
def registrar_compra_bd(id_lista, id_producto, calidad, kg, precio_unitario, nombre_usuario):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        query = """
            INSERT INTO compras (id_lista, id_producto, calidad, cantidad_kg, precio_kg, nombre_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor = connection.cursor()
        cursor.execute(query, (id_lista, id_producto, calidad, kg, precio_unitario, nombre_usuario))
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al registrar la compra en BD: {ex}")
        return False
    finally:
        close_connection(connection)

# VENTA EN BDD
def registrar_venta_bd(id_lista, id_producto, calidad, kg, precio_unitario, nombre_usuario):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        query = """
            INSERT INTO ventas (id_lista, id_producto, calidad, cantidad_kg, precio_kg, nombre_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor = connection.cursor()
        cursor.execute(query, (id_lista, id_producto, calidad, kg, precio_unitario, nombre_usuario))
        connection.commit()

        campo = None
        if calidad == "1ra":
            campo = "kg_c1"
        elif calidad == "2da":
            campo = "kg_c2"
        elif calidad == "3ra":
            campo = "kg_c3"
        else:
            print("Calidad inválida")
            return False

        query_update = f"""
            UPDATE lista_productos
            SET {campo} = {campo} - %s
            WHERE id_lista = %s AND id_producto = %s
        """
        cursor.execute(query_update, (kg, id_lista, id_producto))
        connection.commit()

        return True
    except Exception as ex:
        print(f"Error al registrar la venta en BD: {ex}")
        return False
    finally:
        close_connection(connection)

# OBTENER STOCK DE PRODUCTOS
def obtener_stock_producto_lista(id_lista, id_producto, calidad):
    connection = create_connection()
    if not connection:
        return 0
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                IFNULL((SELECT SUM(cantidad_kg) FROM compras WHERE id_lista=%s AND id_producto=%s AND calidad=%s), 0) -
                IFNULL((SELECT SUM(cantidad_kg) FROM ventas WHERE id_lista=%s AND id_producto=%s AND calidad=%s), 0)
        """, (id_lista, id_producto, calidad, id_lista, id_producto, calidad))
        result = cursor.fetchone()
        return float(result[0]) if result else 0
    except Exception as ex:
        print(f"Error al obtener stock: {ex}")
        return 0
    finally:
        close_connection(connection)

# ELIMINAR PRODUCTO DE LA LISTA
def eliminar_producto_de_lista(id_lista, id_producto):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM lista_productos WHERE id_lista = %s AND id_producto = %s",
            (id_lista, id_producto)
        )
        cursor.execute(
            "UPDATE listas SET ultima_modificacion = NOW() WHERE id_lista = %s",
            (id_lista,)
        )
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al eliminar producto de la lista: {ex}")
        return False
    finally:
        close_connection(connection)

#ELIMINAR PRODUCTO DE FORMA GLOBAL
def eliminar_producto_global(id_producto):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        cursor = connection.cursor()
        # ELIMINAR DE COMPRAS
        cursor.execute("DELETE FROM compras WHERE id_producto = %s", (id_producto,))
        # ELIMINAR DE VENTAS
        cursor.execute("DELETE FROM ventas WHERE id_producto = %s", (id_producto,))
        # ELIMINAR DE LISTA_PRODUCTOS
        cursor.execute("DELETE FROM lista_productos WHERE id_producto = %s", (id_producto,))
        # ELIMINAR DE PRODUCTOS
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al eliminar producto globalmente: {ex}")
        return False
    finally:
        close_connection(connection)

#EDITAR NOMBRE DE PRODUCTO
def actualizar_nombre_producto(id_producto, nuevo_nombre):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE productos SET nombre = %s WHERE id_producto = %s",
            (nuevo_nombre, id_producto)
        )
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al actualizar nombre del producto: {ex}")
        return False
    finally:
        close_connection(connection)

#EDITAR NOMBRE DE LISTA
def actualizar_nombre_lista(id_lista, nuevo_nombre):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE listas SET nombre_lista = %s WHERE id_lista = %s",
            (nuevo_nombre, id_lista)
        )
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al actualizar nombre de la lista: {ex}")
        return False
    finally:
        close_connection(connection)

#BORRAR LISTA
def eliminar_lista(id_lista):
    connection = create_connection()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return False
    try:
        cursor = connection.cursor()
        # BORRAR COMPRAS Y VENTAS ASOCIADAS A LA LISTA
        cursor.execute("DELETE FROM compras WHERE id_lista = %s", (id_lista,))
        cursor.execute("DELETE FROM ventas WHERE id_lista = %s", (id_lista,))
        # BORRAR PRODUCTOS DE LA LISTA
        cursor.execute("DELETE FROM lista_productos WHERE id_lista = %s", (id_lista,))
        # BORRAR LA LISTA
        cursor.execute("DELETE FROM listas WHERE id_lista = %s", (id_lista,))
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al eliminar lista: {ex}")
        return False
    finally:
        close_connection(connection)