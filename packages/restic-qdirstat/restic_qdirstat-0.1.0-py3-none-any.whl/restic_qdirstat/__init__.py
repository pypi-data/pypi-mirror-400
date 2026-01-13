import argparse
from datetime import datetime
from pathlib import Path
import sys
import re
import gzip

from .lib import Item, parse_permissions


ls_regex = re.compile(
    r"([Ld-])t?([rwx-]{9})\s*?(\d+)\s*?(\d+)\s*?(\d+)\s*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.*)"
)


def main():
    parser = argparse.ArgumentParser(
        prog="restic-qdirstat",
        description="Creates a QDirStat cache archive from the output of `restic ls -l`",
        epilog="Pipe the output of restic into this program, i.e. `restic ls -l | restic-qdirstat`",
    )

    parser.add_argument(
        "-i",
        "--input",
        help="Instead of using stdin, you can also provide the output of restic as a file",
        required=False,
        type=Path,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file, defaults to restic.cache.gz",
        required=False,
        default="restic.cache.gz",
    )

    args = parser.parse_args()

    roots = set[Item]()
    last: Item | None = None
    i = 0

    if args.input:
        input = open(args.input)
    else:
        input = sys.stdin

    while line := input.readline():
        i += 1

        if match := ls_regex.match(line):
            type, permissions, uid, gid, size, timestamp, path = match.groups()

            if type == "L":
                # symbolic link
                continue

            assert type in ("-", "d")
            is_dir = type == "d"

            path = Path(path)

            parent = None

            while parent is None:
                if last is None:
                    assert is_dir
                    break
                elif last.path == path.parent:
                    parent = last
                else:
                    last = last.parent

            item = Item(
                path=path,
                type="D" if is_dir else "F",
                size=int(size),
                permissions=parse_permissions(permissions),
                uid=uid,
                gid=gid,
                modified=datetime.fromisoformat(timestamp),
                parent=parent,
            )

            if parent is None:
                roots.add(item)
            else:
                parent.children.add(item)

            if parent is None or is_dir:
                last = item
        elif i != 1:
            print(f"Error: Could not parse line {i}")
            sys.exit(1)

    if args.input:
        input.close()

    with gzip.open(args.output, "wb") as f:
        f.write(b"[qdirstat 2.0 cache file]\n")  # pyright: ignore[reportArgumentType]

        if not roots:
            print("Error: No files found")
            sys.exit(1)
        elif len(roots) > 1:
            root = Item(
                path=Path("/"),
                type="D",
                size=0,
                permissions="0777",
                uid="0",
                gid="0",
                modified=datetime.now(),
                parent=None,
                children=roots,
            )
        else:
            root = roots.pop()

        f.write(root.to_qdirstat().encode())  # pyright: ignore[reportArgumentType]
