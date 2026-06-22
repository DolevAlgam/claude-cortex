# 🧠 AI Brain Monitor

**A Chief of Staff for every Claude Code session on your machine.**

Run many Claude Code sessions at once and you lose the plot — what's shipping, what's
blocked, what you asked for three hours ago that never got done. AI Brain Monitor is a
self-contained agent loop that watches **all** your active Claude Code sessions and git
repos, and regenerates a single **diff-first dashboard** you can glance at in seconds.

It doesn't write features. It preserves **work state**: what's happening, why, what
changed since last time, what's stuck, and what to do next.

---

## What it gives you

- **A scrollable thought-log.** The dashboard's hero is a change feed — the newest
  deltas glow at the top, older ones fade by age. You see *what moved since last cycle*
  without re-reading anything.
- **Glance, then dive.** Compact by default; every workstream expands into a condensed
  **chain of actions & thought** plus facts (done / blocked / open / validation).
- **Active signal detection.** Forgotten requests, repeated attempts, work drift,
  validation gaps, rabbit holes, and **attention debt** (`requests made − completed`).
- **Aging risks get louder.** An unverified fix that survives multiple cycles escalates
  in the feed instead of quietly disappearing.

It tracks engineering *and* non-engineering threads (anything you're actively working).

---

## How it works

Three plain files drive everything:

| File | Role |
|------|------|
| `CLAUDE.md` | **Charter** — who the agent is, principles, scope rules, the dashboard design law. |
| `loop-prompt.dm` | **Per-cycle runbook** — the exact steps to run each cycle. |
| *(generated)* | `dashboard.html`, `state.json`, `changelog.json` — the output + persisted state. |

Each cycle the agent:

1. Discovers active real-project sessions in `~/.claude/projects/` modified ≤24h
   (excluding itself and throwaway temp/eval dirs).
2. Reads **only what's new** since the last cycle + recent git activity per repo.
3. **Diffs** against `state.json`, appends every delta to `changelog.json`.
4. Regenerates `dashboard.html` (newest changes lit, older faded).
5. Writes new state and opens the dashboard.

State persistence is what makes the diff work: cycle *N* compares against cycle *N−1*,
so the feed only lights up genuine change.

---

## Quick start

This is a prompt-driven agent loop, not a binary — it runs **inside Claude Code**.

1. Clone into a directory Claude Code can see (the agent reads/writes files here):
   ```bash
   git clone <your-fork> claude-monitor && cd claude-monitor
   ```
2. Open Claude Code with this repo as the working directory. The `CLAUDE.md` here
   becomes the agent's instructions.
3. Kick off a recurring loop (15-minute cadence shown):
   ```
   /loop 15m Run ONE AI Brain Monitor cycle. Read CLAUDE.md and loop-prompt.dm, then
   execute exactly what loop-prompt.dm says.
   ```
   Or run a single cycle on demand by pasting the runbook prompt.

The dashboard auto-opens in your browser after each cycle.

> **Paths:** the runbook references absolute paths under the repo. If you clone
> elsewhere, update the paths in `loop-prompt.dm` (or the kickoff prompt) to match.

---

## Privacy

The generated files (`dashboard.html`, `state.json`, `changelog.json`) summarize the
contents of your real sessions — they **will** contain private project, code, and
personal details. They are **gitignored by default**. Don't commit them. Only the
charter and runbook (both generic) are tracked.

---

## License

MIT — see [LICENSE](./LICENSE).
