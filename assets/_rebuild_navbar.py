# -*- coding: utf-8 -*-
from pathlib import Path
path = Path("/Users/jonas/Downloads/liquify-2-0.webflow/source/components/Navbar.component.js")
raw = path.read_text(encoding="utf-8")
start_mc = raw.find('<div class="nav_mini-cart">')
start_nb = raw.find('<div class="nav_menu-button w-nav-button"')
mini_cart = raw[start_mc:start_nb].rstrip()
# nav_account: from <div class="nav_account" to matching </div>
start_na = raw.find('<div class="nav_account"')
if start_na == -1:
    nav_account = '''<div class="nav_account" li-if="shop.customer_accounts_optional">
                    <a class="nav_shop-icon w-inline-block" li-attribute:href="{% if customer %}{{ routes.account_url }}{% else %}{{ routes.account_login_url }}{% endif %}" href="#">
                      <div class="icon-embed-xsmall w-embed">
                        <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewbox="0 0 24 24" fill="none" preserveaspectratio="xMidYMid meet" aria-hidden="true" role="img">
                          <mask id="mask0_2941_121306" style="mask-type:alpha" maskunits="userSpaceOnUse" x="0" y="0" width="24" height="24">
                            <rect width="24" height="24" fill="currentColor"></rect>
                          </mask>
                          <g mask="url(#mask0_2941_121306)">
                            <path d="M12 12C10.9 12 9.95833 11.6083 9.175 10.825C8.39167 10.0417 8 9.1 8 8C8 6.9 8.39167 5.95833 9.175 5.175C9.95833 4.39167 10.9 4 12 4C13.1 4 14.0417 4.39167 14.825 5.175C15.6083 5.95833 16 6.9 16 8C16 9.1 15.6083 10.0417 14.825 10.825C14.0417 11.6083 13.1 12 12 12ZM4 20V17.2C4 16.6333 4.14583 16.1125 4.4375 15.6375C4.72917 15.1625 5.11667 14.8 5.6 14.55C6.63333 14.0333 7.68333 13.6458 8.75 13.3875C9.81667 13.1292 10.9 13 12 13C13.1 13 14.1833 13.1292 15.25 13.3875C16.3167 13.6458 17.3667 14.0333 18.4 14.55C18.8833 14.8 19.2708 15.1625 19.5625 15.6375C19.8542 16.1125 20 16.6333 20 17.2V20H4ZM6 18H18V17.2C18 17.0167 17.9542 16.85 17.8625 16.7C17.7708 16.55 17.65 16.4333 17.5 16.35C16.6 15.9 15.6917 15.5625 14.775 15.3375C13.8583 15.1125 12.9333 15 12 15C11.0667 15 10.1417 15.1125 9.225 15.3375C8.30833 15.5625 7.4 15.9 6.5 16.35C6.35 16.4333 6.22917 16.55 6.1375 16.7C6.04583 16.85 6 17.0167 6 17.2V18ZM12 10C12.55 10 13.0208 9.80417 13.4125 9.4125C13.8042 9.02083 14 8.55 14 8C14 7.45 13.8042 6.97917 13.4125 6.5875C13.0208 6.19583 12.55 6 12 6C11.45 6 10.9792 6.19583 10.5875 6.5875C10.1958 6.97917 10 7.45 10 8C10 8.55 10.1958 9.02083 10.5875 9.4125C10.9792 9.80417 11.45 10 12 10Z" fill="currentColor"></path>
                          </g>
                        </svg>
                      </div>
                    </a>
                  </div>'''
else:
    depth = 0
    i = start_na
    end_na = None
    while i < len(raw):
        if raw.startswith("<div", i) and not raw.startswith("</div", i):
            depth += 1
            i = raw.find(">", i) + 1
            continue
        if raw.startswith("</div>", i):
            depth -= 1
            i = raw.find(">", i) + 1
            if depth == 0:
                end_na = i
                break
            continue
        i += 1
    nav_account = raw[start_na:end_na].strip()

def ind(s, n):
    pad = " " * n
    return "\n".join(pad + ln.lstrip() for ln in s.split("\n") if ln.strip())

tail = """
                </div>
              </div>
            </div>
          </div>
        </nav>
        <div class="nav_menu-button w-nav-button" aria-label="Menü">
          <div class="menu-icon">
            <div class="menu-icon_line-top"></div>
            <div class="menu-icon_line-middle">
              <div class="menu-icon_line-middle-inner"></div>
            </div>
            <div class="menu-icon_line-bottom"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="li-custom w-embed" li-settings:custom="Navigation">[{"type":"link_list","id":"menu","label":"Hauptmenü links","default":"main-menu"},{"type":"link_list","id":"menu_right","label":"Hauptmenü rechts (Über uns, Club …)","default":"main-menu"}]</div>
</div>
`"""

# Read prefix from embedded file start — full template through end of search closing divs
with open(Path(__file__).parent / "_navbar_prefix.txt", "r", encoding="utf-8") as f:
    prefix = f.read()

out = prefix.rstrip() + "\n" + ind(nav_account, 18) + "\n" + ind(mini_cart, 18) + tail
path.write_text(out, encoding="utf-8")
print("Wrote", path, "bytes", len(out))
