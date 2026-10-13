"""
Todo lo relacionado con la base de datos MySQL vive aquí:
- Cómo se abre y se cierra la conexión.
- La estructura (tablas) del sistema.
- Los usuarios iniciales de prueba.

Si necesitas agregar una tabla nueva o cambiar una columna, este es el
único archivo que debes modificar.

Requiere tener MySQL instalado y corriendo, y haber creado la base de
datos vacía una sola vez (ver README.md, sección "Base de datos MySQL").
"""

import pymysql # type: ignore
import pymysql.cursors# type: ignore
from flask import g# type: ignore
from werkzeug.security import generate_password_hash# type: ignore

from .configuracion import (
    MYSQL_HOST, MYSQL_PUERTO, MYSQL_USUARIO, MYSQL_PASSWORD, MYSQL_BASE_DATOS,
)


class ConexionBD:
    """
    Pequeño envoltorio sobre la conexión de PyMySQL para poder seguir
    escribiendo `bd.execute(sql, parametros).fetchone()` igual que antes,
    sin tener que manejar cursores manualmente en cada ruta.
    """

    def __init__(self, conexion):
        self._conexion = conexion

    def execute(self, sql, parametros=()):
        cursor = self._conexion.cursor()
        cursor.execute(sql, parametros)
        return cursor

    def commit(self):
        self._conexion.commit()

    def close(self):
        self._conexion.close()


def _conectar():
    """Abre una nueva conexión a MySQL. Cada fila se devuelve como diccionario."""
    conexion = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PUERTO,
        user=MYSQL_USUARIO,
        password=MYSQL_PASSWORD,
        database=MYSQL_BASE_DATOS,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    return ConexionBD(conexion)


def obtener_bd():
    """Devuelve la conexión a la base de datos de la petición actual."""
    if "bd" not in g:
        g.bd = _conectar()
    return g.bd


def cerrar_bd(excepcion=None):
    """Cierra la conexión al terminar la petición (registrado en __init__.py)."""
    bd = g.pop("bd", None)
    if bd is not None:
        bd.close()


def inicializar_bd():
    """Crea las tablas si no existen y siembra los usuarios de prueba."""
    bd = _conectar()
    cursor = bd.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            rol ENUM('estudiante','docente','coordinador','administrador') NOT NULL,
            empresa VARCHAR(150),
            grado VARCHAR(20),
            creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS horas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            estudiante_id INT NOT NULL,
            fecha DATE NOT NULL,
            horas DECIMAL(5,2) NOT NULL,
            actividad TEXT NOT NULL,
            estado ENUM('Pendiente','Aprobado','Rechazado') NOT NULL DEFAULT 'Pendiente',
            observacion TEXT,
            archivo VARCHAR(255),
            FOREIGN KEY (estudiante_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    # Migración: si la tabla "horas" ya existía de antes (sin la columna
    # "archivo"), se la agregamos ahora sin borrar nada de lo que ya había.
    cursor.execute(
        """
        SELECT COUNT(*) c FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'horas' AND column_name = 'archivo'
        """,
        (MYSQL_BASE_DATOS,),
    )
    if cursor.fetchone()["c"] == 0:
        cursor.execute("ALTER TABLE horas ADD COLUMN archivo VARCHAR(255)")
        bd.commit()
    
    # Migración: agrega la columna "modalidad" a usuarios si no existe todavía
    cursor.execute(
        """
        SELECT COUNT(*) c FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'usuarios' AND column_name = 'modalidad'
        """,
        (MYSQL_BASE_DATOS,),
    )
    if cursor.fetchone()["c"] == 0:
        cursor.execute(
            "ALTER TABLE usuarios ADD COLUMN modalidad "
            "ENUM('pasantias_100','etapa_100','mixta_50_50') NULL"
        )
        bd.commit()
    cursor.execute(
        """
        SELECT COUNT(*) c FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'usuarios' AND column_name = 'modalidad_principal'
        """,
        (MYSQL_BASE_DATOS,),
    )
    if cursor.fetchone()["c"] == 0:
        cursor.execute(
            "ALTER TABLE usuarios ADD COLUMN modalidad_principal "
            "ENUM('proyecto_productivo','pasantias','contrato_aprendizaje','monitorias') NULL"
        )
        cursor.execute(
            "ALTER TABLE usuarios ADD COLUMN porcentaje_modalidad ENUM('100','50') NULL"
        )
        cursor.execute(
            "ALTER TABLE usuarios ADD COLUMN modalidad_secundaria "
            "ENUM('proyecto_productivo','pasantias','contrato_aprendizaje','monitorias') NULL"
        )
        bd.commit()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evidencias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            estudiante_id INT NOT NULL,
            descripcion VARCHAR(255) NOT NULL,
            archivo VARCHAR(255) NOT NULL,
            fecha DATE NOT NULL,
            estado ENUM('Pendiente','Aprobado','Rechazado') NOT NULL DEFAULT 'Pendiente',
            FOREIGN KEY (estudiante_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS arl (
            id INT AUTO_INCREMENT PRIMARY KEY,
            estudiante_id INT NOT NULL,
            mes VARCHAR(20) NOT NULL,
            anio INT NOT NULL,
            archivo VARCHAR(255) NOT NULL,
            fecha_carga DATE NOT NULL,
            estado ENUM('Pendiente','Aprobado','Rechazado') NOT NULL DEFAULT 'Pendiente',
            FOREIGN KEY (estudiante_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bitacora (
            id INT AUTO_INCREMENT PRIMARY KEY,
            estudiante_id INT NOT NULL,
            mes VARCHAR(20) NOT NULL,
            anio INT NOT NULL,
            archivo VARCHAR(255) NOT NULL,
            fecha_carga DATE NOT NULL,
            estado ENUM('Pendiente','Aprobado','Rechazado') NOT NULL DEFAULT 'Pendiente',
            FOREIGN KEY (estudiante_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS control_horas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            estudiante_id INT NOT NULL,
            mes VARCHAR(20) NOT NULL,
            anio INT NOT NULL,
            archivo VARCHAR(255) NOT NULL,
            total_horas DECIMAL(6,2) NOT NULL,
            trabaja_despues_6pm ENUM('Si','No') NOT NULL DEFAULT 'No',
            hora_salida VARCHAR(20),
            autorizacion_padres VARCHAR(255),
            fecha_carga DATE NOT NULL,
            estado ENUM('Pendiente','Aprobado','Rechazado') NOT NULL DEFAULT 'Pendiente',
            FOREIGN KEY (estudiante_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            estudiante_id INT NOT NULL,
            tipo ENUM('hoja_vida','documento_identidad','seguro_estudiantil','eps','sisben', 'carta_presentacion') NOT NULL,
            archivo VARCHAR(255) NOT NULL,
            fecha_carga DATE NOT NULL,
            UNIQUE KEY unico_doc_por_tipo (estudiante_id, tipo),
            FOREIGN KEY (estudiante_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    cursor.execute(
        """
        SELECT COUNT(*) c FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'control_horas' AND column_name = 'fase'
        """,
        (MYSQL_BASE_DATOS,),
    )
    if cursor.fetchone()["c"] == 0:
        cursor.execute(
            "ALTER TABLE control_horas ADD COLUMN fase "
            "ENUM('etapa_productiva','pasantias') NULL"
        )
        bd.commit()

    cursor.execute(
        """
        SELECT COUNT(*) c FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'usuarios' AND column_name = 'fecha_inicio_practicas'
        """,
        (MYSQL_BASE_DATOS,),
    )
    if cursor.fetchone()["c"] == 0:
        cursor.execute(
            "ALTER TABLE usuarios ADD COLUMN fecha_inicio_practicas DATE NULL"
        )
        bd.commit()
    bd.commit()

    # Usuarios de prueba, solo si la tabla usuarios está vacía
    cursor.execute("SELECT COUNT(*) c FROM usuarios")
    if cursor.fetchone()["c"] == 0:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s,%s,%s,%s)",
            ("Administrador", "admin@controlpe.edu.co",
             generate_password_hash("admin123"), "administrador"),
        )
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s,%s,%s,%s)",
            ("Ing. Yefferzon Perea Valero", "docente@controlpe.edu.co",
             generate_password_hash("docente123"), "docente"),
        )
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s,%s,%s,%s)",
            ("Coordinador Prácticas", "coordinador@controlpe.edu.co",
             generate_password_hash("coord123"), "coordinador"),
        )
        bd.commit()
    cursor.close()
    bd.close()