"""
Panel principal (dashboard). Muestra información distinta según el rol:
- Estudiante: resumen de sus propias horas, evidencias y ARL.
- Docente / Coordinador / Administrador: listado y resumen de estudiantes.

Si hay un error en la pantalla de inicio tras iniciar sesión, revisa
únicamente este archivo.
"""

from datetime import datetime

from flask import Blueprint, render_template, session, request

from ..auxiliares import inicio_sesion_requerido
from ..base_datos import obtener_bd
from ..configuracion import MESES, META_HORAS

bp = Blueprint("panel", __name__)


@bp.route("/dashboard")
@inicio_sesion_requerido
def principal():
    bd = obtener_bd()
    rol = session["rol"]

    if rol == "estudiante":
        uid = session["user_id"]
        total_horas = bd.execute(
            "SELECT COALESCE(SUM(total_horas),0) t FROM control_horas "
            "WHERE estudiante_id=%s AND estado IN ('Aprobado','Pendiente')",
            (uid,),
        ).fetchone()["t"]
        pendientes = bd.execute(
            "SELECT COUNT(*) c FROM control_horas WHERE estudiante_id=%s AND estado='Pendiente'", (uid,)
        ).fetchone()["c"]
        hay_horas_pendientes = pendientes > 0
        evidencias = bd.execute(
            "SELECT COUNT(*) c FROM evidencias WHERE estudiante_id=%s", (uid,)
        ).fetchone()["c"]
        mes_actual = MESES[datetime.now().month - 1]
        anio_actual = datetime.now().year
        arl_mes = bd.execute(
            "SELECT * FROM arl WHERE estudiante_id=%s AND mes=%s AND anio=%s",
            (uid, mes_actual, anio_actual),
        ).fetchone()
        usuario_datos = bd.execute(
            "SELECT modalidad_principal, porcentaje_modalidad, "
            "modalidad_secundaria FROM usuarios WHERE id=%s", (uid,)
        ).fetchone()
        bitacora_mes = bd.execute(
            "SELECT * FROM bitacora WHERE estudiante_id=%s AND mes=%s AND anio=%s",
            (uid, mes_actual, anio_actual),
        ).fetchone()
        control_horas_mes = bd.execute(
            "SELECT * FROM control_horas WHERE estudiante_id=%s AND mes=%s AND anio=%s",
            (uid, mes_actual, anio_actual),
        ).fetchone()

        # Seguimiento real: horas acumuladas vs. meta, y horas que faltan
        total_horas = float(total_horas)
        porcentaje = min(100, round((total_horas / META_HORAS) * 100)) if META_HORAS else 0
        horas_faltantes = max(0, META_HORAS - total_horas)

        return render_template(
            "panel/estudiante.html",
            total_horas=total_horas, pendientes=pendientes,
            hay_horas_pendientes=hay_horas_pendientes,
            evidencias=evidencias, arl_mes=arl_mes, bitacora_mes=bitacora_mes,
            control_horas_mes=control_horas_mes, mes_actual=mes_actual,
            meta_horas=META_HORAS, porcentaje=porcentaje, horas_faltantes=horas_faltantes,
            modalidad_principal=usuario_datos["modalidad_principal"] if usuario_datos else None,
            porcentaje_modalidad=usuario_datos["porcentaje_modalidad"] if usuario_datos else None,
            modalidad_secundaria=usuario_datos["modalidad_secundaria"] if usuario_datos else None,
        )

    # Docente, coordinador y administrador ven el listado de estudiantes
    busqueda = request.args.get("buscar", "").strip()
    if busqueda:
        estudiantes = bd.execute(
            "SELECT * FROM usuarios WHERE rol='estudiante' AND nombre LIKE %s ORDER BY nombre",
            (f"%{busqueda}%",),
        ).fetchall()
    else:
        estudiantes = bd.execute(
            "SELECT * FROM usuarios WHERE rol='estudiante' ORDER BY nombre"
        ).fetchall()

    resumen = []
    for e in estudiantes:
        horas = float(bd.execute(
            "SELECT COALESCE(SUM(total_horas),0) t FROM control_horas WHERE estudiante_id=%s AND estado='Aprobado'",
            (e["id"],),
        ).fetchone()["t"])
        pend_horas = bd.execute(
            "SELECT COUNT(*) c FROM control_horas WHERE estudiante_id=%s AND estado='Pendiente'", (e["id"],)
        ).fetchone()["c"]
        pend_evid = bd.execute(
            "SELECT COUNT(*) c FROM evidencias WHERE estudiante_id=%s AND estado='Pendiente'", (e["id"],)
        ).fetchone()["c"]
        pend_arl = bd.execute(
            "SELECT COUNT(*) c FROM arl WHERE estudiante_id=%s AND estado='Pendiente'", (e["id"],)
        ).fetchone()["c"]
        porcentaje = min(100, round((horas / META_HORAS) * 100)) if META_HORAS else 0
        resumen.append({
            "estudiante": e, "horas": horas, "porcentaje": porcentaje,
            "pend_horas": pend_horas, "pend_evid": pend_evid, "pend_arl": pend_arl,
        })

    return render_template(
        "panel/personal.html", resumen=resumen,
        meta_horas=META_HORAS, busqueda=busqueda,
    ) 