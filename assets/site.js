// Mobile menu toggle. The site works without JavaScript on wide screens.
const btn = document.querySelector(".menu-btn"), nav = document.getElementById("site-nav");
if (btn && nav) btn.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  btn.setAttribute("aria-expanded", open);
});
