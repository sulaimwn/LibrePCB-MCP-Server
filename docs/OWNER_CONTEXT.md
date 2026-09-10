# Owner context and collaboration agreement

Captured from the owner's pasted ChatGPT/Claude conversation on 2026-09-10.

- Working title: **LibrePCB MCP Server**. The owner wants a useful local tool that lets an MCP client operate LibrePCB, inspired by https://github.com/mixelpixx/KiCAD-MCP-Server.
- ChatGPT/Codex is authorized to kick off implementation now. Continue in this folder. Claude can take over when subscription usage runs out; do not wait for another approval to begin the next ordinary development step.
- Keep substantial context in the folder: decisions, exact environment, commands, real results, failures, and the next task. The folder is the shared source of truth. One writer at a time.
- Tone preference: warm, direct and cooperative. Explain technical limits calmly. Avoid argumentative replies or repeated permission questions.
- The week is a working target. Useful read/check/export plus a proven value-edit experiment is the intended progression; edit release gates still apply.
- The historical Python-bindings branch is research material, not a runtime dependency. It does not establish live board-control support.
- Do not infer a personal biography, available hours, API entitlement, or model capabilities from drafts in the pasted conversation.
- No public repository, publication, deployment, maintainer contact, or subscription/API credential use is authorized by this kickoff.

## Context links worth keeping

- LibrePCB: https://github.com/LibrePCB/LibrePCB
- KiCad reference backend: https://github.com/mixelpixx/KiCAD-MCP-Server/blob/main/python/kicad_api/factory.py
- Historical experiment: https://github.com/hephaisto/LibrePCB/tree/python_bindings
- Maintainer discussion: https://librepcb.discourse.group/t/add-python-bindings/37
- Current detailed research and pinned historical source links: `RESEARCH.md`.

## Earlier environment report and correction

Claude reported Git 2.45.1, no LibrePCB on PATH, and no usable Python on PATH. The original folder had no Git repository and no implementation. Codex confirmed these gaps at kickoff, but discovered a usable bundled Python through the desktop runtime. Record the executable in the environment evidence; do not depend on WindowsApps' Python alias.

The pasted conversation remains at the owner's local attachment path. This summary intentionally records project-relevant context rather than copying unrelated personal conversation into version control.
