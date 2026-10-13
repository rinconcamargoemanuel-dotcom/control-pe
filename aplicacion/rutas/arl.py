"""
Control de afiliación ARL mensual del estudiante.

Si hay un error al subir o ver la afiliación ARL, revisa únicamente
este archivo.
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

bp = Blueprint("arl", __name__)


@bp.route("/arl", methods=["GET", "POST"])
@inicio_sesion_requerido
@roles_requeridos("estudiante")
def arl():
    bd = obtener_bd()
    uid = session["user_id"]
    if request.method == "POST":
        mes = request.form["mes"]
        anio = request.form["anio"]
        archivo = request.files.get("archivo")
        if archivo and archivo.filename and archivo_permitido(archivo.filename):
            nombre_seguro = secure_filename(f"arl_{uid}_{mes}_{anio}_{archivo.filename}")
            archivo.save(os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_seguro))
            existente = bd.execute(
                "SELECT id FROM arl WHERE estudiante_id=%s AND mes=%s AND anio=%s",
                (uid, mes, anio),
            ).fetchone()
            if existente:
                bd.execute(
                    "UPDATE arl SET archivo=%s, fecha_carga=%s, estado='Pendiente' WHERE id=%s",
                    (nombre_seguro, datetime.now().strftime("%Y-%m-%d"), existente["id"]),
                )
            else:
                bd.execute(
                    "INSERT INTO arl (estudiante_id, mes, anio, archivo, fecha_carga) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (uid, mes, anio, nombre_seguro, datetime.now().strftime("%Y-%m-%d")),
                )
            bd.commit()
            flash("Afiliación ARL cargada correctamente.", "success")
        else:
            flash("Archivo no válido.", "danger")
        return redirect(url_for("arl.arl"))

    registros = bd.execute(
        "SELECT * FROM arl WHERE estudiante_id=%s ORDER BY anio DESC, id DESC", (uid,)
    ).fetchall()
    return render_template(
        "arl/arl.html", registros=registros, meses=MESES,
        anio_actual=datetime.now().year, mes_actual=MESES[datetime.now().month - 1],
    )
