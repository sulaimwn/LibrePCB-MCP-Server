"""Trusted test-only design faults; never registered as product write tools."""

from pathlib import Path

from librepcb_mcp.adapters.sexpr import parse


def add_erc_fault(directory: Path) -> dict:
    path = directory / "circuit/circuit.lp"
    source = path.read_text(encoding="utf-8")
    root = parse(source)
    identifier = "e260931a-ec03-4dfa-9265-23422f0b3871"
    assert identifier not in source
    netclass = root.children("netclass")[0].atom()
    addition = (f' (net {identifier} (auto false) (name "MCP_DAY3_UNCONNECTED")\n'
                f'  (netclass {netclass})\n )\n')
    path.write_text(source[:root.end-1] + addition + source[root.end-1:], encoding="utf-8", newline="\n")
    return {"fault": "new circuit net with zero connected component signals", "net_id": identifier,
            "net_name": "MCP_DAY3_UNCONNECTED", "file": "circuit/circuit.lp"}


def add_drc_fault(directory: Path) -> dict:
    path = directory / "boards/default/board.lp"
    source = path.read_text(encoding="utf-8")
    root = parse(source)
    trace = next(trace for segment in root.children("netsegment") for trace in segment.children("trace"))
    width = trace.one("width").items[0]
    assert float(width.value) >= .2
    path.write_text(source[:width.start] + "0.01" + source[width.end:], encoding="utf-8", newline="\n")
    return {"fault": "existing copper trace narrowed below the board's 0.2 mm minimum",
            "trace_id": trace.atom(), "before_mm": width.value, "after_mm": "0.01",
            "file": "boards/default/board.lp"}
