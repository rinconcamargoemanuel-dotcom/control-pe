"""
Gestión de usuarios: listar, crear y eliminar. Solo accesible para el
rol Administrador.

Si hay un error al crear, listar o eliminar usuarios, revisa únicamente
este archivo.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from ..auxiliares import inicio_sesion_requerido, roles_requeridos
from ..base_datos import obtener_bd

bp = Blueprint("usuarios", __name__)


@bp.route("/usuarios")
@inicio_sesion_requerido
@roles_requeridos("administrador")
def lista():
    bd = obtener_bd()
    todos = bd.execute("SELECT * FROM usuarios ORDER BY rol, nombre").fetchall()
    return render_template("usuarios/lista.html", usuarios=todos)


@bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@inicio_sesion_requerido
@roles_requeridos("administrador")
def nuevo():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        rol = request.form["rol"]
        bd = obtener_bd()
        existe = bd.execute("SELECT id FROM usuarios WHERE email=%s", (email,)).fetchone()
        if existe:
            flash("Ese correo ya existe.", "danger")
            return redirect(url_for("usuarios.nuevo"))
        bd.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s,%s,%s,%s)",
            (nombre, email, generate_password_hash(password), rol),
        )
        bd.commit()
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("usuarios.lista"))
    return render_template("usuarios/nuevo.html")


@bp.route("/usuarios/eliminar/<int:usuario_id>")
@inicio_sesion_requerido
@roles_requeridos("administrador")
def eliminar(usuario_id):
    bd = obtener_bd()
    bd.execute("DELETE FROM usuarios WHERE id=%s", (usuario_id,))
    bd.commit()
    flash("Usuario eliminado.", "info")
    return redirect(url_for("usuarios.lista"))
