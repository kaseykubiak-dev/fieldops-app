# Delta — Field Operations Tech App

Single-file web app (`fieldtech-app.html`, ~6700+ lines) built for C Spire field technicians. Formerly known as FieldOps, now branded as **Delta**. It connects to a ServiceNow CSM instance to show assigned tickets, customer details, equipment data, and AI-powered customer intelligence via CX 360. There is no build step — everything is inline HTML/CSS/JS in one file.

---

## Repository Layout

```
fieldtech-app.html            <- The entire app (HTML + CSS + JS, ~6700+ lines)
meraki-proxy.js               <- Node.js CORS proxy for Cisco Catalyst Center API
package.json                  <- { "start": "node meraki-proxy.js" }, Node >=18
internet-db.json              <- Simulated ISP circuit data (fiber, cable, DSL, wireless)
firewall-db.json              <- Simulated firewall hardware data
webex-phones-db.json          <- Simulated Webex/VoIP phone data (models + name lists)
phones-db.json                <- Additional phone model reference
delta-logo-dark-v2.png        <- Delta logo, dark mode (cyan glow, transparent bg, 1536×1024)
delta-logo-light-v2.png       <- Delta logo, light mode (steel blue, transparent bg, 1536×1024)
delta-favicon-dark.png        <- Delta triangle icon for favicon (dark mode, transparent bg)
delta-logo-transparent.png    <- Legacy Delta logo (cyan on transparent, 1200×420)
delta-icon-transparent.png    <- Legacy Delta icon (cyan triangle, transparent, 520×520)
pulse-tile-dark.png           <- Pulse brand pattern tile, cyan on transparent (dark theme topbar overlay)
pulse-tile-light.png          <- Pulse brand pattern tile, white on transparent (light theme topbar overlay)
Patterns.pdf                  <- C Spire brand pattern reference sheet (C Burst, Pulse, Solid Stack)
cspire_burst_cyan.png         <- Legacy app icon (C Spire burst logo, unused)
seed_servicenow.py            <- Seeds 12 customer accounts, locations, and contacts
seed_test_user.py             <- Creates test_fieldtech user and initial case set
seed_next_week.py             <- Creates 10 cases for the following work week (March 31 - April 4)
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
| `#screen-cx360` | CX 360 | `cx360Send()` (mock AI chat) |
| `#screen-techtools` | Tech Tools | `initSafetyChecks()` + `initInventoryChecks()` + static tools |
| `#screen-more` | Settings | (static — Appearance, App, Account) |
| `#screen-links` | Important Links | (static) |
| `#login-screen` | Login | (shown by default) |

Desktop uses a top nav bar (`#desktop-topbar` / `.desktop-nav`). Mobile uses a bottom nav bar (`.bottom-nav` / `.bnav-btn`) with 5 tabs: Tickets, Calendar, CX 360, Tech Tools. The primary breakpoint is `800px` — see `isMobileView()`. A tablet breakpoint at `1024px` narrows the list panel and tightens nav spacing.

Settings (`#screen-more` in code) is accessed via the user avatar dropdown menu, not via a nav tab. When Settings is active, no nav tab is highlighted. The screen ID remains `screen-more` in code to avoid breaking existing references.

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

### snFetch — ServiceNow request wrapper

All ServiceNow API calls go through `snFetch(url, opts, timeoutMs)`, which:
- Attaches `Authorization` and `Accept: application/json` headers automatically
- Wraps each call in an `AbortController` with a default 12-second timeout
- Throws a descriptive error on timeout (`"Request timed out"`) or HTTP failure

The only raw `fetch()` calls that intentionally bypass `snFetch` are: `attemptLogin` (uses temporary credentials before session starts), local JSON file loads (`internet-db.json`, etc.), geocoding/routing APIs, and `catalystGet` (has its own timeout logic).

### Session lifecycle

1. Login -> `attemptLogin()` -> stores creds + user info in sessionStorage -> `startSession()`
2. First load shows a disclaimer modal; `dismissDisclaimer()` proceeds to `fetchTickets()`, `initSafetyChecks()`, `checkSafetyModal()`, and `initInventoryChecks()`
3. Force refresh: `forceAppRefresh()` clears `cachedAssignedTickets` and re-fetches, then navigates to the Tickets tab
4. Logout: `logout()` clears sessionStorage and reloads the page

### Test credentials
- **Username**: `test_fieldtech` / **Password**: `TestFieldTech1!`
- Mirrors the roles and group memberships of `kkubiak`

---

## Delta Branding

The app was rebranded from FieldOps to Delta in March 2026. All C Spire logos in the app UI have been replaced with Delta logos.

### Logo assets

Two theme-specific logos are used, both with transparent backgrounds:
- **Dark mode**: `delta-logo-dark-v2.png` — cyan glowing triangle with "DELTA" text
- **Light mode**: `delta-logo-light-v2.png` — steel blue triangle with "DELTA" text

All `<img>` tags referencing a Delta logo carry the `class="delta-logo"` attribute. The `applyLogoForTheme(theme)` function swaps every `.delta-logo` element's `src` when the theme changes. This function is called from both `toggleTheme()` and `restoreSettings()`.

### Favicon

`delta-favicon-dark.png` — the triangle icon cropped from the dark mode logo, square with transparent background. Referenced by `<link rel="icon">` and `<link rel="apple-touch-icon">`.

### Naming in the UI

- Page title: "Delta — Field Operations"
- Sign-out confirmation: "Sign out of Delta?"
- Login screen aria-label: "Sign in to Delta"

---

## CX 360

CX 360 is an AI-powered customer intelligence tool that cross-references Salesforce, ServiceNow, Arkis, and billing data. The Delta app includes a **demo/mockup** of this integration as a dedicated tab — it is not connected to a live CX 360 backend.

### Screen structure

The CX 360 screen (`#screen-cx360`) uses a chat-style Q&A interface:
- **Welcome state**: Centered branding with 4 suggested question chips
- **Chat state**: User message bubbles (right), AI response bubbles (left) with structured data cards
- **Input bar**: Text input + send button pinned to bottom of screen

### Smart routing indicator

Each AI response shows which of the 10 specialized agents handled the query (e.g., "Account Insights Agent", "Billing Agent", "Contract Agent"). This is displayed as a badge above the response bubble. During processing, a "Routing → Processing" animation plays before the response appears.

### Mock responses

`cx360Responses` is keyed by lowercase customer name fragment. Four pre-built responses exist:

| Query trigger | Agent | Response type |
|---|---|---|
| "regions bank" | Account Insights Agent | Full account summary (tier, MRR, services, satisfaction) |
| "baptist memorial" | Ticket Analysis Agent | 5 open tickets with priorities |
| "sanderson farms" | Billing Agent | Billing discrepancy detail with credit memo status |
| "cal-maine" | Contract Agent | Contract renewal dates, auto-renew terms, competitor risk |

Unrecognized queries receive a generic fallback with search statistics and usage tips.

### Key functions

- `cx360Send()` — reads input, renders user bubble, shows routing + typing animation, then delivers response
- `cx360Ask(text)` — convenience wrapper called by suggested question chips
- `cx360MatchResponse(query)` — matches query to pre-built response or returns fallback
- `clearCx360Chat()` — resets chat to welcome state (triggered by the "+" button)

### CSS specificity note

The CX 360 screen must **not** have its own `display:flex` rule on `#screen-cx360`. The base `.screen { display:none; }` / `.screen.active { display:flex; }` rules handle visibility. Adding a higher-specificity rule causes the screen to remain visible over other tabs, blocking touch navigation on mobile.

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

let _calView = 'month'; // 'month' | 'week' — desktop only toggle

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

// Safety Checks
let _safetyChecks = { vehicle: null, ladder: null };
let _safetyBannerDismissed = false;
let _safetyModalShown = false;

// Inventory Tracker
let _inventoryChecks    = { inventory: null }; // null | ISO timestamp
let _inventoryFrequency = { inventory: 7 };    // 7 or 14 days

// Notifications (all declared together at top of script block)
let _notifs             = [];        // array of notification objects
let _notifSeen          = new Set(); // ticket numbers already shown
let _notifLastCheck     = null;      // ISO timestamp of last poll
let _notifPollTimer     = null;      // setInterval handle
let _notifFailCount     = 0;         // consecutive polling failures
const _NOTIF_MAX_FAILS  = 3;         // pause polling after this many failures

// Tickets closed this browser session (shown as resolved without re-fetch)
const _closedThisSession = new Set();
```

---

## Ticket Detail — Extracted Sub-Fetches

`fetchCaseDetail(number)` is the main loader (~90 lines). It fetches the case record, populates the topbar/pills/location/description synchronously, then fires 5 independent async helpers in parallel. Each helper manages its own DOM elements and error handling:

| Helper | API table | DOM targets |
|---|---|---|
| `fetchDetailAssignee(sysId)` | `sys_user` | `#detail-assigned` |
| `fetchDetailSLA(caseSysId)` | `task_sla` | `#detail-cust-sla` |
| `fetchDetailAccount(sysId, fallback)` | `customer_account` | `#detail-cust-name`, `#detail-cust-id`, `#detail-cust-tier` |
| `fetchDetailContact(sysId)` | `customer_contact` | `#detail-cust-contact`, `#detail-cust-phone` |
| `fetchDetailDevice(sysId)` | `cmdb_ci_netgear` | `#affected-device-section` and children |

After the sub-fetches, `fetchCaseDetail` also triggers mock-data renders (`renderInternetSection`, `renderFirewallSection`, `renderVoipSection`), `fetchTravelEstimate()`, `restoreDraft()`, and `fetchTimeline()`.

### Network Equipment Link

The Network Infrastructure accordion on the ticket detail view includes a "Network Equipment" row with a **BETA** badge. Clicking it calls `closeDetail()` then `showScreen('network', ...)` to navigate to the Network Equipment tab. This is currently a static link (same for every ticket) — future work will surface equipment data inline on the ticket detail.

---

## Calendar — Critical Details

The calendar has three views:
- **Desktop Month** (>=800px, default): `renderCalendarGrid()` — a classic month grid with ticket chips
- **Desktop Week** (>=800px, toggled): `renderCalendarWeek()` — a 7-column day layout (Mon-Sun) showing frosted-glass ticket cards with company, type badge, description, ticket number, state pill, and start time
- **Mobile** (<800px): `renderCalendarAgenda()` — a scrollable list of every day in the month

`renderCalendar()` checks `isMobileView()` first, then checks `_calView` (`'month'` or `'week'`) for desktop, and dispatches to the right renderer. A **Week/Month toggle** (`.cal-view-toggle`) sits in the calendar topbar next to the refresh button — desktop only, hidden on mobile via `@media(min-width:800px)`. `setCalView(view)` switches `_calView`, updates button active states, and calls `renderCalendar()`.

The week view determines its anchor day from `_cal.selectedDay` (falling back to today if in the current month, or the 1st otherwise), then calculates the Monday of that week (ISO convention, Mon=0). Cards use `onclick="openDetail('...')"` to navigate directly to the ticket detail. Both the desktop day panel (`renderCalDayPanel`) and mobile agenda render type badges (Repair/Install/Service Call) via `getCaseType(inc)` alongside state pills on each ticket card.

### selectedDay format

`_cal.selectedDay` may be stored as either a **day number** (from `pickerPickDay`, e.g. `30`) or a **date string** (from `selectCalDay`, e.g. `"2026-03-30"`). Both the month and week view renderers handle both formats when comparing against date strings. When constructing a Date from `selectedDay`, always check `typeof selectedDay === 'number' || /^\d{1,2}$/.test(selectedDay)` and use `new Date(year, month, Number(selectedDay))` for numbers vs `new Date(selectedDay + 'T12:00:00')` for strings.

### pickerPickDay — ordering matters

`closeCalDayPanel()` **sets `_cal.selectedDay = null`**. The picker must call it *before* setting `_cal.selectedDay`, not after:

```js
function pickerPickDay(year, month, day) {
  const d = new Date(year, month, day);
  const sameMonth = (d.getFullYear() === _cal.year && d.getMonth() === _cal.month);

  closeCalDayPanel();        // <- nulls _cal.selectedDay — MUST be first
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

### Inspection & Inventory Due Banners

`getInspectionDueDates()` returns a merged array of `{ type, label, shortLabel, dueStr }` objects for all three tracked items: vehicle inspection, ladder inspection, and inventory report. All three calendar renderers call this function and inject the matching entries as red banners (`.chip-inspection`, `.cal-week-inspection`, `.cal-agenda-inspection`) on the due date.

Safety item date logic (vehicle / ladder):
- Completed + monthly (`freq=0`) → end of next month
- Completed + cyclic → completion timestamp + freq days
- Due / overdue → `_safetyCycleInfo(type).deadline`

Inventory item date logic:
- Always cyclic — uses `_inventoryCycleInfo(type).deadline` in all states (never completed → today; completed → completion + freq days)

The function is defined once (near the calendar state, around line 4770) and shared by all three views.

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

**Dark mode** (default): `:root { ... }` defines all CSS variables. Uses `delta-logo-dark-v2.png`.

**C Spire Light mode**: `html[data-theme="cspire"] { ... }` overrides variables. Uses `delta-logo-light-v2.png`. The light theme uses CSS custom properties for shared patterns:

| Variable group | Purpose |
|---|---|
| `--card-bg`, `--card-border`, `--card-shadow` | Frosted glass card surface (ticket, device, customer cards) |
| `--header-grad`, `--header-shadow`, `--header-text-shadow` | Consumer gradient for topbar/detail-topbar/section headers |
| `--pill-*-text` (9 vars) | Dark text colors for each pill state/priority on light gradient backgrounds |
| `--resize-bg`, `--resize-bar`, `--resize-hover`, `--resize-bar-hover` | Panel resize handle colors |

When adding new light-theme overrides, prefer using or extending these variables rather than hardcoding rgba values. Any remaining `!important` flags in the light theme are structurally necessary to override the `topbar *` wildcard color rule.

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
- **Landscape insets**: `@supports(padding-left: env(safe-area-inset-left))` block adds `padding-left`/`padding-right` using `max(Npx, env(safe-area-inset-left/right))` to topbar, detail-topbar, bottom-nav, desktop-topbar, and all `.screen` containers. On non-notched devices, `env()` evaluates to `0px` so the existing padding is preserved.

Do not use `-webkit-fill-available` on `.app` height — it caused double-counting of the safe area inset in PWA mode.

---

## Responsive Breakpoints

| Breakpoint | Layout | Key rules |
|---|---|---|
| < 800px (mobile) | Bottom nav, single-screen view, slide-in detail | `isMobileView()` returns true |
| 800 - 1024px (tablet) | Desktop topbar, list panel narrowed to 300px, tighter nav spacing | `@media(min-width:800px) and (max-width:1024px)` |
| > 1024px (desktop) | Desktop topbar, list panel 340px + detail pane side by side | `@media(min-width:800px)` base rules |

The `data-mobile-preview` HTML attribute forces mobile layout at any width for dev/testing.

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

/* Light mode — uses CSS variables (see Themes section) */
background: var(--card-bg);
border: 1px solid var(--card-border);
box-shadow: var(--card-shadow);
```

Applies to: `.ticket-inner`, `.device-card`, `.cust-banner`, `.cust-card-inner`, `.cust-detail-banner`, `.net-summary`, `.stat-chip`, `.cal-week-card`.

All of these have `position: relative` and `overflow: hidden` set.

### Depth & Dimension — Section Titles

`.section-title` headers use a richer gradient, multi-layer box-shadow, backdrop blur, and a `::after` light-sweep pseudo-element for a 3D elevated feel:

```css
/* Dark mode */
background: linear-gradient(90deg, rgba(0,192,243,0.28) 0%, rgba(0,140,200,0.16) 50%, rgba(19,30,41,0.6) 100%);
backdrop-filter: blur(6px);
box-shadow: 0 1px 4px rgba(0,0,0,0.3), 0 3px 10px rgba(0,0,0,0.15),
            inset 0 1px 0 rgba(0,192,243,0.15), inset 0 -1px 0 rgba(0,0,0,0.2);

/* Light mode */
background: linear-gradient(90deg, rgba(15,61,88,0.82) 0%, rgba(0,120,180,0.65) 50%, rgba(0,192,243,0.78) 100%);
```

### Background Burst Orbs

`.app` has layered radial gradients creating ambient energy — C Spire Blue at top-right, Magnetic Purple at bottom-left, with a soft center glow. Light mode version is slightly more saturated.

### Pill / Badge styling

**Dark mode pills** have a colored border + 3-layer inset shadow for dimension. **Light mode pills** use per-type linear gradient fills + 1.5px solid border + dark text color via `var(--pill-*-text)` variables.

Priority severity pills (`pill-critical`, `pill-high`, `pill-medium`, `pill-low`) are intentionally **not shown** in the Calendar and Notification panel — state and type badges are sufficient context for field techs who are already assigned to the ticket. Severity pills still exist as CSS classes and may appear in other contexts (e.g. network device status).

### Light Mode — Headers

Topbar and detail-topbar use Consumer Hierarchy gradient via `var(--header-grad)`:
```css
background: linear-gradient(90deg, #00c0f3 0%, #009dd6 55%, #7a5598 100%);
```

The topbar `*` selector sets all children to `color: #ffffff`. This cascades into the calendar picker dropdown — override explicitly with `!important` for any picker content that should be dark text.

### Header Pulse Pattern

Both `.topbar` and `.detail-topbar` display the C Spire **Pulse** brand pattern as a subtle overlay via a `::before` pseudo-element. The pattern is extracted directly from the official brand PDF (`Patterns.pdf`) and stored as two transparent PNG tiles:

- **Dark theme**: `pulse-tile-dark.png` — cyan (#00c0f3) lines at ~4.5% opacity
- **Light theme**: `pulse-tile-light.png` — white lines at ~7.5% opacity

The tiles are 80×80px and repeat seamlessly via `background-repeat:repeat; background-size:80px 80px`. The pattern features the characteristic Truchet quarter-circle arcs, small circles, and trefoil shapes from the C Spire Pulse design.

Both topbar elements have `position:relative; overflow:hidden;` and all direct children are `z-index:1` to sit above the pattern. Only one pattern is used per piece (header bars), per brand rules.

### Light Mode — Text Colors

- **Account/case numbers** (`.ticket-id`, `.cust-bn-id`, `.cust-card-num`, `.cust-detail-banner-num`): `color: #ffffff` — solid white, no text-shadow outline
- **Orange note labels** (`[style*="--accent2"]`): `color: #ffffff !important` — solid white overrides the orange variable

### Calendar Day Headers

Both the month view day-of-week row (`.cal-dow-row`) and the week view column headers (`.cal-week-col-hd`) use the same depth treatment as `.section-title`: gradient backgrounds, multi-layer box-shadow, backdrop blur, and a `::after` light-sweep pseudo-element.

**Dark mode**: gradient from `rgba(0,192,243,0.22)` to `rgba(19,30,41,0.55)`, cyan inset glow, text shadow.
**Light mode**: rich blue gradient from `rgba(15,61,88,0.78)` to `rgba(0,192,243,0.72)`, white text with subtle shadows.

Week view column headers additionally support `.today` (accent-tinted) and `.selected` (solid accent gradient) state classes.

---

## Pill & Badge Classes

```
State:     pill-open  pill-progress  pill-resolved  pill-pending  pill-enroute
Priority:  pill-critical  pill-high  pill-medium  pill-low  (CSS exists; not shown in calendar/notifications)
Type:      type-badge repair | installation | service-call
Safety:    safety-urgency-pill urgency-{none|low|medium|high}
           safety-card-status status-{pending|done}
```

`PRIORITY_MAP` and `STATE_MAP` (both keyed by SN integer value AND display string) live around line 2360.

---

## Network Screen

Pulls live data from Cisco Catalyst Center via `catalystGet(path)` -> the proxy at `CATALYST.base`. Two views:

- **List view**: `renderNetworkList(data)` — device cards grouped by type
- **Topology view**: Canvas-drawn network diagram, `drawTopology(data)`

`_networkCache` prevents re-fetching on tab switch. State: `_networkView = 'list' | 'topology'`.

---

## Notifications

`startNotifPolling()` fires on `dismissDisclaimer()`. Polls every 60 seconds via `checkNewNotifs()`. Shows a badge on the bell icon. Notification panel is a dropdown anchored to the bell. `_notifSeen` prevents re-showing already-displayed tickets.

Notification items show ticket number, time ago, company, and description. Priority pill is intentionally omitted.

### Polling backoff

`_notifFailCount` increments on each consecutive polling failure. After `_NOTIF_MAX_FAILS` (3) failures, polling pauses (`clearInterval` + nulls the timer) and logs a warning. Polling resumes automatically on the next manual `refreshCases()` call, which resets `_notifFailCount` to 0 and calls `startNotifPolling()`.

---

## Safety Check Tracker

Monthly vehicle and ladder inspection tracking with escalating urgency reminders. Integrates with the Sospes mobile app for form completion.

### State

```js
// Declared in the App state section at the top of the script block
// (before login/session flow) to avoid Temporal Dead Zone errors —
// showScreen() → updateSafetyBadge() → getSafetyUrgency() references
// these during dismissDisclaimer(), which runs before the safety
// section code at the bottom of the script.
const _SAFETY_TYPES = [
  { key: 'vehicle', label: 'Vehicle Inspection' },
  { key: 'ladder',  label: 'Ladder Inspection'  }
];
let _safetyChecks = { vehicle: null, ladder: null };  // null = pending, ISO string = completed timestamp
let _safetyBannerDismissed = false;  // per-session dismiss (resets on logout)
let _safetyModalShown = false;       // only show once per session
let _safetyFrequency = { vehicle: 0, ladder: 0 }; // per-type: 0 = end of month, 1-31 = custom days

// Inventory tracker — declared alongside safety state (same TDZ reasons)
const _INVENTORY_TYPES = [
  { key: 'inventory', label: 'Inventory Report' }
];
let _inventoryChecks    = { inventory: null }; // null = pending, ISO string = completed timestamp
let _inventoryFrequency = { inventory: 7 };    // 7 or 14 days only (no monthly option)
```

Completion state is stored in `localStorage` keyed as `ft_safety_{type}_{YYYY-MM}` (e.g., `ft_safety_vehicle_2026-03`). Checks reset automatically each calendar month — `_safetyMonthKey()` returns `"YYYY-MM"` based on the current date. Per-type reminder frequency stored as `ft_safety_freq_{type}` (e.g., `ft_safety_freq_vehicle`). Legacy shared key `ft_safety_frequency` is auto-migrated to per-type keys on init.

### Urgency levels

Urgency is now computed **per inspection type** via `_getSafetyUrgencyForType(type)`, which uses that type's own frequency and cycle info. `getSafetyUrgency()` returns the **worst** urgency across all types (used for the overall pill and badge).

| Level | Condition | Behavior |
|---|---|---|
| `none` | All checks complete | Urgency pill **hidden** (no "All Clear" text shown), no banner/badge/modal |
| `low` | ≤25% of cycle elapsed, incomplete | Blue "Due This Month" pill, no banner |
| `medium` | 25-75% of cycle elapsed, incomplete | Yellow "Due Soon" pill, banner on Tickets screen |
| `high` | >75% of cycle elapsed, incomplete | Red "Overdue" pill (pulses), banner, badge dot on Tech Tools nav, login modal |

The urgency pill (`#safety-urgency-pill`) is hidden via `style.display = 'none'` when urgency is `none`. It is only shown (and populated) for `low`, `medium`, and `high` states. The initial HTML also renders it with `display:none`.

With per-type frequency, each inspection can be at a different urgency level independently. The cycle length is either the full month (default, freq=0) or the custom day count.

### UI components

**Section header** (Tech Tools screen): Uses `.section-title` bar with the urgency pill (`#safety-urgency-pill`) inline. Wraps content in a standard `.card` > `.card-body` container.

**Inspection accordions** (Tech Tools screen): Each inspection (Vehicle, Ladder) is wrapped in an `.accordion` container inside the safety card. The accordion header shows the icon, label, description, status pill (Pending/Complete), and a chevron. Expanding the accordion reveals action buttons (Sospes + Done when pending; Reset when complete) and a per-type **Reminder Frequency** control (dropdown + Confirm button). The frequency setting is nested inside each accordion body, allowing independent frequency per inspection. Uses the existing `toggleAcc()` function with IDs `safety-vehicle` and `safety-ladder`. Nested accordions inside `.card-body` have `border-radius:0` and subtler expanded backgrounds via CSS overrides.

**Mobile action layout**: The accordion header `div` carries class `safety-acc-header`. The actions container carries class `acc-actions`. On `max-width:799px`, `.safety-acc-header` enables `flex-wrap:wrap` and `.safety-acc-header .acc-actions` breaks to its own full-width row below the title text (left-aligned with a 42px offset matching the icon column). Button font/padding reduce slightly on mobile. Desktop layout is unchanged. This resolves overflow clipping caused by `.card { overflow:hidden }` when the row contains multiple buttons.

**Progress bar**: Above the inspection accordions (top of the safety card), shows "N of 2 complete" with nearest deadline info and a fill bar (`#safety-progress-bar`). Bar turns green (`.bar-complete`) when all checks are done.

**Safety banner** (`#safety-banner`): Displayed on the Tickets screen (`#screen-list`) for `medium` and `high` urgency. Now shows **per-inspection messages**: "Vehicle Inspection Due in X days" / "Vehicle Inspection Overdue — Please Complete ASAP" (and same for Ladder). Each due inspection gets its own line. Has a "Review" button (navigates to Tech Tools) and a dismiss button (per-session). Red variant when any type is `high` urgency.

**Badge dots**: Orange dot on mobile Tech Tools button (`#safety-badge-mobile`, `.safety-badge-dot`) and desktop Tech Tools nav (`#safety-badge-desktop`, `.dnav-safety-badge`). Pulses red at `high` urgency. Updated on every `showScreen()` call via `updateSafetyBadge()`.

**Safety modal** (`#safety-modal`): Full-screen overlay shown once per session on login when urgency is `high`. Displays checklist of incomplete inspections with inline "Done" buttons. Options to open Sospes or acknowledge ("I'll complete later today").

### Key functions

| Function | Purpose |
|---|---|
| `initSafetyChecks()` | Loads state + per-type frequencies from localStorage (with legacy migration), renders all components |
| `markSafetyComplete(type)` | Saves timestamp to localStorage, re-renders all |
| `undoSafetyCheck(type)` | Clears localStorage entry, re-renders all. Shown as the **Reset** button in the UI. |
| `setSafetyFrequency(type, val)` | Sets per-type reminder frequency, saves to `ft_safety_freq_{type}` in localStorage, triggers a brief toast confirmation ("Vehicle inspection set to remind every 7 days") via `_showFreqToast()` |
| `_showFreqToast(msg)` | Displays a transient bottom-anchored toast (`#safety-freq-toast`) with a checkmark and descriptive message; auto-dismisses after ~3 s |
| `_safetyCycleInfo(type)` | Returns deadline, daysLeft, cycleDays for a specific inspection type based on its frequency (used for urgency/progress calculations; does **not** drive the "Next Inspection Due" display) |
| `_isSafetyDue(type)` | Checks if inspection is due using that type's frequency |
| `_getSafetyUrgencyForType(type)` | Returns urgency level (none/low/medium/high) for a specific inspection |
| `getSafetyUrgency()` | Returns worst urgency across all types |
| `renderSafetySection()` | Updates accordions, pills, progress bar, per-type frequency inputs, and "Next Inspection Due" date in Tech Tools screen |
| `renderSafetyBanner()` | Shows/hides banner with per-inspection messages on Tickets screen |
| `updateSafetyBadge()` | Updates badge dots on mobile + desktop nav |
| `checkSafetyModal()` | Shows modal on login if urgency = high |
| `launchSospes(type)` | Opens Sospes app store page (App Store on iOS, Play Store on Android) |

### Integration hooks

Three existing functions have safety check hooks:
- `dismissDisclaimer()`: calls `initSafetyChecks()` + `checkSafetyModal()` after login
- `showScreen()`: calls `updateSafetyBadge()` on every screen switch (guarded by `typeof` check)
- `logout()`: resets `_safetyBannerDismissed` and `_safetyModalShown`

`showScreen()` also calls `setDesktopNav()` internally with a mapping table (`network` and `links` map to `techtools`, `more` maps to empty string for no highlight) to keep the desktop nav active state in sync.

### Sospes integration

`launchSospes()` opens the Sospes app store page directly based on user agent detection: App Store (`id1485744669`) on iOS, Play Store (`com.sospesinc.safety`) on Android. Custom URL scheme deep-linking (`sospes://`) was removed because Delta is a web app — Safari and mobile browsers show "address is invalid" errors when attempting custom URL schemes from a non-native context.

### Pill styling

Safety pills (urgency pill and status pills) use the same visual pattern as ticket pills: `border-radius:4px`, gradient backgrounds, `1.5px` colored borders, multi-layer box-shadow with glow, and `text-shadow`. Classes: `.safety-urgency-pill.urgency-{none|low|medium|high}` and `.safety-card-status.status-{pending|done}`.

### Action button depth

The three secondary action buttons — **Sospes** (orange), **Truck Stock** (cobalt blue), and **Reset** (neutral) — use a layered depth treatment:
- **Outer shadows**: `0 1px 2px rgba(0,0,0,0.4)` + `0 2px 6px rgba(0,0,0,0.2)`
- **Colored ambient glow**: e.g. `0 0 8px rgba(255,103,32,0.12)` for Sospes, `rgba(37,99,235,0.15)` for Truck Stock
- **Inset top highlight**: `inset 0 1px 0 rgba(255,…,0.18-0.22)` — simulates a light source from above
- **Inset bottom shadow**: `inset 0 -1px 0 rgba(0,0,0,0.22)`
- **Hover**: `translateY(-1px)` lift + enhanced shadow stack
- **Active**: `scale(0.97)` press + reduced shadow
- **C Spire light theme**: softer shadows, `inset 0 1px 0 rgba(255,255,255,0.7)` highlight for the white surface

CSS classes: `.safety-btn-sospes`, `.safety-btn-truckstock`, `.safety-btn-undo`.

---

## Inventory Tracker

Tracks periodic truck stock inventory reports. Lives in the **Inventory Management** section of the Tech Tools screen (`#screen-techtools`), between Monthly Safety Checks and the Tools card. Behavior mirrors the safety check system but is entirely independent state.

### Key differences from Safety Checks

- **Frequency**: cyclic-only — 7 or 14 days. No monthly option. Default is 7 days.
- **External link**: "Truck Stock" button (cobalt blue, `.safety-btn-truckstock`) opens `launchTruckStock()`. URL is a placeholder (`about:blank`) pending the real Truck Stock link.
- **No urgency modal**: does not affect the safety urgency pill, safety banner, badge dot, or login modal.
- **Storage keys**: `ft_inventory_{type}` (completion timestamp) and `ft_inventory_freq_{type}` (frequency, 7 or 14).

### State

```js
const _INVENTORY_TYPES = [{ key: 'inventory', label: 'Inventory Report' }];
let _inventoryChecks    = { inventory: null }; // null | ISO timestamp
let _inventoryFrequency = { inventory: 7 };    // 7 or 14 only
```

### Cycle logic

`_inventoryCycleInfo(type)` always uses cyclic logic (no monthly branch):
- Never completed → deadline = end of today (overdue from start)
- Completed → deadline = `completedAt + freq * 86400000`

`_isInventoryDue(type)` returns `true` if never completed or `elapsed >= freq`.

### Calendar banner

`getInspectionDueDates()` returns a merged array of safety + inventory items. The inventory item uses `_inventoryCycleInfo(type).deadline` in all states, producing an "Inventory Report Due" banner on the due date in all three calendar views (month chip, week row, mobile agenda). Uses the same `.chip-inspection` / `.cal-week-inspection` / `.cal-agenda-inspection` red styling as the safety inspection banners.

### Key functions

| Function | Purpose |
|---|---|
| `initInventoryChecks()` | Loads frequency (clamped to 7 or 14) and completion timestamp from localStorage, renders section |
| `markInventoryComplete(type)` | Saves ISO timestamp to `ft_inventory_{type}`, re-renders |
| `undoInventoryCheck(type)` | Clears localStorage entry, re-renders. Shown as **Reset** button in UI. |
| `setInventoryFrequency(type, val)` | Saves frequency (7 or 14) to `ft_inventory_freq_{type}`, triggers freq toast |
| `renderInventorySection()` | Updates accordion actions, completed date, Next Report Due line, frequency dropdown |
| `launchTruckStock()` | Opens Truck Stock URL in new tab (URL TBD — currently `about:blank`) |

### UI structure

The Inventory Report accordion (`#inventory-acc-inventory`) uses the same `.accordion` / `.acc-header` / `.acc-body` pattern as the safety accordions. Action div carries class `acc-actions` and the header carries `safety-acc-header` for the mobile stacking behavior. Icon and body tint use cobalt blue (`rgba(37,99,235,…)`). The frequency confirm button inline style also uses cobalt.

---

## User Menu

The user avatar button (`.avatar-sm`, `#user-avatar`) in the topbar opens a dropdown panel (`.user-menu-panel`) instead of directly triggering logout. The panel follows the same pattern as the notification panel: fixed positioning anchored below the avatar via `getBoundingClientRect()`, backdrop overlay for click-to-close, `.show` class toggle, `aria-expanded`/`aria-hidden` sync.

### Menu contents

The header shows a larger avatar circle with user initials and full name (from `sessionStorage`), plus a "Field Technician" role label. Two menu items: "Settings" (gear icon, navigates to `#screen-more`) and "Sign Out" (red, calls `confirmLogout()`).

### Mutual exclusion

`toggleUserMenu()` closes the notification panel first; `toggleNotifPanel()` closes the user menu first. Both panels share `z-index:1999` and use separate backdrop elements at `z-index:1998`.

### Key functions

| Function | Purpose |
|---|---|
| `toggleUserMenu(avatarBtn)` | Opens/closes user menu, populates name/initials, positions panel |
| `closeUserMenu()` | Hides panel, resets aria attributes |

---

## Tech Tools vs Settings

The original "More" screen was split into two screens:

**Tech Tools** (`#screen-techtools`) — visible as a nav tab (wrench icon) in both mobile bottom nav and desktop top nav. Contains three sections: Monthly Safety Checks, Inventory Management, and Tools (Network Equipment, Important Links). Safety badge dots appear on this tab.

**Settings** (`#screen-more` in code) — accessible only via the user avatar dropdown menu "Settings" option. Contains Appearance (theme toggle, mobile preview), App (force refresh), and Account (sign out) sections. No nav tab highlights when Settings is active. The screen ID remains `screen-more` in code to avoid breaking existing references.

The desktop nav mapping in `showScreen()` routes `network` and `links` to highlight `techtools`, and `more` to empty string (no tab highlighted).

---

## Accessibility

The app includes ARIA attributes and semantic HTML added in March 2026:
- Login `<div>` converted to `<form>` with `<label>`/`for` associations and `onsubmit` handler
- Disclaimer modal: `role="dialog"`, `aria-modal`, `aria-labelledby`
- Notification panel: `role="region"`, `aria-hidden`, `aria-live="polite"`
- All 4 accordion headers: `aria-expanded`, `aria-controls` (synced by `toggleAcc()`)
- 11 static section-title `<div>`s converted to `<h2>`
- Search inputs: `aria-label`
- Form selects/textarea: `<label>` + `aria-label`
- Back buttons: `aria-label`
- Calendar grid: `role="grid"`, day-of-week cells `role="columnheader"`
- Calendar picker button: `aria-expanded`, `aria-controls`
- More screen interactive `<div>`s converted to `<button>`
- `.sr-only` utility class for screen-reader-only text
- `--text-muted` bumped to `#6889a5` for WCAG AA contrast compliance (4.5:1 ratio)

---

## Visual Polish (March 2026)

### Skeleton loading screens
All list/grid loading states use shimmer skeleton placeholders instead of spinners. The `skeleton-shimmer` keyframe animates a gradient sweep on `.skeleton` elements. Variants: `.skeleton-card` (110px, ticket shape), `.skeleton-card-sm` (72px, customer rows), `.skeleton-line` / `.skeleton-line-short`, `.skeleton-divider` (date header shape). Stagger with `animation-delay` and descending opacity for natural appearance. Light theme has its own skeleton gradient override.

### Enhanced empty states
`.empty-state` provides a centered layout with `.empty-state-icon` (dashed-border rounded box), `.empty-state-title`, and `.empty-state-sub`. Used in: ticket list (no results), notification panel (all caught up), no-ticket-selected overlay (desktop). Light theme tints the icon purple instead of cyan.

### Button loading states
`.btn.is-loading` hides child `.btn-label` via `visibility:hidden` and overlays a centered spinning border via `::after`. Buttons auto-disable during async via `pointer-events:none`. Used on Submit Update and Close Ticket buttons. The submit/close JS uses `classList.add/remove('is-loading')` instead of replacing innerHTML.

### Modal entrance animations
`#disclaimer-modal` fades in via `modalFadeIn` (background transition). `.disc-card` scales up via `modalCardIn` with a spring-like cubic-bezier (`0.34, 1.56, 0.64, 1`).

### SLA urgency indicator
`.cf-val.sla.sla-urgent` applies `slaPulse` animation — alternates between `--accent2` and `--danger` color with a soft red text-shadow. Triggers when `has_breached` is true or `planned_end_time` is < 1 hour away. The class is managed by `fetchDetailSLA()`.

### Mobile card press feedback
On `max-width:799px`, `.ticket-card` and `.cal-mini-card` scale to `0.98` on `:active` with a 120ms transition. Provides tactile confirmation of tap without affecting desktop hover behavior.

### Accordion depth cues
`.accordion.acc-expanded` gains a subtle elevated `box-shadow`. `toggleAcc()` toggles this class alongside the existing chevron rotation and body open/close. Light theme uses a blue-tinted shadow.

### Card hover consistency (desktop)
On `min-width:800px`, `.ticket-inner`, `.cal-mini-card`, and `.cust-card-inner` share a unified hover pattern: `translateY(-1px)` lift with enhanced shadow on parent `:hover`. Both themes have matching shadow definitions.

### prefers-reduced-motion
`@media(prefers-reduced-motion: reduce)` kills all animation/transition durations and replaces skeleton shimmer with a static surface color. Ensures accessibility compliance for motion-sensitive users.

### Data viz stat bars
`.stat-bar-wrap` / `.stat-bar` provide a thin (3px) animated fill bar for numeric values. Variants: `.bar-good` (green), `.bar-warn` (amber), `.bar-bad` (red). Currently used in firewall uptime display. `statBarFill` keyframe animates width from 0.

---

## Important Patterns

- **No framework, no build**: pure DOM manipulation. `escHtml(str)` must be used on all user/API data inserted into innerHTML.
- **`snFetch(url, opts, timeoutMs)`**: wraps all ServiceNow API calls with auth headers and AbortController timeout. Use this for any