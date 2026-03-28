"""
seed_test_user.py
1. Looks up kkubiak in ServiceNow and copies all roles + group memberships
   to a new test user (test_fieldtech / TestFieldTech1!).
2. Queries existing accounts and creates 6 realistic CSM cases assigned
   to the new test user across different priorities and states.

Usage:
    python seed_test_user.py
"""

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import random

# ─── Config ───────────────────────────────────────────────────────────────────
SN_INSTANCE  = "https://dev183548.service-now.com"
SN_USER      = "admin"
SN_PASS      = "5cO*3QL$rRon"        # ← update if changed

SOURCE_USER  = "kkubiak"             # user to copy permissions from

NEW_USER = {
    "user_name":    "test_fieldtech",
    "first_name":   "Test",
    "last_name":    "Technician",
    "email":        "test.fieldtech@cspire.com",
    "title":        "Field Technician",
    "mobile_phone": "(601) 555-0199",
    "active":       "true",
    "user_password": "TestFieldTech1!",
}

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
AUTH    = HTTPBasicAuth(SN_USER, SN_PASS)

# ─── Case templates ───────────────────────────────────────────────────────────
# priority: 1=Critical 2=High 3=Medium 4=Low
# state:    1=Open 2=Pending 3=Solution Proposed
# category: "repair" | "install"
CASES = [
    {
        "short_description": "Primary WAN circuit down — no internet connectivity",
        "description": "Customer reports complete loss of internet service. WAN1 circuit is showing offline in monitoring. ISP has been notified but on-site verification and possible failover configuration required. Affects all locations on this account.",
        "priority": "1",
        "state": "1",
        "u_ticket_type": "repair",
        "u_scheduled_start_offset_hours": -24,
    },
    {
        "short_description": "Firewall HA pair failover — secondary unit not syncing",
        "description": "HA pair failed over to secondary unit last night during maintenance window. Primary unit is back online but HA sync is failing. Secondary unit shows out-of-sync state in dashboard. On-site investigation needed to restore redundancy.",
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "u_scheduled_start_offset_hours": 0,
    },
    {
        "short_description": "Intermittent packet loss — degraded performance reported",
        "description": "Customer is reporting intermittent packet loss and degraded network performance throughout the business day. Monitoring shows periodic spikes in latency on the primary circuit. Physical layer inspection and ISP escalation may be required.",
        "priority": "2",
        "state": "2",
        "u_ticket_type": "repair",
        "u_scheduled_start_offset_hours": -48,
    },
    {
        "short_description": "Managed switch replacement — end of life hardware",
        "description": "Core managed switch has reached end of life and is exhibiting instability under load. Replacement unit has been staged and is ready for deployment. Planned outage window required for swap. Customer has approved Saturday maintenance window.",
        "priority": "3",
        "state": "1",
        "u_ticket_type": "repair",
        "u_scheduled_start_offset_hours": 24,
    },
    {
        "short_description": "Firewall firmware upgrade — scheduled maintenance",
        "description": "Quarterly firmware upgrade for managed FortiGate firewall. Current version has a known vulnerability patched in the target release. Change request approved. Coordinate with customer IT contact for brief maintenance window during off-hours.",
        "priority": "4",
        "state": "1",
        "u_ticket_type": "repair",
        "u_scheduled_start_offset_hours": 48,
    },
    # ── Install tickets ───────────────────────────────────────────────────────
    {
        "short_description": "New fiber circuit installation — equipment staging and CPE config",
        "description": "New dedicated fiber circuit has been provisioned by carrier. On-site work order to rack and configure the new CPE, patch to firewall WAN2 interface, and validate connectivity before cutover. Coordinate with NOC for IP assignment confirmation.",
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "u_scheduled_start_offset_hours": -72,
    },
    {
        "short_description": "Managed firewall deployment — new FortiGate 200F install",
        "description": "New FortiGate 200F has been staged and shipped to site. On-site technician to rack unit, cable WAN/LAN interfaces, apply baseline config from NOC template, and validate policy set with customer IT contact before going live.",
        "priority": "2",
        "state": "1",
        "u_ticket_type": "install",
        "u_scheduled_start_offset_hours": 8,
    },
    {
        "short_description": "VoIP phone system installation — 12-unit Poly deployment",
        "description": "New VoIP phone system rollout for customer. Twelve Poly VVX 350 desktop phones to be unpacked, PoE-powered via new switch, provisioned against hosted PBX, and tested for inbound/outbound call quality. Coordinate with telecom team for DID porting status.",
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "u_scheduled_start_offset_hours": 32,
    },
    {
        "short_description": "Network infrastructure upgrade — core switch stack replacement",
        "description": "Full core switch stack replacement as part of campus refresh. Three new Catalyst 9300 units to be racked, stacked, configured with VLAN templates, and uplinked to existing fiber distribution layer. Coordinate planned outage window with customer facilities.",
        "priority": "2",
        "state": "1",
        "u_ticket_type": "install",
        "u_scheduled_start_offset_hours": 72,
    },
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def sn_get(table, query="", fields="", limit=50):
    url = f"{SN_INSTANCE}/api/now/table/{table}"
    params = {"sysparm_limit": limit}
    if query:  params["sysparm_query"]  = query
    if fields: params["sysparm_fields"] = fields
    r = requests.get(url, auth=AUTH, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json().get("result", [])


def sn_post(table, payload):
    url = f"{SN_INSTANCE}/api/now/table/{table}"
    r = requests.post(url, auth=AUTH, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()["result"]


def sn_patch(table, sys_id, payload):
    url = f"{SN_INSTANCE}/api/now/table/{table}/{sys_id}"
    r = requests.patch(url, auth=AUTH, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()["result"]


def sn_time(offset_hours):
    """ServiceNow datetime string offset from now."""
    dt = datetime.utcnow() + timedelta(hours=offset_hours)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():

    # ── 1. Look up source user ────────────────────────────────────────────────
    print(f"\n── Looking up source user: {SOURCE_USER}")
    users = sn_get("sys_user", f"user_name={SOURCE_USER}", "sys_id,name,user_name")
    if not users:
        print(f"  ERROR: User '{SOURCE_USER}' not found.")
        return
    source = users[0]
    source_id = source["sys_id"]
    print(f"  ✓ Found: {source['name']}  sys_id={source_id}")

    # ── 2. Get source user's roles ────────────────────────────────────────────
    print(f"\n── Fetching roles for {SOURCE_USER}")
    role_records = sn_get("sys_user_has_role", f"user={source_id}", "role,role.name")
    role_ids = [r["role"]["value"] for r in role_records if r.get("role")]
    print(f"  ✓ Found {len(role_ids)} role(s): {[r.get('role.name', r['role']['value']) for r in role_records]}")

    # ── 3. Get source user's group memberships ────────────────────────────────
    print(f"\n── Fetching group memberships for {SOURCE_USER}")
    group_records = sn_get("sys_user_grmember", f"user={source_id}", "group,group.name")
    group_ids = [g["group"]["value"] for g in group_records if g.get("group")]
    print(f"  ✓ Found {len(group_ids)} group(s): {[g.get('group.name', g['group']['value']) for g in group_records]}")

    # ── 4. Create (or reuse) test user ────────────────────────────────────────
    print(f"\n── Creating test user: {NEW_USER['user_name']}")
    existing = sn_get("sys_user", f"user_name={NEW_USER['user_name']}", "sys_id,name")
    if existing:
        new_id = existing[0]["sys_id"]
        print(f"  ℹ  User already exists — reusing sys_id={new_id}")
    else:
        new_rec = sn_post("sys_user", NEW_USER)
        new_id  = new_rec["sys_id"]
        print(f"  ✓ Created  sys_id={new_id}")
        print(f"  ✓ Username: {NEW_USER['user_name']}  Password: {NEW_USER['user_password']}")

    # ── 5. Copy roles ─────────────────────────────────────────────────────────
    print(f"\n── Assigning roles to test user")
    existing_roles = sn_get("sys_user_has_role", f"user={new_id}", "role")
    existing_role_ids = {r["role"]["value"] for r in existing_roles if r.get("role")}
    for role_id in role_ids:
        if role_id in existing_role_ids:
            print(f"  ↷  Role {role_id} already assigned — skipping")
            continue
        try:
            sn_post("sys_user_has_role", {"user": new_id, "role": role_id})
            print(f"  ✓ Assigned role {role_id}")
        except Exception:
            print(f"  ↷  Role {role_id} — skipped (conflict or no-op)")

    # ── 6. Copy group memberships ─────────────────────────────────────────────
    print(f"\n── Assigning group memberships to test user")
    existing_groups = sn_get("sys_user_grmember", f"user={new_id}", "group")
    existing_group_ids = {g["group"]["value"] for g in existing_groups if g.get("group")}
    for group_id in group_ids:
        if group_id in existing_group_ids:
            print(f"  ↷  Group {group_id} already assigned — skipping")
            continue
        sn_post("sys_user_grmember", {"user": new_id, "group": group_id})
        print(f"  ✓ Added to group {group_id}")

    # ── 7. Fetch existing accounts to assign cases to ─────────────────────────
    print(f"\n── Fetching accounts for case assignment")
    accounts = sn_get("customer_account", "active=true^ORDERBYname", "sys_id,name,number", limit=20)
    if not accounts:
        print("  ERROR: No accounts found. Run seed_servicenow.py first.")
        return
    print(f"  ✓ Found {len(accounts)} accounts")

    # ── 8. Fetch primary location + contact per account ───────────────────────
    contacts_by_account = {}
    locations_by_account = {}
    for acct in accounts:
        aid = acct["sys_id"]
        contacts = sn_get("customer_contact", f"account={aid}", "sys_id,name", limit=1)
        if contacts:
            contacts_by_account[aid] = contacts[0]["sys_id"]
        # Prefer primary location from account_address_relationship
        rels = sn_get("account_address_relationship",
                      f"account={aid}^is_primary=true",
                      "location", limit=1)
        if rels and rels[0].get("location"):
            locations_by_account[aid] = rels[0]["location"]["value"]
        else:
            # Fall back to any location for this account
            rels = sn_get("account_address_relationship",
                          f"account={aid}", "location", limit=1)
            if rels and rels[0].get("location"):
                locations_by_account[aid] = rels[0]["location"]["value"]

    # ── 9. Patch any existing cases for this user that are missing a location ──
    print(f"\n── Patching existing cases missing a service address")
    existing_cases = sn_get("sn_customerservice_case",
                            f"assigned_to={new_id}^locationISEMPTY",
                            "sys_id,number,account", limit=50)
    patched = 0
    for case in existing_cases:
        acct_val = case.get("account")
        acct_id  = acct_val["value"] if isinstance(acct_val, dict) else acct_val
        loc_id   = locations_by_account.get(acct_id)
        if loc_id:
            sn_patch("sn_customerservice_case", case["sys_id"], {"location": loc_id})
            print(f"  ✓ Patched {case['number']} with location")
            patched += 1
        else:
            print(f"  ↷  {case['number']} — no location found for account, skipping")
    if patched == 0:
        print("  ℹ  No existing cases needed patching")

    # ── 10. Create new cases ──────────────────────────────────────────────────
    print(f"\n── Creating cases assigned to {NEW_USER['user_name']}")
    created_cases = []

    for i, case_tmpl in enumerate(CASES):
        acct       = accounts[i % len(accounts)]
        acct_id    = acct["sys_id"]
        contact_id = contacts_by_account.get(acct_id, "")
        loc_id     = locations_by_account.get(acct_id, "")

        payload = {
            "short_description": case_tmpl["short_description"],
            "description":       case_tmpl["description"],
            "priority":          case_tmpl["priority"],
            "state":             case_tmpl["state"],
            "u_ticket_type":     case_tmpl.get("u_ticket_type", "repair"),
            "account":           acct_id,
            "assigned_to":       new_id,
            "u_scheduled_start": sn_time(case_tmpl["u_scheduled_start_offset_hours"]),
        }
        if contact_id: payload["contact"]  = contact_id
        if loc_id:     payload["location"] = loc_id

        rec = sn_post("sn_customerservice_case", payload)
        cat_label = case_tmpl.get("u_ticket_type", "repair").upper()
        print(f"  ✓ {rec.get('number','—')}  [{['','Critical','High','Medium','Low'][int(case_tmpl['priority'])]}]  [{cat_label}]  {acct['name']}")
        created_cases.append(rec.get("number", "—"))

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n\n══ Done ══════════════════════════════════════════")
    print(f"Test user : {NEW_USER['user_name']}")
    print(f"Password  : {NEW_USER['user_password']}")
    print(f"sys_id    : {new_id}")
    print(f"Patched   : {patched} existing case(s)")
    print(f"\nNew cases created: {', '.join(created_cases)}")
    print(f"\nLog in at https://dev183548.service-now.com with the credentials above.")


if __name__ == "__main__":
    main()
