"""
CONTROL P.E - Sistema de Control de Prácticas Empresariales
=============================================================
Punto central que arma la aplicación Flask: carga la configuración,
conecta la base de datos y registra cada sección (rutas) del sistema.

Estructura del proyecto (cada carpeta/archivo se corrige de forma aislada):

    aplicacion/
        configuracion.py   -> claves, datos de conexión MySQL, rutas de carpetas
        base_datos.py      -> conexión MySQL y tablas de la base de datos
        auxiliares.py      -> decoradores de permisos y validaciones
        rutas/
            autenticacion.py  -> login, registro, logout, perfil
            panel.py          -> pantalla de inicio (dashboard)
            horas.py          -> bitácora de horas del estudiante
            evidencias.py     -> evidencias del estudiante
            arl.py            -> afiliación ARL del estudiante
            estudiantes.py    -> ver detalle / aprobar-rechazar registros
            usuarios.py       -> gestión de usuarios (administrador)
        plantillas/        -> archivos HTML, organizados por sección
        estaticos/
            css/            -> hojas de estilo
            imagenes/        -> logo, iconos, notas de diseño y subidas de usuarios

Base de datos: MySQL (ver README.md, sección "Base de datos MySQL",
para crear la base de datos vacía antes de ejecutar por primera vez).

Roles del sistema:
- Estudiante: registra horas, sube evidencias, carga afiliación ARL mensual.
- Docente Supervisor: revisa y valida la información registrada por los estudiantes.
- Coordinador: supervisa el proceso general de las prácticas empresariales.
- Administrador: gestiona usuarios y el sistema.
"""

import os

from flask import Flask, session, redirect, url_for

from .configuracion import CLAVE_SECRETA, CARPETA_SUBIDAS, TOKEN_TAREAS
from .base_datos import cerrar_bd, inicializar_bd


def crear_app():
    app = Flask(
        __name__,
        template_folder="plantillas",
        static_folder="estaticos",
    )
    app.config["SECRET_KEY"] = CLAVE_SECRETA
    
    @app.template_filter("capitalizar")
    def capitalizar_texto(texto):
        if not texto:
            return texto
        return " ".join(p.capitalize() for p in str(texto).strip().split(" "))
    
    app.config["CARPETA_SUBIDAS"] = CARPETA_SUBIDAS
    app.config["TOKEN_TAREAS"] = TOKEN_TAREAS
    os.makedirs(CARPETA_SUBIDAS, exist_ok=True)

    # Cierra la conexión a la base de datos al terminar cada petición
    app.teardown_appcontext(cerrar_bd)

    # Crea las tablas (si no existen) y los usuarios de prueba
    inicializar_bd()

    # ------------------------------------------------------------------
    # Registro de cada sección de la aplicación (blueprints)
    # ------------------------------------------------------------------
    from .rutas import autenticacion, panel, horas, evidencias, arl, bitacora, documentos, historial, estudiantes, usuarios, tareas

    app.register_blueprint(autenticacion.bp)
    app.register_blueprint(panel.bp)
    app.register_blueprint(horas.bp)
    app.register_blueprint(evidencias.bp)
    app.register_blueprint(arl.bp)
    app.register_blueprint(bitacora.bp)
    app.register_blueprint(documentos.bp)
    app.register_blueprint(historial.bp)
    app.register_blueprint(estudiantes.bp)
    app.register_blueprint(usuarios.bp)
    app.register_blueprint(tareas.bp)

    @app.route("/")
    def inicio():
        if "user_id" in session:
            return redirect(url_for("panel.principal"))
        return redirect(url_for("autenticacion.iniciar_sesion"))

    @app.context_processor
    def inyectar_usuario_sesion():
        arl_pendiente = False
        bitacora_pendiente = False
        control_horas_pendiente = False
        etapa_productiva_pendiente = False
        mes_anterior_nombre = None
        plazo_bitacora_dias_restantes = None
        plazo_bitacora_vencido = False
        plazo_control_horas_dias_restantes = None
        plazo_control_horas_vencido = False
        total_avisos_pendientes = 0
        if session.get("rol") == "estudiante":
            from datetime import datetime
            from .base_datos import obtener_bd
            from .configuracion import MESES
            bd = obtener_bd()
            mes_actual = MESES[datetime.now().month - 1]
            anio_actual = datetime.now().year

            ya_cargada = bd.execute(
                "SELECT id FROM arl WHERE estudiante_id=%s AND mes=%s AND anio=%s",
                (session["user_id"], mes_actual, anio_actual),
            ).fetchone()
            arl_pendiente = ya_cargada is None

            bitacora_mes = bd.execute(
                "SELECT id FROM bitacora WHERE estudiante_id=%s AND mes=%s AND anio=%s",
                (session["user_id"], mes_actual, anio_actual),
            ).fetchone()
            bitacora_pendiente = bitacora_mes is None

            control_horas_mes = bd.execute(
                "SELECT id FROM control_horas WHERE estudiante_id=%s AND mes=%s AND anio=%s",
                (session["user_id"], mes_actual, anio_actual),
            ).fetchone()
            control_horas_pendiente = control_horas_mes is None
            
            usuario_actual = bd.execute(
                "SELECT modalidad, grado FROM usuarios WHERE id=%s", (session["user_id"],)
            ).fetchone()
                        # Plazo de 10 días para Bitácora y Control de Horas del mes anterior
            hoy = datetime.now()
            if hoy.month == 1:
                mes_anterior_num = 12
                anio_mes_anterior = hoy.year - 1
            else:
                mes_anterior_num = hoy.month - 1
                anio_mes_anterior = hoy.year
            mes_anterior_nombre = MESES[mes_anterior_num - 1]
            dias_transcurridos = hoy.day

            bitacora_anterior = bd.execute(
                "SELECT id FROM bitacora WHERE estudiante_id=%s AND mes=%s AND anio=%s",
                (session["user_id"], mes_anterior_nombre, anio_mes_anterior),
            ).fetchone()
            control_horas_anterior = bd.execute(
                "SELECT id FROM control_horas WHERE estudiante_id=%s AND mes=%s AND anio=%s",
                (session["user_id"], mes_anterior_nombre, anio_mes_anterior),
            ).fetchone()

            plazo_bitacora_dias_restantes = None
            plazo_bitacora_vencido = False
            if bitacora_anterior is None and dias_transcurridos <= 10:
                plazo_bitacora_dias_restantes = 10 - dias_transcurridos
            elif bitacora_anterior is None and dias_transcurridos > 10:
                plazo_bitacora_vencido = True

            plazo_control_horas_dias_restantes = None
            plazo_control_horas_vencido = False
            if control_horas_anterior is None and dias_transcurridos <= 10:
                plazo_control_horas_dias_restantes = 10 - dias_transcurridos
            elif control_horas_anterior is None and dias_transcurridos > 10:
                plazo_control_horas_vencido = True

            usuario_actual = bd.execute(
                "SELECT modalidad, grado FROM usuarios WHERE id=%s", (session["user_id"],)
            ).fetchone()
            if (usuario_actual and usuario_actual["modalidad"] == "mixta_50_50"
                    and (usuario_actual["grado"] or "").startswith("11")):
                suma_etapa = bd.execute(
                    "SELECT COALESCE(SUM(total_horas),0) t FROM control_horas "
                    "WHERE estudiante_id=%s AND fase='etapa_productiva'",
                    (session["user_id"],),
                ).fetchone()["t"]
                etapa_productiva_pendiente = float(suma_etapa) < 432
            total_avisos_pendientes = sum([
        1 if arl_pendiente else 0,
        1 if bitacora_pendiente else 0,
        1 if control_horas_pendiente else 0,
        1 if etapa_productiva_pendiente else 0,
        1 if plazo_bitacora_vencido else 0,
        1 if plazo_control_horas_vencido else 0,
        1 if plazo_bitacora_dias_restantes is not None else 0,
        1 if plazo_control_horas_dias_restantes is not None else 0,
    ])
        return {
            "session_user": session.get("nombre"),
            "session_rol": session.get("rol"),
            "arl_pendiente": arl_pendiente,
            "bitacora_pendiente": bitacora_pendiente,
            "control_horas_pendiente": control_horas_pendiente,
            "etapa_productiva_pendiente": etapa_productiva_pendiente,
            "mes_anterior_nombre": mes_anterior_nombre,
            "plazo_bitacora_dias_restantes": plazo_bitacora_dias_restantes,
            "plazo_bitacora_vencido": plazo_bitacora_vencido,
            "plazo_control_horas_dias_restantes": plazo_control_horas_dias_restantes,
            "plazo_control_horas_vencido": plazo_control_horas_vencido,
            "total_avisos_pendientes": total_avisos_pendientes,
        }

    return app
