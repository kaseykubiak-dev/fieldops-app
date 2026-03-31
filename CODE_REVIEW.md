# FieldTech App JavaScript Code Review

**File**: fieldtech-app.html (~4900 lines, ~280KB)
**Scope**: Single-file web app for C Spire field technicians
**Review Date**: March 2026

---

## Summary

The JavaScript demonstrates solid fundamentals for a single-file demo app but has several issues ranging from critical security/data handling concerns to maintainability gaps. The code is well-structured for its scope (no framework, no build system), but lacks defensive error handling in critical paths and shows some risky patterns around credential storage and API error recovery.

**Overall Assessment**: **Medium Risk** — suitable for demo/training use with the test credentials, but would require hardening before production deployment.

---

## Critical Issues

### 1. Unhandled Promise Rejections in Fire-and-Forget Fetches
**Location**: Lines 554–558, 597–610, 618–629, 635–650, 654–670
**Severity**: HIGH

Multiple fetch calls are made without `.catch()` handlers and their promises are not awaited. If the network fails or the API returns an error, these requests silently fail and the UI shows stale data.

**Examples**:
```javascript
// Line 554–558: fetching assigned_to user
fetch(`${SN.instance}/api/now/table/sys_user/${assignedSysId}?...`)
  .then(r => r.json())
  .then(u => { /* UI update */ })
  .catch(() => { /* fallback */ });
// No await; if this fails, UI silently shows "..."

// Line 597–610: fetching task_sla
fetch(`${SN.instance}/api/now/table/task_sla?...`)
  .then(r => r.json())
  .then(sd => { /* UI update */ })
  .catch(() => { ... });
```

**Impact**: Users may see incomplete or stale data without realizing the backend call failed. The catch handler only sets `textContent = '—'`, but doesn't log or alert the user.

**Recommendation**: Either await these fetches or at minimum log errors to console and show a subtle visual indicator (icon, color change) that data is unavailable.

---

### 2. Unsafe HTML Escaping (Missing escHtml() Calls)
**Location**: Lines 2861, 3984, 4069, 4546, 4587
**Severity**: MEDIUM (XSS Risk)

Several locations insert unsanitized user input into `onclick` handlers or dynamic attributes:

**Line 2861** (Customer card):
```javascript
<div class="cust-card" onclick="openCustomer('${escHtml(acc.sys_id)}','${escHtml((acc.name||'').replace(/'/g,"\\'"))}')`>
```
The `replace(/'/g,"\\'")` approach is dangerous. A name like `O'Reilly` becomes `O\'Reilly`, which breaks the JavaScript string. A customer named `'); alert('xss'); //` would execute code.

**Line 4546** (Topology SVG):
```javascript
onclick="topoNodeClick('${n.id.replace(/'/g,"\\'")}')"`>
```
Same issue with naive quote escaping.

**Impact**: If ServiceNow data contains malicious values, the app could execute arbitrary JavaScript in the browser.

**Recommendation**:
- Use `data-*` attributes instead of inline event handlers:
  ```html
  <div class="cust-card" data-sys-id="${escHtml(acc.sys_id)}" data-name="${escHtml(acc.name)}">
  ```
- Add event listeners via JavaScript instead of inline handlers.

---

### 3. Credentials Stored in sessionStorage (Not Truly Secure)
**Location**: Lines 2195–2199
**Severity**: MEDIUM (Design Issue)

The code stores the username and password in `sessionStorage`:
```javascript
sessionStorage.setItem('sn_username', username);
sessionStorage.setItem('sn_password', password);
```

`sessionStorage` is cleared on tab close, but it is still accessible to any JavaScript in the page, including third-party scripts or XSS payloads.

**Impact**: If the app is vulnerable to XSS, an attacker can steal credentials. Also, if the user pastes a malicious link while logged in, that link's script could access `sessionStorage`.

**Recommendation**:
- For a production app, use OAuth or SSO instead of storing passwords.
- If Basic Auth is required, store only an opaque session token and let the backend manage credential validation.
- Consider using `sessionStorage` only for non-sensitive tokens, not plaintext passwords.

---

### 4. No Network Timeout for Several Long-Running Fetches
**Location**: Lines 2342–2383 (fetchTickets), 2685–2718 (fetchTimeline), 2808–2826 (loadCustomersScreen), 3802–3852 (loadCalendarScreen)
**Severity**: MEDIUM

The main API calls (`fetchTickets`, `fetchCaseDetail`, `fetchTimeline`, `loadCustomersScreen`, `loadCalendarScreen`) lack AbortController timeouts, unlike the Catalyst Center call (line 4175–4191).

If ServiceNow is slow or unresponsive, users will see a spinner forever with no way to cancel or retry automatically.

**Impact**: Poor UX; users may think the app is frozen.

**Recommendation**: Add 10–15 second timeouts to all fetch calls:
```javascript
async function fetchTickets(filterState) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 15000);
  try {
    const res = await fetch(url, {
      headers: { ... },
      signal: ctrl.signal
    });
    ...
  } catch (err) {
    if (err.name === 'AbortError') {
      // show timeout message
    }
    ...
  } finally {
    clearTimeout(timer);
  }
}
```

---

## High-Priority Issues

### 5. Race Condition in Calendar Date Picker
**Location**: Lines 3779–3795 (pickerPickDay)
**Severity**: MEDIUM

The code correctly calls `closeCalDayPanel()` before setting `_cal.selectedDay`, but the order is critical and fragile. If a developer reorders these lines, the state will be corrupted.

**Current (correct)**:
```javascript
closeCalDayPanel();        // clears _cal.selectedDay
// ...
_cal.selectedDay = d.getDate();
```

**Impact**: Subtle bugs if maintainers don't understand the order dependency.

**Recommendation**: Add a comment explaining why this order matters, and consider refactoring to avoid implicit state coupling:
```javascript
function pickerPickDay(year, month, day) {
  const d = new Date(year, month, day);
  // ... normalization ...

  // CRITICAL: closeCalDayPanel() must be called BEFORE setting _cal.selectedDay
  // because closeCalDayPanel() nulls it. Failing to maintain this order
  // will cause the panel to remain visible on the next render.
  closeCalDayPanel();
  closeCalPicker();

  _cal.year = d.getFullYear();
  _cal.month = d.getMonth();
  _cal.selectedDay = d.getDate();

  loadCalendarScreen();
}
```

---

### 6. selectedDay Comparison Logic Error
**Location**: Line 4024
**Severity**: MEDIUM

```javascript
function selectCalDay(dateStr) {
  if (_cal.selectedDay === dateStr) {  // dateStr is "YYYY-MM-DD", _cal.selectedDay is int
    closeCalDayPanel();
    return;
  }
```

`_cal.selectedDay` is an integer (day of month: 1–31), but `dateStr` is a string like `"2026-03-15"`. This comparison will always be false, so the toggle-off behavior never works.

**Impact**: Users can't deselect a day by clicking it again; they must click a different day or navigate away.

**Recommendation**: Compare the full date string:
```javascript
const selectedDateStr = _cal.selectedDay && _cal.year && _cal.month
  ? calDateStr(new Date(_cal.year, _cal.month, _cal.selectedDay))
  : null;
if (selectedDateStr === dateStr) {
  closeCalDayPanel();
  return;
}
```

---

### 7. Memory Leak: Event Listener Never Cleaned Up
**Location**: Line 4798–4800
**Severity**: LOW

The global click event listener (line 3798–3800) closes the calendar picker when clicking outside:
```javascript
document.addEventListener('click', e => {
  if (!e.target.closest('.cal-picker-wrap')) closeCalPicker();
}, true);
```

This listener is never removed and fires on every page click. While not a functional bug for a single-page app, it's inefficient and could cause issues if the app is used for extended periods or if the code is adapted for use in a larger SPA.

**Impact**: Minimal for this demo, but poor practice.

**Recommendation**: Use event delegation with cleanup:
```javascript
const GLOBAL_CLICK_HANDLER = (e) => {
  if (!e.target.closest('.cal-picker-wrap')) closeCalPicker();
};
// Add on picker open, remove on close
function toggleCalPicker() {
  const drop = document.getElementById('cal-picker-drop');
  if (drop.classList.contains('open')) {
    drop.classList.remove('open');
    document.removeEventListener('click', GLOBAL_CLICK_HANDLER, true);
  } else {
    document.addEventListener('click', GLOBAL_CLICK_HANDLER, true);
  }
}
```

---

## Medium-Priority Issues

### 8. Missing Error Context in Calendar Loading
**Location**: Line 3848–3851
**Severity**: MEDIUM

When the calendar fetch fails, the error message is embedded in HTML but not properly escaped:
```javascript
`<div class="list-error"><strong>Could not load calendar</strong>${escHtml(err.message)}<br>
 <button class="retry-btn" onclick="loadCalendarScreen(true)">Retry</button></div>`
```

If `err.message` somehow contains HTML (unlikely but possible from custom errors), it would render unsafely.

**Recommendation**: Ensure the entire block is escaped:
```javascript
const errMsg = escHtml(err?.message || 'Unknown error');
const html = `<div class="list-error">
  <strong>Could not load calendar</strong>${errMsg}<br>
  <button class="retry-btn" onclick="loadCalendarScreen(true)">Retry</button>
</div>`;
```

---

### 9. Avatar Text Truncation Without Fallback
**Location**: Lines 2293–2297 (getInitials)
**Severity**: LOW

```javascript
function getInitials(first, last, fallback) {
  if (first && last) return (first[0] + last[0]).toUpperCase();
  if (first)         return first.slice(0,2).toUpperCase();
  return fallback.slice(0,2).toUpperCase();
}
```

If `fallback` is undefined or not a string, `.slice()` will throw. This could happen if `sn_username` is empty.

**Impact**: App crash if login data is malformed.

**Recommendation**:
```javascript
function getInitials(first, last, fallback) {
  if (first && last) return (first[0] + last[0]).toUpperCase();
  if (first)         return first.slice(0, 2).toUpperCase();
  return (fallback || 'XX').slice(0, 2).toUpperCase();
}
```

---

### 10. Async/Await Inconsistency
**Location**: Lines 2301–2308 (refreshCases), various fetch calls
**Severity**: LOW

The code mixes async/await with `.then()/.catch()` patterns, making it harder to read and maintain.

**Example**:
```javascript
// Line 554–558: .then/.catch
fetch(url, { headers: { ... } })
  .then(r => r.json())
  .then(u => { ... })
  .catch(() => { ... });

// Line 2685–2718: async/await + try/catch
async function fetchTimeline(sysId) {
  try {
    const res = await fetch(url, { ... });
    ...
  } catch (err) { ... }
}
```

**Recommendation**: Standardize on async/await throughout for consistency and readability.

---

### 11. Deterministic Hash Function for Mock Data
**Location**: Lines 3011–3017 (_hash)
**Severity**: LOW (Design, not a bug)

The `_hash()` function uses a simple algorithm:
```javascript
function _hash(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(31, h) + str.charCodeAt(i) | 0;
  }
  return Math.abs(h);
}
```

This is fine for demo data, but collisions are possible, especially with short inputs. If two different ticket numbers hash to the same value, they'll get the same (incorrect) mock Internet/Firewall data.

**Impact**: Demo/training only, but good to document.

**Recommendation**: Add a comment noting the collision possibility and that this is intentional for demo purposes.

---

## Low-Priority Issues

### 12. Unused Variable Assignment
**Location**: Line 3896
**Severity**: LOW (Code quality)

```javascript
const isSelected = dStr === selectedDay;  // used only in className, never checked
```

While not harmful, it's unnecessary. Could be inlined:
```javascript
const cls = ['cal-day',
  !inMonth ? 'other-month' : '',
  isToday ? 'today' : '',
  calDateStr(new Date(year, month, dayNum)) === _cal.selectedDay ? 'selected' : '',
  ...
].filter(Boolean).join(' ');
```

---

### 13. Inconsistent Null Checks
**Location**: Lines 2621–2629 (customer account fetch)
**Severity**: LOW

```javascript
const acct = a.result;
document.getElementById('detail-cust-name').textContent = acct?.name || c.account?.display_value || '—';
```

Uses optional chaining (`?.`) in some places but not others. Consider standardizing:
```javascript
const acct = a.result || {};
document.getElementById('detail-cust-name').textContent = acct.name || c.account?.display_value || '—';
```

---

### 14. Magic Numbers Without Explanation
**Location**: Various
**Severity**: LOW

Examples:
- Line 3424–3432: name generation attempt limit of 200
- Line 4015: double `requestAnimationFrame()` with no explanation
- Line 2897: inline onclick attribute `.includes('selected')` check

**Recommendation**: Add comments explaining the "magic" values:
```javascript
let nameAttempt = 0;
while (usedUsers.has(userName) && nameAttempt < 200) {  // Limit attempts to avoid infinite loop
  lastIdx = (lastIdx + 1) % db.last_names.length;
  userName = db.first_names[firstIdx] + ' ' + db.last_names[lastIdx];
  nameAttempt++;
}
```

---

## Performance Issues

### 15. Large DOM Manipulation in a Loop
**Location**: Lines 4286–4401 (renderListView)
**Severity**: MEDIUM

The network device list is built as a large HTML string with nested collapsible sections. If there are 100+ devices, this could cause layout thrashing.

**Impact**: Slow rendering on large networks.

**Recommendation**: Consider virtualizing the list (show only visible devices) or paginating for large datasets.

---

### 16. Calendar Grid Re-rendered on Every Month Change
**Location**: Lines 3858–3934 (renderCalendar)
**Severity**: LOW

The entire calendar grid is rebuilt even if only the month changed. For a single-file app, this is acceptable, but could be optimized by reusing existing DOM nodes.

**Recommendation**: Not critical for demo use, but consider fragment-based updates if performance becomes an issue.

---

## Security Observations

### 17. Basic Auth Over HTTPS Only (Implied)
**Location**: Lines 2143–2144
**Severity**: MEDIUM

The app uses Basic Auth (`Authorization: Basic base64(...)`), which transmits credentials in base64 (easily decoded). This is safe only over HTTPS.

**Current**:
```javascript
const SN = {
  instance: 'https://dev183548.service-now.com',  // ✓ HTTPS
  ...
};
```

**Good**: The instance URL is HTTPS. However, no validation that the connection is secure.

**Recommendation**: Add a check to prevent running over HTTP in production:
```javascript
if (location.protocol !== 'https:' && !location.hostname.includes('localhost')) {
  alert('This app must run over HTTPS. Please contact your administrator.');
  throw new Error('Insecure connection');
}
```

---

### 18. No CSRF Token Handling
**Location**: Lines 2744–2787 (submitCaseUpdate)
**Severity**: LOW (ServiceNow Responsibility)

The app sends PATCH requests without a CSRF token. This is acceptable if ServiceNow's API is stateless and doesn't use cookies for auth (it uses Basic Auth headers), but it's worth noting.

**Recommendation**: Verify with ServiceNow that the Table API doesn't require CSRF tokens for state-changing operations.

---

## Code Organization & Maintainability

### 19. Global State Scattered Across File
**Location**: Lines 2150–2159, 2503–2505, 2803–2806, etc.
**Severity**: LOW

State variables are declared throughout the file rather than in a single object. This makes it hard to track what state exists and its purpose.

**Current**:
```javascript
let _networkCache = null;
let _networkView = 'list';
let _notifs = [];
let _notifSeen = new Set();
let cachedAssignedTickets = null;
let _custAccounts = [];
let _custSortField = 'name';
let _cal = { year: null, month: null, ... };
```

**Recommendation**: Consider grouping state by feature:
```javascript
const AppState = {
  network: { cache: null, view: 'list' },
  notifs: { list: [], seen: new Set(), lastCheck: null, pollTimer: null },
  tickets: { cached: null, activeFilter: 'today' },
  customers: { accounts: [], sortField: 'name', sortAsc: true, loaded: false },
  calendar: { year: null, month: null, tickets: null, selectedDay: null },
};
```

This improves discoverability and reduces naming collisions.

---

### 20. Long Functions Without Clear Separation
**Location**: Lines 2515–2683 (fetchCaseDetail)
**Severity**: LOW

`fetchCaseDetail()` is ~170 lines and handles multiple concerns:
- Fetching the case
- Rendering multiple sections (assigned_to, SLA, account, contact, CI, travel estimate)
- Managing loading states
- Error handling

**Recommendation**: Break into smaller functions:
```javascript
async function fetchCaseDetail(number) {
  try {
    const c = await loadCaseData(number);
    renderCaseTopbar(c);
    renderCasePriority(c);
    renderCaseCustomer(c);
    await renderInternetSection(c.account?.value);
    // ... etc
  } catch (err) { ... }
}
```

---

## Dead Code & Unused Variables

### 21. Unused State Variable
**Location**: Line 3896
**Severity**: LOW

```javascript
const isSelected = dStr === selectedDay;
```

This is assigned but only used in the className template literal. The assignment is redundant.

---

## Testing Observations

### 22. No Error Boundary for Missing DOM Elements
**Location**: Throughout
**Severity**: MEDIUM

The code assumes DOM elements exist (e.g., `document.getElementById('ticket-list')`). If the HTML changes and an element is renamed or removed, the app will silently fail with `Cannot read property 'textContent' of null`.

**Recommendation**: Add a utility for safe element access:
```javascript
function getElementOrThrow(id) {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing DOM element: ${id}`);
  return el;
}
```

Or use optional chaining:
```javascript
const el = document.getElementById('ticket-list');
if (el) { el.innerHTML = html; }
```

---

## Recommendations Summary

| Category | Count | Examples |
|----------|-------|----------|
| Critical | 1 | Unhandled promise rejections |
| High | 3 | XSS risk, Credential storage, Missing timeouts |
| Medium | 5 | Race conditions, Logic errors, Memory leaks, Large DOM ops |
| Low | 11+ | Code style, unused variables, organization |

**Actionable Priorities**:
1. **Add network timeouts** to all API calls (prevent frozen UI)
2. **Fix XSS vulnerabilities** in onclick handlers (use data attributes)
3. **Add error logging** for failed background requests (inform users)
4. **Fix calendar date selection bug** (line 4024)
5. **Standardize to async/await** (improve readability)
6. **Group state variables** into feature-based objects (maintainability)

---

## Conclusion

The app is **well-suited for demo and training use** with its current architecture. The single-file approach is clean, and the code is generally readable. However, for **production deployment**, you would need to:

1. Implement proper OAuth/SSO instead of Basic Auth with password storage
2. Add comprehensive error handling and user feedback
3. Implement network timeouts on all API calls
4. Fix XSS vulnerabilities in event handlers
5. Add proper logging and monitoring
6. Consider adding unit tests for critical functions

For a demo app running on a dev ServiceNow instance with test credentials, the current implementation is acceptable. Just be aware of the security implications when scaling to production.
