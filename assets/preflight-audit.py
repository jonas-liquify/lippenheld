# -*- coding: utf-8 -*-
"""Audit fuer die Liquiflow-Regeln aus dem liquiflow-builder Skill."""
import re, glob, json, io, os, collections, sys

ROOT = "/Users/jonas/Ablage/Liquiflow Projects/lippenheld-20"
os.chdir(ROOT)
problems = []

def p(msg):
    problems.append(msg)

sections = sorted(glob.glob("_sections/*.html"))
all_html = sorted(glob.glob("**/*.html", recursive=True))

# --- 1) li-settings:custom muss valides JSON enthalten -----------------
for f in all_html:
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r'<div li-settings:custom(?:="[^"]*")? class="li-custom">(.*?)</div>', s, re.S):
        raw = m.group(1).strip()
        try:
            json.loads(raw)
        except Exception as e:
            p("JSON ungueltig in %s: %s ... (%s)" % (f, raw[:70].replace("\n", " "), e))

# --- 2) Sectionnamen <= 30 Zeichen, Blocknamen <= 25, projektweit eindeutig
blocks = collections.defaultdict(set)
for f in sections:
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r'\bli-section="([^"]+)"', s):
        if len(m.group(1)) > 30:
            p("Sectionname zu lang (%d): %s in %s" % (len(m.group(1)), m.group(1), f))
    own = os.path.basename(f)[:-5]
    for attr in ("li-block", "li-static-block"):
        for m in re.finditer(r'\b%s="([^"]+)"' % attr, s):
            name = m.group(1)
            # Blocks, die zu einer *verschachtelten* Section-Instanz gehoeren, ueberspringen
            before = s[:m.start()]
            nested = re.findall(r'li-section="([^"]+)"', before)
            if nested and nested[-1] != own:
                continue
            blocks[name].add(f)
            if len(name) > 25:
                p("Blockname zu lang (%d): %s in %s" % (len(name), name, f))
for name, files in blocks.items():
    if len(files) > 1:
        p("Blockname doppelt: %s in %s" % (name, sorted(files)))

# --- 3) li-attribute NICHT auf dem li-section-Element ------------------
TAG = re.compile(r'<(\w+)((?:\s+[\w:.\-]+(?:="[^"]*"|=\'[^\']*\'|=[^\s"\'>]+)?)*)\s*/?>')
for f in all_html:
    s = io.open(f, encoding="utf-8").read()
    for m in TAG.finditer(s):
        attrs = m.group(2)
        if re.search(r'\bli-section="', attrs) and re.search(r'\bli-attribute:', attrs):
            p("li-attribute auf dem li-section-Element in %s (<%s>)" % (f, m.group(1)))
        if re.search(r'\bli-(if|unless)=', attrs) and re.search(r'\bli-attribute:', attrs):
            p("li-if/li-unless + li-attribute auf demselben Element in %s (<%s>)" % (f, m.group(1)))

# --- 4) hoechstens ein Top-Level li-content-for-theme-blocks je Section -
for f in sections:
    s = io.open(f, encoding="utf-8").read()
    n = len(re.findall(r'li-(?:cf|content-for)-theme-blocks', s))
    static = len(re.findall(r'li-static-block=', s))
    if n > 1 and static == 0:
        p("%d theme-block-Wrapper ohne li-static-block in %s" % (n, f))

# --- 5) nur li-block als direkte Kinder des theme-block-Wrappers -------
for f in sections:
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r'<(\w+)[^>]*li-(?:cf|content-for)-theme-blocks[^>]*>', s):
        tag, start = m.group(1), m.end()
        depth, i = 1, start
        while i < len(s) and depth > 0:
            nxt = re.search(r'<(/?)%s\b[^>]*?(/?)>' % tag, s[i:])
            if not nxt:
                break
            depth += -1 if nxt.group(1) else (0 if nxt.group(2) else 1)
            i += nxt.end()
        inner = s[start:i - len("</%s>" % tag)]
        # direkte Kinder ermitteln
        d, j, children = 0, 0, []
        for cm in re.finditer(r'<(/?)(\w+)([^>]*?)(/?)>', inner):
            closing, name, attrs, self_close = cm.group(1), cm.group(2), cm.group(3), cm.group(4)
            if closing:
                d -= 1
                continue
            if d == 0:
                children.append((name, attrs))
            if not self_close and name not in ("img", "input", "br", "hr", "meta", "link"):
                d += 1
        for name, attrs in children:
            if "li-block=" not in attrs:
                p("Nicht-li-block als direktes Kind von theme-blocks in %s: <%s>" % (f, name))

# --- 6) verwendete CSS-Klassen muessen in css/main.css existieren -------
css = io.open("css/main.css", encoding="utf-8").read()
defined = set(re.findall(r'\.([a-zA-Z][\w\-]*)', css))
used = collections.Counter()
for f in all_html:
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r'\sclass="([^"]*)"', s):
        for c in m.group(1).split():
            if "{" in c or "}" in c:
                continue
            used[c] += 1
missing = sorted(c for c in used if c not in defined)
for c in missing:
    p("CSS-Klasse ohne Regel: .%s (%dx)" % (c, used[c]))

# --- 7) keine min-width-Media-Queries ---------------------------------
if re.search(r'@media[^{]*min-width', css):
    p("min-width Media-Query in css/main.css gefunden")

# --- 8) li-for:inside nicht auf dem zu wiederholenden Element ----------
for f in all_html:
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r'<(\w+)\b([^>]*\bli-for:inside="[^"]+"[^>]*)>', s):
        tag, attrs = m.group(1).lower(), m.group(2)
        cls = re.search(r'class="([^"]+)"', attrs)
        cls = cls.group(1).split() if cls else []
        if tag in ("li", "tr", "option") or "swiper-slide" in cls:
            p("li-for:inside vermutlich falsch platziert in %s (<%s class=%s>)" % (f, tag, cls))

# --- 9) li-for + textbindendes li-object auf demselben Element -----------
#     Der Converter liest dann den li-object-Wert als for-Ausdruck:
#     "For loops require an 'in' clause in \"part.title\""
#     Nur die bare Form bricht; li-object:href/-src sind unproblematisch.
for f in all_html:
    s = io.open(f, encoding="utf-8").read()
    for m in TAG.finditer(s):
        attrs = m.group(2)
        if re.search(r'\bli-for=', attrs) and re.search(r'\bli-object="', attrs):
            p("li-for + li-object=\"…\" auf demselben Element in %s (<%s>) — "
              "Textbindung in ein inneres <span> verschieben" % (f, m.group(1)))

# --- 10) jeder Resource-Picker-Typ nur EINMAL pro Section ----------------
#      Shopify: "setting <typ> type can only be inserted once in the settings"
#      Gilt fuer link_list, collection, product, blog, article, page —
#      auch wenn eine Section eine andere Section inline enthaelt (Header +
#      predictive_search landen in einem Schema).
PICKERS = ("link_list", "collection", "product", "blog", "article", "page")
for f in sections:
    s = io.open(f, encoding="utf-8").read()
    cnt = collections.Counter()
    for t in PICKERS:
        cnt[t] += len(re.findall(r'\bli-settings:%s(?:=|\s|>)' % t, s))
    for m in re.finditer(r'<div li-settings:custom(?:="[^"]*")? class="li-custom">(.*?)</div>', s, re.S):
        try:
            data = json.loads(m.group(1).strip())
        except Exception:
            continue
        for e in (data if isinstance(data, list) else [data]):
            if isinstance(e, dict) and e.get("type") in PICKERS:
                cnt[e["type"]] += 1
    for t, n in cnt.items():
        if n > 1:
            p("%d %s-Settings in %s — Shopify erlaubt nur eines pro Section" % (n, t, f))

# --- 10b) "default": "" ist ungueltig -----------------------------------
#      Shopify: "default can't be blank" — den default-Key stattdessen weglassen
for f in sections:
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r'\{[^{}]*"default":\s*""[^{}]*\}', s):
        idm = re.search(r'"id":\s*"([^"]+)"', m.group(0))
        p("leerer default in %s (id=%s) — Key ganz weglassen"
          % (f, idm.group(1) if idm else "?"))

# --- 11) range-Default muss auf dem Step-Raster liegen -------------------
#      Shopify: "default must be a step in the range"
for f in sections:
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r'<div li-settings:custom(?:="[^"]*")? class="li-custom">(.*?)</div>', s, re.S):
        try:
            data = json.loads(m.group(1).strip())
        except Exception:
            continue
        for e in (data if isinstance(data, list) else [data]):
            if not isinstance(e, dict) or e.get("type") != "range":
                continue
            mn, mx, st, d = e.get("min", 0), e.get("max"), e.get("step", 1), e.get("default")
            if d is None:
                continue
            if (d - mn) % st != 0:
                p("range-Default nicht auf dem Step-Raster in %s: id=%s min=%s step=%s default=%s"
                  % (f, e.get("id"), mn, st, d))
            if mx is not None and not (mn <= d <= mx):
                p("range-Default ausserhalb min/max in %s: id=%s" % (f, e.get("id")))

print("=" * 60)
if problems:
    print("%d Befund(e):" % len(problems))
    for x in problems:
        print("  •", x)
else:
    print("Alle Prüfungen sauber.")
print("=" * 60)
sys.exit(0)
