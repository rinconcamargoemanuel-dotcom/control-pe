"""
Configuración central de la aplicación.
Si necesitas cambiar rutas, claves, carpetas o los datos de conexión a
la base de datos MySQL, este es el único archivo que debes tocar.
"""

import os

DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLAVE_SECRETA = os.environ.get(
    "SECRET_KEY", "control-pe-clave-secreta-cambiar-en-produccion"
)

# ---------------------------------------------------------------------------
# Conexión a MySQL
# ---------------------------------------------------------------------------
# Puedes dejar estos valores por defecto para trabajar en tu propio
# computador (MySQL instalado localmente), o definir las variables de
# entorno correspondientes para usar una base de datos remota (por
# ejemplo, en un hosting como Render, Railway o PlanetScale).
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PUERTO = int(os.environ.get("MYSQL_PUERTO", "3306"))
MYSQL_USUARIO = os.environ.get("MYSQL_USUARIO", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_BASE_DATOS = os.environ.get("MYSQL_BASE_DATOS", "control_pe")

CARPETA_SUBIDAS = os.path.join(
    DIRECTORIO_BASE, "aplicacion", "estaticos", "imagenes", "subidas"
)

EXTENSIONES_PERMITIDAS = {"pdf", "png", "jpg", "jpeg", "docx", "xlsx"}

# Meta de horas exigidas para completar las prácticas empresariales /
# proyecto productivo. Ajusta este número según lo que exija tu institución.
META_HORAS = int(os.environ.get("META_HORAS", "864"))

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
    "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

# ---------------------------------------------------------------------------
# Correo electrónico (recordatorios automáticos de ARL)
# ---------------------------------------------------------------------------
# IMPORTANTE: Render bloquea las conexiones salientes por SMTP (puertos 25,
# 465, 587) en su plan gratuito, así que el envío de correos NO se hace por
# SMTP. En su lugar, se usa la API de Brevo (antes Sendinblue), un servicio
# gratuito (300 correos/día) que envía por HTTPS, sin ese bloqueo.
# Ver README.md, sección "Recordatorios por correo", para la guía paso a
# paso de cómo crear tu cuenta gratuita y obtener la API Key.
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
EMAIL_REMITENTE = os.environ.get("EMAIL_REMITENTE", "")
EMAIL_REMITENTE_NOMBRE = os.environ.get("EMAIL_REMITENTE_NOMBRE", "Control P.E")

# Token secreto para proteger el enlace que dispara el envío de
# recordatorios (ver aplicacion/rutas/tareas.py). Cámbialo por algo propio.
TOKEN_TAREAS = os.environ.get("TOKEN_TAREAS", "cambia-este-token-por-uno-propio")
