#!/usr/bin/env python3
"""
Ersetzt Head/GlobalStyles/Navbar/Footer/Body-Ende durch die gleichen Components wie index.page.js.
Nur ausführen, wenn die Seite die Standard-Struktur mit
  page-wrapper → global-styles → section_header-group → main → section_footer-group → jquery
hat.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

IMPORTS_ROOT = """import BodyCode from './components/Body Code.component.js'
import Footer from './components/Footer.component.js'
import GlobalStyles from './components/Global Styles.component.js'
import HeadCode from './components/Head Code.component.js'
import Navbar from './components/Navbar.component.js'

"""

IMPORTS_SUB = """import BodyCode from '../components/Body Code.component.js'
import Footer from '../components/Footer.component.js'
import GlobalStyles from '../components/Global Styles.component.js'
import HeadCode from '../components/Head Code.component.js'
import Navbar from '../components/Navbar.component.js'

"""


def component_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return "./" if rel.parent == Path(".") else "../"


def ensure_imports(text: str, prefix: str) -> str:
    if "import HeadCode from" in text:
        return text
    imp = IMPORTS_ROOT if prefix == "./" else IMPORTS_SUB
    if not text.startswith("import "):
        return imp + text
    # Einfügen vor export const template
    idx = text.find("export const template")
    if idx == -1:
        return imp + text
    return text[:idx] + imp + text[idx:]


def replace_head(text: str) -> str:
    """Nur den <head>-Block vor dem ersten <body> ersetzen (vermeidet Treffer bei
    </head> in langen <script>-Blöcken im Webflow-<head>)."""
    body_idx = text.find("<body")
    if body_idx == -1:
        return re.sub(
            r"(?s)<head>.*?</head>",
            "  <head>\n    <HeadCode></HeadCode>\n  </head>",
            text,
            count=1,
        )
    before, after = text[:body_idx], text[body_idx:]
    before = re.sub(
        r"(?s)<head>.*?</head>",
        "  <head>\n    <HeadCode></HeadCode>\n  </head>",
        before,
        count=1,
    )
    return before + after


def replace_global_styles(text: str) -> tuple[str, bool]:
    pat = re.compile(
        r'<div class="page-wrapper">\s*<div class="global-styles w-embed" li-snippet="global-styles">.*?</style>\s*</div>\s*',
        re.DOTALL,
    )
    new, n = pat.subn("<GlobalStyles></GlobalStyles>\n    ", text, count=1)
    return new, n == 1


def replace_navbar(text: str) -> tuple[str, bool]:
    nav_start = text.find('<div class="section_header-group"')
    main_start = text.find('<main class="main-wrapper"', nav_start)
    if nav_start == -1 or main_start == -1:
        return text, False
    return text[:nav_start] + "<Navbar></Navbar>\n      " + text[main_start:], True


def replace_footer(text: str) -> tuple[str, bool]:
    foot_start = text.find('<div class="section_footer-group"')
    jq_start = text.find(
        '<script src="https://d3e54v103j8qbb.cloudfront.net/js/jquery', foot_start
    )
    if foot_start == -1 or jq_start == -1:
        return text, False
    return text[:foot_start] + "      <Footer></Footer>\n" + text[jq_start:], True


def replace_body_scripts(text: str) -> tuple[str, bool]:
    script_start = text.find(
        '<script src="https://d3e54v103j8qbb.cloudfront.net/js/jquery'
    )
    body_close = text.rfind("</body>")
    if script_start == -1 or body_close == -1 or script_start >= body_close:
        return text, False
    return text[:script_start] + "    <BodyCode></BodyCode>\n  " + text[body_close:], True


def process_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    if "apply_layout_components" in str(path):
        return False
    if path.name == "index.page.js":
        print(f"skip (bereits Components): {path}")
        return False

    prefix = component_prefix(path)
    text = raw

    text = ensure_imports(text, prefix)
    text = replace_head(text)

    text, ok_gs = replace_global_styles(text)
    text, ok_nav = replace_navbar(text)
    text, ok_foot = replace_footer(text)
    text, ok_body = replace_body_scripts(text)

    if not all([ok_gs, ok_nav, ok_foot, ok_body]):
        print(
            f"WARNUNG {path}: gs={ok_gs} nav={ok_nav} foot={ok_foot} body={ok_body}",
            file=sys.stderr,
        )
        return False

    if text == raw:
        print(f"unverändert: {path}")
        return False

    path.write_text(text, encoding="utf-8")
    print(f"OK: {path}")
    return True


def main() -> None:
    targets = []
    for p in ROOT.rglob("*.page.js"):
        if "node_modules" in p.parts:
            continue
        targets.append(p)

    for path in sorted(targets):
        process_file(path)


if __name__ == "__main__":
    main()
