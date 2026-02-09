/* WP2Django - Vanilla JS */

document.addEventListener("DOMContentLoaded", function () {
    // Mobile menu toggle
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.getElementById("main-nav");

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            const expanded = toggle.getAttribute("aria-expanded") === "true";
            toggle.setAttribute("aria-expanded", !expanded);
            nav.classList.toggle("open");
        });
    }

    // Auto-dismiss alert messages after 5 seconds
    document.querySelectorAll(".alert").forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = "opacity 0.3s ease";
            alert.style.opacity = "0";
            setTimeout(function () {
                alert.remove();
            }, 300);
        }, 5000);
    });
});
