-- Ejecuta este script UNA SOLA VEZ en MySQL para crear la base de datos vacía.
-- Ejemplo desde la terminal:
--   mysql -u root -p < basedatos/crear_base_datos.sql
--
-- Las tablas (usuarios, horas, evidencias, arl) las crea automáticamente
-- la aplicación la primera vez que se ejecuta (ver aplicacion/base_datos.py).

CREATE DATABASE IF NOT EXISTS control_pe
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
