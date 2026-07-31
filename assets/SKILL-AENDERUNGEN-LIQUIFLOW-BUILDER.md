# Liquiflow-Builder-Skill: Änderungsvorschlag

**Anlass:** Erstkonvertierung eines vollständigen Themes (Lippenheld, 45 Sections,
20 Seiten) nach Shopify am 31.07.2026. Der Builder-Lint war **fehlerfrei**, der
Theme-Upload hat trotzdem in zwei Runden 11 Validation-Fehler gemeldet. Dazu kamen zwei stille Probleme ohne jede Fehlermeldung. Alle sechs Ursachen
waren im Skill bisher nicht dokumentiert.

**Betroffene Dateien im Skill:**

| Datei | Änderung |
|---|---|
| `SKILL.md` | Neuer Abschnitt „Shopify-Validation — die Fehler, die erst beim Konvertieren auffallen" (231 Zeilen), eingefügt zwischen „Setting-Defaults — Shopify-Validation beachten" und „Custom Settings — Pflicht für jede Section" |
| `SKILL.md` | Neuer Abschnitt „`li-block` und `li-settings:*` dürfen nicht auf demselben Element stehen" (58 Zeilen), vor „Niemals `li-*` Attribute als CSS-Selector zum Ausblenden nutzen" |
| `SKILL.md` | Neuer Abschnitt „Keine strukturellen CSS-Selektoren über Section-Grenzen — Shopify wrappt jede Section" (68 Zeilen), vor „Schritt 6 — Fehlende CSS-Klassen direkt ins Projekt-CSS schreiben" |
| `SKILL.md` | Hinweis in „Pflichtlektüre vor dem Generieren" (4 Zeilen), der auf den neuen Abschnitt und das Pre-Flight-Audit verweist |
| `references/liquiflow-docs.md` | Neuer Unterabschnitt „Shopify schema/Liquid invariants (fail only at theme upload, not at lint)" (19 Zeilen) und „Builder-only invariants (break silently, no error at all)" (13 Zeilen) unter „Invariants (Never Break These)" |

---

## Teil 1 — Die sechs Ursachen in Kurzform

### 1. `li-for` + textbindendes `li-object` auf demselben Element

```
Liquid syntax error (line 8): For loops require an 'in' clause in "part.title"
```

Der Converter nimmt bei zwei konkurrierenden Bindungen den **`li-object`-Wert als
For-Ausdruck**: `{% for part.title %}` statt `{% for part in paginate.parts %}`.

Entscheidend ist die Form von `li-object`:

| Kombination | Ergebnis |
|---|---|
| `li-for` + `li-object="pfad"` (Textausgabe) | **bricht** |
| `li-for` + `li-object:href` / `:src` / `:alt` | funktioniert |

Das erklärt, warum es in unserem Projekt nur an 8 von 14 Stellen geknallt hat —
was die Diagnose zunächst verschleiert hat.

**Betroffene Muster:** Pagination (`paginate.parts`), Sortier-Dropdowns
(`collection.sort_options`), Predictive-Search-Vorschläge
(`predictive_search.resources.*`), Tag-Listen.

**Workaround:** Textbindung in ein inneres `<span>`. Beim `<option>` ist das nicht
möglich (ungültiges HTML) — dort `li-for:inside` auf das `<select>`.

### 2. Jeder Resource-Picker-Typ nur einmal pro Section

```
Invalid schema: setting link_list type can only be inserted once in the settings.
Invalid schema: setting collection type can only be inserted once in the settings.
```

Gilt für `link_list`, `collection`, `product`, `blog`, `article`, `page`.

**Die unerwartete Falle:** enthält eine Section eine andere **inline** (bei uns
`Header` mit eingebettetem `predictive_search`), landen beide Schemas in *einer*
Datei. Je ein `collection`-Setting pro Quelldatei reicht dann schon für den
Konflikt — an den Einzeldateien ist das nicht zu sehen.

**Workarounds:** (a) Zweitmenü als `text`-Setting mit dem Linklisten-Handle,
`linklists[section.settings.x].links` funktioniert mit beiden Typen;
(b) anderen Picker-Typ wählen, wenn er semantisch passt (Mini-Cart-Upsell ist
EIN Produkt → `product` statt `collection`); (c) auf zwei Sections aufteilen.

### 2b. `"default": ""` ist ungültig

```
Invalid schema: setting with id="menu_right" default can't be blank
```

Ein leerer String als Default wird abgelehnt. Der `default`-Key muss **ganz weg**.
Das ergänzt die bestehende Regel „Setting-Defaults — Shopify-Validation beachten",
die bisher nur sagt „Default weglassen" — ohne klarzustellen, dass ein Leerstring
kein gültiger Ersatz ist.

### 3. `range`-Default muss auf dem Step-Raster liegen

```
Invalid schema: setting with id="min_height" default must be a step in the range
```

Shopify verlangt `(default − min) % step == 0`. Aus Figma übernommene Pixelwerte
treffen das oft nicht: `min 300, step 20, default 637` → `337 % 20 = 17`.
Besonders tückisch, weil es genau dann passiert, wenn man die Design-Werte
*genauer* macht.

### 4. `Section type '…' does not refer to an existing section file`

Kein eigener Fehler, sondern Kaskade: die Section hat die Validation nicht
bestanden und wurde nie geschrieben, die Section-Gruppe verweist ins Leere.

Dazu: **Shopify bricht pro Section beim ersten Fehler ab.** Bei uns kamen deshalb
nach der ersten Korrekturrunde zwei bis dahin verdeckte Fehler zum Vorschein.

### 5. `li-block` + `li-settings:*` auf einem Element (kein Fehler, aber vom Builder verboten)

Der Builder markiert beide Attribute im Inspector **rot** (exklusiv). Es gibt dazu
keine Lint-Meldung und keinen Konvertierungsfehler — man sieht es nur, wenn man
das Element im Inspector anklickt.

Typische Fundstellen: verlinkte Kacheln, bei denen der Block selbst ein `<a>` ist
(Bildraster, Social-Grid, Footer-Social-Icons). Bei uns drei Stellen.

Auflösung: `li-block` auf einen Wrapper, `li-settings:*` auf ein inneres Element.
`li-settings:*` auf *Kindern* des Blocks ist der Normalfall und unproblematisch —
nur die Kombination auf einem Element bricht.

### 6. Strukturelle CSS-Selektoren über Section-Grenzen brechen live

Kein Validation-Fehler, sondern ein stiller Verhaltensunterschied: Shopify wrappt
**jede** Section in `<div class="shopify-section">`. Selektoren wie

```css
.page-wrapper:has(.main-wrapper > .section_hero:first-child) .section_navbar { … }
```

funktionieren in der Builder-Vorschau und **nie** live. Bei uns blieb dadurch die
transparente Overlay-Navigation nach der Konvertierung auf allen Seiten weiß.

Das Muster, das wir stattdessen verwenden (und im Skill dokumentiert haben): die
Section deklariert ihren Wunsch über CSS-Variablen auf `:root` per eingebettetem
`<style>`, das Basis-CSS liest sie mit Fallback. Strukturunabhängig, ohne Liquid,
ohne Template-Listen, pro Section-Instanz über ein Checkbox-Setting steuerbar.

---

## Teil 2 — Empfehlungen an den Builder selbst

Die Skill-Änderung dokumentiert Workarounds. Drei der vier Klassen wären im
Builder besser gelöst als in der Doku:

### A) `li-for` + `li-object` ist vermutlich ein Converter-Bug

Beide Attribute sind laut Cheat-Sheet einzeln legitim, und ihre Kombination ist
nirgends verboten. Dass der Converter dann den falschen Wert als For-Ausdruck
nimmt, sieht nach einer Präzedenz-Verwechslung in der Attribut-Auswertung aus —
nicht nach einer bewussten Einschränkung.

**Vorschlag:** entweder im Converter auflösen (bei `li-for` + bare `li-object`
implizit ein `<span>` um den Textinhalt erzeugen) oder die Kombination im Linter
als Fehler melden. Aktuell ist sie lint-sauber und bricht erst in Shopify.

### B) Der Linter könnte das Shopify-Schema mitprüfen

Alle vier Klassen sind statisch aus den `li-settings:custom`-Blöcken und dem
Markup entscheidbar — kein Shopify-Zugriff nötig:

- `(default − min) % step != 0` bei `type: range`
- `"default": ""` bei irgendeinem Setting
- mehr als ein Setting desselben Picker-Typs **pro kompilierter Section**
  (inkl. inline eingebetteter Sections)
- `li-for` + bare `li-object` auf demselben Element

Das wären vier Regeln analog zu den bestehenden `STANDALONE_CONFLICT` /
`UNKNOWN_ATTR`. Sie hätten uns zwei Konvertierungsrunden gespart.

### C) `UNKNOWN_ATTR` für `li-snippet:product` ist ein False Positive

Der Linter meldet `li-snippet:product` durchgehend als „unbekanntes Attribut —
möglicherweise ein Tippfehler oder veralteter Name". Das Attribut ist in
`references/liquiflow-docs.md` dokumentiert (`li-snippet="name"
li-snippet:product="product"` → `{% render 'name', product: product %}`) und wird
vom **Liquiflow-Starter-Theme selbst** so verwendet
(`_snippets/product-item.html`). In unserem Projekt sind das 51 von 61
Lint-Meldungen — echtes Signal geht darin unter.

### D) `li-prop-*` widerspricht der Doku

Der Linter meldet `li-prop-<key>` zusammen mit `li-snippet` als **Fehler**
(`STANDALONE_CONFLICT: Mehrere exklusive Attribute auf demselben Element —
li-snippet, li-prop-label`). Die projektweite `CLAUDE.md` beschreibt genau das als
den vorgesehenen Property-Mechanismus:

> **Properties** are passed on the instance element via `li-prop-<key>="value"`
> attributes — the analogue of `{% render 'name', key: value %}`. They live ONLY
> on the instance.

Entweder ist die Linter-Regel zu streng oder die Doku veraltet — beides
zusammen führt dazu, dass man den dokumentierten Weg wieder ausbaut. Bei uns
waren das 65 Fehler, die wir durch Inlining der Snippets umgangen haben.

### F) `li-block` + `li-settings` nur im Inspector sichtbar

Die Exklusivität ist im Inspector klar markiert (rot), erzeugt aber **keine
Lint-Meldung**. Man findet sie nur durch Anklicken des Elements. Da der Linter
`STANDALONE_CONFLICT` für andere Attributpaare schon kennt, wäre die Regel dort
gut aufgehoben — sonst geht sie in einem Projekt mit 45 Sections unter.

### G) Der `shopify-section`-Wrapper wäre ein Vorschau-Kandidat

Der wohl folgenreichste Unterschied zwischen Vorschau und Live ist der
`<div class="shopify-section">` um jede Section. Alles, was CSS-seitig auf die
Verwandtschaft zwischen Sections baut, verhält sich deshalb unterschiedlich —
ohne jede Warnung.

Zwei denkbare Ansätze: (a) die Builder-Vorschau rendert denselben Wrapper, dann
fällt es sofort auf; (b) der Linter warnt bei Selektoren in `css/*.css`, die
`.main-wrapper >`, `.section_x + .section_y` oder Ähnliches über Section-Grenzen
hinweg verwenden. (a) wäre die gründlichere Lösung.

### E) Kleinigkeit: `MISSING_CONTENT_FOR_LAYOUT` auf `_sections/*.html`

Section-Dateien haben per Definition keinen Layout-Slot. Die Info-Meldung
erscheint für jede der 45 Sections und ist reines Rauschen — ließe sich auf
Seiten- und Layout-Dateien beschränken.

---

## Teil 3 — Der neue Skill-Abschnitt im Volltext

Zum direkten Übernehmen in `SKILL.md`. Einfügepunkt: zwischen
„## Setting-Defaults — Shopify-Validation beachten" und
„## Custom Settings — Pflicht für jede Section".

## Shopify-Validation — die Fehler, die erst beim Konvertieren auffallen

Diese Fehlerklassen bestehen den Builder-Lint **fehlerfrei** und schlagen erst
beim Theme-Upload in Shopify zu. Sie sind in einem echten Projekt (Lippenheld,
Juli 2026) alle gleichzeitig aufgetreten — prüfe sie mit dem Pre-Flight-Audit am
Ende dieses Abschnitts, bevor du konvertierst.

### 1. `li-for` + textbindendes `li-object` auf demselben Element

```
Error: sections/blog_articles.liquid, Validation failed:
Liquid syntax error (line 8): For loops require an 'in' clause in "part.title"
```

Der Converter liest bei zwei konkurrierenden Bindungen den **`li-object`-Wert als
For-Ausdruck** — `{% for part.title %}` statt `{% for part in paginate.parts %}`.

**Entscheidend ist die Form von `li-object`:**
- `li-object="pfad"` (Textausgabe) + `li-for` auf demselben Element → **bricht**
- `li-object:href="pfad"` / `:src` / `:alt` (Attribut-Modifier) + `li-for` → **unproblematisch**

```html
<!-- ❌ FALSCH: li-for und Textbindung auf dem gleichen <a> -->
<a li-for="part in paginate.parts" li-object="part.title"
   li-object:href="part.url" href="#" class="pagination_link">1</a>

<!-- ✅ RICHTIG: Textbindung in ein inneres <span> -->
<a li-for="part in paginate.parts" li-object:href="part.url" href="#"
   class="pagination_link"><span li-object="part.title">1</span></a>
```

**Sonderfall `<option>`:** dort kann kein `<span>` hinein (ungültiges HTML). Nutze
stattdessen `li-for:inside` auf dem `<select>`:

```html
<!-- ❌ FALSCH -->
<select class="form_input">
  <option li-for="option in collection.sort_options" li-object="option.name"
          li-attribute:value="{{ option.value }}">Empfohlen</option>
</select>

<!-- ✅ RICHTIG: :inside auf dem Wrapper, li-object auf dem <option> -->
<select li-for:inside="option in collection.sort_options" class="form_input">
  <option li-object="option.name" li-attribute:value="{{ option.value }}">Empfohlen</option>
</select>
```

Typische Fundstellen: Pagination (`paginate.parts`), Sortier-Dropdowns
(`collection.sort_options`), Predictive-Search-Vorschläge
(`predictive_search.resources.*`), Tag-Listen.

### 2. Jeder Resource-Picker-Typ nur EINMAL pro Section

```
Invalid schema: setting link_list type can only be inserted once in the settings.
Invalid schema: setting collection type can only be inserted once in the settings.
```

Das gilt für **alle** Resource-Picker: `link_list`, `collection`, `product`,
`blog`, `article`, `page`. Zwei Menüs, zwei Kollektionen oder zwei Produkte in
einer Section sind nicht möglich.

**Achtung bei verschachtelten Sections:** enthält eine Section eine andere inline
(klassisch `Header` + `predictive_search`), landen **beide Schemas in einer
Datei**. Ein `collection`-Setting im Header plus eines im eingebetteten
predictive_search verletzt die Regel, obwohl beide Quelldateien je nur eines
haben. Immer das kompilierte Ziel im Blick behalten.

**Auflösungen, je nach Fall:**

*a) Zweitmenü als `text`-Handle* — die Liquid-Referenz bleibt identisch:

```html
<!-- ❌ zwei link_list-Picker -->
<div li-settings:custom="Navigation" class="li-custom">[
  { "type": "link_list", "id": "menu",       "label": "Menü links", "default": "main-menu" },
  { "type": "link_list", "id": "menu_right", "label": "Menü rechts" }
]</div>

<!-- ✅ einer als Picker, der zweite als Handle -->
<div li-settings:custom="Navigation" class="li-custom">[
  { "type": "link_list", "id": "menu", "label": "Menü links", "default": "main-menu" },
  { "type": "text", "id": "menu_right", "label": "Menü rechts (Linklisten-Handle)",
    "info": "Handle der Linkliste, z. B. main-menu-right" }
]</div>
```

`linklists[section.settings.menu_right].links` funktioniert mit beiden Typen. Ein
leerer Handle liefert `nil`, die `li-for`-Schleife rendert dann nichts.

*b) Anderen Picker-Typ wählen, wenn er semantisch besser passt* — ein
Mini-Cart-Upsell ist EIN Produkt, keine Kollektion. `product` und `collection`
sind verschiedene Typen, dürfen also nebeneinander je einmal vorkommen:

```html
<!-- ❌ zweites collection-Setting -->
<div li-settings:collection="Warenkorb-Empfehlung" class="mini-cart_upsell">
  <div li-object="product.title">…</div>
</div>

<!-- ✅ product-Setting, deterministisch über section.settings referenziert -->
<div li-if="section.settings.upsell_product != blank" class="mini-cart_upsell">
  <div li-object="section.settings.upsell_product.title">…</div>
</div>
<div li-settings:custom="Warenkorb" class="li-custom">
{ "type": "product", "id": "upsell_product", "label": "Warenkorb-Empfehlung" }
</div>
```

Bei `li-settings:custom` bestimmst du die id selbst und referenzierst explizit
`section.settings.<id>.…` — verlässlicher als sich darauf zu stützen, welchen
Variablennamen ein Kurz-Attribut in den Scope legt.

*c) Auf zwei Sections aufteilen*, wenn beide Picker-UX gebraucht wird.

### 2b. `"default": ""` ist ungültig

```
Invalid schema: setting with id="menu_right" default can't be blank
```

Ein leerer String als Default wird abgelehnt. **Den `default`-Key ganz
weglassen**, dann ist das Feld im Editor einfach leer:

```json
❌ { "type": "text", "id": "menu_right", "label": "Menü rechts", "default": "" }
✅ { "type": "text", "id": "menu_right", "label": "Menü rechts" }
```

Das ergänzt die Regel aus „Setting-Defaults — Shopify-Validation beachten":
Handles ohne garantierte Existenz gehören weg — aber eben als **fehlender Key**,
nicht als leerer String.

### 3. `range`-Default muss auf dem Step-Raster liegen

```
Error: sections/form.liquid, Validation failed:
Invalid schema: setting with id="min_height" default must be a step in the range
```

Shopify verlangt `(default − min) % step == 0`. Ein aus Figma übernommener
Pixelwert trifft das oft nicht:

```json
{ "type": "range", "id": "min_height", "min": 300, "max": 900, "step": 20, "default": 637 }
```
`(637 − 300) % 20 = 17` → ungültig. Entweder auf **640** runden oder `step` so
wählen, dass der Figma-Wert erreichbar ist (`step: 1`).

Prüfe das bei **jedem** `range`-Setting, besonders bei aus dem Design
übernommenen Höhen und Abständen.

### 4. `Section type '…' does not refer to an existing section file`

```
Error: sections/footer_group.json, Validation failed:
Section type 'footer' does not refer to an existing section file
```

Das ist **kein eigener Fehler**, sondern Folgefehler: die Section
(`footer.liquid`) hat die Validation nicht bestanden und wurde deshalb nicht
geschrieben — die Section-Gruppe verweist dann auf eine fehlende Datei.
**Nicht die Gruppen-JSON debuggen.** Erst die gemeldeten Section-Fehler beheben,
dann verschwindet die Meldung von selbst.

Gleiches Muster: Shopify bricht die Validation einer Section beim **ersten**
Fehler ab. Eine Section mit zwei Problemen zeigt nur eines — nach dem Fix kann
also ein neuer Fehler in derselben Datei auftauchen. Nach jeder Korrekturrunde
erneut konvertieren, bis der Log leer ist.

### Pre-Flight-Audit (vor jeder Konvertierung ausführen)

```bash
python3 - <<'EOF'
import re, glob, io, json, collections
TAG = re.compile(r'<(\w+)((?:\s+[\w:.\-]+(?:="[^"]*"|=\'[^\']*\'|=[^\s"\'>]+)?)*)\s*/?>')
problems = []

for f in sorted(glob.glob("_sections/*.html")):
    s = io.open(f, encoding="utf-8").read()

    # 1) li-for + textbindendes li-object
    for m in TAG.finditer(s):
        a = m.group(2)
        if re.search(r'\bli-for=', a) and re.search(r'\bli-object="', a):
            problems.append("%s: li-for + li-object=\"…\" auf <%s> — Text in inneres <span>"
                            % (f, m.group(1)))

    # 2) Resource-Picker mehr als einmal + leere Defaults
    PICKERS = ("link_list", "collection", "product", "blog", "article", "page")
    cnt = collections.Counter()
    for t in PICKERS:
        cnt[t] += len(re.findall(r'\bli-settings:%s(?:=|\s|>)' % t, s))
    for m in re.finditer(r'class="li-custom">(.*?)</div>', s, re.S):
        try:
            for e in (lambda d: d if isinstance(d, list) else [d])(json.loads(m.group(1).strip())):
                if isinstance(e, dict) and e.get("type") in PICKERS:
                    cnt[e["type"]] += 1
        except Exception:
            pass
    for t, n in cnt.items():
        if n > 1:
            problems.append("%s: %d %s-Settings — nur eines pro Section erlaubt" % (f, n, t))
    for m in re.finditer(r'\{[^{}]*"default":\s*""[^{}]*\}', s):
        problems.append("%s: leerer default — Key ganz weglassen (%s)" % (f, m.group(0)[:60]))

    # 3) range-Default off-grid + JSON-Validitaet
    for m in re.finditer(r'<div li-settings:custom(?:="[^"]*")? class="li-custom">(.*?)</div>', s, re.S):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except Exception as e:
            problems.append("%s: ungueltiges Setting-JSON (%s)" % (f, e)); continue
        for e in (data if isinstance(data, list) else [data]):
            if not isinstance(e, dict) or e.get("type") != "range":
                continue
            mn, mx, st, d = e.get("min", 0), e.get("max"), e.get("step", 1), e.get("default")
            if d is None:
                continue
            if (d - mn) % st != 0:
                problems.append("%s: range id=%s default=%s nicht auf Step-Raster (min=%s step=%s)"
                                % (f, e.get("id"), d, mn, st))
            if mx is not None and not (mn <= d <= mx):
                problems.append("%s: range id=%s default ausserhalb min/max" % (f, e.get("id")))

print("\n".join(problems) if problems else "Pre-Flight sauber.")
EOF
```

---

---

## Teil 3b — Abschnitt „li-block und li-settings"

Einfügepunkt in `SKILL.md`: vor „### Niemals `li-*` Attribute als CSS-Selector
zum Ausblenden nutzen".

### `li-block` und `li-settings:*` dürfen nicht auf demselben Element stehen

Der Builder markiert beide Attribute im Inspector **rot** (exklusiv) — sie lassen
sich nicht kombinieren. Betrifft `li-block` genauso wie `li-static-block`.

```html
<!-- ❌ FALSCH: Block-Marker und Setting auf demselben <a> -->
<div li-cf-theme-blocks class="image-grid_list">
  <a li-block="Bildkachel" li-settings:url="Link" href="#" class="image-grid_item">
    <div class="image-grid_media"><img li-settings:image="Bild" src="/assets/ph.svg" alt=""></div>
    <div li-settings:text="Label" class="image-grid_label">Label</div>
  </a>
</div>

<!-- ✅ RICHTIG: li-block auf den Wrapper, li-settings auf ein inneres Element -->
<div li-cf-theme-blocks class="image-grid_list">
  <div li-block="Bildkachel" class="image-grid_item">
    <a li-settings:url="Link" href="#" class="image-grid_link">
      <div class="image-grid_media"><img li-settings:image="Bild" src="/assets/ph.svg" alt=""></div>
      <div li-settings:text="Label" class="image-grid_label">Label</div>
    </a>
  </div>
</div>
```

Nur die **Kombination auf einem Element** ist das Problem — `li-settings:*` auf
Kindern des Blocks ist der Normalfall und völlig in Ordnung (im Beispiel oben
`li-settings:image` und `li-settings:text`).

**Wichtig beim Umbau:** der neue Wrapper wird zum direkten Kind des
theme-blocks-Wrappers und muss deshalb das `li-block` tragen (sonst löscht der
Converter ihn, siehe „Nur `li-block` als direkte Kinder…"). Und das Layout-CSS
wandert vom Block-Wrapper auf das innere Element mit:

```css
.image-grid_item { position: relative; display: block; }   /* traegt li-block */
.image-grid_link { display: flex; flex-direction: column; gap: 1rem; height: 100%; }
```

Typische Fundstellen: verlinkte Karten und Kacheln (Bildraster, Social-Grid,
Footer-Social-Icons) — überall, wo der Block selbst ein `<a>` ist.

**Audit-Snippet:**
```bash
python3 -c "
import re, glob, io
TAG = re.compile(r'<(\w+)((?:\s+[\w:.\-]+(?:=\"[^\"]*\")?)*)\s*/?>')
for f in glob.glob('_sections/*.html') + glob.glob('_snippets/*.html'):
    s = io.open(f, encoding='utf-8').read()
    for m in TAG.finditer(s):
        a = m.group(2)
        blk = re.search(r'\bli-(?:static-)?block=\"([^\"]+)\"', a)
        if blk and re.search(r'\bli-settings:', a):
            print('%s: li-block=%r + %s auf <%s>' % (f, blk.group(1),
                  ', '.join(re.findall(r'li-settings:[\w-]+', a)), m.group(1)))
"
```

---

## Teil 3c — Abschnitt „Keine strukturellen CSS-Selektoren"

Einfügepunkt in `SKILL.md`: vor „### Schritt 6 — Fehlende CSS-Klassen direkt ins
Projekt-CSS schreiben".

### Keine strukturellen CSS-Selektoren über Section-Grenzen — Shopify wrappt jede Section

Shopify rendert **jede** Section in einen eigenen Container:

```html
<main class="main-wrapper">
  <div id="shopify-section-template--123__hero" class="shopify-section">
    <section class="section_hero">…</section>
  </div>
  …
</main>
```

Im Builder-HTML fehlt dieser Wrapper. Selektoren, die auf die Verwandtschaft
zwischen Sections bauen, funktionieren deshalb in der Vorschau, aber **nicht
live**:

```css
/* ❌ Greift live ins Leere: der Hero ist kein direktes Kind mehr */
.page-wrapper:has(.main-wrapper > .section_hero:first-child) .section_navbar { … }

/* ❌ Ebenso betroffen: Nachbar-Selektoren zwischen Sections */
.section_hero + .section_product { … }
.section_header-group + .main-wrapper > .section_hero { … }
```

Innerhalb einer Section ist alles erlaubt — die Grenze ist der Section-Rand.

**Lösung: die Section deklariert ihren Wunsch über CSS-Variablen**, statt dass
das CSS die DOM-Struktur abfragt. Das Basis-CSS liest die Variablen mit Fallback,
die Section setzt sie per `<style>` auf `:root` um:

```css
/* css/main.css — Fallback = Standardzustand */
.section_header-group { position: var(--header-position, sticky); top: 0;
  left: var(--header-inset, auto); right: var(--header-inset, auto); }
.section_navbar { background-color: var(--header-bg, var(--color--white));
  color: var(--header-fg, var(--color--black)); }
```

```html
<!-- _snippets/header-overlay.html — von jeder Section eingebunden,
     die den Header ueber sich legen will -->
<div li-snippet="header-overlay" class="header-overlay"><style>
  :root { --header-position: fixed; --header-inset: 0;
          --header-bg: transparent; --header-fg: #ffffff; }
</style></div>
```

Eigenschaften dieses Musters:

- **strukturunabhängig** — Builder und Shopify verhalten sich identisch
- **kein Liquid, keine Template-Listen** — kein `{% if template.name == 'index' %}`,
  das man bei jeder neuen Seite nachpflegen müsste
- **händlersteuerbar** — als `li-if="section.settings.header_overlay"` um die
  Snippet-Instanz plus Checkbox-Setting, pro Section-Instanz an/aus
- **kombinierbar** — zusätzlich eine winzige eigene Section (nur das Snippet, kein
  sichtbarer Inhalt) für Seiten, die den Zustand ohne passende Leitsection wollen
- **Zustandswechsel bleiben möglich** — eine Regel mit höherer Spezifität
  gewinnt weiter, z. B. `.section_navbar:has(.nav_component.is-scrolled)` für den
  soliden Header beim Scrollen

**Beim Testen im Browser beachten:** hat das Element eine `transition` auf der
geprüften Eigenschaft, liefert `getComputedStyle` den Zwischenwert — in einem
nicht sichtbaren Tab laufen Transitions gar nicht weiter und man liest dauerhaft
den Startwert. Vor der Messung `el.style.transition = 'none'` setzen, sonst
diagnostiziert man Phantom-Bugs.

---

## Teil 4 — Der neue Unterabschnitt in `references/liquiflow-docs.md`

Einfügepunkt: am Ende von „## Invariants (Never Break These)", vor
„## Cheat Sheet — All Attributes".

### Shopify schema/Liquid invariants (fail only at theme upload, not at lint)

- **Never put `li-for` and a text-binding `li-object="path"` on the same element** — the
  converter emits the `li-object` value as the for-expression → `For loops require an 'in'
  clause in "part.title"`. Move the text binding into an inner `<span>`. Attribute
  modifiers (`li-object:href`, `:src`, `:alt`) are fine alongside `li-for`.
  For `<option>` (no `<span>` allowed) put `li-for:inside` on the `<select>` instead.
- **At most ONE `link_list` setting per section** — `Invalid schema: setting link_list type
  can only be inserted once in the settings`. Use a `text` setting holding the linklist
  handle for any additional menu; `linklists[section.settings.x].links` works for both.
- **`range` defaults must sit on the step grid** — `(default - min) % step == 0`, otherwise
  `default must be a step in the range`. Figma pixel values often violate this.
- **`Section type '…' does not refer to an existing section file`** is a cascade, not a root
  cause: the section itself failed validation and was never written. Fix the section errors.
- **Shopify stops at the first error per section** — after each fix, re-convert; a second
  problem in the same file only surfaces once the first is gone.

---

---

### Zusätzlich: Builder-only invariants

### Builder-only invariants (break silently, no error at all)

- **`li-block` / `li-static-block` and `li-settings:*` are mutually exclusive on the same
  element** (Builder marks both red in the Inspector). Put `li-block` on a wrapper and
  `li-settings:*` on an inner element. `li-settings:*` on *children* of the block is fine.
- **Never let CSS depend on the DOM relationship between sections.** Shopify wraps every
  section in `<div class="shopify-section">`, so `.main-wrapper > .section_x:first-child`,
  `.section_a + .section_b` and similar work in the Builder preview but never live. Let the
  section declare intent through CSS custom properties on `:root` (via an embedded
  `<style>`) and read them with a fallback in the base CSS instead.

---

---

## Teil 5 — Pre-Flight-Audit als eigenständiges Skript

Das im Skill eingebettete Snippet liegt bei uns zusätzlich als
`preflight-audit.py` im Projekt und prüft 13 Regeln: die vier Shopify-Klassen
plus Blocknamen-Eindeutigkeit und -Länge (max. 25 Zeichen), `li-attribute` auf
dem `li-section`-Element, `li-if`/`li-unless` + `li-attribute` auf demselben
Element, Theme-Block-Struktur (ein Top-Level-Wrapper, nur `li-block` als direkte
Kinder), JSON-Validität aller Setting-Blöcke, CSS-Klassen ohne Regel in
`css/*.css`, `min-width`-Media-Queries und falsch platzierte `li-for:inside`.

Beide neuen Regelgruppen sind per Fehlerinjektion gegengeprüft: die Originalfehler
werden erkannt, im korrigierten Stand gibt es null Treffer.

Ein solches Skript als Teil des Skills (statt nur als Code-Block) wäre aus meiner
Sicht die wirksamste Ergänzung — es macht die Regeln ausführbar statt lesbar.
