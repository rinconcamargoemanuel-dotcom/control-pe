"""
Historial de todo lo que el estudiante ha subido: Bitácora, Control de
Horas, ARL y Evidencias, todo junto en una sola tabla ordenada por fecha.

Si hay un error en esta pantalla, revisa únicamente este archivo.
"""

from flask import Blueprint, render_template, session

from ..auxiliares import inicio_sesion_requerido, roles_requeridos
from ..base_datos import obtener_bd

bp = Blueprint("historial", __name__)


@bp.route("/historial")
@inicio_sesion_requerido
@roles_requeridos("estudiante")
def historial():
    bd = obtener_bd()
    uid = session["user_id"]

    registros = []

    for r in bd.execute(
        "SELECT mes, anio, archivo, estado, fecha_carga FROM bitacora "
        "WHERE estudiante_id=%s", (uid,)
    ).fetchall():
        registros.append({
            "tipo": "Bitácora", "detalle": f"{r['mes']} {r['anio']}",
            "archivo": r["archivo"], "estado": r["estado"], "fecha": r["fecha_carga"],
        })

    for r in bd.execute(
        "SELECT mes, anio, archivo, estado, fecha_carga FROM control_horas "
        "WHERE estudiante_id=%s", (uid,)
    ).fetchall():
        registros.append({
            "tipo": "Control de Horas", "detalle": f"{r['mes']} {r['anio']}",
            "archivo": r["archivo"], "estado": r["estado"], "fecha": r["fecha_carga"],
        })

    for r in bd.execute(
        "SELECT mes, anio, archivo, estado, fecha_carga FROM arl "
        "WHERE estudiante_id=%s", (uid,)
    ).fetchall():
        registros.append({
            "tipo": "ARL", "detalle": f"{r['mes']} {r['anio']}",
            "archivo": r["archivo"], "estado": r["estado"], "fecha": r["fecha_carga"],
        })

    for r in bd.execute(
        "SELECT descripcion, archivo, estado, fecha FROM evidencias "
        "WHERE estudiante_id=%s", (uid,)
    ).fetchall():
        registros.append({
            "tipo": "Evidencia", "detalle": r["descripcion"],
            "archivo": r["archivo"], "estado": r["estado"], "fecha": r["fecha"],
        })

    registros.sort(key=lambda r: r["fecha"], reverse=True)

    return render_template("historial/historial.html", registros=registros)