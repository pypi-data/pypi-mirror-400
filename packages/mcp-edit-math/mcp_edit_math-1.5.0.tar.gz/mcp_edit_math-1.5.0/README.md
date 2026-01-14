# 🛡️ Edit Math Supervisor (MCP Server)

### An implementation of the Edit Approval State Machine (EASM)  
### A stateful gatekeeper for AI-driven code editing

[![Donate](https://img.shields.io/badge/Donate-Crypto-green?style=flat-square)](#donate)
![PyPI](https://img.shields.io/pypi/v/mcp-edit-math)

## Overview

This project implements a **Model Context Protocol (MCP) server** that acts as
an architectural gatekeeper between an AI coding agent and the file system.

Its purpose is simple:

> **An AI is not allowed to edit code unless it has demonstrated awareness of
the consequences and obtained explicit human approval.**

The server enforces this rule procedurally, not heuristically.

---

## Why this exists

Modern AI coding assistants can generate and apply code changes faster than
humans can reliably reason about their impact.

This creates a dangerous asymmetry:
- the AI can *act immediately*
- the human can only *review after the fact*

In practice, this leads to:
- silent breaking changes
- accidental dependency violations
- refactors without understanding downstream effects

This project explores a different model.

**The AI must stop. Explain. Ask. And wait.**

Only then is it allowed to modify code.

---

### 🧠 Philosophy: Architectural Control over AI Action

This project is intentionally not focused on making AI “smarter”.

Instead, it explores a different question:

> What architectural constraints are required
> when an AI system is allowed to act on real code?

Most AI coding tools optimize for fluency and speed.
This project optimizes for **procedural awareness**.

The core assumption is simple:
AI systems do not lack intelligence —  
they lack **structural incentives to pause, explain, and verify**.

The Edit Approval State Machine introduces such a structure.

It forces the AI to:
- stop before acting
- externalize its assumptions
- acknowledge dependencies
- wait for explicit human intent

In this model, the human provides **intent and responsibility**.
The AI provides **execution and analysis**.

The result is not “better code generation”,
but **controlled code modification**.

---

## The core idea: Edit Approval State Machine (EASM)

At the heart of this server is the **Edit Approval State Machine** —  
a security and control pattern for AI-driven code edits.

Each edit target exists in one of three states:

- `NONE`  
  No approval. Editing is forbidden.

- `PENDING`  
  Dependencies have been analyzed.  
  The system is waiting for explicit human confirmation.

- `APPROVED`  
  Permission granted.  
  A single safe edit is allowed.

State transitions are enforced by the server.
The AI cannot skip steps, self-approve, or persist approval silently.

---

## Human confirmation token

For any edit that is potentially non-trivial — for example:
- detected dependencies
- renaming
- declared breaking changes

the server requires an explicit **human confirmation token**.

By default, this token is the literal string: ок


The token:
- must come from the user
- is validated by the server
- cannot be generated or assumed by the AI on first pass

This creates a **hard human-in-the-loop boundary**.

---

## What this project is (and is not)

### This project **is**:
- a procedural safety layer for AI coding agents
- a stateful MCP server enforcing edit discipline
- an experiment in AI control, not AI intelligence

### This project **is not**:
- ❌ a linter
- ❌ a static analyzer
- ❌ a sandbox
- ❌ a code correctness verifier

The goal is not to prove code correctness.

The goal is to **prevent unreviewed action**.

---

## Supported analysis

The server performs lightweight dependency extraction using:
- Python AST (`ast`)
- Tree-sitter for JavaScript, TypeScript, and HTML

The analysis is intentionally conservative and incomplete.
It is used to **force awareness and explanation**, not to model full semantics.

---

## Threat model

This project assumes:

- AI agents optimize for task completion speed
- AI agents may skip reasoning steps if not explicitly blocked
- silent failures are more dangerous than slow workflows

As a result, the system is designed to **fail closed**.

---

## Typical workflow

1. AI requests dependency analysis for a target
2. Server returns detected dependencies and revokes edit access
3. AI explains risks and plan to the user
4. User explicitly confirms by typing `ok`
5. Server grants approval for a single edit
6. Approval is reset after commit

Any deviation resets the process.

---

## Origin

This project and the **Edit Approval State Machine (EASM)** pattern
were created by **Annenkov Yuriy** in 2025.

The goal was to explore architectural safeguards
for AI-assisted software development,
especially in environments where correctness and trust matter.

---

### 🆕 What's New in v1.5.0
*   **Python Support:** Native AST parsing for Python files.
*   **HTML Support:** Dependency detection in `<script>` tags and event handlers.
*   **2-Step Handshake:** New security mechanism. The server now requires a specific token (`'ok'`) to confirm dangerous edits, preventing the AI from "hallucinating" user consent.
*   **Renaming Detection:** Automatically triggers Strict Mode if a function signature changes.

---

### ✨ Key Features

*   **Polyglot AST Parsing:** Accurate dependency detection for **JavaScript**, **TypeScript**, **Python**, and **HTML**.
*   **Stateful Gatekeeper:** The server tracks verification status. The `commit_safe_edit` tool returns `⛔ ACCESS DENIED` if the Integrity Score is not 1.0.
*   **Interactive Conflict Resolution:** If the AI detects breaking changes, the server forces it to **stop and ask the user** for confirmation using a secure handshake protocol.
*   **Smart Filtering:** Automatically ignores standard language methods (e.g., `.map()`, `print()`) to keep the focus on your business logic.

### 🚀 The "#editmath" Protocol

The server enforces a strict workflow:

1.  **🔍 SCAN:** The AI scans the target function using AST.
2.  **🎫 TICKET:** The AI verifies dependencies. If conflicts exist, the server puts the request in `PENDING` state and demands user confirmation.
3.  **💾 COMMIT:** Only with a valid ticket (or user override) can the AI save changes.

### 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yrannkv/mcp-edit-math.git
    cd mcp-edit-math
    ```

2.  **Install dependencies:**
    *Note: Specific versions are required for stability.*
    ```bash
    pip install mcp tree-sitter==0.21.3 tree-sitter-javascript==0.21.0 tree-sitter-typescript==0.21.0 tree-sitter-html==0.20.3
    ```

3.  **Configure your MCP Client:**
    Add this to your configuration file (e.g., `claude_desktop_config.json`):
    ```json
    {
      "mcpServers": {
        "edit-math": {
          "command": "python",
          "args": ["/absolute/path/to/mcp-edit-math/mcp_edit_math.py"]
        }
      }
    }
    ```

### ⚡ Quick Start (via uvx)

If you use `uv`, you can run the server directly without cloning the repo:

```json
{
  "mcpServers": {
    "edit-math": {
      "command": "uvx",
      "args": ["mcp-edit-math"]
    }
  }
}
```

---

### 🤖 System Prompt (Required)

Add this to your AI's **Custom Instructions** or `.cursorrules` to activate the protocol:

```

=== 🛡️ EDIT MATH PROTOCOL (v1.5.0) ===
Trigger: When user types "#editmath".

You are operating under a strict safety protocol. Direct file editing is FORBIDDEN.
Follow this sequence precisely:

1. 🔍 SCAN: Call `scan_dependencies(code, target_function)`.
   - **REQUIRED:** Provide `file_path` (absolute or relative) to scope the security check.
   - Determine `language` ("js", "ts", "html", "python") based on file extension.

2. 🎫 GET TICKET: Call `calculate_integrity_score`.
   - **REQUIRED:** Provide `file_path` matching the scan step.
   - **REQUIRED:** Provide `proposed_header` to check for renaming.
   - **If server returns "STOP. INTERVENTION REQUIRED":**
     a. STOP generating immediately.
     b. Present the plan/conflicts to the user.
     c. ASK: "Do you approve? (Type 'ok')"
     d. **CRITICAL:** END YOUR TURN. Do not simulate user response.
     e. When user replies "ok", call `calculate_integrity_score` again with `confirmation_token='ok'`.

3. 💾 COMMIT: Call `commit_safe_edit`.
   - If you need to force a commit (e.g., for unverified external libs), ask the user first, then use `force_override=True`.

```


<a id="donate"></a>
## ☕ Support the Project

If this tool saved you time or prevented a bug, you can support the development via crypto:

*   **EVM (Ethereum / Base / BNB):** `0x2D7CDf70F44169989953e4cfA671D0E456fBe465`
*   **Solana:** `CGG9JouoxAs5Lja948h8ktn3CxLmbVmH1ocxPLEPCfVx`
*   **Bitcoin:** `bc1q30u6rsyu8gx3urcf20p36npgj4uc2aan7k5ntn`

---
License: Apache-2.0
Author: Annenkov Yuriy
