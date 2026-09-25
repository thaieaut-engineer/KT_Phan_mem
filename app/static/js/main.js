document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("headerSearchToggle");
    var box = document.getElementById("headerSearchBox");
    var input = document.getElementById("headerSearchInput");

    if (!toggle || !box) {
        return;
    }

    toggle.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();

        box.classList.toggle("is-open");

        if (box.classList.contains("is-open") && input) {
            input.focus();
        }
    });

    box.addEventListener("click", function (event) {
        event.stopPropagation();
    });

    document.addEventListener("click", function () {
        box.classList.remove("is-open");
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            box.classList.remove("is-open");
        }
    });
});
