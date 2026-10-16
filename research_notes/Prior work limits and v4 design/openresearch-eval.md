# OpenResearch (alphaXiv) evaluation for the VLM refusal-gap project

Date: 2026-10-15. Nothing was installed or run. Labels: VERIFIED = page/file read; SNIPPET = search snippet or summarised by the fetch tool only; UNVERIFIED = not found.

## 1. What it is, where data lives, what leaves the machine

- VERIFIED: github.com/alphaXiv/OpenResearch, MIT licence, copyright alphaXiv 2026. Rust CLI (`orx`) plus a desktop app and a local dashboard at 127.0.0.1:4791. Latest release v0.2.19 (15 Oct 2026); about 7.3k stars, 49 open issues. It is a very young, fast-moving project (releases every 2-3 days).
- VERIFIED: it is a harness around a coding agent (Claude Code, Codex, OpenCode, Cursor, Antigravity). The research behaviour comes from 14+ shipped skills (`agent-skills/`: orx-lit-review, orx-results, orx-logs, orx-figures, orx-paper, orx-experiment-tree, orx-compute, orx-git, orx-reports, ...) plus SYSTEM_PROMPT.md. Skills are prompts that call `orx` subcommands.
- VERIFIED (README): projects, conversations, experiments, logs, code and artifacts are stored locally; experiments go in a local SQL database. UNVERIFIED: the exact DB path/engine (paths.rs does not say). VERIFIED: secrets/env values go in `~/.openresearch/env`; settings and telemetry outbox under `$XDG_CONFIG_HOME/openresearch/`.
- Literature (VERIFIED, orx-lit-review SKILL.md): queries, arXiv IDs, DOIs go to alphaXiv, OpenAlex, bioRxiv, NCBI E-utilities, arxiv.org; web search is a fallback. No login required for this skill. Your prompts also go to whichever coding-agent provider you use, as with Claude Code today.
- Telemetry (VERIFIED, src/telemetry.rs): official release builds only (source/dev builds send nothing). POST to `https://api.openresearch.sh/analytics/v1/cli-events` with a random install UUID, CLI version, OS, arch, event names (command, experiment_started with compute target, project_created, skill_invoked, chat_message_sent with harness name, telemetry_consent). The onboarding profile event can include free text you type (research area/background). README also says agents send "feedback" reports and anonymised token/message counts feed public rankings. Opt-out: `orx telemetry off`, `--no-telemetry`, or the dashboard toggle; stored as `telemetryDisabled` in settings.json. Runtime kill: `ORX_TELEMETRY_ENV` set to anything but `production`. Unparseable settings.json = disabled.
- Installer (VERIFIED by reading the v0.2.19 script text): `openresearch.sh/install.sh` 302-redirects to the GitHub release asset `openresearch-cli-installer.sh` (cargo-dist 0.32.0, POSIX sh). It downloads `openresearch-cli-<target>.tar.xz` only from github.com/alphaXiv/OpenResearch/releases/download/v0.2.19 (hosts found in the script: github.com only, plus comment links), verifies a SHA-256 hardcoded in the script (skips with a notice if `sha256sum` is missing; macOS lacks it by default, so verification is likely skipped on a Mac - UNVERIFIED on your machine), installs `orx` to `$CARGO_HOME/bin` or `~/.cargo/bin`, appends a source line to the first shell rc it finds (`.profile`, `.bashrc`, `.bash_profile`, `.bash_login`, `.zshrc`, `.zshenv`), writes a receipt to `~/.config/openresearch-cli/`. No telemetry in the script.
- Open issue #627 (SNIPPET, title only): "Remote installer hides group-writable binary directory rejection" - a security-relevant installer bug, still open.

## 2. Is curl|sh safe? Safer paths

The script itself reads as a standard cargo-dist installer and pulls only from GitHub releases, so risk is moderate and mostly "trust alphaXiv + GitHub". Release binaries are unsigned (README says managed Macs may block it). Safer, in rising order of effort (do NOT run these yet; the user decides):

1. Inspect-then-run (a download only, user approves):
   `curl -LsSf -o orx-installer.sh https://github.com/alphaXiv/OpenResearch/releases/download/v0.2.19/openresearch-cli-installer.sh`
   `shasum -a 256 orx-installer.sh` and compare with the release page value 216216bf7deb5471ef7bdd714aaf5ef328cb7664b53c1fed325a64625aa7921c; read it; then `OPENRESEARCH_CLI_NO_MODIFY_PATH=1 sh orx-installer.sh` (stops the rc edit; or use `OPENRESEARCH_CLI_UNMANAGED_INSTALL=$HOME/tools/orx` for a flat install with no PATH edit or updater).
2. Pinned tarball with checksum (no script): download `openresearch-cli-aarch64-apple-darwin.tar.xz` and its `.sha256` from the v0.2.19 release; expected sha256 9e26b9a68b8d4f3305ded44d43293c9e690a2c923889b70d05ae2c9f823fdcb1; verify with `shasum -a 256 -c`; extract to a new empty directory and place `orx` in `~/tools`. (Release page checksums are same-origin as the file, so this guards against corruption, not a compromised release.)
3. Build from source (Cargo.toml in repo; read-able Rust): `git clone https://github.com/alphaXiv/OpenResearch && cd OpenResearch && git checkout v0.2.19 && cargo build --release`. Bonus: VERIFIED that source builds send no telemetry. Cost: needs Rust toolchain; the repo also has a `ui/` that may need Node (UNVERIFIED build steps).
4. Disposable sandbox first: a throwaway macOS user account or VM/container, never the account holding SSH keys, HF tokens, or the research repo.

No npm or pip package was found (UNVERIFIED that none exists). The desktop .dmg is the signed-ish alternative (README says "signed desktop app"; macOS notarisation UNVERIFIED).

## 3. How it would help THIS project (Colab-only, no GPU box)

- Compute: Colab is NOT a backend (VERIFIED list: local, SSH, Slurm, Kubernetes, Modal, Tinker, Ray, Hugging Face Jobs, managed RunPod/Lambda). Issue #551 asks for Kaggle; no Colab issue. So OpenResearch cannot launch or monitor Colab runs. Realistic GPU options: Hugging Face Jobs (needs a write-scoped `HF_TOKEN`, paid), Modal (token, paid), or its managed compute (account, paid). The user's own Colab Pro workflow stays outside it.
- Experiment ledger: it logs experiments it launches itself. VERIFIED: no documented command to import an existing results.json or notebook outputs; orx-results SKILL.md only governs how the agent reads logs and reports. (UNVERIFIED whether `orx exp` can create a record manually; docs list no such command.) Realistic use: have the agent record Colab results by reading exported JSON, at best as notes, not as first-class runs. Poor fit.
- Literature grounding: genuinely useful and low-risk. orx-lit-review ranks 5-15 candidates, reads full text, cites with links; sources include alphaXiv, OpenAlex, arXiv. But you can get the same with the alphaXiv MCP alone (section 4) without installing a harness.
- Reproducibility appendix: it records git commits per experiment (issue #604 says source commit is not stable across upserts - a correctness concern) and has orx-reports/orx-figures. Only helpful for runs launched through it. For Colab, a hand-written ledger with model revision, seed, library versions and judge prompt hash is more defensible.
- Other cautions: open data-loss/accumulation issues (#637 agent output stays in internal worktrees; #667 files under $HOME/.orx never cleaned), #656 project creation failure on macOS v0.2.18. Pace of change means pinning a version matters for a reproducibility claim.

## 4. Alternatives

- alphaXiv MCP (VERIFIED, alphaxiv.org/docs/mcp): `https://api.alphaxiv.org/mcp/v1`, streamable HTTP, OAuth 2.1 or API key. 21 tools: `discover_papers`, `get_paper_content`, `answer_pdf_queries`, `read_files_from_github_repository`, researcher lookup, and library tools that WRITE to your account (save/move/delete folders). Install line (user runs): `claude mcp add --transport http alphaxiv https://api.alphaxiv.org/mcp/v1`. Quota unspecified; privacy policy not on page. Also alphaxiv.org paper pages/search/bookmarks (VERIFIED nav: paper pages, search, assistant, MCP, API, extension).
- Zotero + Better BibTeX for the references database and BibTeX (UNVERIFIED here; standard tool) - best for the limitations-review bibliography.
- Simple results ledger: one `runs.jsonl` per notebook (run_id, git sha, model id + HF revision, dataset hash, seed, library versions, judge model + prompt hash, metric values, Drive path), appended by a 10-line helper at the end of each Colab cell, committed to GitHub. Optionally mirror to Weights & Biases or an HF dataset repo (UNVERIFIED details).
- Existing repo tools already cover much of this (Claude Code, the v3 notebook, docs/).

## 5. Adoption plan, go/no-go, and approvals

Recommendation: do not adopt OpenResearch for the ledger or compute now. Adopt the alphaXiv MCP now (read-only use), and re-evaluate OpenResearch later if you move to HF Jobs/Modal or after the paper deadline pressure eases.

Phase 0 (now, no OpenResearch): add alphaXiv MCP; build the runs.jsonl ledger; Zotero for refs.
Phase 1 (optional trial, 1 afternoon, only if wanted): sandbox account, pinned v0.2.19, install option 1 or 3, run `orx telemetry off` first, point at a scratch repo with a copy of results.json. Go/no-go for continuing: (a) it can ingest or display your results.json without manual agent glue; (b) no unexpected network hosts (check with Little Snitch/`lsof -i` equivalent, user-run); (c) a re-run reproduces recorded numbers; (d) no data-loss behaviour from issues #637/#667 on your files; (e) advisor is fine with a third-party tool in the pipeline. Any "no" = stop.

Items the user must approve themselves (I will not do them):
1. Running any installer or build (download, checksum compare, PATH/rc edit).
2. Choosing telemetry stance (off is advised) and any onboarding free-text entry.
3. OAuth sign-in to alphaXiv, or creating an API key (and granting library write tools; consider a key you can revoke).
4. `orx login`, any account creation, managed compute spend, `HF_TOKEN` (write scope) or Modal tokens - never paste into a chat.
5. Granting the agent access to the research repo and Drive data; the coding-agent provider sees whatever the agent reads.
6. Adding any MCP server to Claude Code config (persistent configuration).
7. Anything touching the shared PSU cluster (remembered rule: user runs cluster commands; Slurm backend should stay unused).

## Sources
- https://github.com/alphaXiv/OpenResearch (README, LICENSE, releases, issues, src/, agent-skills/)
- https://raw.githubusercontent.com/alphaXiv/OpenResearch/main/src/telemetry.rs
- https://raw.githubusercontent.com/alphaXiv/OpenResearch/main/agent-skills/orx-lit-review/SKILL.md and orx-results/SKILL.md
- Installer v0.2.19 (read as text, via the redirect from https://openresearch.sh/install.sh)
- https://openresearch.sh/docs, /docs/cli, /docs/env-vars
- https://www.alphaxiv.org/docs/mcp ; https://alphaxiv.org/
