(function() {
    "use strict";

    var zone = document.getElementById("media-upload-zone");
    var input = document.getElementById("media-upload-input");
    var btn = document.getElementById("media-upload-btn");
    var progress = document.getElementById("media-upload-progress");
    var fill = document.getElementById("media-upload-fill");
    var label = document.getElementById("media-upload-label");
    var results = document.getElementById("media-upload-results");

    if (!zone || !input) return;

    // Browse button
    btn.addEventListener("click", function() { input.click(); });
    input.addEventListener("change", function() {
        if (input.files.length) uploadFiles(input.files);
    });

    // Drag events
    ["dragenter", "dragover"].forEach(function(evt) {
        zone.addEventListener(evt, function(e) {
            e.preventDefault();
            e.stopPropagation();
            zone.classList.add("drag-hover");
        });
    });
    ["dragleave", "drop"].forEach(function(evt) {
        zone.addEventListener(evt, function(e) {
            e.preventDefault();
            e.stopPropagation();
            zone.classList.remove("drag-hover");
        });
    });
    zone.addEventListener("drop", function(e) {
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

        progress.style.display = "block";
        fill.style.width = "0%";
        label.textContent = "Upload de " + files.length + " fichier(s)...";

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "upload-dnd/");

        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));

        xhr.upload.addEventListener("progress", function(e) {
            if (e.lengthComputable) {
                var pct = Math.round((e.loaded / e.total) * 100);
                fill.style.width = pct + "%";
                label.textContent = pct + "%";
            }
        });

        xhr.addEventListener("load", function() {
            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                fill.style.width = "100%";
                label.textContent = data.uploaded.length + " fichier(s) uploade(s)";
                showResults(data.uploaded);
            } else {
                label.textContent = "Erreur (" + xhr.status + ")";
                fill.style.width = "0%";
            }
        });

        xhr.addEventListener("error", function() {
            label.textContent = "Erreur reseau";
        });

        xhr.send(formData);
    }

    function showResults(items) {
        items.forEach(function(item) {
            var card = document.createElement("div");
            card.className = "upload-result-card";
            if (item.is_image && item.url) {
                card.innerHTML = '<img src="' + item.url + '" alt=""><div class="upload-result-name">' + escHtml(item.title) + '</div>';
            } else {
                card.innerHTML = '<div class="file-icon">' + escHtml(item.mime_type || "?") + '</div><div class="upload-result-name">' + escHtml(item.title) + '</div>';
            }
            results.appendChild(card);
        });
    }

    function escHtml(s) {
        var d = document.createElement("div");
        d.appendChild(document.createTextNode(s));
        return d.innerHTML;
    }
})();
