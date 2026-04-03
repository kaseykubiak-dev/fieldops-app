# Delta App — FieldTechApp Project

## What This Is
A single-file HTML/CSS/JS pitch demo app ("Delta app") for C Spire field technicians. Goal: give techs a single source-of-truth for dispatching on tickets, closing tickets, finding customer info, and accessing company resources. All choices should be made from the point of view of a technician working a ticket in the field.

The entire app lives in one file: `fieldtech-app.html` (no build step, no framework).

When making choices regarding color, scheme, tone, or overall presentation, reference the `/brand-alignment` skill for additional context. For code changes, use the `code-optimizer` skill.

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
| CX 360       | `cx360`      | Placeholder AI agent UI — frosted glass ONE CUSTOMER panel, search bar, 9 query-type pills, Attach/Agents/Send action bar. Header note: "· Placeholder for future implementation." |
| My Tools     | `techtools`  | Tech tools, On-Call Line, Teams contacts, Safety tracker |
| Settings     | `more`       | Accessed via TT avatar → profile area. Six sections: Appearance, Preferences, Profile, Notifications, App, Account. |

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

Per-commit versioning convention: commit subject prefixed with version (e.g. `v0.38 —`), in-app Settings version span updated in same commit. Increment by 0.01 until next major version.

---

## Current State (as of v0.39)

### Completed this sprint
- **Settings panel**: Reorganized into 6 named sections — Appearance, Preferences, Profile, Notifications, App, Account. Accessed via the TT avatar in the topbar.
- **Settings — Auto-Refresh**: `ft_auto_refresh` localStorage key. `startAutoRefresh()` sets a `setInterval` that only fires `refreshCases()` when `#screen-list` is active. Pulsing dot indicator on the Refresh Cases button.
- **Settings — Default Map App**: `ft_map_app` key. `openMaps()` branches on `auto` / `google` / `waze` / `apple`.
- **Screen headers**: All tabs except My Work now have a consistent `detail-topbar` header with icon + title. Calendar header omits label (replaced with icon+label spacer — now just the full-width date picker row). CX 360 has the placeholder note in the header.
- **Mobile topbar gap fix**: `.detail-topbar { padding-top: 0 }` in mobile media query prevents double safe-area-inset.
- **Ticket close confirmation**: After `closeTicket()` API success, shows a centered modal with ticket number (mono), customer name, type pill, time on site (if tech tapped Start Work), and a "Back to My Work" button. No auto-dismiss.
- **Action button state machine fixes**:
  - "Close Ticket" no longer advances to "Ticket Closed" prematurely — button stays at `close` state until API returns success.
  - Already-closed tickets (SN state 4 or 5) now show "Ticket Closed" on open, not "Start Travel".
  - `closeTicket()` success block sets `_ticketActionState[number] = 'done'` and re-renders.

### Seed data
- `seed_next_week.py` — 10 cases for March 30–April 3, 2026
- `seed_rest_of_april.py` — 38 cases for April 6–30, 2026 (weekdays only, 2/day, mix of install/repair)

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

---

## CSS Notes

- `.app` uses `height:100vh; height:100dvh` (dvh for dynamic viewport on mobile)
- `html, body` has `overflow:hidden` — absolutely positioned `::after` elements that go below the viewport will be clipped
- Bottom nav: `min-height: 64px`, `align-items: center`, `padding: 0 4px` — no safe-area padding (intentional, PWA standalone mode)
- Desktop nav hidden on mobile (`display:none` at `max-width:799px`), bottom nav hidden on desktop
- `.topbar` — dark gradient bg, used by the persistent `#mobile-topbar` and formerly by Calendar/CX360 sub-topbars
- `.detail-topbar` — `background:var(--surface)`, lighter border. Used by detail view, Settings, My Tools, My Calendar topbar, CX 360 topbar. On mobile: `padding-top: 0` (mobile topbar owns the safe-area-inset-top)
- `#screen-calendar .detail-topbar` and `#screen-cx360 .detail-topbar`: `min-height:auto; padding-top:7px; padding-bottom:7px` on mobile (compact, sit below persistent topbar)
- `#screen-calendar .detail-topbar { position: relative }` — needed for date picker dropdown positioning
