(function() {
    "use strict";

    function initGalleryDnD() {
        var container = document.querySelector(".gallery-dnd-zone");
        if (!container) return;

        var dragItem = null;

        container.addEventListener("dragstart", function(e) {
            var card = e.target.closest(".gallery-card");
            if (!card) return;
            dragItem = card;
            card.classList.add("dragging");
            e.dataTransfer.effectAllowed = "move";
        });

        container.addEventListener("dragend", function(e) {
            var card = e.target.closest(".gallery-card");
            if (card) card.classList.remove("dragging");
            dragItem = null;
            container.querySelectorAll(".gallery-card").forEach(function(c) {
                c.classList.remove("drag-over");
            });
            updatePositions();
        });

        container.addEventListener("dragover", function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
            var card = e.target.closest(".gallery-card");
            if (card && card !== dragItem) {
                var rect = card.getBoundingClientRect();
                var midX = rect.left + rect.width / 2;
                container.querySelectorAll(".gallery-card").forEach(function(c) {
                    c.classList.remove("drag-over");
                });
                if (e.clientX < midX) {
                    card.parentNode.insertBefore(dragItem, card);
                } else {
                    card.parentNode.insertBefore(dragItem, card.nextSibling);
                }
            }
        });

        // Delete button
        container.addEventListener("click", function(e) {
            var btn = e.target.closest(".gallery-card-delete");
            if (!btn) return;
            var card = btn.closest(".gallery-card");
            if (!card) return;
            var checkbox = card.querySelector("input[type='checkbox'][id$='-DELETE']");
            if (checkbox) {
                checkbox.checked = true;
                card.style.display = "none";
            }
            updatePositions();
        });

        function updatePositions() {
            var cards = container.querySelectorAll(".gallery-card:not([style*='display: none'])");
            cards.forEach(function(card, idx) {
                var posInput = card.querySelector("input[id$='-position']");
                if (posInput) posInput.value = idx;
            });
        }

        // Init positions on load
        updatePositions();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initGalleryDnD);
    } else {
        initGalleryDnD();
    }
})();
