import json
import argparse
import sys

RU_JSON_PATH = "./ru.json"
RUSSIAN_JS_PATH = "./russian.js"


def _generate_js_content(ru_json_path: str) -> str:
    with open(ru_json_path, "r", encoding="utf-8") as f:
        ru_data = json.load(f)

    ru_json_string = json.dumps(ru_data, ensure_ascii=False, separators=(",", ":"))
    escaped_json = ru_json_string.replace("\\", "\\\\").replace('"', '\\"')

    js_content = f"""// ==UserScript==
// @name         russian warera
// @namespace    http://tampermonkey.net/
// @version      0.3
// @description  makes warera russian
// @match        https://app.warera.io/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {{

    const RU_LOCALE_JSON = "{escaped_json}";

    const RU_LOCALE = JSON.parse(RU_LOCALE_JSON);

    const originalParse = JSON.parse;

    JSON.parse = function (text) {{
        const obj = originalParse.apply(this, arguments);

        if (obj && typeof obj === "object" && obj["+/LYvo"] && obj["4wyw8H"]) {{
            console.log("🇷🇺 Russian locale injected");

            Object.assign(obj, RU_LOCALE);
        }}

        return obj;
    }};

}})();
"""
    return js_content


def main():
    parser = argparse.ArgumentParser(
        description="Generate or verify russian.js from ru.json"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare generated content with existing russian.js without writing",
    )
    args = parser.parse_args()

    js_content = _generate_js_content(RU_JSON_PATH)

    if args.check:
        try:
            with open(RUSSIAN_JS_PATH, "r", encoding="utf-8") as f:
                current = f.read()
        except FileNotFoundError:
            sys.exit(1)

        if current == js_content:
            sys.exit(0)
        else:
            sys.exit(2)

    with open(RUSSIAN_JS_PATH, "w", encoding="utf-8") as f:
        f.write(js_content)


if __name__ == "__main__":
    main()
