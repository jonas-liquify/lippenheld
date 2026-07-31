# Lippenheld — Theme-Übergabe

Das komplette Theme ist aus dem Figma-Design
(`-EXTERN- Lippenheld – Review`, Node `10740:13608`) neu aufgebaut.
Das Blueprint-Starter-Theme ist vollständig ersetzt.

**Stand:** 20 Seiten · 45 Sections · 3 Snippets · 2 Layouts · 1 CSS-Datei

---

## 1. Designsystem (`css/main.css`)

Alle Werte sind aus Figma gezogen (`get_variable_defs` + `get_design_context`),
nicht geschätzt.

### Farben
| Token | Wert | Einsatz |
|---|---|---|
| `--color--black` | `#26261f` | Text, Primary-Button, dunkle Sections |
| `--color--white` | `#ffffff` | Canvas |
| `--color--paper` | `#f7f7f7` | helle Flächen (FAQ, USP, Trustpilot, Suche) |
| `--color--card` | `#efefee` | Produktbild-Hintergrund |
| `--color--olive` | `#afbaab` | Footer, Bildraster, Vorher/Nachher |
| `--color--ocean` | `#abbaba` | Split-Accordion, Inhaltsstoffe, About-Karten |
| `--color--sand` | `#e7ded2` | Produktvorteile |
| `--color--dark-green` | `#232e20` | Hero-Fallback |
| `--color--red` | `#450202` | USP-Ticker-Lippen, Sale-Tag |

### Typografie
| Rolle | Font | Desktop | Mobil |
|---|---|---|---|
| H1 | Cormorant Infant 600 | 28px / lh 1.11 / ls 0.1em | 22px |
| H2 | Cormorant Infant 600 | 26px / lh 1.11 / ls 0.06em | 20px |
| H3 | Playfair 400 | 22px / lh 1.5 | 18px |
| Fließtext | Playfair 400 | 14px / lh 1.5 / ls 0.03em | 13px |
| UI-Versalien | Outfit 500 | 12px / ls 0.11em | 11px |
| Produkttitel | Outfit 400 | 14px / ls 0.12em uppercase | 14px |
| Subline (Bogen) | Outfit 500 | 9px / ls 0.16em | — |

Fonts werden im Layout per Google-Fonts-`<link>` geladen.
**Campton** (kommerziell) ist wie abgestimmt durch **Outfit** ersetzt — das Design
nutzt im Hero an derselben Stelle bereits Outfit Medium 8.7px.

### Raster
`--side: 60px` (Tablet 40, Mobil 20) · Container 1320 / 1000 / 720 px ·
`--section-padding: 80px`.
**Breakpoints ausschließlich `max-width` in px:** 991 / 767 / 479. Keine einzige
`min-width`-Query im Projekt.

---

## 2. Section-Baukasten

Jede Section hat dieselben Grundregler im Theme-Editor:

| Gruppe | Setting | Werte |
|---|---|---|
| Abstände | `padding_top` / `padding_bottom` | 0–200px, Schritt 4 |
| Abstände | `padding_mobile` | Kein / Klein / Mittel / Groß |
| Darstellung | `color_scheme` | Weiß · Papier · Olive · Ocean · Sand · Schwarz · Dunkelgrün |
| Darstellung | `content_width` | Schmal · Mittel · Breit · Randlos |
| Darstellung | `content_align` | Links · Zentriert · Rechts |
| Layout | `columns` | wo ein Raster existiert (Produkte, Kacheln, Icons, Artikel …) |
| Layout | `media_position` | bei Split-Sections: Bild links / rechts |

**So funktioniert es technisch:** Die Settings hängen als `li-attribute:class` und
`li-attribute:style` auf dem inneren `.padding-global`-Div — nie auf dem
`li-section`-Element (Liquiflow-Regel). Das Farbschema setzt die Variablen
`--section-bg/-fg/-muted/-border/-btn-*` um, aus denen sich Text, Rahmen, Buttons
und Flächen speisen. Ein neues Schema kostet dadurch genau einen CSS-Block.

Die **Mobil-Abstände sind klassenbasiert** (`is-mpad-*`), nicht inline — nur so
schlagen sie den Inline-Style der Desktop-Settings zuverlässig.

Jeder Default im JSON ist als CSS-Default gespiegelt. Deshalb sieht die
Builder-Vorschau genauso aus wie die Live-Seite, obwohl `{{ … }}` dort nicht
ausgewertet wird.

---

## 3. Figma → Theme

| Figma-Frame | Section(s) |
|---|---|
| Startpage Hero `10526:6203` | `Hero` |
| `10526:6242` | `Featured Products` |
| `10526:6302` | `Image Grid` |
| Reviews `10526:6320` | `Section Header` + `Video Slider` + `Stats` |
| `10526:6446` | `Split Accordion` |
| `10526:6482` | `Quote` |
| Trusted `10526:6495` | `Before After` |
| Trustpilot `10526:6557` | `Trustpilot` |
| `10526:6558` | `Story` |
| Social Media `10526:6604` | `Social Media` |
| Footer `10526:6605` | `USP Ticker` + `Footer` |
| Product v2 `10526:7937` | `Product Header` |
| `10526:8189` | `USP Icons` |
| `10526:8206` | `Ingredients` |
| `10526:8246` | `Product Benefits` |
| `10526:8273` | `FAQ` |
| Blog `10526:8375` | `Blog-Articles` (+ `Blog posts` für die Startseite) |
| Blogdetail `10526:8499` | `Article Content` |
| Desktop-6 `10526:8624` | `Form` (Glas-Card über Bild) |
| About `10562:21891` | `Expanding Cards` |
| Erfahrungen `10526:9507` | `Review Wall` |
| Search `10526:8713` | Such-Overlay im `Header` |
| Basket-Drawer `10526:7118` | Mini-Cart im `Header` |

### Seiten
Bestehend neu bespielt: `index`, `products/product`, `collections/collection`,
`list-collections`, `cart`, `blogs/blog`, `blog-posts/blog-article`,
`others/search-page`, `others/404-page`, `others/password-page`, `gift-card`,
`pages/page`, `pages/contact`, `pages/thank-you`.

Neu angelegt: `pages/newsletter`, `pages/faq`, `pages/wirkung`,
`pages/erfahrungen`, `pages/about-us`, `pages/influencer`.

Alle `pages/*.html` tragen **kein** `li-page` — Ausnahme ist
`pages/page.html` (`li-page="page"`, das Default-Template). So registriert der
Converter sie korrekt als `templates/page.<name>.json`.

---

## 4. Header-Verhalten

Der Header ist **ohne Liquid** gelöst, damit Builder-Vorschau und Live-Seite
identisch sind:

- Startet eine Seite mit einer `Hero`-Section, wird der Header über
  `.page-wrapper:has(.main-wrapper > .section_hero:first-child)` automatisch
  fixiert und transparent mit weißer Schrift.
- Auf allen anderen Seiten ist er klebend, weiß und mit Hairline.
- Beim Scrollen (>40px) setzt Alpine `is-scrolled` und der Header wird in jedem
  Fall solide.
- Mobil: Burger + Suche links, Marke zentriert, Konto + Warenkorb rechts —
  wie im Figma-Mobile-Frame.

---

## 5. Was noch Platzhalter ist

1. **Alle Bilder** — jedes Bild ist `images/placeholder.svg` mit dem exakten
   `aspect-ratio` aus Figma und der Markenfarbe als Container-Hintergrund. Beim
   Austausch bleibt das Layout stabil. Jedes Bild hängt an einem
   `li-settings:image`-Setting, ist also im Theme-Editor tauschbar.
2. **USP-Icons** (`USP Icons`), **Siegel** auf der Produktseite und die
   **Social-Icons** im Footer sind ebenfalls Image-Settings — dort gehören die
   Strichzeichnungen aus dem Figma hinein.
3. **Trustpilot** ist statisch nachgebaut (Score, Sterne, Karten als Blöcke).
   Für Live-Bewertungen später das Trustpilot-Widget in die Section hängen.
4. **Texte** sind 1:1 aus dem Figma übernommen und alle über Settings editierbar.

---

## 6. Bekannte Punkte

- **Lint:** Der Builder-Linter meldet `li-snippet:product` als „unbekanntes
  Attribut". Das ist ein False Positive — das Attribut ist in der
  Liquiflow-Doku dokumentiert und wurde bereits vom Starter-Theme so verwendet.
  Ebenso `MISSING_CONTENT_FOR_LAYOUT` auf `_sections/*.html`: Section-Dateien
  haben naturgemäß keinen Layout-Slot. **Fehler gibt es keine.**
- **`{{ content_for_header }}`** steht wie im Starter-Theme nicht im
  `<head>` — der Builder fügt es bei der Konvertierung selbst ein. Ich habe den
  Head des Starters unverändert übernommen und nur die Fonts ergänzt.
- **`pages/contact.html`** nutzt die Section `Contact` (echtes Kontaktformular
  mit Nachrichtenfeld, `li-form="contact"`) statt der Glas-Card aus dem Figma —
  die Figma-Variante ist ein Newsletter-Formular (`li-form="customer"`) und
  liegt unverändert auf `pages/newsletter.html`. Wenn du die Kontaktseite exakt
  wie im Figma willst: `Contact` durch `Form` ersetzen.
- **`_sections/Featured collections.html`** und **`Image with Text.html`** aus
  dem Starter wurden gelöscht (im Lippenheld-Design nicht vorhanden).

---

## 7. Präzisions-Nachlauf (zweiter Durchgang)

Beim ersten Aufbau war der Figma-MCP nur über einen HTTP-Umweg erreichbar, deshalb
lagen für einige Sections zunächst nur Screenshot-Schätzungen vor. Diese Werte
sind inzwischen aus `get_design_context` nachgezogen und korrigiert — **38 Werte**
insgesamt:

| Bereich | vorher (geschätzt) | jetzt (Figma) |
|---|---|---|
| Kennzahl „94%" | 64px | **94px** (Label 14 → 16px) |
| Blog-Kartenbild | 3:2 | **434.667 : 361** (= 1.204) |
| Blog-Grid-Abstand | 40 / 24px | **60 / 8px** |
| Blog-Anriss / Tag | 14 / 9px | **12 / 8px** |
| Trustpilot-Karte | 276px, Titel 16px | **356px, Titel 22px** |
| Trustpilot-Text | Playfair 14px | **PT Serif Caption 14px / lh 1.66** |
| Trustpilot-Autor | Outfit 12px | **PT Serif Caption 10px / ls 0.25em** |
| Video-Kachel | 239:397, Abstand 4px | **332:553, Abstand 8px** |
| Vorher/Nachher | 328px-Kacheln, 328:248 | **Intro 300:451, Paar 333:451** |
| Review-Wall-Kacheln | 4px Abstand | **8px**, Video 327:553, Paar 324:276 |
| Formular-Card | 368px, Blur 6px | **407px, Blur 11.2px** |
| Aufklapp-Karten | 392px hoch, Padding 24px | **549px hoch, Padding 40px** |
| Kartentitel | 16px | **22px / lh 1.25** |
| Suchfeld / Eingabe | 592px / 14px | **832px / 16px** |
| Such-Tags | ls 0.11em | **ls 0.19em** |
| Mini-Cart | Titel 22px, Labels 12px | **Titel 20px, Labels 10px, Bild 95px** |

Zusätzlich im ersten Durchgang schon korrigiert: Desktop-H1 von 32 auf **28px**
(Figma-Wert) und die komplette Mobil-Typografie aus dem Mobile-Frame
(H1 22px, H2 20px, Body 13px, UI 11px).

**Hinweis zum Figma-MCP:** Das registrierte `mcp__Figma__*`-Tool antwortete in
dieser Session durchgehend mit „enable Dev Mode MCP Server", obwohl der Server
auf Port 3845 lief. Ein Neustart der App repariert die Client-Verbindung.
Als Umweg funktioniert JSON-RPC direkt gegen `http://127.0.0.1:3845/mcp`
(`initialize` → `mcp-session-id` aus den Headern → `tools/call`).

---

## 8. Interaktionen & Mobil-Abgleich (dritter Durchgang)

### Gebaut
- **Slider-Navigation** für `Video Slider`, `Before After` und `Trustpilot`:
  runde Pfeil-Buttons wie im Figma, per Section-Script an den Scroll-Container
  gebunden. Die Pfeile blenden sich automatisch aus, wenn nichts zu scrollen ist
  (bei nur einem Block also unsichtbar — korrekt). Trustpilot nutzt die dunkle
  Variante, die beiden anderen die weiße, entsprechend dem Design.
  Ein gemeinsamer `window.__liSlider` wird nur einmal pro Seite angelegt, jede
  Section initialisiert nur ihren eigenen Track.
- **Inhaltsstoff-Liste ist klickbar**: Klick auf einen Eintrag schaltet Bild
  (Spalte 2) und Wirkstoff-Text (Spalte 3) um, der aktive Eintrag wird
  hervorgehoben. Die Panes liegen im DOM im jeweiligen Theme-Block und werden per
  CSS in die richtigen Grid-Spalten positioniert (31.25% / 68.75%) — so bleibt
  das Block-Modell intakt und Händler können Inhaltsstoffe frei hinzufügen.
- **PDP-Galerie**: Klick oder Enter auf ein Thumbnail tauscht das Hauptbild
  (volle Auflösung über `data-full`), das aktive Thumbnail wird markiert.

### Mobil-Abgleich Produktseite & Warenkorb
Zwei echte Abweichungen gefunden und behoben:

1. **Reihenfolge auf der Produktseite.** Im Figma-Mobile folgt die Kaufspalte
   direkt auf die Galerie; die Redaktionsblöcke kommen danach. Bei mir lagen sie
   dazwischen und haben den „In den Warenkorb"-Button rund 1.000px nach unten
   geschoben. Gelöst über `display: contents` auf der Medienspalte plus `order`
   — jetzt: Galerie (113px) → Kaufspalte (533px) → Redaktion (1.761px).
2. **Galeriebild.** Figma-Mobile ist 375 × 400, nicht quadratisch. Korrigiert.

Der **mobile Warenkorb** ist im Figma identisch mit dem Mini-Cart-Drawer über die
volle Breite (375px, 20px Innenabstand, 95px Produktbild) — das deckt die
bestehende Umsetzung bereits ab, hier war nichts zu ändern.

### Bewusste Abweichung
Das Figma zeigt auf der mobilen Produktseite **keine Thumbnails** unter dem
Galeriebild. Ich habe sie trotzdem drin gelassen: ohne sie gäbe es auf Mobil
keine Möglichkeit mehr, zwischen den Produktbildern zu wechseln. Wenn du es
strikt wie im Design willst, reicht eine Regel:
`@media (max-width: 767px) { .product-header_thumbs { display: none; } }` —
dann brauchst du aber eine Swipe-Galerie als Ersatz.

### Was danach noch offen ist
- **Account-Templates** (`login`, `register`, `account`, `addresses`, `order`,
  `reset_password`, `activate_account`) fehlen komplett. Der Header verlinkt auf
  `routes.account_login_url`, der Login-Flow läuft also ins Leere. Im Figma nicht
  designt — müsste aus dem Designsystem entstehen.
- **Shopify-Presets**: Jede Section bringt genau einen Template-Block mit. Ob der
  Converter daraus ein `presets`-Default erzeugt (Händler zieht „Stats" rein und
  bekommt drei Kennzahlen) oder bei null Blöcken landet, ist ungeprüft — das
  zeigt sich erst am konvertierten Theme.
- **Weitere Mobile-Frames**: Blog, Blogdetail und die Content-Seiten sind mobil
  nur über die gemeinsamen Breakpoint-Regeln abgedeckt, nicht Frame für Frame
  gegen Figma gelegt.

---

## 9. Shopify-Konvertierung: behobene Validation-Fehler

Der erste Upload hat neun Fehler gemeldet. Alle gehen auf **drei** Ursachen
zurück, die vierte Meldung war ein Folgefehler. Alle sind behoben.

### 1. `li-for` + textbindendes `li-object` auf demselben Element
```
Liquid syntax error (line 8): For loops require an 'in' clause in "part.title"
```
Der Converter nimmt den `li-object`-Wert als For-Ausdruck. Entscheidend ist die
**Form**: `li-object="pfad"` (Textausgabe) bricht, `li-object:href` / `:src` /
`:alt` nicht. Betroffen waren Pagination (`Blog-Articles`, `Search`,
`Collection Products`), das Sortier-Dropdown und die Suchvorschläge in `Header`
und `predictive_search` — insgesamt 8 Stellen.

Behoben: Textbindung in ein inneres `<span>` verschoben. Beim `<option>` geht das
nicht (ungültiges HTML), dort sitzt jetzt `li-for:inside` auf dem `<select>`.

### 2. Resource-Picker mehrfach pro Section
```
Invalid schema: setting link_list type can only be inserted once in the settings.
Invalid schema: setting collection type can only be inserted once in the settings.
```
Die Regel gilt für **alle** Picker-Typen: `link_list`, `collection`, `product`,
`blog`, `article`, `page`.

- **`Header`** (Menü links + rechts) und **`Footer`** (Spalten + Rechtliches)
  hatten je zwei `link_list`-Picker. Behoben: erstes Menü bleibt Picker, das
  zweite ist ein `text`-Setting mit dem Linklisten-Handle. Die Liquid-Referenz
  `linklists[section.settings.x].links` ist identisch geblieben.
- **`Header`** hatte außerdem zwei `collection`-Settings — eines im Mini-Cart-
  Upsell, eines im eingebetteten `predictive_search`. Weil die Suche inline im
  Header liegt, landen beide in **einem** Schema. Behoben: der Upsell ist jetzt
  ein `product`-Setting (`upsell_product`) — semantisch richtig, es ist ein
  einzelnes Produkt — und wird deterministisch über
  `section.settings.upsell_product.…` referenziert. `product` und `collection`
  sind verschiedene Typen und dürfen nebeneinander je einmal auftreten.

**Für dich heißt das:** in Shopify eintragen — Header „Menü rechts" z. B.
`main-menu-right`, Footer „Rechtliches" z. B. `legal`, und im Header unter
„Warenkorb" das Upsell-Produkt wählen.

### 2b. `"default": ""` ist ungültig
```
Invalid schema: setting with id="legal_menu" default can't be blank
```
Ich hatte die beiden neuen text-Settings mit `"default": ""` angelegt. Shopify
lehnt einen leeren String ab — der `default`-Key muss **ganz weg**, dann ist das
Feld im Editor einfach leer. Behoben.

### 3. `range`-Default nicht auf dem Step-Raster
```
Invalid schema: setting with id="min_height" default must be a step in the range
```
`Form`: `min 300, step 20, default 637` → `(637−300) % 20 = 17`. Shopify verlangt
`(default − min) % step == 0`. Behoben: 640. Alle anderen 40+ range-Settings
wurden geprüft und sind korrekt.

### 4. `Section type '…' does not refer to an existing section file`
Folgefehler: `header.liquid`/`footer.liquid` hatten die Validation nicht
bestanden und wurden nie geschrieben, die Section-Gruppen verwiesen deshalb ins
Leere. Erledigt sich mit 1–3.

### Pre-Flight-Audit
Diese drei Klassen bestehen den Builder-Lint **fehlerfrei** — der Lint prüft
`li-*`-Syntax, nicht das Shopify-Schema. Deshalb liegt jetzt
[`preflight-audit.py`](preflight-audit.py) im Projekt. Vor jeder Konvertierung:

```bash
cd "/Users/jonas/Ablage/Liquiflow Projects/lippenheld-20" && python3 preflight-audit.py
```

Es prüft 12 Regeln: die vier Shopify-Klassen (For-Loop-Kollision, Picker-Dopplung,
leerer Default, range-Step) plus Blocknamen-Eindeutigkeit und -Länge,
`li-attribute` auf `li-section`, `li-if` + `li-attribute`, Theme-Block-Struktur,
JSON-Validität, CSS-Klassen ohne Regel, `min-width`-Queries und falsch platzierte
`li-for:inside`.

**Shopify bricht pro Section beim ersten Fehler ab.** Genau das ist hier passiert:
Runde 1 meldete neun Fehler, nach dem Fix kamen in Runde 2 zwei weitere zum
Vorschein, die vorher verdeckt waren. Also nach jeder Korrekturrunde erneut
konvertieren, bis der Log leer bleibt.

Die vier Fehlerklassen sind zusätzlich im `liquiflow-builder`-Skill verankert
(neuer Abschnitt „Shopify-Validation" plus Invarianten in
`references/liquiflow-docs.md`), damit sie beim nächsten Projekt nicht wieder
auftreten.

---

## 10. Vor der Shopify-Konvertierung

1. Bilder in den Sections austauschen (Theme-Editor oder direkt die
   `li-settings:image`-Platzhalter).
2. Linklisten in Shopify anlegen und im Header/Footer zuweisen:
   Header links, Header rechts, Footer-Spalten, Rechtliches.
   (Nur `main-menu` und `footer` sind als Defaults gesetzt — alle anderen
   Link-List-Settings bewusst ohne Default, sonst schlägt die Shopify-Validation
   fehl.)
3. Im Publish-Dialog die Vorschau prüfen und im Zweifel **„Alle Dateien"**
   statt „nur Änderungen" wählen.

---

## 11. Vorschau

Für einen schnellen Blick ohne Builder:

```bash
cd "/Users/jonas/Ablage/Liquiflow Projects/lippenheld-20" && python3 -m http.server 8777
```

Danach `http://127.0.0.1:8777/index.html` öffnen. `li-for`-Schleifen zeigen dort
je ein Template-Element und `li-if`-Zweige alle gleichzeitig — das ist normal und
löst sich in Shopify auf.
