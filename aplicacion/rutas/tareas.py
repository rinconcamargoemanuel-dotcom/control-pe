"""
Tarea de recordatorios automáticos de ARL.

Esta ruta NO requiere haber iniciado sesión — está protegida por un
"token" secreto en la URL (ver TOKEN_TAREAS en configuracion.py), para
que un servicio externo (como cron-job.org) pueda "tocarla" una vez al
día sin necesidad de una cuenta de usuario.

Si el envío de recordatorios falla o no llega, revisa únicamente este
archivo y aplicacion/correo.py.
"""

from datetime import datetime

from flask import Blueprint, request, jsonify

from ..base_datos import obtener_bd
from ..configuracion import MESES, TOKEN_TAREAS
from ..correo import enviar_correo, correo_recordatorio_arl

bp = Blueprint("tareas", __name__)


def _enviar_recordatorios_arl():
    """
    Busca estudiantes que NO tengan cargada la ARL del mes actual y les
    envía un correo recordatorio. Devuelve un resumen (lista de resultados).
    """
    bd = obtener_bd()
    mes_actual = MESES[datetime.now().month - 1]
    anio_actual = datetime.now().year

    estudiantes = bd.execute(
        "SELECT id, nombre, email FROM usuarios WHERE rol='estudiante'"
    ).fetchall()

    resultados = []
    for estudiante in estudiantes:
        ya_cargada = bd.execute(
            "SELECT id FROM arl WHERE estudiante_id=%s AND mes=%s AND anio=%s",
            (estudiante["id"], mes_actual, anio_actual),
        ).fetchone()
        if ya_cargada:
            continue  # este estudiante ya está al día, no se le molesta

        asunto, cuerpo = correo_recordatorio_arl(estudiante["nombre"], mes_actual, anio_actual)
        enviado, error = enviar_correo(estudiante["email"], asunto, cuerpo)
        resultados.append({
            "estudiante": estudiante["nombre"],
            "email": estudiante["email"],
            "enviado": enviado,
            "error": error,
        })
    return resultados


@bp.route("/tareas/recordatorio-arl")
def recordatorio_arl():
    """Pensada para ser llamada por un servicio externo de tipo 'cron' una vez al día."""
    token_recibido = request.args.get("token", "")
    if token_recibido != TOKEN_TAREAS:
        return jsonify({"error": "Token inválido."}), 403

    resultados = _enviar_recordatorios_arl()
    return jsonify({
        "total_recordatorios_enviados": sum(1 for r in resultados if r["enviado"]),
        "total_fallidos": sum(1 for r in resultados if not r["enviado"]),
        "detalle": resultados,
    })

