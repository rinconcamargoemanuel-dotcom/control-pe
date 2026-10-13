"""
Funciones de apoyo reutilizadas por varias rutas:
- Verificar si un archivo subido tiene una extensión permitida.
- Exigir que el usuario haya iniciado sesión.
- Exigir que el usuario tenga cierto rol (estudiante, docente, etc.).

Si necesitas cambiar las reglas de permisos, este es el único archivo
que debes tocar.
"""

from functools import wraps

from flask import session, flash, redirect, url_for

from .configuracion import EXTENSIONES_PERMITIDAS


def archivo_permitido(nombre_archivo):
    return (
        "." in nombre_archivo
        and nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS
    )


def inicio_sesion_requerido(f):
    """Decorador: bloquea la ruta si no hay una sesión iniciada."""
    @wraps(f)
    def envoltura(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("autenticacion.iniciar_sesion"))
        return f(*args, **kwargs)
    return envoltura


def roles_requeridos(*roles):
    """Decorador: bloquea la ruta si el rol de la sesión no está permitido."""
    def decorador(f):
        @wraps(f)
        def envoltura(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("autenticacion.iniciar_sesion"))
            if session.get("rol") not in roles:
                flash("No tienes permisos para acceder a esta sección.", "danger")
                return redirect(url_for("panel.principal"))
            return f(*args, **kwargs)
        return envoltura
    return decorador
