# Day 4: one controlled resistance edit

In progress, September 11, 2026. Codex remains the active coding client; the owner
requested regular GitHub checkpoints and no Claude handoff. Day 3's eight tools
remain the working baseline while this experiment is validated.

The experiment changes R17 from 1.5 to 2.2 **kiloohm** on an isolated copy of the
CC0 D0 reader fixture. Its raw value is exactly `{{RESISTANCE}}`; changing that
template would bypass the typed attribute. The new adapter patches only the
quoted scalar in the existing RESISTANCE attribute using parser source spans.
It accepts a narrow nonnegative decimal subset in the existing unit, rejects
unchanged values, extra attributes and populated part choices, and verifies
exact full-project bytes against the expected patch. No general serializer or
live-editor API is introduced.

Verified source: [typed resistance behavior](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/attribute/attrtyperesistance.cpp),
[attribute serialization](https://github.com/LibrePCB/LibrePCB/blob/2.1.1/libs/librepcb/core/attribute/attribute.cpp),
[CLI save/strict interface](https://librepcb.org/docs/cli/open-project/).
Real CLI `--strict`, `--save`, `--strict` succeeded on the edited copy. Saving
introduces four `settings.user.lp` files on this fixture. These contain editor
preferences; GUI saving also fills board-layer visibility preferences. Compare
against an independently saved unmodified control so these changes are explicit,
rather than silently ignoring file changes.

The GUI was launched on a disposable candidate with process-local
`LIBREPCB_WORKSPACE` and `LIBREPCB_CONFIG_DIR` pointing into `work/d4g/`.
Both settings are verified in the pinned application source. GUI `--help` is
unsupported; it launches workspace selection, so the initial exploratory process
was terminated after its timeout. Subsequent GUI trials use the actual `.lpp`
argument and isolated workspace/config. No normal workspace settings are edited.

Windows UI Automation and scoped keyboard/mouse input are test helpers only.
They refuse input unless the owned LibrePCB process is foreground. The editor
showed R17 at 2.2 kΩ, reported “Project saved!”, and a new GUI process reopened
the saved value. Normal GUI closure releases project/workspace locks. The GUI
has no installed workspace libraries; this example embeds the libraries it needs.

The final acceptance record will distinguish the pure patch tests, real CLI
round trip, GUI observations, MCP tool calls, rule-check comparisons, visual
exports, source preservation and rollback. MCP editing is not yet registered
at this checkpoint; completion is recorded in STATUS and the Day 4 evidence.
