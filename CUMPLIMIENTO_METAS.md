# Cumplimiento de metas de entrega — CONTROL P.E

Este documento cruza cada punto del archivo **METAS_DE_ENTREGA_CONTROL_P_E.docx**
con lo que ya está implementado en el sistema, para facilitar la entrega
semana a semana.

## Semana 1 — Diseño ✅

| Meta | Dónde está |
|---|---|
| Pantallas principales de Control P.E | `aplicacion/plantillas/` (una carpeta por sección) |
| Navegación entre registro, control y seguimiento | Menú superior en `aplicacion/plantillas/base.html` |
| Interfaz de inicio de sesión y acceso de usuarios | `aplicacion/plantillas/autenticacion/login.html` |
| Estructura de base de datos (estudiantes, horas, actividades, evidencias) | `aplicacion/base_datos.py` (tablas `usuarios`, `horas`, `evidencias`, `arl`) |

## Semana 2 — Desarrollo ✅

| Meta | Dónde está |
|---|---|
| Interfaz principal del sistema | `aplicacion/plantillas/panel/` |
| Sistema de base de datos | `aplicacion/base_datos.py` (MySQL) |
| Inicio de sesión y acceso de usuarios | `aplicacion/rutas/autenticacion.py` |
| Registro de horas de prácticas / proyecto productivo | `aplicacion/rutas/horas.py` |
| Registro de actividades realizadas | Campo `actividad` en cada registro de horas |
| Cargue y almacenamiento de evidencias | `aplicacion/rutas/evidencias.py` |
| Control y validación de horas y evidencias | `aplicacion/rutas/estudiantes.py` (función `validar`) |
| Seguimiento de horas acumuladas y pendientes | Barra de progreso (meta de horas) en `panel.py` + `panel/estudiante.html` y `panel/personal.html` |

## Semana 3 — Prueba ✅

Todas las verificaciones de esta semana están cubiertas por **pruebas
automatizadas** en la carpeta `pruebas/` (no solo revisión manual):

| Meta | Prueba automatizada que lo comprueba |
|---|---|
| Los usuarios pueden iniciar sesión correctamente | `test_login_correcto`, `test_login_incorrecto` |
| Las horas y actividades se guardan correctamente | `test_registro_de_horas_se_guarda_correctamente` |
| Las evidencias se cargan y consultan correctamente | `test_evidencia_se_carga_y_se_puede_consultar` |
| La información puede ser revisada y validada | `test_docente_puede_aprobar_un_registro_de_horas` |
| El seguimiento muestra horas acumuladas y pendientes | `test_seguimiento_muestra_horas_acumuladas_y_meta` |
| Los estados se actualizan correctamente | Verificado dentro de `test_docente_puede_aprobar_un_registro_de_horas` |
| Permisos por rol (buscar y corregir errores del sistema) | `test_solo_administrador_puede_ver_usuarios`, `test_pagina_protegida_sin_sesion_redirige_a_login` |

**Cómo ejecutar las pruebas** (ver también `README.md`):
```bash
mysql -u root -p < basedatos/crear_base_datos_pruebas.sql
pytest pruebas/ -v
```
Resultado esperado: `8 passed`.

## Semana 4 — Puesta en marcha ✅ (con acción tuya pendiente)

| Meta | Estado |
|---|---|
| Poner Control P.E en funcionamiento | Listo para ejecutar (`python ejecutar.py`) o desplegar (ver README, sección Render) |
| Configurar la base de datos | `basedatos/crear_base_datos.sql` + `aplicacion/base_datos.py` (automático) |
| Configurar usuarios y permisos de acceso | `aplicacion/rutas/usuarios.py` + roles en `aplicacion/auxiliares.py` |
| Verificar módulos de registro, control y seguimiento | Cubierto por las pruebas de la Semana 3 |
| Comprobar almacenamiento de horas y evidencias | Cubierto por las pruebas de la Semana 3 |

⚠️ Esta semana requiere una acción tuya: decidir dónde va a "vivir" el
sistema en producción (tu propio computador, un servidor del colegio, o
un hosting como Render) y configurar ahí las variables de entorno de MySQL.

## Semana 5 — Implementación (requiere uso real)

El sistema ya permite que **estudiantes, docentes y coordinadores** lo
usen, cada uno con su propio rol y permisos. Esta semana consiste en que
personas reales (no pruebas automatizadas) usen el sistema y confirmen que
todo funciona en la práctica — no es algo que se resuelva solo con código,
sino con una prueba piloto real.

## Semana 6 — Mantenimiento (proceso continuo)

No es una entrega de código puntual, sino un compromiso continuo:
revisar errores que reporten los usuarios, mantener la base de datos, y
mejorar las funciones existentes. El sistema está preparado para esto
gracias a la organización modular (cada sección en su propio archivo, ver
tabla "¿Dónde corrijo qué?" en `README.md`).
