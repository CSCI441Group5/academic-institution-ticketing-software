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

/* Font Size Toggle Logic */
const savedSize = localStorage.getItem("font-size");
if(savedSize){
    root.style.setProperty("--font-size", savedSize);
}

const smaller = document.getElementById("text-smaller");
const bigger = document.getElementById("text-bigger");
const reset = document.getElementById("text-reset");

function changeSize(delta){
    const current = parseFloat(getComputedStyle(root).getPropertyValue("--font-size"));
    const next = current + delta;
    root.style.setProperty("--font-size", next + "px");
    localStorage.setItem("font-size", next + "px");
}

if(smaller){
    smaller.addEventListener("click", () => changeSize(-2));
}

if(bigger){
    bigger.addEventListener("click", () => changeSize(2));
}

if(reset){
    reset.addEventListener("click", () => {
        root.style.setProperty("--font-size", "16px");
        localStorage.setItem("font-size", "16px");
    });
}