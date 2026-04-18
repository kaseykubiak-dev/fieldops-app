# Delta App — FieldTechApp Project

## What This Is
A single-file HTML/CSS/JS pitch demo app ("Delta app") for C Spire field technicians. Goal: give techs a single source-of-truth for dispatching on tickets, closing tickets, finding customer info, and accessing company resources. All choices should be made from the point of view of a technician working a ticket in the field.

The entire app lives in one file: `fieldtech-app.html` (no build step, no framework).

When making choices regarding color, scheme, tone, or overall presentation, reference the `/brand-alignment` skill for additional context. For code changes, use the `code-optimizer` skill.

---

## Branches

- `main` — stable production baseline (C Spire branding, cyan palette)
- `portfolio` — portfolio/demo branch; indigo/violet palette, C Spire branding removed, Compass tab redesigned. **Active development branch.**

---

## Architecture

- **Single-file**: All HTML, CSS, and JS in `fieldtech-app.html`
- **No framework**: Vanilla JS, no build step
- **APIs**: ServiceNow CSM (`snFetch`, `sn_customerservice_case` table, dot-walked fields), Nominatim (geocoding), OSRM (routing)
- **CSS custom properties**: `--accent`, `--accent2`, `--success`, `--warning`, `--danger`, `--text`, `--text-muted`, `--surface`, `--surface2`, `--border`
- **Responsive**: Mobile-first, desktop at `min-width: 800px`. Mobile bottom nav, desktop top nav.
- **PWA**: `viewport-fit=cover`, `apple-mobile-web-app-capable`, manifest linked

---

## Screens / Tabs

| Tab Label    | Screen ID    | Notes |
|--------------|--------------|-------|
| My Work      | `list`       | Ticket list (Today / Assigned / Closed views) |
| My Calendar  | `calendar`   | Week and Month views, Sun–Sat, cal-mini-card components. **Hidden on mobile bottom nav** (layout issues at small viewports); accessible via desktop top nav only. |
| Compass      | `cx360`      | Account dossier / field brief UI. Account search typeahead, 5-tab strip (Summary / Tickets / Billing / Contract / Renewal), briefing sections matching ticket-card visual treatment. Large centered Delta logo behind content. Header note: "· Placeholder for future implementation." **Formerly CX 360.** |
| My Tools     | `techtools`  | Tech tools, On-Call Line, Teams contacts, Safety tracker |
| Settings     | `more`       | Accessed via TT avatar → profile area. Six sections: Appearance, Preferences, Profile, Notifications, App, Account. |

---

## Dark Theme Palette (portfolio branch — `:root`)

The portfolio branch uses an indigo/violet palette replacing the original C Spire cyan:

```css
:root {
  --bg: #12111e;
  --surface: #12111e;
  --surface2: #1c1a2e;
  --border: #2a2744;
  --accent: #7C6FCD;        /* indigo/violet — primary */
  --accent2: #E8834A;       /* warm orange — secondary */
  --success: #3DD68C;
  --text-dim: #9B94D4;
  --text-muted: #6b6494;
  --toggle-knob: #7C6FCD;
  --cust-banner-bg: rgba(124,111,205,0.05);
}
```

Light theme (`html[data-theme="cspire"]`) is **unchanged** — all C Spire cyan values are preserved there.

**Important when editing palette**: The Python-based replacement scripts must track context to avoid accidentally overwriting the `html[data-theme="cspire"] {}` block. Use brace-depth counting to skip lines inside that block.

---

## Topbar Tagline (portfolio branch)

The persistent mobile topbar tagline reads **"Navigate Every Job"** (replaced C Spire's "We Are Customer Inspired").

Shimmer gradient uses the indigo palette:
```css
background: linear-gradient(90deg, #7C6FCD 0%, #E2DCFF 60%, #7C6FCD 100%);
animation: tagline-shimmer 4s linear infinite;
```

---

## Git Tags / Versions

- `v0.1` — initial release
- `v0.2` — On-Call feature added
- `v0.3` — Calendar month view redesign, CX 360 UI redesign
- `v1.0-stable` — stable baseline
- `v0.31` — Settings panel reorganized into 6 sections; Auto-Refresh and Default Map App added
- `v0.32` — Consistent screen headers added to My Calendar, CX 360, My Tools
- `v0.33` — Calendar and CX 360 headers unified to `detail-topbar` style (surface bg)
- `v0.34` — "My Calendar" label removed from calendar topbar (crowded next to date picker)
- `v0.35` — CX 360 header placeholder note added
- `v0.36` — Ticket close confirmation screen (Ticket Closed Successfully popup)
- `v0.37` — Ticket action button state machine fixed (premature done state + already-closed tickets)
- `v0.38` — PWA manifest link, request deduplication in snFetch, stale ticket cache with offline indicator
- `v0.39` — Notification bell: accent color, time accuracy (display_value=false), Mark All Read persistence
- `v0.40` — Install type badge recolored gold for distinction from Closed (green)
- `v0.41` — Replaced Open/Closed pills and Install/Repair badges with card-body color encoding: blue=Install, orange=Repair, green=Closed. Applied to calendar tab too.
- `v0.42` — Fixed TDZ crash from v0.41 (variable name collision in `tickets.forEach`)
- `v0.43` — Near-white status text; deep blue Install label, deep orange Repair label; removed Open pill from ticket detail
- `v0.44` — Restored "Ticket Status:" label; added Force Refresh confirmation dialog (`showConfirmDialog`)
- `v0.45` — Stripped pill chrome from VPN and Pending Installation labels (text-only)
- `v0.46` — Stripped pill chrome from Complete/Pending status labels on Tools tab
- `v0.47` — Stripped urgency pill chrome (Due This Month/Overdue); fixed calendar mobile topbar centering (3-column flex layout); renamed Badge # → Job Title; live avatar initials update on Name field change
- `v0.48` — Removed dot (::before) from ticket action button; stripped pill chrome from all Services & Equipment section items
- `v0.49` — Fixed `_statusColor` scope error in firewall render function; updated no-firewall empty state to "No Firewall On Record"
- `v0.50` — Light theme polish: increased card color intensity (install/repair/closed), section-title notes white, Navigate/Call button text deep navy, CX 360 ONE CUSTOMER panel unified with header gradient
- `v0.51` — Box-arrow link icons on Salesforce Order, ServiceNow Order, and Arkis Circuit ID fields; scroll-to-top on ticket open; safety badge dot repositioned closer to Tools icon
- `v0.52` — Login popup for pending inspections/reports: fires on due date (urgency ≠ none), lists only due items, Acknowledge button
- `v0.53` — Reduced burst watermark opacity on ticket cards from 0.12 → 0.09
- `v0.54` — **[portfolio]** CX 360 renamed to Compass; compass SVG icon in nav; screen ID remains `cx360`
- `v0.55` — **[portfolio]** Compass tab UI redesigned: old chat/CX 360 interface replaced with account dossier layout (search bar typeahead, 5-tab strip, `.cb-section` briefing cards matching ticket-inner visual treatment)
- `v0.56` — **[portfolio]** Compass card watermarks removed; single large centered Delta logo added as `#screen-cx360::before` pseudo-element (`opacity:0.07`, `width:min(72vw,300px)`)
- `v0.57` — **[portfolio]** Light theme override for Compass background logo (`delta-logo-light-transparent.png`, `opacity:0.09`)
- `v0.58` — **[portfolio]** Dark theme palette switched from C Spire cyan to indigo/violet (`--accent:#7C6FCD`); cspire theme block preserved
- `v0.59` — **[portfolio]** Topbar tagline changed from "We Are Customer Inspired" to "Navigate Every Job"; shimmer gradient updated to indigo palette
- `v0.60` — **[portfolio]** Compass section cards fixed: `flex-shrink:0` added to `.cb-section` and `.cb-skeleton` so cards render at natural height; `.cb-brief-area` overflow-y:auto now scrolls correctly

Per-commit versioning convention: commit subject prefixed with version (e.g. `v0.38 —`), in-app Settings version span updated in same commit. Increment by 0.01 until next major version.

---

## Current State (as of v0.60)

### Completed this sprint
- **Card color system**: Pills replaced by CSS class variants on `.ticket-inner`, `.cal-mini-card`, `.cal-week-card`. Classes: `tc-install` (blue default), `tc-repair` (orange), `tc-closed` (green). Plain-text labels use `.tc-label` (colored per variant) and `.tc-status` (near-white). Light theme (`cspire`) has explicit overrides for all three variants with boosted opacity tints.
- **Pill cleanup**: Removed pill chrome from VPN badges, Pending Installation, Complete/Pending (Tools tab), urgency labels (Due This Month/Overdue), ticket action button dot (::before), and all Services & Equipment items. Text color preserved throughout.
- **Services & Equipment dynamic templates**: `wanBlock` and `fwBlock` use a `_statusColor` map (`pill-resolved` → `var(--success)`, `pill-critical` → `var(--danger)`, `pill-warning` → `var(--warning)`) for inline-styled plain text. Map is defined inside each function's scope to avoid reference errors.
- **Light theme (C Spire) polish**: Section-title notes scoped to `rgba(255,255,255,0.65)` (dark gradient bg always present); Navigate/Call `btn-ghost` text changed to `#0f3d58`; CX 360 ONE CUSTOMER panel switched from dark navy to a soft translucent blue-violet gradient matching the header palette.
- **Link icons**: `order-link` is now `inline-flex`. Box-arrow SVG icon appended to Salesforce Order and ServiceNow Order via `innerHTML`. `arkisVal()` helper also includes the icon. All use `opacity:0.65`.
- **Scroll-to-top on ticket open**: `openDetail()` sets `#screen-detail .detail-scroll { scrollTop = 0 }` before `fetchCaseDetail()`.
- **Login inspection popup**: `checkSafetyModal()` fires whenever `getSafetyUrgency() !== 'none'`. `_safetyModalShown` resets to `false` on every `startSession()`. Modal shows only due items (no completed rows, no inline Done buttons). Title: "Pending Inspections/Reports". Buttons: "Open Sospes to Complete" (primary) + "Acknowledge" (dismiss).
- **Safety badge dot**: Repositioned from `right:4px` to `right:calc(50% - 18px)` to sit over the My Tools icon.
- **Burst watermark**: `opacity:0.09` (was 0.12) on `.ticket-inner::after`.
- **Compass tab** (portfolio branch): Full UI redesign — dossier/field-brief model replacing the old chat interface. Account typeahead search, 5-tab strip, `.cb-section` cards matching ticket visual treatment, large centered Delta logo watermark, `flex-shrink:0` on cards for correct scroll behavior.
- **Portfolio palette**: Dark theme switched to indigo/violet. Tagline changed to "Navigate Every Job" with indigo shimmer.

### Seed data
- `seed_next_week.py` — 10 cases for March 30–April 3, 2026
- `seed_rest_of_april.py` — 38 cases for April 6–30, 2026 (weekdays only, 2/day, mix of install/repair)

### Pending tasks
- **Update Compass mock data + wire ticket navigation**: (1) Update `_compassBriefs` company names to match real SN accounts once next month's tickets are added. (2) Make Compass "Tickets" brief rows clickable, calling `openDetail(ticketNumber)`.

### Next up (candidates)
- On-site timer UI — visible stopwatch while ticket is On Site
- Weather badge on ticket detail
- Pre-arrival "Brief Me" card

---

## Key Components / Patterns

### Settings (`#screen-more`)
- Sections: Appearance, Preferences, Profile, Notifications, App, Account
- All settings stored under `ft_*` keys in `localStorage`
- `restoreSettings()` IIFE runs on load to populate all controls
- `startSession()` seeds `#prof-name` from `sn_user_name` sessionStorage if `ft_profile_name` not set
- Version row shows `Delta vX.XX` in monospace (update on every commit)

### Ticket action state machine
States: `travel` → `work` → `close` → `done`
- `_ticketActionState` map: ticket number → current state key
- `advanceTicketAction()`: advances through travel/work only. When state = `close`, just scrolls to the update form and returns — does **not** advance state.
- `closeTicket()`: on API success, sets state to `done` and calls `renderTicketActionButton()`.
- On case load: if SN state is 4 or 5 (or in `_closedThisSession`), seeds `_ticketActionState[number] = 'done'` before rendering.
- `_onSiteStartTime`: set to `Date.now()` when tech taps "Start Work" (state = `work`). Reset to `null` on new case open.

### Close confirmation popup (`#close-success-overlay`)
- `showCloseSuccessPopup(onDismiss)` populates: ticket number (`currentCaseNumber`), company (`currentCaseCompany`), type pill (`currentCaseType`), time on site (from `_onSiteStartTime`).
- Time on site row hidden if `_onSiteStartTime` is null (tech skipped Start Work).
- Dismissed by "Back to My Work" button or clicking the backdrop. No auto-dismiss timer.
- Module vars reset on new case open: `currentCaseCompany = null`, `currentCaseType = null`, `_onSiteStartTime = null`.

### Card color variant system
Three CSS classes applied to `.ticket-inner`, `.cal-mini-card`, `.cal-week-card`:
- `tc-install` — blue (default; matches `--accent`)
- `tc-repair` — orange (matches `--accent2`)
- `tc-closed` — green (matches `--success`)

Label classes inside cards:
- `.tc-label` — uppercase type label, colored per variant (deep blue/orange/muted); `margin-left:auto`
- `.tc-status` — state text, near-white (`rgba(255,255,255,0.88)`)

Light theme overrides (`html[data-theme="cspire"]`) boost cust-glance tint opacity and adjust border colors for all three variants on both ticket cards and calendar mini-cards.

### Compass tab (`#screen-cx360`)

**Structure:**
```
#screen-cx360
  .detail-topbar         ← compact header (sits below mobile topbar)
  .cb-account-bar        ← search input + dropdown (flex-shrink:0)
  .cb-tab-strip          ← Summary / Tickets / Billing / Contract / Renewal (flex-shrink:0)
  .cb-brief-area         ← flex:1; overflow-y:auto; flex-direction:column; gap:12px
    .cb-section × N      ← flex-shrink:0 — renders at natural height, no squish
```

**Background logo:**
```css
#screen-cx360::before {
  content:''; position:absolute; top:50%; left:50%;
  transform:translate(-50%, -50%);
  width:min(72vw, 300px); height:min(72vw, 300px);
  background:url('delta-logo-dark-transparent.png') no-repeat center/contain;
  opacity:0.07; pointer-events:none; z-index:0;
}
html[data-theme="cspire"] #screen-cx360::before {
  background-image:url('delta-logo-light-transparent.png'); opacity:0.09;
}
```

**JS data:**
- `_compassAccounts` — array of 4 demo accounts (id, name, industry, location, tier)
- `_compassBriefs` — object keyed by account id × tab name; each tab returns an array of section objects `{ title, badge?, rows:[{label, val, cls?}] }`
- `compassRunBrief(accountId, tab)` — renders shimmer skeleton, then replaces with `.cb-section` cards
- `compassAccountInput()`, `compassShowDropdown()`, `compassHideDropdown()`, `compassSetTab()`, `compassClearAccount()` — search/tab interaction handlers

**Section card CSS classes:**
- `.cb-section` — `flex-shrink:0` + frosted glass card, border-left accent
- `.cb-section-header` — indigo gradient bg, section title + optional badge
- `.cb-section-badge` — `.high` / `.warn` / `.ok` color variants
- `.cb-row` — label/value pair row; `.cb-row-val` takes `.accent`, `.danger`, `.success`, `.warning`
- `.cb-skeleton` — `flex-shrink:0` shimmer placeholder card

### Safety check modal (`#safety-modal`)
- Fires on every login if any inspection/report is due (`getSafetyUrgency() !== 'none'`)
- `_safetyModalShown` is session-only; reset in `startSession()` so popup recurs each login
- `_renderSafetyModalChecklist()` renders only `_isSafetyDue(type) === true` items
- Dismissed via "Acknowledge" button (`acknowledgeSafetyModal()`) or auto-dismissed after 600ms if all items complete

### Services & Equipment dynamic status text
Both `wanBlock` and `fwBlock` template functions define a local `_statusColor` map:
```js
const _statusColor = { 'pill-resolved': 'var(--success)', 'pill-critical': 'var(--danger)', 'pill-warning': 'var(--warning)' };
```
Status spans use `style="font-size:10px;font-weight:700;color:${_statusColor[statusCls]||'var(--text-muted)'};"`.
**Important**: the map must be defined inside each function scope separately — `wanBlock` and `fwBlock` live in different function scopes.

### cal-mini-card
Frosted glass card used in week view, day panel, agenda, and month view. Border-left accent, company name, time, state pill, type badge right-aligned.

### Two-span responsive label pattern
```html
<span class="tpl-full">Out of Office</span>
<span class="tpl-short">Out</span>
```
```css
.tpl-short { display:none; }
@media(max-width:799px) {
  .tpl-full  { display:none; }
  .tpl-short { display:inline; }
}
```

### fetchTravelEstimate()
Uses Nominatim + OSRM. Key behaviors:
- `countrycodes=us` on all Nominatim requests
- Fallback: if full address fails to geocode, retries with city+state only
- Stale-result guard: captures `currentCaseNumber` at async start, checks before writing result

### Auto-refresh indicator
`updateAutoRefreshIndicator()` updates `#refresh-label` to show a pulsing `.auto-refresh-dot` + "Auto · N min" when active, or plain "Refresh Cases" when manual. `.refresh-label` uses `display:flex; align-items:center; gap:6px`.

### Confirm dialog
`showConfirmDialog(message, onYes)` — generic modal helper. Uses `#confirm-dialog-overlay` and `_confirmDialogResolve` callback. Currently used by Force Refresh.

---

## CSS Notes

- `.app` uses `height:100vh; height:100dvh` (dvh for dynamic viewport on mobile)
- `html, body` has `overflow:hidden` — absolutely positioned `::after` elements that go below the viewport will be clipped
- Bottom nav: `min-height: 64px`, `align-items: center`, `padding: 0 4px` — no safe-area padding (intentional, PWA standalone mode)
- Desktop nav hidden on mobile (`display:none` at `max-width:799px`), bottom nav hidden on desktop
- `.topbar` — dark gradient bg, used by the persistent `#mobile-topbar` and formerly by Calendar/CX360 sub-topbars
- `.detail-topbar` — `background:var(--surface)`, lighter border. Used by detail view, Settings, My Tools, My Calendar topbar, Compass topbar. On mobile: `padding-top: 0` (mobile topbar owns the safe-area-inset-top)
- `#screen-calendar .detail-topbar` and `#screen-cx360 .detail-topbar`: `min-height:auto; padding-top:7px; padding-bottom:7px` on mobile (compact, sit below persistent topbar)
- `#screen-calendar .detail-topbar { position: relative }` — needed for date picker dropdown positioning
- `.section-title .section-title-note` — scoped to `rgba(255,255,255,0.65)`; section headings always have a dark gradient bg so white reads correctly in both themes. Standalone `.section-title-note` (e.g. Compass header) retains `var(--accent2)`.
- `.ticket-inner::after` — C Spire burst watermark, `opacity:0.09`, `z-index:0`, `pointer-events:none`
- `.safety-badge-dot` — `right:calc(50% - 18px)` positions dot above the My Tools icon, not at the button's far-right edge
- `.cb-brief-area` — `flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:12px` — scrollable briefing area
- `.cb-section`, `.cb-skeleton` — `flex-shrink:0` — cards render at natural height; never squished by flexbox
