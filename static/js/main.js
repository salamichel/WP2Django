/**
 * Rêves de Chiens - Main Frontend Application
 * Vanilla JS ES6+ - Modern, fast, accessible
 */

document.addEventListener("DOMContentLoaded", function () {
    initNavigation();
    initSidebar();
    initScrollAnimations();
    initAlerts();
    initLiveFilters();
    initStickyHeader();
});

/* ==========================================================================
   1. Navigation & Mobile Drawer
   ========================================================================== */
function initNavigation() {
    const toggle = document.getElementById("menu-toggle");
    const nav = document.getElementById("main-nav");
    const overlay = document.getElementById("nav-overlay");
    const closeBtn = document.getElementById("nav-drawer-close");

    if (!toggle || !nav) return;

    function openNav() {
        toggle.setAttribute("aria-expanded", "true");
        toggle.classList.add("is-active");
        nav.classList.add("open");
        if (overlay) overlay.classList.add("active");
        document.body.classList.add("no-scroll");
    }

    function closeNav() {
        toggle.setAttribute("aria-expanded", "false");
        toggle.classList.remove("is-active");
        nav.classList.remove("open");
        if (overlay) overlay.classList.remove("active");
        document.body.classList.remove("no-scroll");
    }

    toggle.addEventListener("click", function () {
        const isOpen = nav.classList.contains("open");
        if (isOpen) {
            closeNav();
        } else {
            openNav();
        }
    });

    if (closeBtn) closeBtn.addEventListener("click", closeNav);
    if (overlay) overlay.addEventListener("click", closeNav);

    // Close on Escape key
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && nav.classList.contains("open")) {
            closeNav();
        }
    });

    // Mobile accordion for submenus & megamenu
    const expandableNavItems = nav.querySelectorAll(".nav-item.has-children, .nav-item.has-megamenu");
    expandableNavItems.forEach(function (item) {
        const link = item.querySelector(".nav-link");
        if (link) {
            link.addEventListener("click", function (e) {
                if (window.innerWidth <= 968) {
                    const hasDropdown = item.querySelector(".sub-menu, .megamenu-dropdown");
                    if (hasDropdown) {
                        const isExpanded = item.classList.contains("expanded");
                        if (!isExpanded) {
                            e.preventDefault();
                            // Close siblings
                            expandableNavItems.forEach(other => {
                                if (other !== item) other.classList.remove("expanded");
                            });
                            item.classList.add("expanded");
                        } else if (e.target.closest(".dropdown-chevron")) {
                            e.preventDefault();
                            item.classList.remove("expanded");
                        }
                    }
                }
            });
        }

        // Desktop hover intent with comfort timeout
        let closeTimeout = null;
        item.addEventListener("mouseenter", function () {
            if (window.innerWidth > 968) {
                if (closeTimeout) clearTimeout(closeTimeout);
                expandableNavItems.forEach(other => {
                    if (other !== item) other.classList.remove("is-open");
                });
                item.classList.add("is-open");
            }
        });

        item.addEventListener("mouseleave", function () {
            if (window.innerWidth > 968) {
                closeTimeout = setTimeout(function () {
                    item.classList.remove("is-open");
                }, 200); // 200ms grace period
            }
        });
    });
}

/* ==========================================================================
   2. Mobile Sidebar Drawer
   ========================================================================== */
function initSidebar() {
    const sidebarToggle = document.querySelector(".sidebar-toggle");
    const sidebar = document.getElementById("sidebar");

    if (!sidebarToggle || !sidebar) return;

    let overlay = document.querySelector(".sidebar-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.className = "sidebar-overlay";
        document.body.appendChild(overlay);
    }

    function openSidebar() {
        sidebar.classList.add("open");
        overlay.classList.add("active");
        sidebarToggle.setAttribute("aria-expanded", "true");
        document.body.classList.add("no-scroll");
    }

    function closeSidebar() {
        sidebar.classList.remove("open");
        overlay.classList.remove("active");
        sidebarToggle.setAttribute("aria-expanded", "false");
        document.body.classList.remove("no-scroll");
    }

    sidebarToggle.addEventListener("click", function () {
        if (sidebar.classList.contains("open")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    overlay.addEventListener("click", closeSidebar);

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && sidebar.classList.contains("open")) {
            closeSidebar();
        }
    });
}

/* ==========================================================================
   3. Live Multi-Filter Engine (AJAX without page reload + History State)
   ========================================================================== */
function initLiveFilters() {
    const form = document.getElementById("live-filter-form");
    const resultsWrapper = document.getElementById("live-results-wrapper");
    const speciesTabs = document.querySelectorAll(".species-tab");
    const speciesInput = document.getElementById("filter-species-input");
    const qInput = document.getElementById("filter-q-input");
    const clearBtn = document.getElementById("search-clear-btn");
    const resetBtn = document.getElementById("btn-reset-all");
    const resetContainer = document.getElementById("filter-reset-container");
    const activeChipsBar = document.getElementById("active-chips-bar");
    const activeChipsList = document.getElementById("active-chips-list");

    if (!form || !resultsWrapper) return;

    let currentAbortController = null;
    let debounceTimer = null;

    // --- Helper: Build FormData and Query String ---
    function getFilterParams(pageOverride = null) {
        const formData = new FormData(form);
        const params = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
            const val = String(value).trim();
            if (val && key !== "page") {
                params.set(key, val);
            }
        }

        if (pageOverride) {
            params.set("page", String(pageOverride));
        }

        return params;
    }

    // --- Helper: Fetch results via AJAX ---
    function applyFilters(page = null, pushHistory = true, isSearchTyping = false) {
        if (currentAbortController) {
            currentAbortController.abort();
        }
        currentAbortController = new AbortController();

        const params = getFilterParams(page);
        const baseUrl = form.getAttribute("action") || window.location.pathname;
        const queryString = params.toString();
        const requestUrl = queryString ? `${baseUrl}?${queryString}` : baseUrl;

        // UI Loading state
        resultsWrapper.classList.add("is-loading");
        const loader = document.getElementById("results-loader");
        if (loader) loader.classList.add("active");

        fetch(requestUrl, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "text/html"
            },
            signal: currentAbortController.signal
        })
            .then(function (response) {
                if (!response.ok) throw new Error("Erreur de chargement des résultats");
                return response.text();
            })
            .then(function (html) {
                resultsWrapper.innerHTML = html;
                resultsWrapper.classList.remove("is-loading");

                // Update Active Filter Chips and Reset Button
                updateActiveChips(params);

                // Re-bind pagination click events
                bindPaginationEvents();

                // Re-trigger scroll entrance animations
                reinitAnimations(resultsWrapper);

                // If pagination was clicked, smoothly scroll to top of filters/results
                if (page) {
                    const filterCard = document.getElementById("live-filter-wrapper");
                    if (filterCard) {
                        const topPos = filterCard.getBoundingClientRect().top + window.pageYOffset - 80;
                        window.scrollTo({ top: topPos, behavior: "smooth" });
                    }
                }
            })
            .catch(function (err) {
                if (err.name === "AbortError") return;
                console.error("Filtre AJAX Erreur:", err);
                resultsWrapper.classList.remove("is-loading");
            });
    }

    // --- Helper: Update Active Chips & Reset Bar ---
    function updateActiveChips(params) {
        if (!activeChipsBar || !activeChipsList) return;

        activeChipsList.innerHTML = "";
        let hasAnyFilter = false;

        const labels = {
            species: function (v) {
                const map = { chien: "🐕 Chiens", chat: "🐈 Chats", rongeur: "🐹 Rongeurs" };
                return `Espèce : ${map[v] || v}`;
            },
            q: function (v) { return `Recherche : "${v}"`; },
            status: function (v) {
                const map = { adoptable: "Adoptable", recherche_fa: "Recherche FA", reserve: "Réservé", adopte: "Adopté" };
                return `Statut : ${map[v] || v}`;
            },
            sex: function (v) {
                const map = { male: "Mâle", femelle: "Femelle" };
                return `Sexe : ${map[v] || v}`;
            },
            housing: function (v) {
                const map = { maison: "Maison", appartement: "Appartement" };
                return `Habitat : ${map[v] || v}`;
            },
            ok_dogs: function () { return "🐕 Ok chiens"; },
            ok_cats: function () { return "🐈 Ok chats"; },
            ok_children: function () { return "👶 Ok enfants"; },
            emergency: function () { return "🚨 Urgences"; }
        };

        for (const [key, value] of params.entries()) {
            if (key === "page" || !value) continue;
            hasAnyFilter = true;

            const chip = document.createElement("span");
            chip.className = `active-chip${key === "emergency" ? " active-chip--emergency" : ""}`;
            chip.setAttribute("data-field", key);

            const labelFormatter = labels[key];
            const textContent = labelFormatter ? labelFormatter(value) : `${key}: ${value}`;

            chip.innerHTML = `${textContent} <button type="button" class="chip-remove" aria-label="Supprimer ce filtre">&times;</button>`;
            activeChipsList.appendChild(chip);
        }

        if (hasAnyFilter) {
            activeChipsBar.classList.remove("hidden");
            if (resetContainer) resetContainer.classList.remove("hidden");
        } else {
            activeChipsBar.classList.add("hidden");
            if (resetContainer) resetContainer.classList.add("hidden");
        }

        if (clearBtn) {
            if (params.get("q")) {
                clearBtn.classList.remove("hidden");
            } else {
                clearBtn.classList.add("hidden");
            }
        }
    }

    // --- Helper: Bind Pagination Clicks ---
    function bindPaginationEvents() {
        const pagLinks = resultsWrapper.querySelectorAll(".btn-pagination[data-page]");
        pagLinks.forEach(function (link) {
            link.addEventListener("click", function (e) {
                e.preventDefault();
                const pageNumber = this.getAttribute("data-page");
                if (pageNumber) {
                    applyFilters(pageNumber, true, false);
                }
            });
        });

        // Bind Empty state reset button if present
        const emptyResetBtn = resultsWrapper.querySelector("#btn-empty-reset");
        if (emptyResetBtn) {
            emptyResetBtn.addEventListener("click", function () {
                resetAllFilters();
            });
        }
    }

    // --- Reset All Filters ---
    function resetAllFilters() {
        form.reset();
        if (speciesInput) speciesInput.value = "";
        if (qInput) qInput.value = "";

        speciesTabs.forEach(function (tab) {
            if (tab.getAttribute("data-species") === "") {
                tab.classList.add("active");
                tab.setAttribute("aria-selected", "true");
            } else {
                tab.classList.remove("active");
                tab.setAttribute("aria-selected", "false");
            }
        });

        if (clearBtn) clearBtn.classList.add("hidden");
        applyFilters(null, true, false);
    }

    // --- Event: Species Tabs Click ---
    speciesTabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
            const speciesVal = this.getAttribute("data-species") || "";
            speciesTabs.forEach(t => {
                t.classList.remove("active");
                t.setAttribute("aria-selected", "false");
            });
            this.classList.add("active");
            this.setAttribute("aria-selected", "true");

            if (speciesInput) {
                speciesInput.value = speciesVal;
            }
            applyFilters(null, true, false);
        });
    });

    // --- Event: Select Dropdowns Change ---
    const selects = form.querySelectorAll("select");
    selects.forEach(function (select) {
        select.addEventListener("change", function () {
            applyFilters(null, true, false);
        });
    });

    // --- Event: Checkboxes Change ---
    const checkboxes = form.querySelectorAll("input[type='checkbox']");
    checkboxes.forEach(function (cb) {
        cb.addEventListener("change", function () {
            applyFilters(null, true, false);
        });
    });

    // --- Event: Search Input with Debounce ---
    if (qInput) {
        qInput.addEventListener("input", function () {
            if (clearBtn) {
                if (this.value.trim().length > 0) {
                    clearBtn.classList.remove("hidden");
                } else {
                    clearBtn.classList.add("hidden");
                }
            }
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function () {
                applyFilters(null, true, true);
            }, 280);
        });

        qInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                clearTimeout(debounceTimer);
                applyFilters(null, true, false);
            }
        });
    }

    // --- Event: Search Clear Button ---
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            if (qInput) {
                qInput.value = "";
                clearBtn.classList.add("hidden");
                qInput.focus();
                applyFilters(null, true, false);
            }
        });
    }

    // --- Event: Global Reset Button ---
    if (resetBtn) {
        resetBtn.addEventListener("click", function () {
            resetAllFilters();
        });
    }

    // --- Event: Active Chip Click (Remove single filter) ---
    if (activeChipsList) {
        activeChipsList.addEventListener("click", function (e) {
            const removeBtn = e.target.closest(".chip-remove");
            if (!removeBtn) return;

            const chip = removeBtn.closest(".active-chip");
            if (!chip) return;

            const fieldName = chip.getAttribute("data-field");
            if (!fieldName) return;

            if (fieldName === "species") {
                if (speciesInput) speciesInput.value = "";
                speciesTabs.forEach(t => {
                    if (t.getAttribute("data-species") === "") {
                        t.classList.add("active");
                        t.setAttribute("aria-selected", "true");
                    } else {
                        t.classList.remove("active");
                        t.setAttribute("aria-selected", "false");
                    }
                });
            } else if (fieldName === "q") {
                if (qInput) qInput.value = "";
                if (clearBtn) clearBtn.classList.add("hidden");
            } else {
                const inputElement = form.elements[fieldName];
                if (inputElement) {
                    if (inputElement.type === "checkbox") {
                        inputElement.checked = false;
                    } else {
                        inputElement.value = "";
                    }
                }
            }

            applyFilters(null, true, false);
        });
    }

    // --- Event: Browser Back/Forward navigation (popstate) ---
    window.addEventListener("popstate", function () {
        const urlParams = new URLSearchParams(window.location.search);

        // Sync Species tab
        const speciesVal = urlParams.get("species") || "";
        if (speciesInput) speciesInput.value = speciesVal;
        speciesTabs.forEach(tab => {
            if (tab.getAttribute("data-species") === speciesVal) {
                tab.classList.add("active");
                tab.setAttribute("aria-selected", "true");
            } else {
                tab.classList.remove("active");
                tab.setAttribute("aria-selected", "false");
            }
        });

        // Sync Search input
        const qVal = urlParams.get("q") || "";
        if (qInput) {
            qInput.value = qVal;
            if (clearBtn) {
                if (qVal) clearBtn.classList.remove("hidden");
                else clearBtn.classList.add("hidden");
            }
        }

        // Sync Selects
        selects.forEach(select => {
            const val = urlParams.get(select.name) || "";
            select.value = val;
        });

        // Sync Checkboxes
        checkboxes.forEach(cb => {
            const val = urlParams.get(cb.name);
            cb.checked = (val === cb.value || (cb.name === "emergency" && (val === "1" || val === "true")));
        });

        // Fetch without pushing another history entry
        applyFilters(urlParams.get("page") || null, false, false);
    });

    // Initial binding for pagination on first page load
    bindPaginationEvents();
}

/* ==========================================================================
   4. Scroll Animations (IntersectionObserver)
   ========================================================================== */
function initScrollAnimations() {
    reinitAnimations(document);
}

function reinitAnimations(rootElement) {
    const animatedElements = rootElement.querySelectorAll("[data-animate]:not(.animated)");
    if (animatedElements.length === 0) return;

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    const cards = Array.from(animatedElements);
                    const idx = cards.indexOf(entry.target);
                    const delay = (idx >= 0 ? (idx % 4) * 80 : 0);

                    setTimeout(function () {
                        entry.target.classList.add("animated");
                    }, delay);

                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.05,
            rootMargin: "0px 0px -20px 0px"
        });

        animatedElements.forEach(function (el) {
            observer.observe(el);
        });
    } else {
        animatedElements.forEach(function (el) {
            el.classList.add("animated");
        });
    }
}

/* ==========================================================================
   5. Alerts & Notifications
   ========================================================================== */
function initAlerts() {
    document.querySelectorAll(".alert").forEach(function (alert) {
        const closeBtn = alert.querySelector(".alert-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", function () {
                dismissAlert(alert);
            });
        }
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
}

/* ==========================================================================
   6. Sticky Header Elevation
   ========================================================================== */
function initStickyHeader() {
    const header = document.getElementById("site-header");
    if (!header) return;

    window.addEventListener("scroll", function () {
        const scrollY = window.pageYOffset;
        if (scrollY > 15) {
            header.classList.add("is-scrolled");
        } else {
            header.classList.remove("is-scrolled");
        }
    }, { passive: true });
}
