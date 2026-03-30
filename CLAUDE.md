# FieldOps — Technician Portal

Single-file web app (`fieldtech-app.html`) built for C Spire field technicians. It connects to a ServiceNow CSM instance to show assigned tickets, customer details, and equipment data. There is no build step — everything is inline HTML/CSS/JS in one file.

---

## Repository Layout

```
fieldtech-app.html       ← The entire app (HTML + CSS + JS, ~4900 lines)
meraki-proxy.js          ← Node.js CORS proxy for Cisco Catalyst Center API
package.json             ← { "start": "node meraki-proxy.js" }, Node ≥18
internet-db.json         ← Simulated ISP circuit data (fiber, cable, DSL, wireless)
firewall-db.json         ← Simulated firewall hardware data
webex-phones-db.json     ← Simulated Webex/VoIP phone data (models + name lists)
phones-db.json           ← Additional phone model reference
cspire_burst_cyan.png    ← App icon (C Spire burst logo)
seed_servicenow.py       ← Seeds 12 customer accounts, locations, and contacts
seed_test_user.py        ← Creates test_fieldtech user and initial case set
seed_next_week.py        ← Creates 10 cases for the following work week (March 31 – April 4)
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

### Test credentials
- **Username**: `test_fieldtech` / **Password**: `TestFieldTech1!`
- Mirrors the roles and group memberships of `kkubiak`

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

`renderCalendarAgenda()` always renders **all days** in the month (empty days show "No tickets assigned"). After setting `innerHTML`, scroll uses double-`requestAnimationFrame` + `getBoundingClientRect` delta applied to `grid.scrollTop` to land on the selected day (or today if no selection). Do **not** revert to `scrollIntoView`, `offsetTop`, or single-`setTimeout` — these cause the entire iOS viewport to shift:

```js
requestAnimationFrame(() => requestAnimationFrame(() => {
  const el = grid.querySelector(`.cal-agenda-day[data-date="${scrollTarget}"]`);
  if (el) grid.scrollTop += el.getBoundingClientRect().top - grid.getBoundingClientRect().top;
}));
```

`#cal-grid` has `overflow-y: auto` and is the scroll container. Its parent `.cal-body-wrap` has `overflow: hidden`.

### Calendar topbar layout

The calendar topbar uses a **3-column flex layout** to keep the month/year label + picker widget truly centered regardless of the refresh button on the right:

```html
<div style="width:36px;flex-shrink:0;"></div>   <!-- spacer balances refresh btn -->
<div style="flex:1;display:flex;align-items:center;justify-content:center;">
  <span class="cal-month-label" ...>March 2026</span>
  <div class="cal-picker-wrap" style="margin-left:8px;">...</div>
</div>
<button class="icon-btn" ...>  <!-- refresh -->
```

Do not switch back to `position:absolute` on the label or move the picker to the right side — the picker dropdown clips against the screen edge when placed near the refresh button.

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
| Steel Blue | `#0f3d58` | Secondary |
| Onyx Black | `#131e29` | Secondary — `--bg`/`--surface` in dark mode |
| Magnetic Purple | `#884d9d` | Tertiary — consumer only |
| Quantum Violet | `#543161` | Tertiary — `--violet` |
| Kinetic Orange | `#FF6720` | CTAs, buttons, highlights — `--accent2` in dark mode |
| Cool Grey | `#85A7CA` | Supporting — calendar day-of-week header (light mode) |
| Nano Grey | `#EDF1F7` | Supporting |
| C Spire Glow | `#B9DEF3` | Supporting |

---

## iOS PWA / Safe Area

The app is configured as a full-screen iOS PWA:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0e1a2a">
```

Key safe-area rules:
- `.topbar` and `.detail-topbar`: `min-height` (not `height`), `padding-top: env(safe-area-inset-top)`
- `.bottom-nav`: `min-height`, `padding-bottom: env(safe-area-inset-bottom)`, `position: relative`
- `.bottom-nav::after`: fills the home indicator zone below the nav bar with the background color

Do not use `-webkit-fill-available` on `.app` height — it caused double-counting of the safe area inset in PWA mode.

---

## Visual Design System

### Depth & Dimension — Cards

All primary card containers use frosted glass + 3-layer box-shadow + left accent border:

```css
/* Dark mode pattern */
background: rgba(22,34,54,0.72);
backdrop-filter: blur(10px);
-webkit-backdrop-filter: blur(10px);
border: 1px solid rgba(255,255,255,0.1);
border-left: 3px solid var(--accent);
box-shadow:
  0 1px 3px rgba(0,0,0,0.5),
  0 4px 16px rgba(0,0,0,0.4),
  0 10px 30px rgba(0,0,0,0.2),
  inset 0 1px 0 rgba(255,255,255,0.08),
  inset 0 -1px 0 rgba(0,0,0,0.18);

/* Light mode pattern */
background: rgba(255,255,255,0.78);
backdrop-filter: blur(10px);
-webkit-backdrop-filter: blur(10px);
border: 1px solid rgba(0,192,243,0.22);
border-left: 3px solid var(--accent);
box-shadow:
  0 1px 3px rgba(0,0,0,0.08),
  0 4px 16px rgba(0,192,243,0.1),
  0 10px 28px rgba(122,85,152,0.07),
  inset 0 1px 0 rgba(255,255,255,0.95),
  inset 0 -1px 0 rgba(0,0,0,0.04);
```

Applies to: `.ticket-inner`, `.device-card`, `.cust-banner`, `.cust-card-inner`, `.cust-detail-banner`, `.net-summary`, `.stat-chip`.

All of these have `position: relative` and `overflow: hidden` set.

### Background Burst Orbs

`.app` has layered radial gradients creating ambient energy — C Spire Blue at top-right, Magnetic Purple at bottom-left, with a soft center glow. Light mode version is slightly more saturated:

```css
/* Dark mode */
.app { background:
  radial-gradient(circle at 82% 7%, rgba(0,192,243,0.17) 0%, transparent 42%),
  radial-gradient(circle at 14% 90%, rgba(136,77,157,0.15) 0%, transparent 40%),
  radial-gradient(circle at 50% 50%, rgba(0,192,243,0.05) 0%, transparent 55%); }

/* Light mode */
html[data-theme="cspire"] .app { background:
  radial-gradient(circle at 82% 7%, rgba(0,192,243,0.22) 0%, transparent 40%),
  radial-gradient(circle at 14% 90%, rgba(136,77,157,0.15) 0%, transparent 37%),
  radial-gradient(circle at 50% 50%, rgba(0,192,243,0.07) 0%, transparent 52%); }
```

### Pill / Badge styling

**Dark mode pills** have a colored border + 3-layer inset shadow for dimension:
```css
border: 1.5px solid rgba(<color>, 0.42);
box-shadow: 0 1px 4px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.07), inset 0 -1px 0 rgba(0,0,0,0.14);
```

**Light mode pills** use per-type linear gradient fills + 1.5px solid border + dark text color.

Priority severity pills (`pill-critical`, `pill-high`, `pill-medium`, `pill-low`) are intentionally **not shown** in the Calendar and Notification panel — state and type badges are sufficient context for field techs who are already assigned to the ticket. Severity pills still exist as CSS classes and may appear in other contexts (e.g. network device status).

### Light Mode — Headers

Topbar and detail-topbar use Consumer Hierarchy gradient (blue-dominant, soft purple tail):
```css
background: linear-gradient(90deg, #00c0f3 0%, #009dd6 55%, #7a5598 100%);
```

The topbar `*` selector sets all children to `color: #ffffff`. This cascades into the calendar picker dropdown — override explicitly with `!important` for any picker content that should be dark text.

### Light Mode — Text Colors

- **Account/case numbers** (`.ticket-id`, `.cust-bn-id`, `.cust-card-num`, `.cust-detail-banner-num`): `color: #ffffff` — solid white, no text-shadow outline
- **Orange note labels** (`[style*="--accent2"]`): `color: #ffffff !important` — solid white overrides the orange variable

### Calendar Day-of-Week Header (Light Mode)

Solid `#85A7CA` (Cool Grey) background, white text. Weekend cells (Sun/Sat) use `rgba(255,255,255,0.75)` and `opacity: 1` (the base dark style sets opacity for these; override it in light mode).

---

## Pill & Badge Classes

```
State:     pill-open  pill-progress  pill-resolved  pill-pending  pill-enroute
Priority:  pill-critical  pill-high  pill-medium  pill-low  (CSS exists; not shown in calendar/notifications)
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

Notification items show ticket number, time ago, company, and description. Priority pill is intentionally omitted.

---

## Important Patterns

- **No framework, no build**: pure DOM manipulation. `escHtml(str)` must be used on all user/API data inserted into innerHTML.
- **`isMobileView()`**: `window.innerWidth < 800 || document.documentElement.hasAttribute('data-mobile-preview')`. The `data-mobile-preview` attribute enables mobile layout on desktop for dev/testing.
- **ServiceNow dates**: always internal format `"YYYY-MM-DD HH:MM:SS"` UTC. Use `parseSNDate(str)` or `.replace(' ','T')+'Z'` before `new Date()`.
- **Detail screen sections** (Internet, Firewall, Voice, Service Order) are conditionally shown/hidden based on ticket type (`getCaseType(inc)`).
- **Draft notes**: `saveDraft()` / `restoreDraft(sysId)` persist the update textarea to `localStorage` keyed by ticket sys_id.
- **`_closedThisSession`**: a Set of ticket numbers closed in this browser session. `renderTickets` and detail view check this to show closed state without waiting for a re-fetch.
- **Seed scripts**: require `tzdata` pip package on Windows (`python -m pip install tzdata`). Use ASCII-only print statements — Windows terminal (cp1252) can't encode Unicode symbols like `✓` or `──`.

---

## Active Development Notes

- The `/cspire-brand` Claude Code slash command (`~/.claude/commands/cspire-brand.md`) contains the full C Spire Brand Guidelines — invoke it when making any design/copy/color decisions.
- Both themes are actively maintained. Dark mode is the default; light mode (C Spire branded) is the secondary theme.
- The calendar agenda scroll implementation (double-rAF + `getBoundingClientRect` delta) is the stable solution. Do not revert to `scrollIntoView`, `offsetTop`, or single-`setTimeout`.
- Mock data sections (Internet, Firewall, Voice) intentionally use local JSON rather than live APIs — this is by design for demo/training use.
- The `u_scheduled_start` custom field on `sn_customerservice_case` drives the calendar display for install/repair appointment times. Always populate this field when seeding tickets.
- `overflow: hidden` on card containers clips `::before`/`::after` pseudo-elements — useful for brand shape accents, but means z-index layering inside cards requires `position: relative` on the container and `z-index: -1` on pseudo-elements so they render behind content.
