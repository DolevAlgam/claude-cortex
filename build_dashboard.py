#!/usr/bin/env python3
# AI Brain Monitor dashboard generator.
# - STORIES section: EVERY current (non-archived) session, always shown, with its next step.
#   Ages are computed live from lastActivityEpoch vs now (never a frozen relative string).
# - Change feed + exec summary are authored per-cycle in cycle_top.py (PRIVATE / gitignored).
# - Per-session action log is generated from changelog.json (append-only, persistent).
import json, html, time

NOW = int(time.time())
state = json.load(open("state.json"))
clog  = json.load(open("changelog.json"))
cycle = state["cycle"]

try:
    from cycle_top import HEADER_DATE, FEED, EXEC
except ImportError:
    HEADER_DATE = "YYYY-MM-DD · HH:MM TZ"
    FEED = []
    EXEC = "Executive summary of the current state."

def esc(s): return html.escape(str(s), quote=False)

def ago(ep):
    if not ep: return ""
    d = NOW - int(ep)
    if d < 90: return "just now"
    if d < 3600: return f"~{round(d/60)}m ago"
    if d < 86400: return f"~{round(d/3600)}h ago"
    return f"~{round(d/86400)}d ago"

# status -> (dot color, chip classes, bucket-order)
STATUS = {
  "active":  ("bg-indigo-400",  "bg-indigo-500/15 text-indigo-300",  0),
  "done":    ("bg-emerald-500", "bg-emerald-500/15 text-emerald-300",1),
  "dormant": ("bg-slate-600",   "bg-slate-600/20 text-slate-400",    2),
  "archived":("bg-slate-700",   "bg-slate-700/20 text-slate-500",    3),
}
CARDC = {"emerald":"border-emerald-700/55 bg-emerald-950/20","indigo":"border-indigo-700/60 bg-indigo-950/20",
         "amber":"border-amber-600/60 bg-amber-950/25","red":"border-red-700/55 bg-red-950/20",
         "slate":"border-slate-800 bg-slate-900/30","sky":"border-sky-700/55 bg-sky-950/20"}
TXTC = {"emerald":"text-emerald-100","indigo":"text-indigo-100","amber":"text-amber-100",
        "red":"text-red-100","slate":"text-slate-200","sky":"text-sky-100"}
KIND_COLOR = {"new":"sky","progress":"indigo","blocked":"red","resolved":"emerald",
              "validated":"emerald","forgotten":"amber","drift":"amber","note":"slate"}

# ---- changelog grouped by stream (newest first) ----
by_stream = {}
for e in clog: by_stream.setdefault(e.get("stream","_"), []).append(e)
for k in by_stream: by_stream[k].sort(key=lambda e: e.get("cycle",0), reverse=True)

# ---- CHANGE FEED (authored) ----
feed_html = ""
for color,icon,title,sid,body in FEED:
    feed_html += f'''<div class="rounded-xl border {CARDC.get(color,CARDC['slate'])} px-4 py-3 mb-2">
      <div class="flex items-center gap-2"><i data-lucide="{icon}" class="w-4 h-4 shrink-0"></i>
      <span class="text-sm font-semibold {TXTC.get(color,TXTC['slate'])} flex-1">{esc(title)} <span class="sid mono">{esc(sid)}</span></span></div>
      <p class="text-xs text-slate-300 mt-1 ml-6">{body}</p></div>'''
if not feed_html:
    feed_html = '<div class="rounded-xl border border-slate-800 bg-slate-900/30 px-4 py-2.5 text-xs text-slate-400">No change this cycle — full story state below.</div>'

# ---- STORIES: every current (non-archived) session, ALWAYS, with next step ----
cur = [(k,v) for k,v in state["streams"].items() if not v.get("archived")]
cur.sort(key=lambda kv: (STATUS.get(kv[1].get("status","dormant"),("","",2))[2],
                          -(kv[1].get("lastActivityEpoch") or 0)))
stories_html = ""
for k,v in cur:
    dot,chip,_ = STATUS.get(v.get("status","dormant"), STATUS["dormant"])
    label=esc(v.get("label",k)); sid=esc(v.get("sessionId","")); repo=esc(v.get("repo",""))
    status=esc(v.get("status","")); age=ago(v.get("lastActivityEpoch"))
    state_line=esc(v.get("valStatus","")); nxt=esc(v.get("nextAction","—"))
    stories_html += f'''<div class="rounded-xl border border-slate-800 bg-slate-900/40 px-4 py-3 mb-2">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full {dot} shrink-0"></span>
        <span class="text-sm font-semibold text-slate-100 flex-1">{label} <span class="sid mono">{sid}</span> <span class="text-slate-600 text-xs">{repo}</span></span>
        <span class="chip px-1.5 py-0.5 rounded {chip}">{status}</span>
        <span class="age text-slate-500 mono">{age}</span></div>
      <p class="text-xs text-slate-400 mt-1.5 ml-4">{state_line}</p>
      <p class="text-xs text-slate-200 mt-1 ml-4"><span class="text-emerald-400 font-semibold">Next →</span> {nxt}</p></div>'''

# ---- per-session action log (current stories first, then archived) ----
log_html = ""
order = [k for k,_ in cur] + [k for k,v in state["streams"].items() if v.get("archived")]
for k in order:
    v=state["streams"][k]; entries=by_stream.get(k,[])
    if not entries: continue
    label=esc(v.get("label",k)); sid=esc(v.get("sessionId","")); status=esc(v.get("status",""))
    _,chip,_=STATUS.get(v.get("status","dormant"),STATUS["dormant"])
    rows=""
    for e in entries:
        col=KIND_COLOR.get(e.get("kind","note"),"slate")
        rows+=f'''<div class="flex gap-2 py-1 border-b border-slate-800/60">
          <span class="w-1.5 h-1.5 rounded-full bg-{col}-400 mt-1.5 shrink-0"></span>
          <span class="age text-slate-500 mono shrink-0 w-10">c{e.get("cycle","")}</span>
          <span class="text-xs text-slate-300 flex-1">{esc(e.get("text",""))}</span></div>'''
    log_html+=f'''<div class="rounded-xl border border-slate-800 bg-slate-900/40 mb-3">
      <div class="flex items-center gap-2 px-3 py-2 border-b border-slate-800">
        <span class="text-sm font-semibold text-slate-100">{label}</span><span class="sid mono">{sid}</span>
        <span class="chip px-1.5 py-0.5 rounded {chip} ml-auto">{status}</span></div>
      <div class="px-3 py-1.5 overflow-y-auto" style="max-height:170px">{rows}</div></div>'''

narch = sum(1 for v in state["streams"].values() if v.get("archived"))

html_out = f'''<!DOCTYPE html><html lang="en" class="dark"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AI Brain Monitor · Cycle {cycle}</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script>
<style>body{{background:#0a0b0e}}.mono{{font-family:ui-monospace,monospace}}.sid{{font-size:9px;opacity:.45;font-family:ui-monospace,monospace}}
.chip{{font-size:10px;letter-spacing:.04em}}.age{{font-size:10px}}
::-webkit-scrollbar{{width:8px;height:8px}}::-webkit-scrollbar-thumb{{background:#26282f;border-radius:6px}}</style></head>
<body class="text-slate-200 font-sans antialiased"><div class="max-w-5xl mx-auto px-5 py-7">
  <div class="flex items-baseline justify-between border-b border-slate-800 pb-3 mb-5">
    <div><h1 class="text-lg font-semibold text-white tracking-tight">AI Brain Monitor</h1>
    <p class="text-xs text-slate-500">Every story · its state · its next step — always</p></div>
    <div class="text-right"><div class="text-indigo-400 mono text-sm">CYCLE {cycle}</div>
    <div class="text-[11px] text-slate-500 mono">{esc(HEADER_DATE)}</div></div></div>

  <h2 class="text-[11px] uppercase tracking-widest text-slate-400 mb-2 flex items-center gap-1.5"><i data-lucide="zap" class="w-3.5 h-3.5 text-indigo-400"></i>What changed · cycle {cycle}</h2>
  <div class="mb-5">{feed_html}</div>

  <div class="rounded-lg bg-slate-900/50 border border-slate-800 px-4 py-2.5 mb-6"><p class="text-xs text-slate-300">{EXEC}</p></div>

  <h2 class="text-[11px] uppercase tracking-widest text-slate-400 mb-2 flex items-center gap-1.5"><i data-lucide="layout-list" class="w-3.5 h-3.5 text-emerald-400"></i>Stories — state &amp; next step <span class="normal-case tracking-normal text-slate-600">· every current session, live → dormant</span></h2>
  <div class="mb-6">{stories_html}</div>

  <h2 class="text-[11px] uppercase tracking-widest text-slate-500 mb-2 flex items-center gap-1.5"><i data-lucide="history" class="w-3.5 h-3.5 text-slate-400"></i>Per-session action log <span class="normal-case tracking-normal text-slate-600">· persistent · scrollable · newest on top</span></h2>
  <div class="mb-4">{log_html}</div>
  <p class="text-[11px] text-slate-600 mb-6">+ {narch} archived (done / &gt;24h) — kept in the log above, hidden from Stories.</p>

  <p class="text-center text-[11px] text-slate-600 mt-2 mono">cycle {cycle} · {len(cur)} current stories · ages live-computed · loop c33fe614</p>
</div><script>lucide.createIcons()</script></body></html>'''
open("dashboard.html","w").write(html_out)
print(f"dashboard written · {len(cur)} current stories · {narch} archived")
