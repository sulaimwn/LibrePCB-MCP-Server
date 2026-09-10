"""Read a documented format-2 projection; let LibrePCB validate full semantics."""

from dataclasses import dataclass
from uuid import UUID

from librepcb_mcp.adapters.files import Capture, relative_design_path
from librepcb_mcp.adapters.sexpr import Atom, Node, parse
from librepcb_mcp.errors import ProjectError, require


def uuid(value: str) -> str:
    try:
        require(str(UUID(value)) == value, "Identifiers must be canonical UUIDs.")
    except ValueError as exc:
        raise ProjectError("invalid_project", "Invalid UUID in project.") from exc
    return value


def text(value: str, limit: int = 4096) -> str:
    require(len(value) <= limit, "Project text exceeds supported result size.", "resource_limit")
    return value


def unique(nodes: list[Node]) -> dict[str, Node]:
    result = {}
    for node in nodes:
        identifier = uuid(node.atom())
        require(identifier not in result, "Duplicate UUID in project.")
        result[identifier] = node
    return result


def allowed(node: Node, names: set[str], *, leading_id: bool = False) -> None:
    items = node.items[1:] if leading_id else node.items
    require(all(isinstance(item, Node) and item.name in names for item in items),
            f"Unsupported fields in '{node.name}'.", "unsupported_project")


@dataclass(frozen=True)
class ProjectData:
    metadata: dict
    boards: list[dict]
    schematics: list[dict]
    components: list[dict]
    nets: list[dict]


def inspect_project(captured: Capture, project_filename: str) -> ProjectData:
    files = captured.files
    require(files.get(".librepcb-project", b"").strip() == b"2",
            "Only LibrePCB stable file format 2 is supported.", "unsupported_version")
    require(files.get(project_filename, b"").strip() == b"LIBREPCB-PROJECT",
            "Not a LibrePCB project marker file.")

    def document(name: str, root_name: str) -> Node:
        name = relative_design_path(name)
        require(name in files, f"Missing required project file: {name}.")
        try:
            source = files[name].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ProjectError("invalid_project", "Project text is not valid UTF-8.") from exc
        root = parse(source)
        require(root.name == root_name, f"Unexpected root in {name}.")
        return root

    metadata = document("project/metadata.lp", "librepcb_project_metadata")
    info = {"id": uuid(metadata.atom()), **{
        name: text(metadata.field(name), 512) for name in ("name", "author", "version", "created")
    }}
    circuit = document("circuit/circuit.lp", "librepcb_circuit")
    allowed(circuit, {"variant", "netclass", "net", "component"})
    netclasses = unique(circuit.children("netclass"))
    net_nodes = unique(circuit.children("net"))
    component_nodes = unique(circuit.children("component"))
    require(len(component_nodes) <= 5000 and len(net_nodes) <= 10000,
            "Project exceeds supported component/net counts.", "resource_limit")
    net_records = {}
    net_components = {}
    names = set()
    for identifier, net in net_nodes.items():
        allowed(net, {"auto", "name", "netclass"}, leading_id=True)
        name = text(net.field("name"), 512)
        require(name not in names, "Duplicate net name.")
        names.add(name)
        netclass = uuid(net.field("netclass"))
        require(netclass in netclasses, "Net refers to a missing net class.")
        net_records[identifier] = {"id": identifier, "name": name, "netclass_id": netclass,
                                   "signal_count": 0, "component_count": 0}
        net_components[identifier] = set()

    library_cache = {}
    components = []
    references = set()
    for identifier, component in component_nodes.items():
        allowed(component, {"lib_component", "lib_variant", "name", "value", "lock_assembly",
                            "attribute", "device", "signal"}, leading_id=True)
        reference = text(component.field("name"), 512)
        require(reference not in references, "Duplicate component reference.")
        references.add(reference)
        lib_id = uuid(component.field("lib_component"))
        if lib_id not in library_cache:
            lib = document(f"library/cmp/{lib_id}/component.lp", "librepcb_component")
            require(uuid(lib.atom()) == lib_id, "Embedded component identifier mismatch.")
            library_cache[lib_id] = lib
        library = library_cache[lib_id]
        signals = unique(library.children("signal"))
        variants = unique(library.children("variant"))
        require(uuid(component.field("lib_variant")) in variants, "Missing library component variant.")
        assignments = unique(component.children("signal"))
        require(assignments.keys() == signals.keys(), "Component signal assignments do not match its embedded library.")
        connected = 0
        for signal in assignments.values():
            target = signal.field("net")
            if target == "none":
                continue
            target = uuid(target)
            require(target in net_records, "Component signal refers to a missing net.")
            net_records[target]["signal_count"] += 1
            net_components[target].add(identifier)
            connected += 1
        attributes = []
        keys = set()
        for attribute in component.children("attribute"):
            key = text(attribute.atom(), 256)
            require(key not in keys, "Duplicate component attribute.")
            keys.add(key)
            attributes.append({"key": key, **{
                name: text(attribute.field(name)) for name in ("type", "unit", "value")
            }})
        require(len(attributes) <= 32, "Too many attributes for bounded inspection.", "resource_limit")
        value = text(component.field("value"))
        schematic_only = library.field("schematic_only")
        require(schematic_only in {"true", "false"}, "Invalid schematic_only flag.")
        components.append({"id": identifier, "reference": reference, "value_raw": value,
                           "value_is_template": "{{" in value, "attributes": attributes,
                           "library_component_id": lib_id, "schematic_only": schematic_only == "true",
                           "signal_count": len(assignments), "connected_signal_count": connected})
    for identifier, record in net_records.items():
        record["component_count"] = len(net_components[identifier])

    def pages(plural: str, singular: str) -> list[dict]:
        index = document(f"{plural}/{plural}.lp", f"librepcb_{plural}")
        allowed(index, {singular})
        result = []
        ids, paths = set(), set()
        for item in index.children(singular):
            require(len(item.items) == 1, "Unsupported page-index entry.")
            path = relative_design_path(item.atom())
            page = document(path, f"librepcb_{singular}")
            identifier = uuid(page.atom())
            require(identifier not in ids and path not in paths, "Duplicate schematic/board entry.")
            ids.add(identifier)
            paths.add(path)
            # Validate the projected component relationships; the CLI covers geometry.
            for instance in page.children("symbol" if singular == "schematic" else "device"):
                component_id = instance.field("component") if singular == "schematic" else instance.atom()
                require(uuid(component_id) in component_nodes, "Schematic/board refers to an unknown component.")
            result.append({"id": identifier, "name": text(page.field("name"), 512), "file": path})
        require(len(result) <= 32, "Too many schematic/board pages.", "resource_limit")
        return result

    return ProjectData(info, pages("boards", "board"), pages("schematics", "schematic"),
                       sorted(components, key=lambda item: item["reference"]),
                       sorted(net_records.values(), key=lambda item: (item["name"], item["id"])))
