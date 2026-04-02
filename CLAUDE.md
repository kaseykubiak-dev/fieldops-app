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

| Tab Label | Screen ID | Notes |
|-----------|-----------|-------|
| My Work | `list` | Ticket list (Today / Assigned / Closed views) |
| My Calendar | `calendar` | Week and Month views, Sun–Sat, cal-mini-card components |
| CX 360 | `cx360` | Placeholder AI agent UI (frosted glass, query pills) |
| My Tools | `techtools` | Tech tools, On-Call Line, Teams contacts, Safety tracker |

---

## Git Tags / Versions

- `v0.1` — initial release
- `v0.2` — On-Call feature added
- `v0.3` — Calendar month view redesign, CX 360 UI redesign
- `v1.0-stable` — stable baseline

---

## Current State (as of end of this session)

### Recently completed
- **Calendar month view**: `cal-mini-card` frosted glass cards (company, time, state pill, type badge right-aligned)
- **Calendar week + month unified**: Both now Sun–Sat
- **CX 360 redesign**: Frosted glass ONE CUSTOMER panel, search bar, 9 query-type pills, Attach/Agents/Send action bar
- **Mobile fixes**: Tool tab pills/Done left-justified, On-Call call button left-justified, CX360 Send button no longer clips on mobile
- **Teams status**: "OOO" → "Out of Office" on desktop, "Out" on mobile (two-span CSS toggle)
- **Travel time robustness**: `fetchTravelEstimate()` — added `countrycodes=us`, city/state fallback geocoding, stale-result guard
- **Bottom nav PWA fix**: Removed `env(safe-area-inset-bottom)` padding that was causing nav to appear raised in PWA standalone mode. Nav is now a fixed 64px in all contexts. `viewport-fit=cover` + `100dvh` extends the nav background to the physical screen edge.
- **Tab renames**: Tickets → My Work, Calendar → My Calendar, Tools → My Tools (CX 360 unchanged). Applied to both mobile bottom nav and desktop nav.

### In-progress / next up: Settings panel
The user wants to add a Settings section to the app. Already has Theme and Clear Cache. Proposed additions (to be confirmed in next session):

**Candidate settings:**
- Default Tab — which screen opens on launch
- Auto-Refresh Interval — how often ticket list refreshes (manual, 5 min, 15 min)
- Technician Profile — name, badge number, region
- Notification Toggles — push notifications, sound, quiet hours
- Default Ticket View — Today / Assigned / Closed
- GPS / Location toggle — for travel time estimates
- Distance Units — miles vs km
- Default Map App — Apple Maps / Google Maps / Waze
- Sign Out

**Preferred location for Settings UI** — needs to be confirmed:
- Option A: Under My Tools tab (most consistent with current layout)
- Option B: Tapping the TT avatar in the top bar opens a settings drawer
- Option C: New dedicated Settings tab in the bottom nav

**Approach**: Build in phases, one feature at a time to minimize mistakes.

---

## Key Components / Patterns

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

### Mobile left-margin fix
After removing square accordion icons from Tech Tools, the mobile CSS for `.safety-acc-header .acc-actions` had a leftover `margin:0 0 4px 42px !important`. Changed to `margin:0 0 4px 0 !important`.

---

## CSS Notes

- `.app` uses `height:100vh; height:100dvh` (dvh for dynamic viewport on mobile)
- `html, body` has `overflow:hidden` — absolutely positioned `::after` elements that go below the viewport will be clipped
- Bottom nav: `min-height: 64px`, `align-items: center`, `padding: 0 4px` — no safe-area padding (intentional, see PWA note above)
- Desktop nav hidden on mobile (`display:none` at `max-width:799px`), bottom nav hidden on desktop
