import json
import re
import sys
from typing import Any, List

EN_JSON_PATH = "./en.json"
RU_JSON_PATH = "./ru.json"

TAG_RE = re.compile(r"<[^>]+>")


def _load(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _string_tags(value: str) -> List[str]:
    return TAG_RE.findall(value)


def _compare_item(
    en_item: Any, ru_item: Any, path: List[str], errors: List[str], max_errors: int = 20
):
    if len(errors) >= max_errors:
        return

    if isinstance(en_item, list):
        if not isinstance(ru_item, list):
            errors.append(
                f"Type mismatch at {'/'.join(path)}: expected list, got {type(ru_item).__name__}"
            )
            return
        if len(en_item) != len(ru_item):
            errors.append(
                f"List length mismatch at {'/'.join(path)}: {len(en_item)} != {len(ru_item)}"
            )
            return
        for i, (e_sub, r_sub) in enumerate(zip(en_item, ru_item)):
            sub_path = path + [f"[{i}]"]
            if isinstance(e_sub, list):
                if not isinstance(r_sub, list):
                    errors.append(
                        f"Type mismatch at {'/'.join(sub_path)}: expected placeholder list, got {type(r_sub).__name__}"
                    )
                    continue
                if not (
                    all(isinstance(x, str) for x in e_sub)
                    and all(isinstance(x, str) for x in r_sub)
                ):
                    errors.append(
                        f"Invalid placeholder structure at {'/'.join(sub_path)}"
                    )
                    continue
                if e_sub != r_sub:
                    errors.append(
                        f"Placeholder mismatch at {'/'.join(sub_path)}: {e_sub} != {r_sub}"
                    )
                continue
            elif isinstance(e_sub, str):
                if not isinstance(r_sub, str):
                    errors.append(
                        f"Type mismatch at {'/'.join(sub_path)}: expected string, got {type(r_sub).__name__}"
                    )
                    continue
                en_tags = _string_tags(e_sub)
                ru_tags = _string_tags(r_sub)
                if en_tags != ru_tags:
                    errors.append(
                        f"Tag sequence mismatch at {'/'.join(sub_path)}: {en_tags} != {ru_tags}"
                    )
                continue
            else:
                if type(e_sub) is not type(r_sub):
                    errors.append(
                        f"Type mismatch at {'/'.join(sub_path)}: {type(e_sub).__name__} != {type(r_sub).__name__}"
                    )
        return

    if isinstance(en_item, str):
        if not isinstance(ru_item, str):
            errors.append(
                f"Type mismatch at {'/'.join(path)}: expected string, got {type(ru_item).__name__}"
            )
            return
        en_tags = _string_tags(en_item)
        ru_tags = _string_tags(ru_item)
        if en_tags != ru_tags:
            errors.append(
                f"Tag sequence mismatch at {'/'.join(path)}: {en_tags} != {ru_tags}"
            )
        return

    if type(en_item) is not type(ru_item):
        errors.append(
            f"Type mismatch at {'/'.join(path)}: {type(en_item).__name__} != {type(ru_item).__name__}"
        )


def main():
    en = _load(EN_JSON_PATH)
    ru = _load(RU_JSON_PATH)

    en_keys = set(en.keys())
    ru_keys = set(ru.keys())

    missing = en_keys - ru_keys
    extra = ru_keys - en_keys

    errors: List[str] = []

    if missing:
        errors.append(
            f"Missing keys in ru.json: {sorted(list(missing))[:10]}"
            + (" ..." if len(missing) > 10 else "")
        )
    if extra:
        errors.append(
            f"Extra keys in ru.json: {sorted(list(extra))[:10]}"
            + (" ..." if len(extra) > 10 else "")
        )

    for k in sorted(en_keys & ru_keys):
        _compare_item(en[k], ru[k], [k], errors)
        if len(errors) >= 20:
            break

    if errors:
        for e in errors:
            print(e)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
