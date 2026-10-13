"""
Documentos importantes del estudiante: hoja de vida, documento de
identidad, seguro estudiantil, EPS y SISBEN. Cada uno se puede subir
o reemplazar en cualquier momento.

Si hay un error al subir o ver estos documentos, revisa únicamente
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

bp = Blueprint("documentos", __name__)

TIPOS_DOCUMENTOS = {
    "hoja_vida": "Hoja de vida",
    "documento_identidad": "Documento de identidad",
    "seguro_estudiantil": "Seguro estudiantil",
    "eps": "EPS",
    "sisben": "SISBEN",
    "carta_presentacion": "Carta de presentación",
}


@bp.route("/documentos", methods=["GET", "POST"])
@inicio_sesion_requerido
@roles_requeridos("estudiante")
def documentos():
    bd = obtener_bd()
    uid = session["user_id"]

    if request.method == "POST":
        tipo = request.form.get("tipo")
        if tipo not in TIPOS_DOCUMENTOS:
            flash("Tipo de documento no válido.", "danger")
            return redirect(url_for("documentos.documentos"))

        archivo = request.files.get("archivo")
        if not (archivo and archivo.filename and archivo_permitido(archivo.filename)):
            flash("Archivo no válido. Formatos permitidos: pdf, png, jpg, jpeg, docx, xlsx.", "danger")
            return redirect(url_for("documentos.documentos"))

        nombre_seguro = secure_filename(f"{tipo}_{uid}_{datetime.now().timestamp()}_{archivo.filename}")
        archivo.save(os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_seguro))

        existente = bd.execute(
            "SELECT id FROM documentos WHERE estudiante_id=%s AND tipo=%s", (uid, tipo)
        ).fetchone()
        if existente:
            bd.execute(
                "UPDATE documentos SET archivo=%s, fecha_carga=%s WHERE id=%s",
                (nombre_seguro, datetime.now().strftime("%Y-%m-%d"), existente["id"]),
            )
        else:
            bd.execute(
                "INSERT INTO documentos (estudiante_id, tipo, archivo, fecha_carga) "
                "VALUES (%s,%s,%s,%s)",
                (uid, tipo, nombre_seguro, datetime.now().strftime("%Y-%m-%d")),
            )
        flash(f"{TIPOS_DOCUMENTOS[tipo]} cargado correctamente.", "success")
        return redirect(url_for("documentos.documentos"))

    primera_vez = request.args.get("primera_vez") == "1"

    registros = bd.execute(
        "SELECT * FROM documentos WHERE estudiante_id=%s", (uid,)
    ).fetchall()
    documentos_por_tipo = {r["tipo"]: r for r in registros}

    return render_template(
        "documentos/documentos.html",
        tipos=TIPOS_DOCUMENTOS,
        documentos_por_tipo=documentos_por_tipo,
        primera_vez=primera_vez,
    )