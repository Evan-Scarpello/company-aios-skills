---
name: connector-setup
description: Use whenever someone wants to add, register or troubleshoot an MCP server or connector in Claude Code ("set up the X MCP", "connect X to Claude", "why isn't the connector showing up"), even when they never say "MCP".
---

# connector-setup

Adding a connector is the same four-step loop every time. Two facts get re-derived every session for no reason; state them up front.

## The two facts to state once

1. **New or edited MCP servers usually need a full restart of Claude Code** (quit and reopen, not just a new chat) before their tools appear. The agent can't do that restart for you; it is the one manual step. A connector that "isn't showing up" right after you add it is almost always this, not a broken config.
2. **Secrets never go in notes.** Values live in the tool's own credential store, a `.env` file outside the repo, or a password manager. Your notes keep only a **map**: which key, and where its value lives. Never paste a value into a note, a log, a commit or a chat.

## The loop

1. **Check what's already there.** `claude mcp list` (and your connectors page) before adding anything. Report what is present and what's missing.
2. **Register at the right scope.** "For all my projects" means user scope (`claude mcp add --scope user …`), not one project. Say which scope you used.
3. **Restart, then sign in.**
   - OAuth (most SaaS): the browser sign-in happens in the person's own browser. The agent can't host it.
   - API key or token: note which token and its scopes; the value goes to the credential store and the pointer goes in your notes.
   - Self-hosted: confirm the URL and auth header, then check it is reachable before wiring it in.
4. **Verify and record.** Make one real read call through the new tools. A green "connected" badge is not proof. For connectors that sit in front of another service (an automation tool that calls your email, say), the badge only proves the link to the first hop; the downstream login can expire on its own. Then add the key-map line and note the connector in your inventory.

## Notes

- If a connector the task needs is missing from the session, say so and ask. Don't improvise around it.
- Treat any third-party MCP server like a dependency: read what it can do before granting it your accounts.
