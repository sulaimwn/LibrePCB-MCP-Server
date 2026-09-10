"""Bounded, read-only LibrePCB S-expression parser.

Grammar verified against LibrePCB 2.1.1 serialization/sexpression.cpp.
No evaluation or serialization. Offsets refer to the untouched UTF-8-decoded
source so unrecognized fields and formatting need never be rewritten.
"""

from dataclasses import dataclass
import string

from librepcb_mcp.errors import ProjectError, require

TOKEN_CHARS = frozenset(string.ascii_letters + string.digits + "\\.:_-")
SPACES = " \f\r\t\v\n"
ESCAPES = {"'": "'", '"': '"', "?": "?", "\\": "\\", "a": "\a", "b": "\b",
           "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v"}


@dataclass(frozen=True)
class Atom:
    value: str
    quoted: bool
    start: int
    end: int


@dataclass(frozen=True)
class Node:
    name: str
    items: tuple["Node | Atom", ...]
    start: int
    end: int

    def children(self, name: str) -> list["Node"]:
        return [item for item in self.items if isinstance(item, Node) and item.name == name]

    def one(self, name: str) -> "Node":
        matches = self.children(name)
        require(len(matches) == 1, f"Expected exactly one '{name}' field in '{self.name}'.")
        return matches[0]

    def atom(self, index: int = 0) -> str:
        require(index < len(self.items) and isinstance(self.items[index], Atom),
                f"Expected scalar {index} in '{self.name}'.")
        return self.items[index].value

    def field(self, name: str) -> str:
        child = self.one(name)
        require(len(child.items) == 1, f"Unsupported shape of '{name}'.")
        return child.atom()


def parse(source: str, *, max_depth: int = 64, max_nodes: int = 250_000) -> Node:
    require(len(source) <= 16_000_000, "S-expression file exceeds size limit.", "resource_limit")
    require("\x00" not in source, "NUL bytes are not supported.")
    position = 0
    count = 0

    def fail(message: str):
        raise ProjectError("invalid_project", f"{message} At character {position}.")

    def skip():
        nonlocal position
        while position < len(source):
            if source[position] in SPACES:
                position += 1
            elif source[position] == ";":
                newline = source.find("\n", position)
                position = len(source) if newline < 0 else newline + 1
            else:
                break

    def token() -> str:
        nonlocal position
        start = position
        while position < len(source) and source[position] in TOKEN_CHARS:
            position += 1
        if start == position:
            fail("Invalid token")
        return source[start:position]

    def read(depth: int) -> Node | Atom:
        nonlocal position, count
        count += 1
        require(depth <= max_depth and count <= max_nodes, "S-expression complexity limit exceeded.", "resource_limit")
        if position >= len(source):
            fail("Unexpected end of file")
        start = position
        current = source[position]
        if current == "(":
            position += 1
            name = token()  # LibrePCB requires the list name immediately after '('.
            items = []
            skip()
            while position < len(source) and source[position] != ")":
                items.append(read(depth + 1))
                skip()
            if position >= len(source):
                fail("Unclosed list")
            position += 1
            return Node(name, tuple(items), start, position)
        if current == '"':
            position += 1
            value = []
            while position < len(source) and source[position] != '"':
                character = source[position]
                position += 1
                if character == "\\":
                    if position >= len(source) or source[position] not in ESCAPES:
                        fail("Illegal string escape")
                    character = ESCAPES[source[position]]
                    position += 1
                value.append(character)
                require(len(value) <= 65_536, "String exceeds parser limit.", "resource_limit")
            if position >= len(source):
                fail("Unclosed string")
            position += 1
            return Atom("".join(value), True, start, position)
        return Atom(token(), False, start, position)

    skip()
    root = read(0)
    skip()
    require(position == len(source), "More than one root node or trailing invalid data.")
    require(isinstance(root, Node), "Expected a list root.")
    return root
