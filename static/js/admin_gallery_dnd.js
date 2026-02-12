(function() {
    "use strict";

    function initGalleryDnD() {
        var container = document.querySelector(".gallery-dnd-zone");
        if (!container) return;

        var prefix = "postgalleryimage_set";
        var dragItem = null;

        // ── Reorder drag-and-drop ──

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

        // ── File upload zone ──

        var uploadZone = document.getElementById("gallery-upload-zone");
        var uploadInput = document.getElementById("gallery-upload-input");
        var uploadBtn = document.getElementById("gallery-upload-btn");
        var progressEl = document.getElementById("gallery-upload-progress");
        var fillEl = document.getElementById("gallery-upload-fill");
        var labelEl = document.getElementById("gallery-upload-label");

        if (!uploadZone || !uploadInput) return;

        uploadBtn.addEventListener("click", function() { uploadInput.click(); });
        uploadInput.addEventListener("change", function() {
            if (uploadInput.files.length) uploadFiles(uploadInput.files);
        });

        ["dragenter", "dragover"].forEach(function(evt) {
            uploadZone.addEventListener(evt, function(e) {
                e.preventDefault();
                e.stopPropagation();
                uploadZone.classList.add("drag-hover");
            });
        });
        ["dragleave", "drop"].forEach(function(evt) {
            uploadZone.addEventListener(evt, function(e) {
                e.preventDefault();
                e.stopPropagation();
                uploadZone.classList.remove("drag-hover");
            });
        });
        uploadZone.addEventListener("drop", function(e) {
            var files = e.dataTransfer.files;
            if (files.length) uploadFiles(files);
        });

        function getCookie(name) {
            var value = "; " + document.cookie;
            var parts = value.split("; " + name + "=");
            if (parts.length === 2) return parts.pop().split(";").shift();
            return "";
        }

        function uploadFiles(files) {
            var formData = new FormData();
            for (var i = 0; i < files.length; i++) {
                formData.append("files", files[i]);
            }

            progressEl.style.display = "block";
            fillEl.style.width = "0%";
            labelEl.textContent = "Upload de " + files.length + " fichier(s)...";

            var xhr = new XMLHttpRequest();
            // The upload endpoint is on PostAdmin: /admin/blog/post/upload-media/
            xhr.open("POST", "/admin/blog/post/upload-media/");
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));

            xhr.upload.addEventListener("progress", function(e) {
                if (e.lengthComputable) {
                    var pct = Math.round((e.loaded / e.total) * 100);
                    fillEl.style.width = pct + "%";
                    labelEl.textContent = pct + "%";
                }
            });

            xhr.addEventListener("load", function() {
                if (xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    fillEl.style.width = "100%";
                    labelEl.textContent = data.uploaded.length + " image(s) ajoutee(s)";
                    data.uploaded.forEach(function(item) {
                        if (item.is_image) {
                            addGalleryCard(item);
                        }
                    });
                    // Reset input so same files can be re-selected
                    uploadInput.value = "";
                } else {
                    labelEl.textContent = "Erreur (" + xhr.status + ")";
                    fillEl.style.width = "0%";
                }
            });

            xhr.addEventListener("error", function() {
                labelEl.textContent = "Erreur reseau";
            });

            xhr.send(formData);
        }

        function addGalleryCard(item) {
            // Get the TOTAL_FORMS management field
            var totalInput = document.getElementById("id_" + prefix + "-TOTAL_FORMS");
            if (!totalInput) return;
            var idx = parseInt(totalInput.value, 10);

            // Find an empty (unused) inline form, or clone from extra forms
            var extraForms = document.querySelector(".gallery-dnd-extra-forms");
            var emptyForm = extraForms ? extraForms.querySelector(".inline-related") : null;

            // Build the new card
            var card = document.createElement("div");
            card.className = "gallery-card";
            card.draggable = true;
            card.setAttribute("data-inline-idx", idx);
            card.innerHTML =
                '<img src="' + escHtml(item.url) + '" alt="">' +
                '<div class="gallery-card-label">' + escHtml(item.title).substring(0, 18) + '</div>' +
                '<span class="gallery-card-delete" title="Retirer">&times;</span>' +
                '<div style="display:none">' +
                    '<input type="hidden" name="' + prefix + '-' + idx + '-media" value="' + item.id + '">' +
                    '<input type="hidden" name="' + prefix + '-' + idx + '-position" value="' + idx + '">' +
                    '<input type="hidden" name="' + prefix + '-' + idx + '-id" value="">' +
                    '<input type="hidden" name="' + prefix + '-' + idx + '-post" value="">' +
                    '<input type="hidden" name="' + prefix + '-' + idx + '-DELETE" value="">' +
                '</div>';

            container.appendChild(card);
            totalInput.value = idx + 1;

            // Update all positions
            updatePositions();
        }

        function escHtml(s) {
            var d = document.createElement("div");
            d.appendChild(document.createTextNode(s));
            return d.innerHTML;
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initGalleryDnD);
    } else {
        initGalleryDnD();
    }
})();
