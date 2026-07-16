# inventory-monitor

A downloadable, run-it-on-your-own-computer **restock monitor** for
trading-card products — ONE PIECE TCG, Pokémon (including the current
"Pitch Black" / latest sets), or honestly anything with a product URL.

It watches the pages you point it at, detects the instant something flips from
**sold out → in stock** (or changes price), and alerts you across as many
channels as you want: a terminal banner, a native desktop popup, a terminal
bell, a **Discord webhook** (great for phone alerts), and optionally
**auto-opening the product page in your browser** so you can check out in
seconds.

It also keeps a local **guest-checkout quick-fill** block (your shipping
address + contact info) that you can copy to your clipboard with one command,
so filling a guest-checkout form is a couple of pastes.

---

## What it does — and what it deliberately doesn't

**It does:**
- Poll product/collection pages on a polite, jittered interval.
- Understand Shopify stores natively (exact per-variant availability), plus
  generic stores via a CSS-selector or JSON-field rule you provide.
- Remember state between runs so you don't get re-spammed on restart.
- Alert fast, on the channels you choose.
- Store a **non-sensitive** shipping/contact profile for quick guest checkout.

**It does NOT:**
- **Auto-purchase / auto-checkout.** It never submits a cart or completes an
  order. It tells *you* to go buy; you buy.
- **Store your card number, CVV, or account passwords.** There are no config
  fields for them, on purpose.

### Why no auto-checkout and no stored payment/login?

This isn't me being precious — there are two concrete reasons:

1. **It would put you at real risk.** A card number or account password sitting
   in plaintext in a script folder is exactly what gets drained if that folder
   is ever synced to the cloud, backed up, copied to another machine, or shared.
   Your browser already stores payment details behind OS-level encryption and
   fills them in for you — that's strictly safer than any text file this tool
   could write. Let it do that job.
2. **Auto-checkout bots get you banned.** Software that races real buyers to
   complete orders for scarce inventory violates essentially every major
   retailer's terms of service and anti-bot rules. When it's detected — and it
   increasingly is — the order is cancelled and the card/account can be
   blocked. You'd be spending effort to make yourself *less* likely to get the
   product.

The thing that actually wins limited drops is **being alerted first and
checking out quickly** — and that's exactly what this tool optimizes. The
quick-fill profile + `open_browser_on_restock` gets you onto the product page
with your shipping details one paste away, while your browser handles payment.

---

## Install

Requires **Python 3.9+**.

```bash
cd inventory-monitor
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

The two optional packages (`plyer` for desktop popups, `pyperclip` for
clipboard) are nice-to-haves — the tool runs fine without them and just prints
a note if a channel is unavailable.

## Configure

```bash
cp config.example.yaml config.yaml
```

Open `config.yaml` and:

1. Add your products under `watch:` (see **Watch targets** below).
2. (Optional) Fill in the `profile:` block with your shipping/contact info.
3. (Optional) Paste a `discord_webhook:` URL for phone alerts, and/or set
   `open_browser_on_restock: true`.

## Run

```bash
python run.py                 # start monitoring (default)
python run.py once            # check everything one time and exit
python run.py list            # show configured targets
python run.py profile show    # print your guest-checkout quick-fill block
python run.py profile copy    # copy that block to the clipboard
```

Leave `python run.py` running in a terminal. On a restock you'll get a big
green banner (plus whatever other channels you enabled). Press **Ctrl-C** to
stop.

---

## Watch targets

Each entry needs a `name` and a `url`. The `type` defaults to `auto`, which
picks the right method from the URL.

### 1. Shopify stores (easiest — a huge share of TCG shops)

Just paste the product or collection URL. No rule needed.

```yaml
- name: "ONE PIECE OP-11 Booster Box"
  url: "https://some-tcg-store.com/products/one-piece-op11-booster-box"
  type: auto        # reads <url>.json for exact per-variant availability

- name: "Pokemon new releases"
  url: "https://some-tcg-store.com/collections/pokemon"
  type: auto        # in stock if ANY product in the collection is buyable
```

How to tell it's Shopify: the URL has `/products/…` or `/collections/…`, and
visiting `<product-url>.json` returns product data.

### 2. Any store, via a CSS rule (`type: css`)

Tell it how the page reads when the item is buyable:

| `in_stock_when`    | Means "in stock when…"                          | Needs        |
|--------------------|-------------------------------------------------|--------------|
| `selector_present` | this CSS selector matches something             | `selector`   |
| `selector_absent`  | this CSS selector matches nothing               | `selector`   |
| `text_contains`    | the page text contains this string              | `match_text` |
| `text_absent`      | the page text does **not** contain this string  | `match_text` |

```yaml
- name: "Pokemon Pitch Black — Booster Box"
  url: "https://a-store.com/pokemon-pitch-black-booster-box"
  type: css
  in_stock_when: selector_present
  selector: "button.add-to-cart:not([disabled])"
  price_selector: ".price"     # optional, shown in the alert

- name: "ONE PIECE box (sold-out-text store)"
  url: "https://another-store.com/one-piece-box"
  type: css
  in_stock_when: text_absent
  match_text: "Sold Out"
```

**Finding a selector:** open the product page, right-click the Add-to-Cart
button → *Inspect*, and read its tag/class. Test your rule with
`python run.py once` before leaving it running.

### 3. A JSON API (`type: json`)

If a store has a product API, point at the field that indicates stock using a
dotted path (array indices are plain numbers):

```yaml
- name: "Pokemon Pitch Black — ETB"
  url: "https://a-store.com/api/products/pitch-black-etb"
  type: json
  availability_path: "data.product.inventory"   # bool, number, or string
  price_path: "data.product.price"
```

- A **boolean** uses its truth value.
- A **number** is in stock when `> 0`.
- A **string** is in stock when it matches `in_stock_values`
  (default: `true/instock/in_stock/available/1`).

---

## Being a good citizen

Scarce-product pages are under load; don't make it worse:

- Keep `poll_interval_seconds` sane (90s is a reasonable default). Hammering a
  site every second gets your IP rate-limited or blocked and doesn't help you.
- `per_domain_min_gap_seconds` and the random `jitter_seconds` keep you from
  bursting a single store.
- Check each store's terms; some publish an official stock API or Discord —
  prefer those when they exist.

## Troubleshooting

- **"still in stock" spam / no alert:** the tool only alerts on *changes*. Use
  `python run.py once` to see the current read for every target.
- **Desktop popups don't appear:** `pip install plyer`. On some Linux setups
  you also need a notification daemon; the terminal banner always works.
- **A CSS rule is always in/out of stock:** your `selector`/`match_text` is off.
  Inspect the page and adjust; re-test with `once`.
- **Discord alert missing:** confirm the webhook URL is correct and the channel
  still exists (the tool prints the HTTP status if it fails).

## Project layout

```
inventory-monitor/
├── run.py                  # launcher: python run.py
├── config.example.yaml     # copy to config.yaml
├── requirements.txt
└── monitor/
    ├── cli.py              # argument parsing / subcommands
    ├── runner.py           # the poll loop + change detection
    ├── checker.py          # HTTP session + polite per-domain pacing
    ├── notifier.py         # console / desktop / sound / Discord
    ├── profile.py          # guest-checkout quick-fill (non-sensitive)
    ├── state.py            # remembers last-seen stock across runs
    ├── config.py           # YAML -> typed config
    ├── models.py           # shared data types
    └── adapters/
        ├── shopify.py      # Shopify product + collection JSON
        └── generic.py      # CSS-selector and JSON-path adapters
```
