-- Base de datos SEPARADA, solo para ejecutar las pruebas automatizadas.
-- No mezcla datos con la base de datos real de producción/uso diario.
--
-- Ejecuta este script UNA SOLA VEZ:
--   mysql -u root -p < basedatos/crear_base_datos_pruebas.sql

CREATE DATABASE IF NOT EXISTS control_pe_pruebas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
