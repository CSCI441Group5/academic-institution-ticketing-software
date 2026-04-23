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

const minSize = 8;  // Minimum font size in px
const maxSize = 36;  // Maximum font size in px

function changeSize(delta){
    const current = parseFloat(getComputedStyle(root).getPropertyValue("--font-size"));
    const next = current + delta;



    if (next >= minSize && next <= maxSize) {
        root.style.setProperty("--font-size", next + "px");
        localStorage.setItem("font-size", next + "px");

        // Update button states after the change
        updateButtonStates();
    }
}

function updateButtonStates() {
    const current = parseFloat(getComputedStyle(root).getPropertyValue("--font-size"));
    
    // Disable/enable smaller button
    if (current <= minSize) {
        smaller.disabled = true;
        smaller.classList.add("disabled");  // Add CSS class for graying out
    } else {
        smaller.disabled = false;
        smaller.classList.remove("disabled");
    }
    
    // Disable/enable bigger button
    if (current >= maxSize) {
        bigger.disabled = true;
        bigger.classList.add("disabled");
    } else {
        bigger.disabled = false;
        bigger.classList.remove("disabled");
    }
    
    // Reset button can stay enabled always, or add similar logic if needed
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