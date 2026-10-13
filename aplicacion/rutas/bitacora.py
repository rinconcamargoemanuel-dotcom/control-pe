"""
Carga de la bitácora mensual de seguimiento (formato SENA), un solo
archivo por mes.

Si hay un error al subir o ver la bitácora, revisa únicamente este archivo.
"""

import os
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, flash, current_app
)
from werkzeug.utils import secure_filename

from ..auxiliares import inicio_sesion_requerido, roles_requeridos, archivo_permitido
from ..base_datos import obtener_bd
from ..configuracion import MESES

bp = Blueprint("bitacora", __name__)


@bp.route("/bitacora", methods=["GET", "POST"])
@inicio_sesion_requerido
@roles_requeridos("estudiante")
def bitacora():
    bd = obtener_bd()
    uid = session["user_id"]
    if request.method == "POST":
        mes = request.form["mes"]
        anio = request.form["anio"]
        archivo = request.files.get("archivo")
        if archivo and archivo.filename and archivo_permitido(archivo.filename):
            nombre_seguro = secure_filename(f"bitacora_{uid}_{mes}_{anio}_{archivo.filename}")
            archivo.save(os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_seguro))
            existente = bd.execute(
                "SELECT id FROM bitacora WHERE estudiante_id=%s AND mes=%s AND anio=%s",
                (uid, mes, anio),
            ).fetchone()
            if existente:
                bd.execute(
                    "UPDATE bitacora SET archivo=%s, fecha_carga=%s, estado='Pendiente' WHERE id=%s",
                    (nombre_seguro, datetime.now().strftime("%Y-%m-%d"), existente["id"]),
                )
            else:
                bd.execute(
                    "INSERT INTO bitacora (estudiante_id, mes, anio, archivo, fecha_carga) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (uid, mes, anio, nombre_seguro, datetime.now().strftime("%Y-%m-%d")),
                )
            bd.commit()
            flash("Bitácora cargada correctamente.", "success")
        else:
            flash("Archivo no válido.", "danger")
        return redirect(url_for("bitacora.bitacora"))

    registros = bd.execute(
        "SELECT * FROM bitacora WHERE estudiante_id=%s ORDER BY anio DESC, id DESC", (uid,)
    ).fetchall()
    return render_template(
        "bitacora/bitacora.html", registros=registros, meses=MESES,
        anio_actual=datetime.now().year, mes_actual=MESES[datetime.now().month - 1],
    )