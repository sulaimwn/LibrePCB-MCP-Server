# Day 6: installation and user-workflow trial

Engineering verification completed September 14, 2026. The owner subsequently
accepted the sample REVIEW.md. Historical evidence retains its original pending
status at collection time; current acceptance is recorded in STATUS.md.
Package `0.1.0.dev6`; domain/transport behavior is unchanged from Day 5 apart
from its version. Work focuses on the Windows
bootstrap, generated configuration and a reviewable sample workflow.

## Findings from a fresh GitHub checkout

A new private GitHub clone under a temporary directory containing a space started
without a venv or portable LibrePCB. The original quickstart failed because
Windows PowerShell 5.1 defaults to Restricted execution policy on this machine.
The revised command uses `-ExecutionPolicy RemoteSigned` for that process only;
registry policy remains unchanged and managed policy still takes precedence.

The first full download attempt was aborted by the host after 77,283,328 of the
expected 85,142,354 bytes. The old script left those bytes in its final archive
path. Setup now downloads to a unique partial file, checks its pinned SHA256,
then accepts it as the cached archive. Failed partials remain for diagnosis and
do not get treated as successful cached downloads on retry.

Bootstrap also checks Python 3.12 x64 before downloading, uses a small Python
script instead of shell-quoted inline Python, explicitly imports this PowerShell
edition's built-in modules, uses basic parsing/quiet download progress, checks
the exact CLI version/format, and restores the caller's Qt environment variable.
The module selection resolved an actual test-launcher issue: Python inherited
PowerShell 7 module paths and Windows PowerShell 5.1 could not find its hash,
archive or signature commands. No global module-path change was made.

Actual prerequisite tests reject missing Python before creating work/venv data,
and reject/preserve a corrupt cached ZIP before installation. Both pass. Final
fresh setup at Git commit `718c50d` passed with a new verified 85,142,354-byte
download, valid signature, new venv and locked dependencies. Repeat setup also
passed, preserving all 1258 existing demo files byte-for-byte.

## Sample workflow

`prepare_demo.py --verify` checks the generated command/argument array through
a real SDK client. The new `verify_demo.py` deliberately starts the server from
a different working directory to catch configurations dependent on the source
checkout's current directory. It checks all component/net pages, findings, native
PNG delivery, PDF and Gerber/Excellon exports, source preservation and optionally
one validated R17 candidate. Client snippets must agree on the launch command.

The result is a `review-<id>/` folder with real images, PDF, JSON evidence and a
readable `REVIEW.md`. [Owner trial](OWNER_TRIAL.md) explains how to inspect it and
connect a live client. Generating/checking snippets does not alter client settings.
Owner acceptance, personal-design review and live UI connection remain separate
from automated SDK/CLI verification.

## Recorded acceptance

- Fresh generated default configuration: **21 checks / 10 actual MCP calls**.
- Fresh generated experimental configuration: **26 checks / 12 calls**.
- Fresh-environment unit/adapter suite: **57 passed**, 129.657 seconds.
- Noneditable dev6 wheel: installed into that environment, verified module loading
  from site-packages and packaged output-job resources; `pip check` passes. The
  experimental sample workflow passes **26 checks / 12 calls** after installation.
- Workspace review packet: **26 checks / 12 calls**, original/candidate PNGs
  visually inspected. Packaged images match those bytes. Every source file is
  preserved; server stderr is empty in all four sample runs.

The test suite includes synthetic fault cases. Actual MCP/LibrePCB workflows are
recorded separately in [the Day 6 packet](../evidence/2026-09-14-day6/README.md),
including raw CLI diagnostics, failed setup logs, source commit and wheel hash.
Day 5's wider 82/73/103/38-check integrations and Codex host remain historical
evidence for the unchanged runtime behavior. They were not all rerun in Day 6.

`work/demo-e8a9b4/review-fb79f0/` is the durable workspace review packet; its parent
contains the actual usable client configuration and prompt. Owner feedback was
requested in the current thread and was subsequently accepted. The owner chose
to leave the server license undecided for now. A private local candidate can be
prepared; a public software release remains outside the authorized scope.

## Evidence boundaries

The clean checkout and environment are on the same Windows machine. They reuse
the installed base Python, certificate store and available package download cache;
this is not a fresh Windows machine or a new owner-followed installation.
Retain actual failed and passing setup logs, source revisions, hashes and commands
in the final evidence packet. Do not mark owner review complete without feedback.

Sources: [PowerShell process execution policy](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe?view=powershell-5.1#-executionpolicy-executionpolicy),
[Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
Actual installed PowerShell/SDK interfaces and real local trials determine the
compatibility claims; no native LibrePCB fork or hosted service was introduced.
