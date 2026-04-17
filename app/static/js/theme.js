const toggle = document.getElementById("theme-toggle")
const root = document.documentElement;

if(localStorage.getItem("theme")){
    root.setAttribute("data-theme", localStorage.getItem("theme"));
}

toggle.addEventListener("click", () => { 
    const current = root.getAttribute("data-theme")
    const next = current === "dark" ? "light" : "dark";

    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
});