import os
import html
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
import yaml

APP_NAME = "WizardWebb"
ROOT = Path(__file__).parent
DEFAULT_LINKS_FILE = ROOT / "data" / "links.yml"
LINKS_FILE = Path(os.environ.get("LINKS_FILE", str(DEFAULT_LINKS_FILE)))

@st.cache_data
def load_links(path: str) -> List[Dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise ValueError("links.yml must be a YAML list")
    out: List[Dict[str, Any]] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        out.append({
            "id": item.get("id") or f"item_{i+1}",
            "name": str(item.get("name", "")).strip() or "(Unnamed)",
            "url": (str(item.get("url")).strip() if item.get("url") else None),
            "description": str(item.get("description", "")).strip(),
            "category": str(item.get("category", "Other")).strip() or "Other",
            "tags": item.get("tags") if isinstance(item.get("tags"), list) else ([] if item.get("tags") is None else [str(item.get("tags"))]),
            "status": str(item.get("status", "ok")).strip().lower(),
            "note": str(item.get("note", "")).strip(),
        })
    return out

def categories(links: List[Dict[str, Any]]) -> List[str]:
    cats = sorted({(l.get("category") or "Other") for l in links})
    preferred = ["Search", "Research", "OSINT", "Security & Privacy", "Web Tools", "Freebies & Deals", "Other"]
    ordered = [c for c in preferred if c in cats] + [c for c in cats if c not in preferred]
    return ordered

def esc(s: str) -> str:
    return html.escape(str(s or ""))

def badge(status: str) -> str:
    status = (status or "ok").lower()
    if status == "ok":
        return '<span class="badge ok">Linked</span>'
    if status == "omitted":
        return '<span class="badge omitted">Unlinked by default</span>'
    return '<span class="badge caution">Caution</span>'

st.set_page_config(page_title=APP_NAME, page_icon="🕵️", layout="wide")

# Noir CSS
st.markdown("""
<style>
:root{ --mx:50vw; --my:20vh; }
.stApp{
  background:
    radial-gradient(1200px 700px at 70% -10%, rgba(68,217,255,.12), transparent 55%),
    radial-gradient(900px 600px at 15% 10%, rgba(255,209,122,.08), transparent 55%),
    radial-gradient(900px 700px at 40% 120%, rgba(183,255,107,.06), transparent 60%),
    linear-gradient(180deg, rgba(255,255,255,.03), transparent 18%),
    #07080b !important;
  color:#eef2f7 !important;
}
.noir-top{
  border:1px solid rgba(238,242,247,.10);
  background:linear-gradient(180deg, rgba(12,15,20,.82), rgba(10,12,16,.72));
  border-radius:18px; padding:14px 16px;
  box-shadow:0 20px 60px rgba(0,0,0,.35);
  display:flex; align-items:center; justify-content:space-between; gap:14px;
}
.noir-brand{ display:flex; align-items:center; gap:12px; }
.noir-logo{
  width:38px; height:38px; border-radius:14px;
  background:
    radial-gradient(circle at 25% 30%, rgba(255,209,122,.95), rgba(255,209,122,0) 55%),
    linear-gradient(135deg, rgba(68,217,255,.9), rgba(183,255,107,.55));
  box-shadow:0 14px 40px rgba(68,217,255,.12);
  border:1px solid rgba(255,255,255,.10);
}
.noir-title{ margin:0; font-size:16px; letter-spacing:.6px; }
.noir-sub{ margin-top:2px; color:#aab3c2; font-size:12px; }
.pill{
  display:inline-flex; align-items:center; gap:8px;
  border:1px solid rgba(238,242,247,.10);
  background:linear-gradient(180deg, rgba(12,15,20,.78), rgba(10,12,16,.62));
  padding:8px 12px; border-radius:999px;
  color:#aab3c2; text-decoration:none; font-size:13px;
}
.pill:hover{ border-color:rgba(68,217,255,.35); color:#eef2f7; }
.card{
  border:1px solid rgba(238,242,247,.10);
  background:linear-gradient(180deg, rgba(12,15,20,.78), rgba(10,12,16,.66));
  border-radius:18px; padding:14px;
  box-shadow:0 18px 60px rgba(0,0,0,.28);
  transition:transform .12s ease, border-color .12s ease, box-shadow .12s ease;
  height:100%;
  position:relative;
  overflow:hidden;
}
.card:hover{ transform:translateY(-2px); border-color:rgba(68,217,255,.30); box-shadow:0 22px 70px rgba(0,0,0,.40); }
.card::after{
  content:"";
  position:absolute; inset:-2px;
  background: radial-gradient(600px 180px at 20% 0%, rgba(68,217,255,.10), transparent 45%);
  opacity:.7; pointer-events:none;
}
.h3{ margin:0 0 6px; font-size:16px; letter-spacing:.2px; }
.p{ margin:0; color:#aab3c2; line-height:1.45; font-size:13px; }
.meta{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; position:relative; z-index:1; }
.badge{
  font-size:11px; padding:4px 8px; border-radius:999px;
  border:1px solid rgba(238,242,247,.10); color:#aab3c2;
  background:rgba(255,255,255,.02);
}
.badge.ok{ border-color:rgba(183,255,107,.30); color:rgba(183,255,107,.95); background:rgba(183,255,107,.05); }
.badge.omitted{ border-color:rgba(255,209,102,.30); color:rgba(255,209,102,.98); background:rgba(255,209,102,.06); }
.badge.caution{ border-color:rgba(255,107,107,.30); color:rgba(255,107,107,.98); background:rgba(255,107,107,.06); }
.actions{ display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; position:relative; z-index:1; }
.linkbtn{
  display:inline-flex; align-items:center; gap:8px;
  padding:9px 11px; border-radius:14px;
  border:1px solid rgba(238,242,247,.10);
  background:rgba(255,255,255,.02);
  text-decoration:none; color:#eef2f7; font-size:13px;
}
.linkbtn:hover{ border-color:rgba(68,217,255,.35); }
.small{ color:#aab3c2; font-size:12px; }
</style>
""", unsafe_allow_html=True)

links = load_links(str(LINKS_FILE))
cats = ["All"] + categories(links)

# Header
st.markdown(f"""
<div class="noir-top">
  <div class="noir-brand">
    <div class="noir-logo"></div>
    <div>
      <div class="noir-title">{APP_NAME}</div>
      <div class="noir-sub">Noir directory of web tools • search • filter • save time</div>
    </div>
  </div>
  <div style="display:flex; gap:10px; flex-wrap:wrap;">
    <a class="pill" href="https://github.com/MichaelWave369/WizardWebb" target="_blank">GitHub ↗</a>
  </div>
</div>
""", unsafe_allow_html=True)

st.write("")
col1, col2, col3, col4 = st.columns([3, 2, 1.3, 1])
q = col1.text_input("Search", placeholder="Search (name, description, tags)...")
cat = col2.selectbox("Category", options=cats, index=0)
show_unlinked = col3.toggle("Show unlinked", value=True)
clear = col4.button("Clear")

if clear:
    st.session_state.clear()
    st.experimental_rerun()

def match(it: Dict[str, Any]) -> bool:
    if not show_unlinked and not it.get("url"):
        return False
    if cat != "All" and (it.get("category") or "Other") != cat:
        return False
    if q:
        hay = " ".join([
            it.get("name",""),
            it.get("description",""),
            it.get("category",""),
            " ".join(it.get("tags") or [])
        ]).lower()
        if q.lower() not in hay:
            return False
    return True

filtered = [it for it in links if match(it)]
st.caption(f"{len(filtered)} shown / {len(links)} total  •  Source: {LINKS_FILE}")

# Render cards (2 columns)
for i in range(0, len(filtered), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j >= len(filtered):
            break
        it = filtered[i + j]
        url = it.get("url")
        open_btn = f'<a class="linkbtn" href="{esc(url)}" target="_blank" rel="noopener noreferrer">Open ↗</a>' if url else '<span class="linkbtn" style="opacity:.55; cursor:not-allowed;">No link</span>'
        tags = "".join([f'<span class="badge">{esc(t)}</span>' for t in (it.get("tags") or [])[:6]])
        note = f'<div class="small" style="margin-top:8px;">{esc(it.get("note"))}</div>' if it.get("note") else ""
        card_html = f"""
        <div class="card">
          <div class="h3">{esc(it.get("name"))}</div>
          <div class="p">{esc(it.get("description"))}</div>
          {note}
          <div class="meta">
            {badge(it.get("status"))}
            <span class="badge">{esc(it.get("category"))}</span>
            {tags}
          </div>
          <div class="actions">{open_btn}</div>
        </div>
        """
        cols[j].markdown(card_html, unsafe_allow_html=True)
