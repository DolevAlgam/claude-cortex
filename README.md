# 🧠 AI Brain Monitor

Watches your active Claude Code sessions and regenerates a diff-first `dashboard.html`:
what shipped, what's blocked, what you asked for and never got, what to do next. It
tracks work state — it doesn't write code.

## How it works

- `CLAUDE.md` — agent identity, scope rules, dashboard design law.
- `loop-prompt.md` — the steps run each cycle.
- `build_dashboard.py` — data-driven generator: reads `state.json` + `changelog.json`
  and renders `dashboard.html`. The per-cycle authored copy (change feed + summary) lives
  in `cycle_top.py`, which is private/gitignored (falls back to neutral placeholders).

Each cycle: re-scan **all** sessions in `~/.claude/projects/` whose real last-user
activity is within the last 12h (not just files touched since last cycle), read what's
new, read-only-cross-check git for work waiting to merge, diff against `state.json`,
append deltas to `changelog.json`, regenerate and open `dashboard.html`. Cycle *N* diffs
against *N−1*.

The dashboard shows: a **change feed** (what moved this cycle), a **Stories** section
(every current session with its state + explicit *next step*, always — even on a no-change
cycle), and a persistent, scrollable **per-session action log**. Ages are computed live
from timestamps; finished / >12h sessions archive out of the live view.

## Quick start

Runs inside Claude Code.

```bash
git clone https://github.com/DolevAlgam/claude-cortex.git && cd claude-cortex
```

Open Claude Code here, then:

```
/loop 15m Run ONE AI Brain Monitor cycle. Read CLAUDE.md and loop-prompt.md, then
execute exactly what loop-prompt.md says.
```

Change `15m` for a different cadence; adjust scope (e.g. the 12h window) in `CLAUDE.md`.

## Privacy

`dashboard.html`, `state.json`, `changelog.json`, and `cycle_top.py` contain private
session details. They're gitignored — don't commit them.

## License

MIT — see [LICENSE](./LICENSE).
