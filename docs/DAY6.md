# Day 6: installation and user-workflow trial

In progress, September 12–14, 2026. Package `0.1.0.dev6`; domain/transport behavior
is unchanged from Day 5 apart from its version. Work focuses on the Windows
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
and reject/preserve a corrupt cached ZIP before installation. Full fresh setup
and repeat setup still need their recorded acceptance runs.

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
