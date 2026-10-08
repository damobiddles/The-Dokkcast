// Mobile menu toggle. The site works without JavaScript on wide screens.
const btn = document.querySelector(".menu-btn"), nav = document.getElementById("site-nav");
if (btn && nav) btn.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  btn.setAttribute("aria-expanded", open);
});

// Close the Listen menu when you click elsewhere or press Escape.
const listen = document.querySelector(".listen-menu");
if (listen) {
  document.addEventListener("click", e => { if (!listen.contains(e.target)) listen.removeAttribute("open"); });
  document.addEventListener("keydown", e => { if (e.key === "Escape" && listen.open) { listen.removeAttribute("open"); listen.querySelector("summary").focus(); } });
}
