"""
Vista de detalle de un estudiante (para docente/coordinador/administrador)
y validación (aprobar/rechazar) de bitácora, control de horas, evidencias y ARL.

Si hay un error al ver el detalle de un estudiante o al aprobar/rechazar
un registro, revisa únicamente este archivo.
"""

from flask import Blueprint, render_template, redirect, url_for, flash

from ..auxiliares import inicio_sesion_requerido, roles_requeridos
from ..base_datos import obtener_bd
from ..configuracion import META_HORAS

bp = Blueprint("estudiantes", __name__)


@bp.route("/estudiante/<int:estudiante_id>")
@inicio_sesion_requerido
@roles_requeridos("docente", "coordinador", "administrador")
def ver(estudiante_id):
    bd = obtener_bd()
    estudiante = bd.execute("SELECT * FROM usuarios WHERE id=%s", (estudiante_id,)).fetchone()
    if not estudiante:
        flash("Estudiante no encontrado.", "danger")
        return redirect(url_for("panel.principal"))

    bitacora_registros = bd.execute(
        "SELECT * FROM bitacora WHERE estudiante_id=%s ORDER BY anio DESC, id DESC", (estudiante_id,)
    ).fetchall()
    control_horas_registros = bd.execute(
        "SELECT * FROM control_horas WHERE estudiante_id=%s ORDER BY anio DESC, id DESC", (estudiante_id,)
    ).fetchall()
    evidencias = bd.execute(
        "SELECT * FROM evidencias WHERE estudiante_id=%s ORDER BY fecha DESC", (estudiante_id,)
    ).fetchall()
    arl_registros = bd.execute(
        "SELECT * FROM arl WHERE estudiante_id=%s ORDER BY anio DESC, id DESC", (estudiante_id,)
    ).fetchall()
    documentos_registros = bd.execute(
        "SELECT * FROM documentos WHERE estudiante_id=%s", (estudiante_id,)
    ).fetchall()
    total_aprobadas = float(bd.execute(
        "SELECT COALESCE(SUM(total_horas),0) t FROM control_horas WHERE estudiante_id=%s AND estado='Aprobado'",
        (estudiante_id,),
    ).fetchone()["t"])
    porcentaje = min(100, round((total_aprobadas / META_HORAS) * 100)) if META_HORAS else 0

    return render_template(
        "estudiantes/ver.html", estudiante=estudiante,
        bitacora_registros=bitacora_registros, control_horas_registros=control_horas_registros,
        evidencias=evidencias, arl_registros=arl_registros, documentos_registros=documentos_registros,
        total_aprobadas=total_aprobadas, meta_horas=META_HORAS, porcentaje=porcentaje,
    )


@bp.route("/validar/<tipo>/<int:registro_id>/<accion>")
@inicio_sesion_requerido
@roles_requeridos("docente", "coordinador")
def validar(tipo, registro_id, accion):
    tablas = {
        "bitacora": "bitacora", "control_horas": "control_horas",
        "evidencias": "evidencias", "arl": "arl",
    }
    if tipo not in tablas or accion not in ("Aprobado", "Rechazado"):
        flash("Operación no válida.", "danger")
        return redirect(url_for("panel.principal"))

    bd = obtener_bd()
    tabla = tablas[tipo]
    registro = bd.execute(f"SELECT * FROM {tabla} WHERE id=%s", (registro_id,)).fetchone()
    if not registro:
        flash("Registro no encontrado.", "danger")
        return redirect(url_for("panel.principal"))

    bd.execute(f"UPDATE {tabla} SET estado=%s WHERE id=%s", (accion, registro_id))
    bd.commit()
    flash(f"Registro marcado como {accion}.", "success")
    return redirect(url_for("estudiantes.ver", estudiante_id=registro["estudiante_id"]))