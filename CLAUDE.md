# FieldOps — Technician Portal

Single-file web app (`fieldtech-app.html`) built for C Spire field technicians. It connects to a ServiceNow CSM instance to show assigned tickets, customer details, and equipment data. There is no build step — everything is inline HTML/CSS/JS in one file.

---

## Repository Layout

```
fieldtech-app.html       ← The entire app (HTML + CSS + JS, ~4800 lines)
meraki-proxy.js          ← Node.js CORS proxy for Cisco Catalyst Center API
package.json             ← { "start": "node meraki-proxy.js" }, Node ≥18
internet-db.json         ← Simulated ISP circuit data (fiber, cable, DSL, wireless)
firewall-db.json         ← Simulated firewall hardware data
webex-phones-db.json     ← Simulated Webex/VoIP phone data (models + name lists)
phones-db.json           ← Additional phone model reference
cspire_burst_cyan.png    ← App icon (C Spire burst logo)
```

`.gitignore` excludes `node_modules/`, `.env`, `App History/`, and seed scripts.

---

## Running Locally

1. Open `fieldtech-app.html` directly in a browser (no server required for most features)
2. For the Network screen (Catalyst Center data): `node meraki-proxy.js` (runs on port 3001)
3. In production the proxy is hosted on Railway: `https://fieldops-app-production-2ec3.up.railway.app`

---

## Architecture

### Single-file structure

All CSS is in a `<style>` block, all JS in a `<script>` block at the bottom of `<body>`. There are no imports, no bundler, no framework.

### Screens

Navigation is handled by `showScreen(name, btn)` which toggles `.active` on the relevant `#screen-*` div and calls the appropriate load function.

| Screen ID | Name | Load function |
|---|---|---|
| `#screen-list` | Tickets | `fetchTickets(filterState)` |
| `#screen-detail` | Ticket Detail | `fetchCaseDetail(number)` |
| `#screen-calendar` | Calendar | `loadCalendarScreen(forceRefresh)` |
| `#screen-customers` | Customers | `loadCustomersScreen(force)` |
| `#screen-customer-detail` | Customer Detail | `fetchCustomerDetail(sysId)` |
| `#screen-network` | Network Equipment | `loadNetworkScreen()` |
| `#screen-more` | More / Settings | (static) |
| `#screen-links` | Important Links | (static) |
| `#login-screen` | Login | (shown by default) |

Desktop uses a left sidebar nav (`.desktop-nav`). Mobile uses a bottom nav bar (`.bottom-nav` / `.bnav-btn`). The breakpoint is `800px` — see `isMobileView()`.

---

## ServiceNow Integration

```js
const SN = {
  instance: 'https://dev183548.service-now.com',
  get username()     { return sessionStorage.getItem('sn_username') || ''; },
  get password()     { return sessionStorage.getItem('sn_password') || ''; },
  get technicianId() { return sessionStorage.getItem('sn_user_sysid') || ''; }
};
```

Auth is Basic (`authHeader()` builds `Authorization: Basic base64(user:pass)`). Credentials are stored in `sessionStorage` only — never localStorage. The table used is `sn_customerservice_case` (CSM Cases, not incidents).

Session lifecycle:
1. Login → `attemptLogin()` → stores creds + user info in sessionStorage → `startSession()`
2. First load shows a disclaimer modal; `dismissDisclaimer()` proceeds to `fetchTickets()`
3. Force refresh: `forceAppRefresh()` clears `cachedAssignedTickets` and re-fetches, then navigates to the Tickets tab
4. Logout: `logout()` clears sessionStorage and reloads the page

---

## Key State Objects

```js
// Calendar
let _cal = {
  year: null,       // current display year (int)
  month: null,      // current display month (0-11)
  tickets: null,    // array of SN case objects for the month, or null = needs fetch
  selectedDay: null // int (1-31) of the currently highlighted day, or null
};

// Calendar date picker (the mini month widget in the header)
const _picker = { year: null, month: null };

// Tickets
let cachedAssignedTickets = null;  // all assigned open tickets, used for search

// Customers
let _custAccounts  = [];
let _custSortField = 'name';
let _custSortAsc   = true;
let _custLoaded    = false;

// Network
let _networkCache = null;
let _networkView  = 'list'; // 'list' | 'topology'

// Notifications
let _notifs         = [];        // array of notification objects
let _notifSeen      = new Set(); // ticket numbers already shown
let _notifLastCheck = null;      // ISO timestamp of last poll
let _notifPollTimer = null;      // setInterval handle

// Tickets closed this browser session (shown as resolved without re-fetch)
const _closedThisSession = new Set();
```

---

## Calendar — Critical Details

The calendar has two views:
- **Desktop** (≥800px): `renderCalendarGrid()` — a classic month grid with ticket chips
- **Mobile** (<800px): `renderCalendarAgenda()` — a scrollable list of every day in the month

`renderCalendar()` checks `isMobileView()` and dispatches to the right renderer.

### pickerPickDay — ordering matters

`closeCalDayPanel()` **sets `_cal.selectedDay = null`**. The picker must call it *before* setting `_cal.selectedDay`, not after:

```js
function pickerPickDay(year, month, day) {
  const d = new Date(year, month, day);
  const sameMonth = (d.getFullYear() === _cal.year && d.getMonth() === _cal.month);

  closeCalDayPanel();        // ← nulls _cal.selectedDay — MUST be first
  closeCalPicker();

  _cal.year        = d.getFullYear();
  _cal.month       = d.getMonth();
  _cal.selectedDay = d.getDate();
  if (!sameMonth) _cal.tickets = null;  // only refetch on month change

  loadCalendarScreen();
}
```

### Agenda scroll

`renderCalendarAgenda()` always renders **all days** in the month (empty days show "No tickets assigned"). After setting `innerHTML`, scroll uses double-`requestAnimationFrame` + `scrollIntoView` to land on the selected day (or today if no selection):

```js
requestAnimationFrame(() => requestAnimationFrame(() => {
  const el = grid.querySelector(`.cal-agenda-day[data-date="${scrollTarget}"]`);
  if (el) el.scrollIntoView({ block: 'start' });
}));
```

`#cal-grid` has `overflow-y: auto` and is the scroll container. Its parent `.cal-body-wrap` has `overflow: hidden`.

### Date strings

`calDateStr(d)` returns `"YYYY-MM-DD"` in local time. ServiceNow internal dates are `"YYYY-MM-DD HH:MM:SS"` UTC — always convert with `.replace(' ', 'T') + 'Z'` before passing to `new Date()`.

---

## Mock / Simulated Data

Several sections of the ticket detail screen are populated from local JSON databases seeded by the ticket's `number` field (used as a deterministic hash seed). Nothing is fetched from a real API for these sections.

| Section | Source | Notes |
|---|---|---|
| Internet | `internet-db.json` | Primary (fiber) + secondary (cable/DSL/wireless) circuits |
| Firewall | `firewall-db.json` | Firewall model, serial, uptime, interface IPs |
| Voice/VoIP | `webex-phones-db.json` | Webex Calling phones, extension list |
| Service Order | `_SO_CATALOG` (inline JS) | Install/repair service order items |

The `_hash(str)` function produces a stable integer from a ticket number, used to deterministically pick items from each database so the same ticket always shows the same equipment.

---

## CSS Architecture

### Fonts (brand-compliant)
- `--sans`: `'Nunito'` — all expressive/marketing/UI text, headers
- `--body`: `'Source Sans 3'` — functional body copy, data-dense views
- `--mono`: `'IBM Plex Mono'` — ticket numbers, IPs, codes

### Themes

**Dark mode** (default): `:root { ... }` defines all CSS variables.

**C Spire Light mode**: `html[data-theme="cspire"] { ... }` overrides variables, then a large block of `html[data-theme="cspire"] .selector { ... }` rules handle elements that hardcode rgba/hex values.

Toggle is stored in `localStorage` key `ft_theme`. Applied via `document.documentElement.setAttribute('data-theme', ...)`.

### C Spire Brand Palette (digital)

| Token | Hex | Role |
|---|---|---|
| C Spire Blue | `#00c0f3` | Primary — `--accent` in both themes |
| Steel Blue | `#0f3d58` | Secondary — `--accent2` in light mode |
| Onyx Black | `#131e29` | Secondary — `--bg`/`--surface` in dark mode |
| Magnetic Purple | `#884d9d` | Tertiary — consumer only |
| Quantum Violet | `#543161` | Tertiary — `--violet` |
| Kinetic Orange | `#FF6720` | CTAs, buttons, highlights — `--accent2` in dark mode |
| Cool Grey | `#85A7CA` | Supporting — `--text-dim` in dark mode |
| Nano Grey | `#EDF1F7` | Supporting — `--text` in dark mode |
| C Spire Glow | `#B9DEF3` | Supporting — `--bg` in light mode |

### Light mode gradient system (as of latest commits)

**Headers** (topbar, detail-topbar, list-header, stat-strip, filter-tabs, section-title, cust-banner-head, dev-section-hd, cal-month-nav, cal-dow-row):
```css
linear-gradient(90deg, rgba(15,61,88,0.88) 0%, rgba(0,120,180,0.72) 50%, rgba(0,192,243,0.85) 100%)
/* Steel Blue → mid-blue → C Spire Blue */
```

**Containers** (ticket-inner, device-card, stat-chip, net-summary):
```css
linear-gradient(155deg, rgba(0,192,243,0.42) 0%, rgba(0,152,220,0.22) 55%, rgba(15,61,88,0.08) 100%)
/* C Spire Blue → fading to Steel, diagonal */
```

**Pills** in light mode all have a per-type gradient fill + `1.5px` solid border + dark text color. The rule block lives right after the `html[data-theme="cspire"]` variable block.

**Text-shadow outline**: All accent-blue (`#00c0f3`) text elements in light mode get `text-shadow: 0 0 1px rgba(0,0,0,0.5), 0 1px 3px rgba(0,0,0,0.18)` for legibility on the light surface.

---

## Pill & Badge Classes

```
Priority:  pill-critical  pill-high  pill-medium  pill-low
State:     pill-open  pill-progress  pill-resolved  pill-pending  pill-enroute
Type:      type-badge repair | installation | service-call
```

`PRIORITY_MAP` and `STATE_MAP` (both keyed by SN integer value AND display string) live around line 2272.

---

## Network Screen

Pulls live data from Cisco Catalyst Center via `catalystGet(path)` → the proxy at `CATALYST.base`. Two views:

- **List view**: `renderNetworkList(data)` — device cards grouped by type
- **Topology view**: Canvas-drawn network diagram, `drawTopology(data)`

`_networkCache` prevents re-fetching on tab switch. State: `_networkView = 'list' | 'topology'`.

---

## Notifications

`startNotifPolling()` fires on `dismissDisclaimer()`. Polls every 60 seconds via `checkNewNotifs()`. Shows a badge on the bell icon. Notification panel is a dropdown anchored to the bell. `_notifSeen` prevents re-showing already-displayed tickets.

---

## Important Patterns

- **No framework, no build**: pure DOM manipulation. `escHtml(str)` must be used on all user/API data inserted into innerHTML.
- **`isMobileView()`**: `window.innerWidth < 800 || document.documentElement.hasAttribute('data-mobile-preview')`. The `data-mobile-preview` attribute enables mobile layout on desktop for dev/testing.
- **ServiceNow dates**: always internal format `"YYYY-MM-DD HH:MM:SS"` UTC. Use `parseSNDate(str)` or `.replace(' ','T')+'Z'` before `new Date()`.
- **Detail screen sections** (Internet, Firewall, Voice, Service Order) are conditionally shown/hidden based on ticket type (`getCaseType(inc)`).
- **Draft notes**: `saveDraft()` / `restoreDraft(sysId)` persist the update textarea to `localStorage` keyed by ticket sys_id.
- **`_closedThisSession`**: a Set of ticket numbers closed in this browser session. `renderTickets` and detail view check this to show closed state without waiting for a re-fetch.

---

## Active Development Notes

- The `/cspire-brand` Claude Code slash command (`~/.claude/commands/cspire-brand.md`) contains the full C Spire Brand Guidelines — invoke it when making any design/copy/color decisions.
- Light mode is the actively refined theme; dark mode is considered stable.
- The calendar picker scroll has had several iterations — the current implementation (double-rAF + scrollIntoView) is the stable solution. Do not revert to `offsetTop` or single-`setTimeout` approaches.
- Mock data sections (Internet, Firewall, Voice) intentionally use local JSON rather than live APIs — this is by design for demo/training use.
