/*
 * Agrega automáticamente un botón "ojito" a TODOS los campos de
 * contraseña (<input type="password">) que haya en la página, sin
 * necesidad de tocar cada formulario. Al hacer clic, muestra u oculta
 * el texto que se está escribiendo.
 *
 * Si en el futuro agregas un nuevo campo type="password" en cualquier
 * plantilla, el ojito aparece solo — no hay que editar nada más aquí.
 */
document.addEventListener("DOMContentLoaded", function () {
    var campos = document.querySelectorAll('input[type="password"]');

    campos.forEach(function (campo) {
        // Envuelve el input en un contenedor para poder posicionar el ojito
        var envoltorio = document.createElement("div");
        envoltorio.className = "campo-password-wrap";
        campo.parentNode.insertBefore(envoltorio, campo);
        envoltorio.appendChild(campo);

        var boton = document.createElement("button");
        boton.type = "button";
        boton.className = "btn-ojo-password";
        boton.setAttribute("aria-label", "Mostrar contraseña");
        boton.textContent = "👁";

        boton.addEventListener("click", function () {
            var oculto = campo.type === "password";
            campo.type = oculto ? "text" : "password";
            boton.textContent = oculto ? "🙈" : "👁";
            boton.setAttribute(
                "aria-label",
                oculto ? "Ocultar contraseña" : "Mostrar contraseña"
            );
        });

        envoltorio.appendChild(boton);
    });
});
