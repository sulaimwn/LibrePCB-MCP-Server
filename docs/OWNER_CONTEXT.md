# Owner context and collaboration agreement

Captured from the owner's pasted ChatGPT/Claude conversation on 2026-09-10.

- Working title: **LibrePCB MCP Server**. The owner wants a useful local tool that lets an MCP client operate LibrePCB, inspired by https://github.com/mixelpixx/KiCAD-MCP-Server.
- ChatGPT/Codex is authorized to kick off implementation now. Continue in this folder. Claude can take over when subscription usage runs out; do not wait for another approval to begin the next ordinary development step.
- Keep substantial context in the folder: decisions, exact environment, commands, real results, failures, and the next task. The folder is the shared source of truth. One writer at a time.
- Tone preference: warm, direct and cooperative. Explain technical limits calmly. Avoid argumentative replies or repeated permission questions.
- The week is a working target. Useful read/check/export plus a proven value-edit experiment is the intended progression; edit release gates still apply.
- The historical Python-bindings branch is research material, not a runtime dependency. It does not establish live board-control support.
- Do not infer a personal biography, available hours, API entitlement, or model capabilities from drafts in the pasted conversation.
- The original kickoff did not authorize publication. The owner subsequently
  asked Codex to continue Day 3 and push the project to GitHub as
  **LibrePCB-MCP-Server**, with a README that clearly says WIP. That later request
  authorizes repository creation and pushing the project/history. Deployment,
  maintainer contact and subscription/API credential use remain outside the task.

## Context links worth keeping

- LibrePCB: https://github.com/LibrePCB/LibrePCB
- KiCad reference backend: https://github.com/mixelpixx/KiCAD-MCP-Server/blob/main/python/kicad_api/factory.py
- Historical experiment: https://github.com/hephaisto/LibrePCB/tree/python_bindings
- Maintainer discussion: https://librepcb.discourse.group/t/add-python-bindings/37
- Current detailed research and pinned historical source links: `RESEARCH.md`.

## Earlier environment report and correction

Claude reported Git 2.45.1, no LibrePCB on PATH, and no usable Python on PATH. The original folder had no Git repository and no implementation. Codex confirmed these gaps at kickoff, but discovered a usable bundled Python through the desktop runtime. Record the executable in the environment evidence; do not depend on WindowsApps' Python alias.

The pasted conversation remains at the owner's local attachment path. This summary intentionally records project-relevant context rather than copying unrelated personal conversation into version control.


## Completed owner-requested Day 3 / GitHub checkpoint (September 11)

Codex completed Day 3 and preserved the latest evidence and continuation notes.
The GitHub repository is `sulaimwn/LibrePCB-MCP-Server`, with a WIP README and
project history. Visibility was unspecified; private was the stated default
and was used. This is not an owner-selected public release or a hosted deployment.
Claude context remains available, but the owner chose Codex to do Day 3.


## Current continuation instruction (September 11)

Owner: “start day 4 / whatever else u gotta do”, “push to github regularly”, and
“Im not sending this to claude any time soon”. Codex continues; preserve regular
meaningful checkpoints and context. A live handoff/client-switch trial is deferred.
Native editor API investigation remains after the initial seven milestones, as
discussed with the owner; Day 4 proves a limited saved-copy resistance edit.


## September 12 continuation

The owner continued with “keep going” during Day 5. Codex completed reliability
and retained all evidence and setup context. The next milestone is Day 6
installation/user-workflow trial. Regular private GitHub pushes remain authorized;
no Claude handoff or public software release was requested.
