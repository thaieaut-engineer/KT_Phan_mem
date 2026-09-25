document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("headerSearchToggle");
    var box = document.getElementById("headerSearchBox");
    var input = document.getElementById("headerSearchInput");
    var navbar = document.querySelector(".site-navbar");
    var backToTop = document.getElementById("backToTop");

    if (toggle && box) {
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
    }

    function onScroll() {
        var y = window.scrollY || 0;

        if (navbar) {
            navbar.classList.toggle("is-scrolled", y > 12);
        }

        if (backToTop) {
            backToTop.classList.toggle("is-visible", y > 420);
        }
    }

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    if (backToTop) {
        backToTop.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    var reveals = document.querySelectorAll(".reveal");

    if (!reveals.length) {
        return;
    }

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        reveals.forEach(function (el) {
            el.classList.add("is-visible");
        });
        return;
    }

    if (!("IntersectionObserver" in window)) {
        reveals.forEach(function (el) {
            el.classList.add("is-visible");
        });
        return;
    }

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: "0px 0px -40px 0px"
    });

    reveals.forEach(function (el) {
        observer.observe(el);
    });
});
