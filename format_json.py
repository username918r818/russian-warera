import argparse
import json
import sys
from pathlib import Path
from typing import List

DEFAULT_FILES = ["./ru.json", "./en.json"]


def format_json_text(
    data: object, indent: int, sort_keys: bool, ensure_ascii: bool
) -> str:
    text = json.dumps(
        data,
        ensure_ascii=ensure_ascii,
        indent=indent,
        separators=(",", ": "),
        sort_keys=sort_keys,
    )
    if not text.endswith("\n"):
        text += "\n"
    return text


def process_file(
    path: Path, check: bool, indent: int, sort_keys: bool, ensure_ascii: bool
) -> bool:
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except Exception:
        return False

    formatted = format_json_text(
        data, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii
    )

    if check:
        return raw == formatted

    path.write_text(formatted, encoding="utf-8")
    return True


def main(argv: List[str] = None) -> int:
    p = argparse.ArgumentParser(description="Format JSON files consistently")
    p.add_argument(
        "files", nargs="*", default=DEFAULT_FILES, help="JSON files to format"
    )
    p.add_argument(
        "--check", action="store_true", help="Only check, do not write changes"
    )
    p.add_argument("--indent", type=int, default=2, help="Indent size (default: 2)")
    p.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort object keys for deterministic order",
    )
    p.add_argument(
        "--ensure-ascii",
        action="store_true",
        help="Escape non-ASCII characters (default: keep unicode)",
    )

    args = p.parse_args(argv)

    ok = True
    for f in args.files:
        path = Path(f)
        if not path.exists():
            ok = False
            continue
        same = process_file(
            path,
            check=args.check,
            indent=args.indent,
            sort_keys=args.sort_keys,
            ensure_ascii=args.ensure_ascii,
        )
        ok = ok and same

    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
