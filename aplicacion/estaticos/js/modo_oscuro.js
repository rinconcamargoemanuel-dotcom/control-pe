(function () {
    var temaGuardado = localStorage.getItem("tema") || "claro";
    document.documentElement.setAttribute("data-theme", temaGuardado);

    document.addEventListener("DOMContentLoaded", function () {
        var boton = document.getElementById("btn-modo-oscuro");
        if (!boton) return;
        actualizarTextoBoton();

        boton.addEventListener("click", function () {
            var actual = document.documentElement.getAttribute("data-theme");
            var nuevo = actual === "oscuro" ? "claro" : "oscuro";
            document.documentElement.setAttribute("data-theme", nuevo);
            localStorage.setItem("tema", nuevo);
            actualizarTextoBoton();
        });

        function actualizarTextoBoton() {
            var actual = document.documentElement.getAttribute("data-theme");
            boton.textContent = actual === "oscuro" ? "☀️ Claro" : "🌙 Oscuro";
        }
    });
})();