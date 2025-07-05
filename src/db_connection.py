import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # SERVIDOR DE LA BASE DE DATOS
            user="root",       # USUARIO DE MYSQL
            password="empanadas.com",  # CONTRASEÑA DE MYSQL
            database="VendorAtlas"  # NOMBRE DE LA BASE DE DATOS
        )
        if connection.is_connected():
            print("Conexión exitosa a la base de datos")
        return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print("Conexión cerrada")