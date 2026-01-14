# Aichat: Session continuation without compaction, and fast full-text session search for Claude Code and Codex CLI



In the [claude-code-tools](https://github.com/pchalasani/claude-code-tools) repo, I
I've been sharing various tools I've built to improve productivity when working 
with Claude-Code or Codex-CLI. I wanted to share `aichat` command which I use heavily to continue work **without having to compact**.

Here is the thought process underlying this tool -- I think knowing the thought process and motivation helps understand what the `aichat` command-group does and why it might be useful to you. 

### Compaction is lossy: clone the session and truncate long messages

Session compaction is **lossy:** there are very often situations where compaction loses important details, so I wanted to find ways to continue my work without compaction. A typical scenario is this -- I am at 90% context usage, and I wish I can go on a bit longer to finish the current work-phase. So I thought,

> I wish I could **truncate** some long messages (e.g. tool calls/results for file writes/reads, long assistant responses, etc) and clear out some space to continue my work.

This lead to the [`aichat trim`](https://github.com/pchalasani/claude-code-tools#three-resume-strategies) utility. It provides two variants:

- a "blind" [`trim`](https://github.com/pchalasani/claude-code-tools#three-resume-strategies) mode that truncates all messages longer than a threshold (default 500 chars), and optionally all-but-recent assistant messages -- all user-configurable. This can free up 40-60% context, depending on what's been going on in the session.

- a [`smart-trim`](https://github.com/pchalasani/claude-code-tools#three-resume-strategies) mode that uses a headless Claude/Codex agent to determine which messages can be safely truncated in order to continue the current work. The precise truncation criteria can be customized (e.g. the user may want to continue some prior work rather than the current task).

Both of these modes *clone* the current session before truncation, and inject two types of [*lineage*](https://github.com/pchalasani/claude-code-tools#lineage-nothing-is-lost):
- *Session-lineage* is injected into the first user message: a chronological listing of sessions from which the current session was derived. This allows the (sub-) agent to extract needed context from ancestor sessions, either when prompted by the user, or on its own initiative.
- Each truncated message also carries a pointer to the specific message index in the parent session so full details can always be looked up if needed.

### A cleaner alternative: Start new session with lineage and context summary

Session trimming can be a quick way to clear out context in order to continue the current task for a bit longer, but after a couple of trims, does not yield as much benefit. But the lineage-injection lead to a different idea to avoid compaction:

> Create a fresh session, inject parent-session lineage into the first user message, along with instructions to extract (using sub-agents if available) context of the latest task from the parent session, or skip context extraction and leave it to the user to extract context once the session starts.

This is the idea behind the [`aichat rollover`](https://github.com/pchalasani/claude-code-tools#three-resume-strategies) functionality, which is the variant I use the most frequently, and I use this instead of first trimming a session. I usually choose to skip the summarization (this is the `quick` rollover option in the TUI) so that the new session starts quickly and I can instruct Claude-Code/Codex-CLI to extract needed context (usually from the latest chat session shown in the lineage), as shown in the demo video below.

### A hook to simplify continuing work from a session

I wanted to make it seamless to pick any of the above three task continuation modes, when inside a Claude Code session, so I set up a `UserPromptSubmit` [hook](https://github.com/pchalasani/claude-code-tools#resume-options) (via the `aichat` plugin) that is triggered when the user types `>resume` (or `>continue` or `>handoff`). When I am close to full context usage, I type `>resume`, and the hook script copies the current session id into the clipboard and shows instructions asking the user to run `aichat resume <pasted-session-id>`; this launches a TUI that offering options to choose one of the above [session resumption modes](https://github.com/pchalasani/claude-code-tools#three-resume-strategies).

**Demo video (resume/rollover flow):**

https://github.com/user-attachments/assets/310dfa5b-a13b-4a2b-aef8-f73954ef8fe9

### Fast full-text session search for humans/agents to find prior work context

The above session resumption methods are useful to continue your work from the *current* session, but often you want to continue work that was done in an *older* Claude-Code/Codex-CLI session. This is why I added this:

> Super-fast Rust/Tantivy-based [full-text search](https://github.com/pchalasani/claude-code-tools#aichat-search--find-and-select-sessions) of all sessions across Claude-Code and Codex-CLI, with a pleasant self-explanatory TUI for humans, and a CLI mode for Agents to find past work. (The Rust/Tantivy-based search and TUI was inspired by the excellent TUI in the [zippoxer/recall](https://github.com/zippoxer/recall) repo).

Users can launch the search TUI using [`aichat search ...`](https://github.com/pchalasani/claude-code-tools#aichat-search--find-and-select-sessions) and (sub-) [agents can run](https://github.com/pchalasani/claude-code-tools#agent-access-to-history-the-session-searcher-sub-agent) `aichat search ... --json` and get results in JSONL format for quick analysis and filtering using `jq` which of course CLI agents are great at using. There is a corresponding *skill* called `session-search` and a *sub-agent* called `session-searcher`, both available via the `aichat` [plugin](https://github.com/pchalasani/claude-code-tools#claude-code-plugins). For example in Claude Code, users can recover context of some older work by simply saying something like:

> Use your session-searcher sub-agent to recover the context of how we worked on connecting the Rust search TUI with the node-based Resume Action menus.

**Demo GIF (search TUI):**

![aichat search demo](https://raw.githubusercontent.com/pchalasani/claude-code-tools/main/demos/aichat-search-asciinema.gif)

---

**Links:**
- GitHub repo: https://github.com/pchalasani/claude-code-tools

**Install:**
```bash
# Step 1: Python package
uv tool install claude-code-tools

# Step 2: Rust search engine (pick one)
brew install pchalasani/tap/aichat-search   # Homebrew
cargo install aichat-search                  # Cargo
# Or download binary from Releases

# Step 3: Claude Code plugins (for >resume hook, session-searcher agent, etc.)
# From terminal:
claude plugin marketplace add pchalasani/claude-code-tools
claude plugin install "aichat@cctools-plugins"
# Or from within Claude Code:
/plugin marketplace add pchalasani/claude-code-tools
/plugin install aichat@cctools-plugins
```
