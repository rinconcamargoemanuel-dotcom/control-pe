"""
Rutas de autenticación: iniciar sesión, registro público de estudiantes,
recuperar/restablecer contraseña, cerrar sesión y ver el perfil propio.

Si hay un error al iniciar sesión, registrarse o ver el perfil, revisa
únicamente este archivo.
"""

from flask import ( #type: ignore
    Blueprint, render_template, request, redirect, url_for, session, flash,
    current_app
)
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired# type: ignore

from ..base_datos import obtener_bd

bp = Blueprint("autenticacion", __name__)

SAL_RECUPERACION = "recuperar-password"
MINUTOS_VALIDEZ_ENLACE = 60


def _generar_token_recuperacion(email):
    serializador = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializador.dumps(email, salt=SAL_RECUPERACION)


def _leer_email_desde_token(token):
    """Devuelve el email si el token es válido y no ha expirado, o None si no."""
    serializador = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return serializador.loads(
            token, salt=SAL_RECUPERACION, max_age=MINUTOS_VALIDEZ_ENLACE * 60
        )
    except (BadSignature, SignatureExpired):
        return None


@bp.route("/login", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        bd = obtener_bd()
        usuario = bd.execute(
            "SELECT * FROM usuarios WHERE email = %s", (email,)
        ).fetchone()
        if usuario and check_password_hash(usuario["password"], password):
            session["user_id"] = usuario["id"]
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]
            nombre_capitalizado = " ".join(p.capitalize() for p in usuario['nombre'].strip().split(" "))
            flash(f"Bienvenido, {nombre_capitalizado}.", "success")
            if usuario["rol"] == "estudiante" and not usuario.get("modalidad_principal"):
                return redirect(url_for("autenticacion.elegir_modalidad"))
            return redirect(url_for("panel.principal"))
        flash("Correo o contraseña incorrectos.", "danger")
    return render_template("autenticacion/login.html")


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Registro público, solo para el rol Estudiante."""
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        empresa = request.form.get("empresa", "").strip()
        grado = request.form.get("grado", "").strip()
        fecha_inicio_practicas = request.form.get("fecha_inicio_practicas") or None

        bd = obtener_bd()
        existe = bd.execute(
            "SELECT id FROM usuarios WHERE email = %s", (email,)
        ).fetchone()
        if existe:
            flash("Ese correo ya está registrado.", "danger")
            return redirect(url_for("autenticacion.registro"))

        bd.execute(
            "INSERT INTO usuarios (nombre, email, password, rol, empresa, grado) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (nombre, email, generate_password_hash(password), "estudiante", empresa, grado),
        )
        bd.commit()
        flash("Registro exitoso. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("autenticacion.iniciar_sesion"))
    return render_template("autenticacion/registro.html")


@bp.route("/recuperar-password", methods=["GET", "POST"])
def recuperar_password():
    """Paso 1: el usuario escribe su correo; si existe, se le muestra el enlace."""
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        bd = obtener_bd()
        usuario = bd.execute(
            "SELECT id, nombre FROM usuarios WHERE email = %s", (email,)
        ).fetchone()

        if usuario:
            token = _generar_token_recuperacion(email)
            enlace = url_for(
                "autenticacion.restablecer_password", token=token, _external=True
            )
            flash(
                f"Enlace para restablecer tu contraseña (válido por 1 hora): {enlace}",
                "success",
            )
        else:
            # Mismo mensaje aunque el correo no exista, para no revelar
            # qué cuentas están registradas en el sistema.
            flash(
                "Si ese correo está registrado, verás aquí tu enlace de "
                "recuperación.",
                "success",
            )
        return redirect(url_for("autenticacion.iniciar_sesion"))

    return render_template("autenticacion/recuperar.html")


@bp.route("/restablecer-password/<token>", methods=["GET", "POST"])
def restablecer_password(token):
    """Paso 2: el enlace lleva aquí para elegir la contraseña nueva."""
    email = _leer_email_desde_token(token)
    if email is None:
        flash(
            "Ese enlace ya no es válido o expiró. Solicita uno nuevo.", "danger"
        )
        return redirect(url_for("autenticacion.recuperar_password"))

    if request.method == "POST":
        password = request.form["password"]
        confirmar = request.form["confirmar_password"]
        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "danger")
            return render_template("autenticacion/restablecer.html", token=token)
        if password != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("autenticacion/restablecer.html", token=token)

        bd = obtener_bd()
        bd.execute(
            "UPDATE usuarios SET password=%s WHERE email=%s",
            (generate_password_hash(password), email),
        )
        bd.commit()
        flash("Contraseña actualizada. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("autenticacion.iniciar_sesion"))

    return render_template("autenticacion/restablecer.html", token=token)


@bp.route("/logout")
def cerrar_sesion():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("autenticacion.iniciar_sesion"))


@bp.route("/perfil", methods=["GET", "POST"])
def perfil():
    """Muestra y permite editar la información propia del usuario que inició sesión."""
    if "user_id" not in session:
        flash("Debes iniciar sesión para continuar.", "warning")
        return redirect(url_for("autenticacion.iniciar_sesion"))

    bd = obtener_bd()

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip().lower()
        empresa = request.form.get("empresa", "").strip()
        grado = request.form.get("grado", "").strip()
        fecha_inicio_practicas = request.form.get("fecha_inicio_practicas") or None

        existe = bd.execute(
            "SELECT id FROM usuarios WHERE email = %s AND id != %s",
            (email, session["user_id"]),
        ).fetchone()
        if existe:
            flash("Ese correo ya está en uso por otra cuenta.", "danger")
            return redirect(url_for("autenticacion.perfil"))

        bd.execute(
            "UPDATE usuarios SET nombre=%s, email=%s, empresa=%s, grado=%s, "
            "fecha_inicio_practicas=%s WHERE id=%s",
            (nombre, email, empresa, grado, fecha_inicio_practicas, session["user_id"]),
        )
        bd.commit()
        session["nombre"] = nombre
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("autenticacion.perfil"))

    usuario = bd.execute(
        "SELECT nombre, email, rol, empresa, grado, fecha_inicio_practicas FROM usuarios WHERE id = %s",
        (session["user_id"],),
    ).fetchone()
    if usuario is None:
        flash("No se pudo cargar tu información. Vuelve a iniciar sesión.", "danger")
        session.clear()
        return redirect(url_for("autenticacion.iniciar_sesion"))
    return render_template("perfil.html", usuario=usuario)

@bp.route("/elegir-modalidad", methods=["GET", "POST"])
def elegir_modalidad():
    """Primera vez que un estudiante inicia sesión: debe elegir su modalidad."""
    if "user_id" not in session:
        flash("Debes iniciar sesión para continuar.", "warning")
        return redirect(url_for("autenticacion.iniciar_sesion"))

    modalidades_validas = ("proyecto_productivo", "pasantias", "contrato_aprendizaje", "monitorias")

    if request.method == "POST":
        modalidad_principal = request.form.get("modalidad_principal")
        porcentaje_modalidad = request.form.get("porcentaje_modalidad")
        modalidad_secundaria = request.form.get("modalidad_secundaria") or None

        if modalidad_principal not in modalidades_validas:
            flash("Selecciona una modalidad válida.", "danger")
            return redirect(url_for("autenticacion.elegir_modalidad"))
        if porcentaje_modalidad not in ("100", "50"):
            flash("Selecciona un porcentaje válido.", "danger")
            return redirect(url_for("autenticacion.elegir_modalidad"))
        if porcentaje_modalidad == "50":
            if modalidad_secundaria not in modalidades_validas or modalidad_secundaria == modalidad_principal:
                flash("Selecciona con cuál otra modalidad se combina el 50% restante.", "danger")
                return redirect(url_for("autenticacion.elegir_modalidad"))
        else:
            modalidad_secundaria = None

        bd = obtener_bd()
        bd.execute(
            "UPDATE usuarios SET modalidad_principal=%s, porcentaje_modalidad=%s, "
            "modalidad_secundaria=%s WHERE id=%s",
            (modalidad_principal, porcentaje_modalidad, modalidad_secundaria, session["user_id"]),
        )
        bd.commit()
        flash("Modalidad guardada correctamente.", "success")
        return redirect(url_for("documentos.documentos", primera_vez=1))

    return render_template("autenticacion/elegir_modalidad.html")
