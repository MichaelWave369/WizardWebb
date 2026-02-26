function $(sel){ return document.querySelector(sel); }
function $all(sel){ return Array.from(document.querySelectorAll(sel)); }

function norm(s){ return (s || "").toLowerCase(); }

function renderCards(items){
  const grid = $("#grid");
  grid.innerHTML = "";
  if(!items.length){
    grid.innerHTML = `<div class="notice" style="grid-column: span 12;">
      <strong>No matches</strong>
      <p>Try clearing filters, changing your search, or toggling “Show unlinked”.</p>
    </div>`;
    return;
  }
  for(const it of items){
    const status = (it.status || "ok").toLowerCase();
    const badgeClass = status === "ok" ? "ok" : (status === "omitted" ? "omitted" : "caution");
    const statusLabel = status === "ok" ? "Linked" : (status === "omitted" ? "Unlinked by default" : "Caution");
    const url = it.url ? it.url : null;

    const tags = (it.tags || []).slice(0,6).map(t => `<span class="badge">${escapeHtml(t)}</span>`).join("");

    const note = it.note ? `<div class="smallmuted" style="margin-top:8px;">${escapeHtml(it.note)}</div>` : "";

    const openBtn = url
      ? `<a class="linkbtn" href="${escapeAttr(url)}" target="_blank" rel="noopener noreferrer">Open ↗</a>`
      : `<span class="linkbtn" style="opacity:.55;cursor:not-allowed;">No link</span>`;

    const copyBtn = url
      ? `<button class="btn small secondary" data-copy="${escapeAttr(url)}">Copy link</button>`
      : `<button class="btn small secondary" disabled>Copy link</button>`;

    const el = document.createElement("div");
    el.className = "card";
    el.innerHTML = `
      <h3>${escapeHtml(it.name)}</h3>
      <p>${escapeHtml(it.description || "")}</p>
      ${note}
      <div class="meta">
        <span class="badge ${badgeClass}">${statusLabel}</span>
        <span class="badge">${escapeHtml(it.category || "Other")}</span>
        ${tags}
      </div>
      <div class="actions">
        ${openBtn}
        ${copyBtn}
      </div>
    `;
    grid.appendChild(el);
  }

  $all("button[data-copy]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const text = btn.getAttribute("data-copy");
      try{
        await navigator.clipboard.writeText(text);
        const prev = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(()=>btn.textContent = prev, 900);
      }catch(e){
        alert("Could not copy to clipboard. Your browser may block clipboard access.");
      }
    });
  });
}

function escapeHtml(s){
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
function escapeAttr(s){ return escapeHtml(s); }

function computeFiltered(allLinks, state){
  const q = norm(state.query);
  const cat = state.category;
  const showUnlinked = state.showUnlinked;

  return allLinks.filter(it => {
    const hay = [
      it.name, it.description, it.category,
      ...(it.tags || [])
    ].map(norm).join(" ");
    if(q && !hay.includes(q)) return false;
    if(cat && cat !== "All" && (it.category || "Other") !== cat) return false;
    const hasUrl = Boolean(it.url);
    if(!showUnlinked && !hasUrl) return false;
    return true;
  });
}

window.addEventListener("DOMContentLoaded", () => {
  const allLinks = window.__LINKS__ || [];
  const categories = window.__CATEGORIES__ || [];
  const chips = $("#chips");

  window.addEventListener("mousemove", (e) => {
    document.documentElement.style.setProperty("--mx", e.clientX + "px");
    document.documentElement.style.setProperty("--my", e.clientY + "px");
  });

  window.addEventListener("keydown", (e) => {
    const isCtrlK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k";
    const isSlash = e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey;
    if(isCtrlK || isSlash){
      e.preventDefault();
      const q = document.getElementById("q");
      if(q) q.focus();
    }
  });

  const state = {
    query: "",
    category: "All",
    showUnlinked: true
  };

  function rerender(){
    const filtered = computeFiltered(allLinks, state);
    $("#count").textContent = `${filtered.length} shown / ${allLinks.length} total`;
    renderCards(filtered);
  }

  // Build category chips
  const allCats = ["All", ...categories];
  chips.innerHTML = "";
  for(const c of allCats){
    const chip = document.createElement("div");
    chip.className = "chip" + (c === "All" ? " active" : "");
    chip.textContent = c;
    chip.addEventListener("click", () => {
      state.category = c;
      $all(".chip").forEach(x => x.classList.remove("active"));
      chip.classList.add("active");
      rerender();
    });
    chips.appendChild(chip);
  }

  $("#q").addEventListener("input", (e) => {
    state.query = e.target.value || "";
    rerender();
  });

  $("#toggleUnlinked").addEventListener("click", () => {
    state.showUnlinked = !state.showUnlinked;
    $("#toggleUnlinked").textContent = state.showUnlinked ? "Hide unlinked" : "Show unlinked";
    rerender();
  });

  $("#clear").addEventListener("click", () => {
    $("#q").value = "";
    state.query = "";
    state.category = "All";
    state.showUnlinked = true;
    $("#toggleUnlinked").textContent = "Hide unlinked";
    $all(".chip").forEach((x, idx) => {
      x.classList.toggle("active", idx === 0);
    });
    rerender();
  });

  rerender();
});
