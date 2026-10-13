"""
Configuración compartida para las pruebas automatizadas (pytest).

IMPORTANTE: estas pruebas usan una base de datos SEPARADA
("control_pe_pruebas") para no tocar nunca los datos reales del sistema.
Antes de correr las pruebas, créala una sola vez:

    mysql -u root -p < basedatos/crear_base_datos_pruebas.sql

Cómo ejecutar las pruebas:

    pip install pytest
    pytest pruebas/ -v
"""

import os
import sys

# Apunta la aplicación a la base de datos de pruebas ANTES de importarla
os.environ.setdefault("MYSQL_BASE_DATOS", "control_pe_pruebas")
os.environ.setdefault("MYSQL_USUARIO", os.environ.get("MYSQL_USUARIO", "root"))
os.environ.setdefault("MYSQL_PASSWORD", os.environ.get("MYSQL_PASSWORD", ""))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pymysql

from aplicacion import crear_app
from aplicacion.configuracion import (
    MYSQL_HOST, MYSQL_PUERTO, MYSQL_USUARIO, MYSQL_PASSWORD, MYSQL_BASE_DATOS,
)


def _limpiar_tablas():
    """Vacía todas las tablas antes de cada prueba, para que no interfieran entre sí."""
    conexion = pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PUERTO, user=MYSQL_USUARIO,
        password=MYSQL_PASSWORD, database=MYSQL_BASE_DATOS, charset="utf8mb4",
    )
    cursor = conexion.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    for tabla in ("horas", "evidencias", "arl", "usuarios"):
        cursor.execute(f"TRUNCATE TABLE {tabla}")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    conexion.commit()
    cursor.close()
    conexion.close()


@pytest.fixture()
def app():
    aplicacion_flask = crear_app()
    aplicacion_flask.config.update({"TESTING": True})
    _limpiar_tablas()
    # inicializar_bd() (llamada dentro de crear_app) vuelve a sembrar los
    # 3 usuarios de prueba después del TRUNCATE, así que los recreamos aquí:
    from aplicacion.base_datos import inicializar_bd
    inicializar_bd()
    yield aplicacion_flask


@pytest.fixture()
def cliente(app):
    return app.test_client()
