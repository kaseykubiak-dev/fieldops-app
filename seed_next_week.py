"""
seed_next_week.py
Creates 10 CSM cases (mix of repairs and installs) for the week of
March 30 – April 3, 2026, assigned to test_fieldtech.

Uses u_scheduled_start so the calendar picks up install/repair times.

Usage:
    python seed_next_week.py
"""

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# --─ Config ------------------------------------------------------------------─
SN_INSTANCE = "https://dev183548.service-now.com"
SN_USER     = "admin"
SN_PASS     = "5cO*3QL$rRon"

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
AUTH    = HTTPBasicAuth(SN_USER, SN_PASS)

_CENTRAL = ZoneInfo("America/Chicago")

# --─ Case definitions — day_offset from today (2026-03-29) --------------------
# sched: (day_offset, local_hour, local_minute)
CASES = [
    # -- Monday March 30 --------------------------------------------------------
    {
        "short_description": "WAN circuit degraded — intermittent packet loss reported",
        "description": (
            "Customer is experiencing intermittent packet loss and elevated latency on the primary WAN circuit. "
            "Monitoring confirms periodic drops throughout peak hours. On-site inspection of CPE, patch cables, "
            "and hand-off interface required. ISP loop test may be needed if physical layer checks out clean."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": (1, 8, 0),
    },
    {
        "short_description": "SD-WAN appliance deployment — new branch site",
        "description": (
            "New SD-WAN appliance (Fortinet 60F) has been staged and shipped to branch location. "
            "On-site work order to rack unit, terminate WAN circuits on WAN1/WAN2, apply NOC-provided "
            "base config, validate tunnel formation to hub, and confirm policy routing with customer IT."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": (1, 13, 30),
    },

    # -- Tuesday March 31 ------------------------------------------------------─
    {
        "short_description": "Fiber circuit CPE installation — carrier provisioning complete",
        "description": (
            "Carrier has confirmed provisioning of new dedicated fiber circuit. On-site technician to "
            "install and configure customer premise equipment, patch fiber hand-off to CPE WAN port, "
            "verify link light and IP assignment from NOC, and perform download/upload speed validation "
            "before signing off on service activation."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": (2, 9, 30),
    },
    {
        "short_description": "VoIP phones dropping calls — PoE switch port investigation",
        "description": (
            "Multiple VoIP phones on the second floor are experiencing dropped calls and registration "
            "failures. Preliminary review suggests a flapping PoE switch port may be cycling power to "
            "the phones. On-site inspection of switch, PoE budget, and phone provisioning logs required."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": (2, 14, 0),
    },

    # -- Wednesday April 1 ------------------------------------------------------
    {
        "short_description": "Core switch failover — redundant uplink not passing traffic",
        "description": (
            "Following a brief power event over the weekend, the core switch stack lost its redundant "
            "uplink. Primary uplink is active but LACP negotiation on the secondary port is failing. "
            "On-site technician to inspect SFP modules, verify cable integrity, and restore LAG/LACP "
            "configuration. Coordinate brief maintenance window with facilities."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": (3, 8, 30),
    },
    {
        "short_description": "Wireless AP expansion — three additional access points",
        "description": (
            "Customer has approved scope expansion to add three Cisco Catalyst 9130 access points "
            "to the warehouse floor to resolve coverage gaps. APs have been staged. On-site work to "
            "mount, run Cat6 drops to nearest IDF, patch to PoE switch, and onboard to existing "
            "WLC/DNA Center. Verify roaming and signal overlap with existing APs."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": (3, 15, 0),
    },

    # -- Thursday April 2 ------------------------------------------------------─
    {
        "short_description": "Managed firewall deployment — FortiGate 100F replacement",
        "description": (
            "End-of-support FortiGate 60E being replaced with new 100F. Replacement unit has been "
            "pre-staged with migrated config by NOC team. On-site technician to perform physical swap "
            "during approved maintenance window, re-terminate WAN/LAN cabling, confirm policy sync, "
            "and validate internet and inter-VLAN routing before cutover sign-off."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "install",
        "sched": (4, 8, 0),
    },
    {
        "short_description": "Backup circuit validation — secondary ISP link not failing over",
        "description": (
            "Customer reported that during a planned failover test last week, traffic did not shift to "
            "the backup cable circuit as expected. SD-WAN policy shows both links healthy. On-site "
            "verification of cable modem provisioning, firewall WAN2 interface config, and manual "
            "failover test required to confirm backup circuit behavior."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": (4, 13, 30),
    },

    # -- Friday April 3 --------------------------------------------------------─
    {
        "short_description": "Network performance audit — intermittent slowdowns reported",
        "description": (
            "Customer has reported recurring slowdowns on internal applications during mid-morning hours. "
            "No active alerts in monitoring. On-site visit to run throughput tests, review switch "
            "utilization and error counters, inspect QoS markings on VoIP traffic, and check for "
            "duplex mismatches or broadcast storm conditions on access layer."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": (5, 9, 0),
    },
    {
        "short_description": "Server room structured cabling — patch panel installation",
        "description": (
            "New 48-port patch panel installation in server room IDF as part of campus refresh. "
            "Technician to terminate existing runs at patch panel, label per customer naming convention, "
            "dress cables with velcro ties, and update physical documentation. Validate end-to-end "
            "continuity on all drops before handing off to customer network team."
        ),
        "priority": "4",
        "state": "1",
        "u_ticket_type": "install",
        "sched": (5, 14, 30),
    },
]

# --─ Helpers ------------------------------------------------------------------

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


def central_utc_offset():
    now_central = datetime.now(_CENTRAL)
    offset_seconds = now_central.utcoffset().total_seconds()
    return -int(offset_seconds / 3600)


def sn_time_cst(day_offset, local_hour, local_minute=0):
    offset = central_utc_offset()
    now = datetime.now(timezone.utc)
    local_dt = (now + timedelta(days=day_offset)).replace(
        hour=local_hour, minute=local_minute, second=0, microsecond=0)
    utc_dt = local_dt + timedelta(hours=offset)
    return utc_dt.strftime("%Y-%m-%d %H:%M:%S")


# --─ Main --------------------------------------------------------------------─

def main():
    offset = central_utc_offset()
    tz_label = "CDT (UTC-5)" if offset == 5 else "CST (UTC-6)"
    now_central = datetime.now(_CENTRAL)
    print(f"\n-- Timezone: {tz_label}  |  Local time: {now_central.strftime('%Y-%m-%d %H:%M')} Central")

    # Look up test_fieldtech
    print(f"\n-- Looking up test_fieldtech user")
    users = sn_get("sys_user", "user_name=test_fieldtech", "sys_id,name")
    if not users:
        print("  ERROR: test_fieldtech not found. Run seed_test_user.py first.")
        return
    tech_id = users[0]["sys_id"]
    print(f"  OK Found test_fieldtech  sys_id={tech_id}")

    # Fetch accounts
    print(f"\n-- Fetching accounts")
    accounts = sn_get("customer_account", "active=true^ORDERBYname", "sys_id,name,number", limit=20)
    if not accounts:
        print("  ERROR: No accounts found. Run seed_servicenow.py first.")
        return
    print(f"  OK Found {len(accounts)} accounts")

    # Fetch contacts and primary locations per account
    contacts_by_account = {}
    locations_by_account = {}
    for acct in accounts:
        aid = acct["sys_id"]
        contacts = sn_get("customer_contact", f"account={aid}", "sys_id", limit=1)
        if contacts:
            contacts_by_account[aid] = contacts[0]["sys_id"]
        rels = sn_get("account_address_relationship",
                      f"account={aid}^is_primary=true", "location", limit=1)
        if rels and rels[0].get("location"):
            locations_by_account[aid] = rels[0]["location"]["value"]
        else:
            rels = sn_get("account_address_relationship",
                          f"account={aid}", "location", limit=1)
            if rels and rels[0].get("location"):
                locations_by_account[aid] = rels[0]["location"]["value"]

    # Create cases
    print(f"\n-- Creating {len(CASES)} cases for March 30 – April 3, 2026")
    created = []

    for i, tmpl in enumerate(CASES):
        acct      = accounts[i % len(accounts)]
        acct_id   = acct["sys_id"]
        contact_id = contacts_by_account.get(acct_id, "")
        loc_id    = locations_by_account.get(acct_id, "")

        sched_utc = sn_time_cst(*tmpl["sched"])
        payload = {
            "short_description": tmpl["short_description"],
            "description":       tmpl["description"],
            "priority":          tmpl["priority"],
            "state":             tmpl["state"],
            "u_ticket_type":     tmpl["u_ticket_type"],
            "account":           acct_id,
            "assigned_to":       tech_id,
            "u_scheduled_start": sched_utc,
        }
        if contact_id: payload["contact"]  = contact_id
        if loc_id:     payload["location"] = loc_id

        rec = sn_post("sn_customerservice_case", payload)
        pri_label = ["", "Critical", "High", "Medium", "Low"][int(tmpl["priority"])]
        print(f"  OK {rec.get('number','—')}  [{pri_label}]  [{tmpl['u_ticket_type'].upper()}]  {sched_utc[:10]}  {acct['name']}")
        created.append(rec.get("number", "—"))

    print(f"\n\n== Done ===================================================")
    print(f"Created {len(created)} cases: {', '.join(created)}")


if __name__ == "__main__":
    main()
