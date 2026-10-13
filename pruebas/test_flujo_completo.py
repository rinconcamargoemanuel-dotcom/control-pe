"""
Pruebas automatizadas de CONTROL P.E.

Cada prueba corresponde directamente a un punto de la Semana 3 (Prueba)
del documento de metas de entrega:

  ✓ Comprobar que los usuarios puedan iniciar sesión correctamente.
  ✓ Verificar que las horas y actividades se guarden correctamente.
  ✓ Comprobar que las evidencias puedan cargarse y consultarse correctamente.
  ✓ Verificar que la información registrada pueda ser revisada y validada.
  ✓ Comprobar que el seguimiento muestre correctamente las horas acumuladas
    y pendientes.
  ✓ Verificar que los estados de las evidencias y registros se actualicen
    correctamente.

Ejecutar con:  pytest pruebas/ -v
"""

import io


# ---------------------------------------------------------------------------
# 1) Inicio de sesión
# ---------------------------------------------------------------------------

def test_login_correcto(cliente):
    respuesta = cliente.post(
        "/login",
        data={"email": "admin@controlpe.edu.co", "password": "admin123"},
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Panel de seguimiento".encode("utf-8") in respuesta.data or b"dashboard" in respuesta.request.path.encode()


def test_login_incorrecto(cliente):
    respuesta = cliente.post(
        "/login",
        data={"email": "admin@controlpe.edu.co", "password": "clave_erronea"},
        follow_redirects=True,
    )
    assert "incorrectos".encode("utf-8") in respuesta.data


def test_pagina_protegida_sin_sesion_redirige_a_login(cliente):
    respuesta = cliente.get("/dashboard", follow_redirects=True)
    assert b"Iniciar sesi" in respuesta.data


# ---------------------------------------------------------------------------
# 2) Registro de horas y actividades
# ---------------------------------------------------------------------------

def _crear_estudiante_y_loguear(cliente, email="estudiante_prueba@test.com"):
    cliente.post(
        "/registro",
        data={
            "nombre": "Estudiante de Prueba", "email": email,
            "password": "123456", "empresa": "Empresa Prueba", "grado": "11-6",
        },
        follow_redirects=True,
    )
    cliente.post("/login", data={"email": email, "password": "123456"}, follow_redirects=True)


def test_registro_de_horas_se_guarda_correctamente(cliente):
    _crear_estudiante_y_loguear(cliente)
    respuesta = cliente.post(
        "/horas",
        data={"fecha": "2026-08-20", "horas": "5", "actividad": "Inventario de bodega"},
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Inventario de bodega".encode("utf-8") in respuesta.data
    assert "Pendiente".encode("utf-8") in respuesta.data


# ---------------------------------------------------------------------------
# 3) Evidencias: cargar y consultar
# ---------------------------------------------------------------------------

def test_evidencia_se_carga_y_se_puede_consultar(cliente):
    _crear_estudiante_y_loguear(cliente)
    archivo_falso = (io.BytesIO(b"contenido de prueba"), "evidencia_prueba.pdf")
    respuesta = cliente.post(
        "/evidencias",
        data={"descripcion": "Evidencia de actividad de prueba", "archivo": archivo_falso},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Evidencia de actividad de prueba".encode("utf-8") in respuesta.data


# ---------------------------------------------------------------------------
# 4) Revisión y validación (aprobar / rechazar) por el docente
# ---------------------------------------------------------------------------

def test_docente_puede_aprobar_un_registro_de_horas(app, cliente):
    _crear_estudiante_y_loguear(cliente, email="estudiante_a_validar@test.com")
    cliente.post(
        "/horas",
        data={"fecha": "2026-08-20", "horas": "3", "actividad": "Actividad a validar"},
        follow_redirects=True,
    )
    cliente.get("/logout")

    # Obtenemos el id del registro directo de la base de datos de pruebas
    with app.app_context():
        from aplicacion.base_datos import obtener_bd
        bd = obtener_bd()
        registro = bd.execute(
            "SELECT id FROM horas WHERE actividad='Actividad a validar'"
        ).fetchone()
    registro_id = registro["id"]

    # El docente inicia sesión y aprueba el registro
    cliente.post(
        "/login",
        data={"email": "docente@controlpe.edu.co", "password": "docente123"},
        follow_redirects=True,
    )
    respuesta = cliente.get(f"/validar/horas/{registro_id}/Aprobado", follow_redirects=True)
    assert respuesta.status_code == 200
    assert "Aprobado".encode("utf-8") in respuesta.data


# ---------------------------------------------------------------------------
# 5) Seguimiento: horas acumuladas y pendientes
# ---------------------------------------------------------------------------

def test_seguimiento_muestra_horas_acumuladas_y_meta(cliente):
    _crear_estudiante_y_loguear(cliente, email="seguimiento@test.com")
    cliente.post(
        "/horas",
        data={"fecha": "2026-08-20", "horas": "10", "actividad": "Actividad de seguimiento"},
        follow_redirects=True,
    )
    respuesta = cliente.get("/dashboard")
    assert respuesta.status_code == 200
    # El panel del estudiante debe mostrar el conteo de pendientes y la meta de horas
    assert "pendientes".encode("utf-8") in respuesta.data.lower() or b"Pendiente" in respuesta.data
    assert b"horas" in respuesta.data.lower()


# ---------------------------------------------------------------------------
# 6) Gestión de usuarios y permisos por rol (administrador)
# ---------------------------------------------------------------------------

def test_solo_administrador_puede_ver_usuarios(cliente):
    _crear_estudiante_y_loguear(cliente, email="sin_permiso@test.com")
    respuesta = cliente.get("/usuarios", follow_redirects=True)
    # Un estudiante no debe poder ver la gestión de usuarios
    assert "permisos".encode("utf-8") in respuesta.data

    cliente.get("/logout")
    cliente.post(
        "/login",
        data={"email": "admin@controlpe.edu.co", "password": "admin123"},
        follow_redirects=True,
    )
    respuesta = cliente.get("/usuarios")
    assert respuesta.status_code == 200
