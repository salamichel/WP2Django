/* WP2Django - Vanilla JS */

document.addEventListener("DOMContentLoaded", function () {

    // --- Mobile menu toggle ---
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.getElementById("main-nav");

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            const expanded = toggle.getAttribute("aria-expanded") === "true";
            toggle.setAttribute("aria-expanded", !expanded);
            nav.classList.toggle("open");

            // Animate hamburger to X
            const spans = toggle.querySelectorAll("span");
            if (!expanded) {
                spans[0].style.transform = "rotate(45deg) translate(5px, 5px)";
                spans[1].style.opacity = "0";
                spans[2].style.transform = "rotate(-45deg) translate(5px, -5px)";
            } else {
                spans[0].style.transform = "";
                spans[1].style.opacity = "";
                spans[2].style.transform = "";
            }
        });

        // Close menu when clicking outside
        document.addEventListener("click", function (e) {
            if (nav.classList.contains("open") && !nav.contains(e.target) && !toggle.contains(e.target)) {
                nav.classList.remove("open");
                toggle.setAttribute("aria-expanded", "false");
                const spans = toggle.querySelectorAll("span");
                spans[0].style.transform = "";
                spans[1].style.opacity = "";
                spans[2].style.transform = "";
            }
        });
    }

    // --- Scroll animations (Intersection Observer) ---
    const animatedElements = document.querySelectorAll("[data-animate]");
    if (animatedElements.length > 0 && "IntersectionObserver" in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry, index) {
                if (entry.isIntersecting) {
                    // Stagger animation for grid items
                    const delay = Array.from(animatedElements).indexOf(entry.target) % 3 * 100;
                    setTimeout(function () {
                        entry.target.classList.add("animated");
                    }, delay);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: "0px 0px -40px 0px"
        });

        animatedElements.forEach(function (el) {
            observer.observe(el);
        });
    } else {
        // Fallback: show all elements immediately
        animatedElements.forEach(function (el) {
            el.classList.add("animated");
        });
    }

    // --- Auto-dismiss alert messages ---
    document.querySelectorAll(".alert").forEach(function (alert) {
        // Close button
        var closeBtn = alert.querySelector(".alert-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", function () {
                dismissAlert(alert);
            });
        }
        // Auto-dismiss after 5s
        setTimeout(function () {
            dismissAlert(alert);
        }, 5000);
    });

    function dismissAlert(el) {
        if (!el || !el.parentNode) return;
        el.style.transition = "opacity 0.3s ease, transform 0.3s ease";
        el.style.opacity = "0";
        el.style.transform = "translateY(-10px)";
        setTimeout(function () {
            if (el.parentNode) el.remove();
        }, 300);
    }

    // --- Sidebar toggle (mobile) ---
    var sidebarToggle = document.querySelector(".sidebar-toggle");
    var sidebar = document.getElementById("sidebar");
    if (sidebarToggle && sidebar) {
        // Create overlay element
        var overlay = document.createElement("div");
        overlay.className = "sidebar-overlay";
        document.body.appendChild(overlay);

        function openSidebar() {
            sidebar.classList.add("open");
            overlay.classList.add("active");
            sidebarToggle.setAttribute("aria-expanded", "true");
        }

        function closeSidebar() {
            sidebar.classList.remove("open");
            overlay.classList.remove("active");
            sidebarToggle.setAttribute("aria-expanded", "false");
        }

        sidebarToggle.addEventListener("click", function () {
            if (sidebar.classList.contains("open")) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });

        overlay.addEventListener("click", closeSidebar);
    }

    // --- Sticky header shadow on scroll ---
    var header = document.querySelector(".site-header");
    if (header) {
        var lastScroll = 0;
        window.addEventListener("scroll", function () {
            var scrollY = window.pageYOffset;
            if (scrollY > 10) {
                header.style.boxShadow = "0 2px 12px rgba(0, 0, 0, 0.08)";
            } else {
                header.style.boxShadow = "0 1px 4px rgba(0, 0, 0, 0.04)";
            }
            lastScroll = scrollY;
        }, { passive: true });
    }
});
