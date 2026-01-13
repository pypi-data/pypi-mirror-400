from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from typing import Literal, Union


@dataclass
class Item:
    path: Path
    type: Literal["F"] | Literal["D"]
    size: int
    permissions: str
    uid: str
    gid: str
    modified: datetime
    parent: Union["Item", None]
    children: set["Item"] = field(default_factory=set)

    def to_qdirstat(self) -> str:
        # type, path, size, uid, gid, perm., mtime, <optional fields>
        out = ""

        if self.type == "D":
            self.size = 0

            children = sorted(self.children, key=lambda i: 1 if i.is_dir else -1)

            for item in children:
                out += "\n" + item.to_qdirstat()

        out = (
            f"{self.type} {quote(str(self.path) if self.is_dir else self.path.name)} {self.size}  {self.uid}  {self.gid}  0777\t0x{int(self.modified.timestamp()):02x}"
            + out
        )
        return out

    @property
    def is_dir(self) -> bool:
        return self.type == "D"

    def __hash__(self) -> int:
        return self.path.__hash__()


def parse_permissions(permissions: str) -> str:
    assert len(permissions) == 9

    map = [("r", 4), ("w", 2), ("x", 1)]

    blocks = [permissions[0:3], permissions[3:6], permissions[6:9]]
    out = "0"

    for block in blocks:
        permission = 0

        for char, check in zip(block, map):
            key, n = check

            if char == key:
                permission += n

        out += str(permission)

    return out
