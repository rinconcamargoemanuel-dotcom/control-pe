"""
Control de Horas: carga obligatoria mensual del control de horas
(con la pregunta de si trabaja después de las 6pm y la autorización de
padres si aplica) + evidencias opcionales de las actividades realizadas.

Si hay un error al subir o ver el control de horas o las evidencias,
revisa únicamente este archivo.
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

bp = Blueprint("evidencias", __name__)


@bp.route("/evidencias", methods=["GET", "POST"])
@inicio_sesion_requerido
@roles_requeridos("estudiante")
def evidencias():
    bd = obtener_bd()
    uid = session["user_id"]

    if request.method == "POST":
        tipo_formulario = request.form.get("tipo_formulario")

                # ------------------------------------------------------------
        # Formulario 1: Control de horas (obligatorio, mensual)
        # ------------------------------------------------------------
        if tipo_formulario == "control_horas":
            total_horas = request.form["total_horas"]
            try:
                if float(total_horas) > 90:
                    flash("El máximo de horas permitido al mes es 90. Revisa el valor ingresado.", "danger")
                    return redirect(url_for("evidencias.evidencias"))
            except ValueError:
                flash("El total de horas debe ser un número válido.", "danger")
                return redirect(url_for("evidencias.evidencias"))
            usuario_actual = bd.execute(
                "SELECT modalidad, grado FROM usuarios WHERE id=%s", (uid,)
            ).fetchone()
            if usuario_actual["modalidad"] == "etapa_100":
                fase = "etapa_productiva"
            elif usuario_actual["modalidad"] == "pasantias_100":
                fase = "pasantias"
            elif usuario_actual["modalidad"] == "mixta_50_50":
                fase = "etapa_productiva" if (usuario_actual["grado"] or "").startswith("10") else "pasantias"
            else:
                fase = None
            mes = request.form["mes"]
            anio = request.form["anio"]
            
            trabaja_despues_6pm = request.form.get("trabaja_despues_6pm", "No")
            hora_salida = request.form.get("hora_salida", "").strip()
            archivo = request.files.get("archivo")
            autorizacion = request.files.get("autorizacion_padres")

            if not (archivo and archivo.filename and archivo_permitido(archivo.filename)):
                flash("Debes adjuntar el archivo del control de horas.", "danger")
                return redirect(url_for("evidencias.evidencias"))

            if trabaja_despues_6pm == "Si" and not (
                autorizacion and autorizacion.filename and
                autorizacion.filename.lower().endswith(".pdf")
            ):
                flash(
                    "Si trabajas después de las 6pm, debes adjuntar la "
                    "autorización de tus padres en PDF.", "danger",
                )
                return redirect(url_for("evidencias.evidencias"))

            nombre_archivo = secure_filename(f"controlhoras_{uid}_{mes}_{anio}_{archivo.filename}")
            archivo.save(os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_archivo))

            nombre_autorizacion = None
            if trabaja_despues_6pm == "Si" and autorizacion and autorizacion.filename:
                nombre_autorizacion = secure_filename(
                    f"autorizacion_{uid}_{mes}_{anio}_{autorizacion.filename}"
                )
                autorizacion.save(
                    os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_autorizacion)
                )

            existente = bd.execute(
                "SELECT id FROM control_horas WHERE estudiante_id=%s AND mes=%s AND anio=%s",
                (uid, mes, anio),
            ).fetchone()
            if existente:
                bd.execute(     
                    "UPDATE control_horas SET archivo=%s, total_horas=%s, "
                    "trabaja_despues_6pm=%s, hora_salida=%s, autorizacion_padres=%s, "
                    "fase=%s, fecha_carga=%s, estado='Pendiente' WHERE id=%s",
                    (nombre_archivo, total_horas, trabaja_despues_6pm, hora_salida or None,
                     nombre_autorizacion, fase, datetime.now().strftime("%Y-%m-%d"), existente["id"]),
                )
            else:
                bd.execute(
                    "INSERT INTO control_horas (estudiante_id, mes, anio, archivo, total_horas, "
                    "trabaja_despues_6pm, hora_salida, autorizacion_padres, fase, fecha_carga) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (uid, mes, anio, nombre_archivo, total_horas, trabaja_despues_6pm,
                     hora_salida or None, nombre_autorizacion, fase, datetime.now().strftime("%Y-%m-%d")),
                )
            bd.commit()
            flash("Control de horas cargado correctamente.", "success")
            return redirect(url_for("evidencias.evidencias"))

        # ------------------------------------------------------------
        # Formulario 2: Evidencia (opcional)
        # ------------------------------------------------------------
        else:
            descripcion = request.form["descripcion"].strip()
            archivo = request.files.get("archivo")
            if archivo and archivo.filename and archivo_permitido(archivo.filename):
                nombre_seguro = secure_filename(
                    f"{uid}_{datetime.now().timestamp()}_{archivo.filename}"
                )
                archivo.save(os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_seguro))
                bd.execute(
                    "INSERT INTO evidencias (estudiante_id, descripcion, archivo, fecha) "
                    "VALUES (%s,%s,%s,%s)",
                    (uid, descripcion, nombre_seguro, datetime.now().strftime("%Y-%m-%d")),
                )
                bd.commit()
                flash("Evidencia cargada correctamente.", "success")
            else:
                flash("Archivo no válido. Formatos permitidos: pdf, png, jpg, jpeg, docx, xlsx.", "danger")
            return redirect(url_for("evidencias.evidencias"))

    registros_control = bd.execute(
        "SELECT * FROM control_horas WHERE estudiante_id=%s ORDER BY anio DESC, id DESC", (uid,)
    ).fetchall()
    registros_evidencias = bd.execute(
        "SELECT * FROM evidencias WHERE estudiante_id=%s ORDER BY fecha DESC", (uid,)
    ).fetchall()
    return render_template(
        "evidencias/evidencias.html",
        registros_control=registros_control,
        registros=registros_evidencias,
        meses=MESES,
        anio_actual=datetime.now().year,
        mes_actual=MESES[datetime.now().month - 1],
    )