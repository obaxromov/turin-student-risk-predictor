// Runs before first paint so the saved theme shows with no flash.
try {
  var th = localStorage.getItem("theme");
  if (th === "dark" || th === "light") document.documentElement.setAttribute("data-theme", th);
} catch (e) { /* storage blocked: follow the system theme */ }
