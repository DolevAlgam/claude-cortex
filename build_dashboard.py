#!/usr/bin/env python3
# AI Brain Monitor dashboard generator.
# Top (change-feed/summary) is authored per-cycle in CYCLE_TOP below; the
# per-session ACTION LOG section is generated from changelog.json (persistent, append-only).
import json, html

state = json.load(open("state.json"))
clog  = json.load(open("changelog.json"))
cycle = state["cycle"]

# ---- authored per-cycle top ----
# Real per-cycle content lives in cycle_top.py (PRIVATE / gitignored) so this generator stays
# generic and shareable. Falls back to neutral placeholders when cycle_top.py is absent.
try:
    from cycle_top import HEADER_DATE, FEED, EXEC, STATS, NEXT
except ImportError:
    HEADER_DATE = "YYYY-MM-DD · HH:MM TZ"
    FEED = [
      ("indigo","circle","Headline change since last cycle","<session-id>",
       "One short paragraph: what moved, why it matters, in the user's words. Colors: "
       "emerald=shipped/resolved, indigo=in-progress, amber=aging/decision, red=blocked/frustration, slate=quiet."),
    ]
    EXEC = "Two-line executive summary of the current state. <b>0 hard blockers.</b>"
    STATS = [("0","live"),("0","shipped"),("0","hard blockers"),("0","open")]
    NEXT = [("<session-id>","Recommended next action for this stream.")]
# kind -> color for log dots
KIND_COLOR = {"new":"sky","progress":"indigo","blocked":"red","resolved":"emerald",
              "validated":"emerald","forgotten":"amber","drift":"amber","note":"slate"}

def esc(s): return html.escape(s, quote=False)

# ---- group changelog by stream (newest first) ----
by_stream = {}
for e in clog:
    by_stream.setdefault(e.get("stream","_"), []).append(e)
for k in by_stream: by_stream[k].sort(key=lambda e: e.get("cycle",0), reverse=True)

# order streams by lastMtime desc (active first); _all pseudo-stream last
def stream_key(sid):
    st = state["streams"].get(sid, {})
    return st.get("lastMtime", 0)
stream_ids = [sid for sid in state["streams"]]
stream_ids.sort(key=stream_key, reverse=True)

CARDC = {"emerald":"border-emerald-700/55 bg-emerald-950/20","indigo":"border-indigo-700/60 bg-indigo-950/20",
         "amber":"border-amber-600/60 bg-amber-950/25","red":"border-red-700/55 bg-red-950/20","slate":"border-slate-800 bg-slate-900/30"}
TXTC = {"emerald":"text-emerald-100","indigo":"text-indigo-100","amber":"text-amber-100","red":"text-red-100","slate":"text-slate-200"}

feed_html = ""
for color,icon,title,sid,body in FEED:
    feed_html += f'''<div class="rounded-xl border {CARDC[color]} px-4 py-3 mb-2">
      <div class="flex items-center gap-2"><i data-lucide="{icon}" class="w-4 h-4 shrink-0"></i>
      <span class="text-sm font-semibold {TXTC[color]} flex-1">{esc(title)} <span class="sid mono">{sid}</span></span></div>
      <p class="text-xs text-slate-300 mt-1 ml-6">{body}</p></div>'''

stat_html = ""
for v,l in STATS:
    stat_html += f'<div class="rounded-lg bg-slate-900/60 border border-slate-800 px-3 py-2"><div class="text-xl font-semibold text-white">{v}</div><div class="text-[10px] uppercase tracking-wider text-slate-500">{esc(l)}</div></div>'

next_html = ""
for i,(sid,txt) in enumerate(NEXT,1):
    next_html += f'<li>{i}. <b class="mono text-xs">{sid}</b> — {esc(txt)}</li>'

# ---- persistent per-session action-log section ----
log_html = ""
for sid in stream_ids:
    st = state["streams"][sid]
    entries = by_stream.get(sid, [])
    if not entries: continue
    label = esc(st.get("label", sid))
    sess = esc(st.get("sessionId", sid))
    status = st.get("status","")
    age = esc(st.get("lastActivity",""))
    badge = {"done":"bg-emerald-500/15 text-emerald-300","active":"bg-indigo-500/15 text-indigo-300",
             "dormant":"bg-slate-600/20 text-slate-400"}.get(status,"bg-slate-600/20 text-slate-400")
    rows = ""
    for e in entries:
        col = KIND_COLOR.get(e.get("kind","note"),"slate")
        rows += f'''<div class="flex gap-2 py-1 border-b border-slate-800/60">
          <span class="w-1.5 h-1.5 rounded-full bg-{col}-400 mt-1.5 shrink-0"></span>
          <span class="age text-slate-500 mono shrink-0 w-12">c{e.get("cycle","")}</span>
          <span class="text-xs text-slate-300 flex-1">{esc(e.get("text",""))}</span></div>'''
    log_html += f'''<div class="rounded-xl border border-slate-800 bg-slate-900/40 mb-3">
      <div class="flex items-center gap-2 px-3 py-2 border-b border-slate-800">
        <span class="text-sm font-semibold text-slate-100">{label}</span>
        <span class="sid mono">{sess}</span>
        <span class="chip px-1.5 py-0.5 rounded {badge} ml-auto">{esc(status)}</span>
        <span class="age text-slate-500 mono">{age}</span></div>
      <div class="px-3 py-1.5 overflow-y-auto" style="max-height:190px">{rows}</div></div>'''

html_out = f'''<!DOCTYPE html><html lang="en" class="dark"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AI Brain Monitor · Cycle {cycle}</title>
<script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script>
<style>body{{background:#0a0b0e}}.mono{{font-family:ui-monospace,monospace}}.sid{{font-size:9px;opacity:.4;font-family:ui-monospace,monospace}}
.chip{{font-size:10px;letter-spacing:.04em}}.age{{font-size:10px}}
::-webkit-scrollbar{{width:8px;height:8px}}::-webkit-scrollbar-thumb{{background:#26282f;border-radius:6px}}</style></head>
<body class="text-slate-200 font-sans antialiased"><div class="max-w-5xl mx-auto px-5 py-7">
  <div class="flex items-baseline justify-between border-b border-slate-800 pb-3 mb-5">
    <div><h1 class="text-lg font-semibold text-white tracking-tight">AI Brain Monitor</h1>
    <p class="text-xs text-slate-500">Chief-of-staff view · glance on top · scrollable per-session log below</p></div>
    <div class="text-right"><div class="text-indigo-400 mono text-sm">CYCLE {cycle}</div>
    <div class="text-[11px] text-slate-500 mono">{HEADER_DATE}</div></div></div>

  <h2 class="text-[11px] uppercase tracking-widest text-slate-400 mb-2 flex items-center gap-1.5"><i data-lucide="zap" class="w-3.5 h-3.5 text-indigo-400"></i>What changed · cycle {cycle} <span class="normal-case tracking-normal text-slate-600">· after a ~13h loop gap</span></h2>
  <div class="mb-6">{feed_html}</div>

  <div class="rounded-lg bg-slate-900/50 border border-slate-800 px-4 py-2.5 mb-5"><p class="text-xs text-slate-300">{EXEC}</p></div>
  <div class="grid grid-cols-4 gap-2.5 mb-6">{stat_html}</div>

  <h2 class="text-[11px] uppercase tracking-widest text-slate-500 mb-2 flex items-center gap-1.5"><i data-lucide="list-checks" class="w-3.5 h-3.5 text-indigo-400"></i>Recommended next actions</h2>
  <ol class="text-sm text-slate-300 space-y-1 mb-7 ml-1">{next_html}</ol>

  <h2 class="text-[11px] uppercase tracking-widest text-slate-500 mb-2 flex items-center gap-1.5"><i data-lucide="history" class="w-3.5 h-3.5 text-slate-400"></i>Per-session action log <span class="normal-case tracking-normal text-slate-600">· persistent · scrollable · newest on top · name primary, id secondary</span></h2>
  <div class="mb-6">{log_html}</div>

  <p class="text-center text-[11px] text-slate-600 mt-2 mono">cycle {cycle} · v2: persistent per-session logs · 0 hard blockers · loop c33fe614</p>
</div><script>lucide.createIcons()</script></body></html>'''

open("dashboard.html","w").write(html_out)
print("dashboard v2 written · streams logged:", sum(1 for sid in stream_ids if by_stream.get(sid)))
