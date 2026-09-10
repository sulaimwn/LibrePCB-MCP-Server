# Pinned real LibrePCB fixture

`d0-reader.lppz` is the **unmodified** D0 reader example distributed by LibrePCB.

- Upstream: https://github.com/LibrePCB/librepcb-example-projects
- Exact revision: `3aad10dae67ecfea9535a2cac328497d67e4d142`
- Download: https://raw.githubusercontent.com/LibrePCB/librepcb-example-projects/3aad10dae67ecfea9535a2cac328497d67e4d142/d0-reader.lppz
- Archive SHA256: `264a04f15d873f6f19dbe21556c951f6d9e969eb86d1b4c0a2f3709365d53f5e`
- Archive size: 987,915 bytes. Extracts to 184 files; project format 2.
- Project metadata: author `U. Bruhin`, version `v2`.
- License: the archive contains `LICENSE.txt` declaring CC0 1.0 Universal. An unchanged copy is also stored alongside the archive as `d0-reader.LICENSE.txt`.
- All embedded libraries, 3D models, resources and upstream files stay in the archive unchanged.
- This is a real two-sheet, one-board example, not a minimal synthetic fixture. It is small enough to vendor and avoids migration from an old format.

Never modify the archive to make a test pass. The baseline script verifies its hash, extracts fresh copies under `work/runs/`, and checks all 184 project files remain byte-identical through checks and exports. Negative probes use separate disposable copies.

The baseline has 2 approved ERC and 16 approved DRC messages. Zero **unapproved** messages is not the same as zero findings. These approvals must not be hidden by future model-facing summaries.

The server's own license remains undecided; this fixture's license is separate.
