/* AgenticEdge Blog — client-side helpers */

document.addEventListener("DOMContentLoaded", function () {
    // Confirm before deleting a post
    document.querySelectorAll(".delete-form").forEach(function (form) {
        form.addEventListener("submit", function (e) {
            if (!confirm("Are you sure you want to delete this post?")) {
                e.preventDefault();
            }
        });
    });

    // Auto-resize textareas in the editor
    document.querySelectorAll(".editor-form textarea").forEach(function (ta) {
        ta.addEventListener("input", function () {
            this.style.height = "auto";
            this.style.height = this.scrollHeight + "px";
        });
    });

    // --- Copy URL buttons ---
    function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text);
        }
        // Fallback for older browsers or restricted contexts
        var textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        try { document.execCommand("copy"); } catch (e) { /* ignore */ }
        document.body.removeChild(textarea);
        return Promise.resolve();
    }

    document.querySelectorAll(".btn-copy").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var url = btn.getAttribute("data-url");
            copyToClipboard(url).then(function () {
                btn.classList.add("copied");
                var origHTML = btn.innerHTML;
                btn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>';
                setTimeout(function () {
                    btn.classList.remove("copied");
                    btn.innerHTML = origHTML;
                }, 1500);
            });
        });
    });

    // --- Image paste from clipboard + preview ---
    var fileInput = document.getElementById("image");
    var previewContainer = document.getElementById("image-preview");
    if (!fileInput || !previewContainer) return;

    // Show preview when a file is selected via the file picker
    fileInput.addEventListener("change", function () {
        if (fileInput.files && fileInput.files[0]) {
            showPreview(fileInput.files[0]);
        }
    });

    // Listen for paste anywhere on the editor form
    var editorForm = document.querySelector(".editor-form");
    if (editorForm) {
        editorForm.addEventListener("paste", function (e) {
            var items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (var i = 0; i < items.length; i++) {
                if (items[i].type.indexOf("image") !== -1) {
                    e.preventDefault();
                    var blob = items[i].getAsFile();
                    // Create a new FileList-like DataTransfer to set on the input
                    var dt = new DataTransfer();
                    dt.items.add(blob);
                    fileInput.files = dt.files;
                    showPreview(blob);
                    break;
                }
            }
        });
    }

    function showPreview(file) {
        var reader = new FileReader();
        reader.onload = function (e) {
            previewContainer.innerHTML =
                '<img src="' + e.target.result + '" alt="Image preview" id="preview-img">' +
                '<p class="form-help">Image ready for upload</p>';
        };
        reader.readAsDataURL(file);
    }
});
