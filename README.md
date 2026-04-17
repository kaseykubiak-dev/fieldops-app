# Delta — Field Operations Tech App

A mobile-first progressive web app built for field technicians managing enterprise service tickets. Delta consolidates ServiceNow CSM ticketing, Cisco Catalyst Center network data, and a Webex Calling/VoIP reference layer into a single unified interface — designed around real workflows from my role as a Voice and Data Technician at C Spire.

Built as a single HTML file (~7,700 lines) with no framework, no build step, and no dependencies beyond a lightweight Node.js CORS proxy for Catalyst Center API access. Runs as a PWA on iPhone directly from the browser — no App Store deployment required.

> **Live demo**: [fieldops-app-production-2ec3.up.railway.app](https://kaseykubiak-dev.github.io/fieldops-app/fieldtech-app.html)
> **Test credentials**: Username `test_fieldtech` / Password `TestFieldTech1!`

---

## Demo
 
![Install workflow — closing a ticket](https://github.com/user-attachments/assets/69715da5-731f-444c-a90e-2bfc9a473c87)
 
<details>
<summary>📡 Catalyst Center — Live Network Data</summary>
<br>
![Catalyst Center network data](https://github.com/user-attachments/assets/7fd42558-9119-4038-89ce-871cef01365f)
 
Live device data pulled from Cisco Catalyst Center via an authenticated Node.js proxy hosted on Railway. Devices are grouped by type and rendered in both list and canvas topology views.
 
</details>
<details>
<summary>🎫 Repair Ticket — Sections & Accordions</summary>
<br>
![Repair ticket screen](https://github.com/user-attachments/assets/128a2d0b-835e-48b7-b618-d123d29f6d5f)
 
Ticket detail view populated via five parallel async ServiceNow sub-fetches — assignee, SLA, account, contact, and CMDB device data. Network infrastructure, firewall, and VoIP sections expand via accordions below.
 
</details>
<details>
<summary>📅 Calendar — Ticket Integration</summary>
<br>
![Calendar tab](https://github.com/user-attachments/assets/11b636f3-5980-4cc7-a840-4c472ced3ce7)
 
Month, week, and agenda views with ticket chips linked directly to ticket detail. Safety inspection and inventory due dates surface as calendar banners automatically.
 
</details>
<details>
<summary>🔧 Tech Tools — Safety & Inventory Tracking</summary>
<br>
![Tech Tools section](https://github.com/user-attachments/assets/c2321812-6c70-4a31-93a5-80cea79fda62)
 
Vehicle inspection, ladder inspection, mileage reporting, and truck stock inventory tracking with configurable reminder frequencies, urgency escalation, and badge indicators on the nav tab.
 
</details>

---

## Why I Built This

Field technicians at C Spire work across multiple disconnected systems on every job — ServiceNow for tickets, separate portals for network equipment, and no unified view of customer context or on-call contacts. Switching between tools on a phone in the field is slow and error-prone.

Delta was built to consolidate that into one mobile-optimized interface. A tech can open a ticket, see the customer's service history and equipment, check their SLA clock, get driving directions, log their travel and on-site status, and close the ticket — without leaving the app. The network screen pulls live device data directly from Cisco Catalyst Center, and the Tech Tools section handles compliance tracking (vehicle and ladder inspections, inventory reports) that technicians would otherwise manage manually.

The app started as a proof-of-concept for internal use and grew into a full-featured tool through iteration based on real field workflows.

---

## Skills Demonstrated

| Skill Area | Implementation |
|---|---|
| **REST API integration** | ServiceNow Table API (CSM Cases, sys_user, task_sla, CMDB), Cisco Catalyst Center via authenticated Node.js proxy, Meraki API architecture with public sandbox key |
| **Network tooling** | Live Catalyst Center device data, canvas-drawn network topology diagram, device grouping by type |
| **VoIP / UC familiarity** | Webex Calling phone model data, extension reference, DECT network device modeling (DBS 110/210, Cisco 6825) |
| **Vanilla JavaScript** | 7,700+ line single-file app, zero framework dependencies, full DOM manipulation, state machine for ticket workflow |
| **Responsive UI / PWA** | iOS PWA config with safe-area inset handling, three responsive breakpoints (mobile/tablet/desktop), pull-to-refresh, bottom nav + top nav switching |
| **ITSM workflow knowledge** | ServiceNow ticket states, SLA urgency tracking with breach detection, 4-state ticket action workflow (travel → on-site → close) |
| **Security practices** | SessionStorage-only credential storage (never localStorage), AbortController timeouts on all API calls, XSS escaping on all API-sourced content |
| **Systems architecture** | Modular screen routing, parallel async sub-fetches, polling with backoff, deterministic mock data layer as drop-in replacement for live APIs |
| **Documentation** | Internal technical README, DECT setup guide authored for C Spire field use |

---

## Planned Integrations

The app is architected with mock/stub layers designed as transparent drop-in replacements for live APIs. The following integrations are planned:

- **Microsoft Graph API — Teams Presence**: The `_teamsPresence()`, `_teamsAvatarHTML()`, and `_teamsChatIconHTML()` functions currently use deterministic mocks. Replacing them requires `POST /communications/getPresencesByUserId` for presence status and `GET /users/{id}/photo/$value` for avatars — both are documented in the code with TODO comments.
- **Live Meraki Dashboard**: The Network screen currently uses Catalyst Center. Meraki Dashboard API integration is structured to replace or augment this with MX/MS/MR device data from the Meraki SDK once sandbox access is stable.
- **Sospes Safety Integration**: Vehicle and ladder inspection tracking currently links to the Sospes app store page. Direct deep-link or API integration would allow completion status to sync back into Delta automatically.
- **Truck Stock Portal**: Inventory reporting links to a placeholder URL pending the real internal tool URL.
- **Live On-Call Data**: On-call schedule and call tree are currently hardcoded demo data, sourced from the weekly management distribution email. A live integration would pull from an internal scheduling system.

---
