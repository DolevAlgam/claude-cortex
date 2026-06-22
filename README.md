# 🧠 AI Brain Monitor

Watches your active Claude Code sessions and regenerates a diff-first `dashboard.html`:
what shipped, what's blocked, what you asked for and never got, what to do next. It
tracks work state — it doesn't write code.

## How it works

- `CLAUDE.md` — agent identity, scope rules, dashboard design law.
- `loop-prompt.md` — the steps run each cycle.

Each cycle: discover sessions in `~/.claude/projects/` active in the last 24h, read
what's new since last cycle, diff against `state.json`, append deltas to
`changelog.json`, regenerate and open `dashboard.html`. Cycle *N* diffs against *N−1*.

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

Change `15m` for a different cadence; adjust scope in `CLAUDE.md`.

## Privacy

`dashboard.html`, `state.json`, `changelog.json` contain private session details. They're
gitignored — don't commit them.

## License

MIT — see [LICENSE](./LICENSE).
