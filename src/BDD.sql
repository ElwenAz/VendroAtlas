CREATE DATABASE VendorAtlas;
USE VendorAtlas;

-- Tabla de tipos de usuario
CREATE TABLE tipos_usuario (
    id_tipo_usuario INT AUTO_INCREMENT PRIMARY KEY,
    descripcion CHAR(50) NOT NULL UNIQUE
);

-- Insertar tipos de usuario
INSERT INTO tipos_usuario (descripcion) VALUES
('dueño'),
('vendedor');

-- Tabla de usuarios
CREATE TABLE usuarios (
    correo CHAR(100) NOT NULL PRIMARY KEY,
    nombre CHAR(100) NOT NULL,
    telefono CHAR(15),
    contrasena TEXT NOT NULL,
    id_tipo_usuario INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tipo_usuario) REFERENCES tipos_usuario(id_tipo_usuario)
);

-- Tabla de productos
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre CHAR(100) NOT NULL,
    tipo CHAR(50) NOT NULL, -- Fruta o Verdura
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de compras
CREATE TABLE compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad_kg DECIMAL(10,2) NOT NULL,
    precio_kg DECIMAL(10,2) NOT NULL,
    calidad CHAR(10) NOT NULL, -- 1ra, 2da, 3ra
    fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Tabla de ventas
CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    calidad CHAR(10) NOT NULL, -- 1ra, 2da, 3ra
    cantidad_kg DECIMAL(10,2) NOT NULL,
    precio_kg DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Tabla de inventarios
CREATE TABLE inventarios (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    nombre CHAR(100) NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de listas
CREATE TABLE listas (
    id_lista INT AUTO_INCREMENT PRIMARY KEY,
    id_inventario INT NOT NULL,
    nombre_lista CHAR(100) NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultima_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_inventario) REFERENCES inventarios(id_inventario)
);

-- Relación entre listas y productos
CREATE TABLE lista_productos (
    id_lista INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_lista, id_producto),
    FOREIGN KEY (id_lista) REFERENCES listas(id_lista),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Tabla de desperdicios (opcional, como una lista especial)
CREATE TABLE desperdicios (
    id_desperdicio INT AUTO_INCREMENT PRIMARY KEY,
    id_lista INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_lista) REFERENCES listas(id_lista),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);


ALTER TABLE usuarios ADD COLUMN es_cuenta_inicial BOOLEAN DEFAULT FALSE;

ALTER TABLE productos 
    MODIFY COLUMN precio DECIMAL(10,2) NULL,
    MODIFY COLUMN descripcion TEXT NULL,
    MODIFY COLUMN cantidad DECIMAL(10,2) NULL;
    
ALTER TABLE listas ADD COLUMN id_lista_padre INT NULL;

ALTER TABLE lista_productos
    ADD COLUMN kg_c1 DECIMAL(10,2) DEFAULT 0,
    ADD COLUMN kg_c2 DECIMAL(10,2) DEFAULT 0,
    ADD COLUMN kg_c3 DECIMAL(10,2) DEFAULT 0;
    
ALTER TABLE compras
    ADD COLUMN total DECIMAL(10,2) AS (cantidad_kg * precio_kg) STORED,
    ADD COLUMN id_lista INT NULL,
    ADD FOREIGN KEY (id_lista) REFERENCES listas(id_lista);
    
ALTER TABLE ventas
    ADD COLUMN id_lista INT NULL,
    ADD FOREIGN KEY (id_lista) REFERENCES listas(id_lista);
    
ALTER TABLE ventas
    MODIFY COLUMN total DECIMAL(10,2) AS (cantidad_kg * precio_kg) STORED;
    
ALTER TABLE usuarios
    ADD COLUMN id_inventario INT NULL,
    ADD FOREIGN KEY (id_inventario) REFERENCES inventarios(id_inventario),
    ADD COLUMN ultima_actividad DATETIME NULL;
    
ALTER TABLE usuarios ADD UNIQUE(nombre);
    
ALTER TABLE compras
    ADD COLUMN nombre_usuario CHAR(100) NOT NULL,
    ADD FOREIGN KEY (nombre_usuario) REFERENCES usuarios(nombre);

ALTER TABLE ventas
    ADD COLUMN nombre_usuario CHAR(100) NOT NULL,
    ADD FOREIGN KEY (nombre_usuario) REFERENCES usuarios(nombre);
    
INSERT IGNORE INTO usuarios (correo, nombre, contrasena, id_tipo_usuario, fecha_creacion)
VALUES ('transferencia@auto.com', 'TRANSFERENCIA', 'auto', 1, NOW());

--------------------------------------------------------------------------
USE VendorAtlas;
SHOW TABLES;
SELECT * FROM usuarios;
SELECT * FROM productos;
SELECT * FROM compras;
SELECT * FROM ventas;
SELECT * FROM tipos_usuario;
SELECT * FROM inventarios;
SELECT * FROM lista_productos;
SELECT * FROM listas;

DESCRIBE productos;

SELECT * FROM listas WHERE id_inventario = 4;

SELECT 
    p.id_producto,
    p.nombre AS nombre_producto,
    p.tipo,
    p.descripcion,
    p.precio,
    lp.cantidad
FROM lista_productos lp
JOIN productos p ON p.id_producto = lp.id_producto
WHERE lp.id_lista = 1;

SELECT c.fecha_compra, p.nombre AS producto, c.cantidad_kg AS kilos, c.precio_kg, c.total, c.calidad
FROM compras c
JOIN productos p ON c.id_producto = p.id_producto
ORDER BY c.fecha_compra DESC;

------------------------------------------------------
INSERT INTO listas (id_inventario, nombre_lista, fecha_creacion, ultima_modificacion)
VALUES (1, 'Semana 1', '2024-05-01 10:05:00', '2024-05-01 10:05:00');
-- id_lista = 2

INSERT INTO productos (nombre, tipo, descripcion, precio, cantidad, fecha_creacion)
VALUES 
('Manzana', 'Fruta', 'Manzana roja', 20.00, 0, '2024-05-01 10:10:00'),
('Zanahoria', 'Verdura', 'Zanahoria fresca', 15.00, 0, '2024-05-01 10:11:00'),
('Plátano', 'Fruta', 'Plátano Tabasco', 18.00, 0, '2024-05-01 10:12:00');

INSERT INTO lista_productos (id_lista, id_producto, cantidad, kg_c1, kg_c2, kg_c3)
VALUES
(2, 1, 0, 0, 0, 0), -- Manzana
(2, 2, 0, 0, 0, 0), -- Zanahoria
(2, 3, 0, 0, 0, 0); -- Plátano

-- Lunes 2 de junio 2025
INSERT INTO compras (id_lista, id_producto, calidad, cantidad_kg, precio_kg, fecha_compra)
VALUES (2, 1, '1ra', 50, 20.00, '2025-06-02 09:00:00'); -- Manzana

-- Martes 3 de junio 2025
INSERT INTO compras (id_lista, id_producto, calidad, cantidad_kg, precio_kg, fecha_compra)
VALUES (2, 2, '2da', 30, 12.00, '2025-06-03 10:00:00'); -- Zanahoria

-- Miércoles 4 de junio 2025
INSERT INTO compras (id_lista, id_producto, calidad, cantidad_kg, precio_kg, fecha_compra)
VALUES (2, 3, '1ra', 40, 18.00, '2025-06-04 11:00:00'); -- Plátano

-- Jueves 5 de junio 2025
INSERT INTO ventas (id_lista, id_producto, calidad, cantidad_kg, precio_kg, fecha_venta)
VALUES (2, 1, '1ra', 20, 25.00, '2025-06-05 12:00:00'); -- Manzana

-- Viernes 6 de junio 2025
INSERT INTO ventas (id_lista, id_producto, calidad, cantidad_kg, precio_kg, fecha_venta)
VALUES (2, 2, '2da', 10, 15.00, '2025-06-06 13:00:00'); -- Zanahoria

-- Sábado 7 de junio 2025
INSERT INTO ventas (id_lista, id_producto, calidad, cantidad_kg, precio_kg, fecha_venta)
VALUES (2, 3, '1ra', 15, 22.00, '2025-06-07 14:00:00'); -- Plátano

