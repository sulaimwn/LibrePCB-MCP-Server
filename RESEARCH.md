# Research baseline

Reviewed September 10, 2026. This records documentation/source inspection, not runtime verification. Recheck version-sensitive claims at implementation time. Upstream default-branch links can change; pin supported releases and relevant commits during development.

## Implementation verification added September 10

Runtime evidence exists at `evidence/2026-09-10-day1/` and
`evidence/2026-09-10-day2/`. The historical research below is retained as context.
Day 2's exact source links and implemented limits are in `docs/DAY2.md`.

- Official MCP Python SDK **2.2.0** was verified from PyPI, pinned tag
  `9972c21aa42054fb1450c5fc614761ed11847ec6`, installed source and live clients.
  `MCPServer` and the v2 client imports work. Both legacy initialization and modern
  discovery passed. Codex 0.153.4 also called all five inspection tools through its
  actual app-server host. Claude and UI rendering remain untested.
  - https://github.com/modelcontextprotocol/python-sdk/tree/v2.2.0
  - https://pypi.org/project/mcp/2.2.0/
- The format-2 parser follows pinned token/escape/comment grammar. Unknown content
  is preserved in raw copied files; the documented projection is read-only.
  - https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/serialization/sexpression.cpp

- Official stable download page identified 2.1.1. The downloaded Windows executable reported **LibrePCB CLI 2.1.1**, stable file format **2**, revision **06465bf (2026-06-12)**. Windows verified its Authenticode signature. Exact download and local SHA256 are in `toolchain.json`.
  - https://librepcb.org/download/
  - https://github.com/LibrePCB/LibrePCB/releases/tag/2.1.1
- Real `open-project --help` and executions verified `--strict`, `--erc`, `--drc`, `--jobs`, `--run-job` and `--outdir`.
  - https://librepcb.org/docs/cli/open-project/
- **Observed difference worth retaining:** deprecated `--export-schematics` creates PNGs but returns **2**, unless warnings are suppressed. The supported graphics output job returns **0**. Use jobs.
- Source inspection on the pinned release confirms CLI initialization uses `QGuiApplication`; the Windows ZIP hangs when we force `QT_QPA_PLATFORM=offscreen`. Normal native Windows platform plus hidden console works. This is observed on our host, not a statement about every OS/build.
  - https://github.com/LibrePCB/LibrePCB/blob/2.1.1/apps/librepcb-cli/main.cpp
- The pinned transaction layer uses `.lock`, `.backup/backup.lp`, and `.autosave/autosave.lp`. Day 2 conservatively rejects all lock/recovery entries and tests their preservation.
  - https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/fileio/transactionalfilesystem.cpp
- The official fixture is pinned to `3aad10dae67ecfea9535a2cac328497d67e4d142`; its embedded project license is CC0-1.0. See `tests/fixtures/README.md`.
  - https://github.com/LibrePCB/librepcb-example-projects/tree/3aad10dae67ecfea9535a2cac328497d67e4d142
- The official MCP Python SDK repository was located in Day 1; Day 2 completed version/interface/runtime verification described above.
  - https://github.com/modelcontextprotocol/python-sdk

## Verified from official documentation/source

- LibrePCB's CLI provides ERC, DRC, output-job execution and exports. It also has limited mutation/save options; it is not documented as a general placement/wiring API.
  - https://librepcb.org/docs/cli/open-project/
- LibrePCB uses S-expressions, embeds required library data in projects, and documents file-format stability within major releases.
  - https://librepcb.org/features/file-format/
  - https://developers.librepcb.org/d5/d75/doc_project.html
- File handling includes write locking, in-memory pending changes, backups and autosave. This motivates avoiding concurrent external writes; it does not by itself prove a complete safe locking implementation for our server.
  - https://github.com/LibrePCB/LibrePCB/blob/master/libs/librepcb/core/fileio/transactionalfilesystem.cpp
- The official parts generator provides Python helpers for generating library elements. It does not control a running project editor.
  - https://github.com/LibrePCB/librepcb-parts-generator
- The KiCad reference server chooses IPC or a SWIG/Python backend. LibrePCB would need its own design-operation adapter.
  - https://github.com/mixelpixx/KiCAD-MCP-Server/blob/main/python/kicad_api/factory.py
- Codex documents local STDIO MCP support. Client support/configuration must be checked in the actual installation.
  - https://developers.openai.com/codex/mcp

## Historical native Python experiment

Repository branch: https://github.com/hephaisto/LibrePCB/tree/python_bindings

Inspected tip: `ddf461c96c75b91a9494949a1291c1769eb0a260`, committed May 20, 2018, titled “Add unittests for packages.”

- Module registration exposes basic types, geometry, symbols and packages.
  - https://github.com/hephaisto/LibrePCB/blob/ddf461c96c75b91a9494949a1291c1769eb0a260/libs/librepcb/python/pylibrepcb.cpp
- Footprint bindings include pad position, rotation, dimensions and package saving.
  - https://github.com/hephaisto/LibrePCB/blob/ddf461c96c75b91a9494949a1291c1769eb0a260/libs/librepcb/python/package.cpp
- Script execution embeds Python, supplies library editor context, and begins/commits/aborts undo groups. Property wrappers can route changes through editor commands. Some properties bypass that wrapper, so do not assume all possible script changes are undoable.
  - https://github.com/hephaisto/LibrePCB/blob/ddf461c96c75b91a9494949a1291c1769eb0a260/libs/librepcb/python/embedding.cpp
  - https://github.com/hephaisto/LibrePCB/blob/ddf461c96c75b91a9494949a1291c1769eb0a260/libs/librepcb/python/propertywrapper.h
- Component/device source files exist but are absent from the inspected build source list and module registration. General board/project interfaces were not registered there.
  - https://github.com/hephaisto/LibrePCB/blob/ddf461c96c75b91a9494949a1291c1769eb0a260/libs/librepcb/python/common.pri
- Tests exist for package loading, pads and footprint contents. They have not been run in this project.
  - https://github.com/hephaisto/LibrePCB/blob/ddf461c96c75b91a9494949a1291c1769eb0a260/tests/python/test_package.py
- The maintainer discussion distinguishes standalone scripting from embedded scripting. It is historical context, not evidence of a current supported editor API.
  - https://librepcb.discourse.group/t/add-python-bindings/37

## Inferences and things to prove

- Local CLI/file-based MCP inspection now has real acceptance evidence. Full read/check/export and edit workflows still require subsequent milestones.
- Direct editing needs cross-file semantic validation, not just valid S-expression syntax.
- The historical fork supplies design ideas for a native bridge; porting effort and current compatibility are unknown.
- We did not find a documented supported current editor-control API in the initial research. Absence from this search is not proof none exists; recheck before committing to native work.
- GUI automation is not chosen as the primary architecture because reproducibility and state synchronization would need separate validation.
- Model capability claims and PCB-tool popularity rankings are not inputs to feasibility or release criteria.
