"""
Bitácora de horas del estudiante: registrar y listar horas trabajadas.

Si hay un error al registrar o ver las horas, revisa únicamente este archivo.
"""

import os
from datetime import datetime

from flask import ( # type: ignore
    Blueprint, render_template, request, redirect, url_for,
    session, flash, current_app
)
from werkzeug.utils import secure_filename# type: ignore

from ..auxiliares import inicio_sesion_requerido, roles_requeridos, archivo_permitido
from ..base_datos import obtener_bd

bp = Blueprint("horas", __name__)


@bp.route("/horas", methods=["GET", "POST"])
@inicio_sesion_requerido
@roles_requeridos("estudiante")
def horas():
    bd = obtener_bd()
    uid = session["user_id"]
    if request.method == "POST":
        fecha = request.form["fecha"]
        cantidad = request.form["horas"]
        actividad = request.form["actividad"].strip()

        nombre_archivo = None
        archivo = request.files.get("archivo")
        if not archivo or not archivo.filename:
            flash("Debes adjuntar una foto o escaneo del control de horas físico.", "danger")
            return redirect(url_for("horas.horas"))
        if not archivo_permitido(archivo.filename):
            flash("Archivo no válido. Formatos permitidos: pdf, png, jpg, jpeg, docx, xlsx.", "danger")
            return redirect(url_for("horas.horas"))
        nombre_archivo = secure_filename(
            f"horas_{uid}_{datetime.now().timestamp()}_{archivo.filename}"
        )
        archivo.save(os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_archivo))
        
        bd.execute(
            "INSERT INTO horas (estudiante_id, fecha, horas, actividad, archivo) VALUES (%s,%s,%s,%s,%s)",
            (uid, fecha, cantidad, actividad, nombre_archivo),
        )
        bd.commit()
        flash("Registro de horas guardado. Queda pendiente de revisión.", "success")
        return redirect(url_for("horas.horas"))

    registros = bd.execute(
        "SELECT * FROM horas WHERE estudiante_id=%s ORDER BY fecha DESC", (uid,)
    ).fetchall()
    return render_template("horas/horas.html", registros=registros)