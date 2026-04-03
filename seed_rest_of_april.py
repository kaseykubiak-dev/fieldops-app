"""
seed_rest_of_april.py
Creates 38 CSM cases (mix of installs and repairs) covering the
remaining weekdays of April 2026: April 6–30, Mon–Fri only.
All cases assigned to test_fieldtech, scheduled between 8:00–16:30 CT.

Usage:
    python seed_rest_of_april.py
"""

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# ── Config ────────────────────────────────────────────────────────────────────
SN_INSTANCE = "https://dev183548.service-now.com"
SN_USER     = "admin"
SN_PASS     = "5cO*3QL$rRon"

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
AUTH    = HTTPBasicAuth(SN_USER, SN_PASS)

_CENTRAL = ZoneInfo("America/Chicago")


def sn_datetime_cst(date_str, local_hour, local_minute=0):
    """Convert a local Central time string to UTC for ServiceNow (YYYY-MM-DD HH:MM:SS)."""
    y, m, d = int(date_str[:4]), int(date_str[5:7]), int(date_str[8:10])
    local_dt = datetime(y, m, d, local_hour, local_minute, 0, tzinfo=_CENTRAL)
    utc_dt   = local_dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%d %H:%M:%S")


# ── Case definitions — sched: ("YYYY-MM-DD", hour, minute) ────────────────────
CASES = [

    # ══ Week of April 6 ══════════════════════════════════════════════════════

    # Monday April 6
    {
        "short_description": "Internet outage — primary fiber circuit down, no WAN link",
        "description": (
            "Customer is reporting a complete internet outage as of this morning. CPE shows no WAN link light "
            "and the NOC has confirmed the fiber hand-off is not passing signal. On-site technician to inspect "
            "CPE, ONT, and hand-off patch point, test for physical damage along the demarc run, and coordinate "
            "with NOC for fiber plant inspection if physical layer checks out clean at the premises."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-06", 8, 0),
    },
    {
        "short_description": "Managed switch installation — conference room AV network segment",
        "description": (
            "Customer has approved a separate VLAN and managed switch for the conference room AV network to "
            "isolate presentation traffic from the corporate LAN. Cisco SG350-10 has been staged. On-site work "
            "to rack the switch in the IDF, configure access and trunk ports per NOC-provided VLAN map, patch "
            "HDMI extender and display endpoints, and verify traffic isolation with customer IT before sign-off."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-06", 13, 0),
    },

    # Tuesday April 7
    {
        "short_description": "Fiber CPE installation — new business service activation",
        "description": (
            "New business customer activation on dedicated fiber. Carrier provisioning confirmed by NOC. "
            "On-site technician to install CPE, connect fiber hand-off from ONT to WAN port, verify IP "
            "assignment from NOC DHCP, and run download/upload speed validation per service tier SLA. "
            "Customer IT contact will be on-site for LAN-side handoff and internal routing confirmation."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-07", 9, 0),
    },
    {
        "short_description": "Wi-Fi dead zones — AP roaming failure on second floor",
        "description": (
            "Multiple employees on the second floor are experiencing dropped connections when moving between "
            "conference rooms. Investigation suggests two APs are not participating in fast BSS transition. "
            "On-site technician to inspect AP placement and signal overlap, review WLC roaming configuration, "
            "check for mismatched 802.11r/k/v settings, and confirm client steering thresholds are correct."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-07", 14, 0),
    },

    # Wednesday April 8
    {
        "short_description": "VPN tunnel down — remote branch cannot reach HQ resources",
        "description": (
            "Branch office VPN tunnel has been down since late yesterday. Remote staff cannot access internal "
            "file shares, ERP system, or print services. NOC confirms IKE phase 1 is completing but phase 2 "
            "negotiation is failing. On-site technician to inspect firewall config, confirm pre-shared key "
            "integrity, review phase 2 proposals, and coordinate test with HQ NOC for bring-up."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-08", 8, 30),
    },
    {
        "short_description": "Security camera system — eight-camera NVR deployment",
        "description": (
            "Customer has approved an eight-camera IP security system for parking lot and entry coverage. "
            "Hikvision cameras and NVR have been staged and shipped. On-site work to mount cameras per "
            "approved placement diagram, run Cat6 drops to each location, terminate and test PoE, configure "
            "NVR recording schedule and motion zones, and demonstrate remote viewing access to customer."
        ),
        "priority": "4",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-08", 13, 30),
    },

    # Thursday April 9
    {
        "short_description": "FortiGate firewall installation — new retail branch site",
        "description": (
            "New retail branch requires managed firewall with SD-WAN capability. FortiGate 60F has been "
            "pre-staged by NOC with base policy template. On-site technician to rack unit, terminate ISP "
            "circuit on WAN1, patch internal switch on LAN, validate SD-WAN tunnel formation to hub firewall, "
            "and confirm internet access and POS network reachability before leaving site."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-09", 8, 0),
    },
    {
        "short_description": "Slow upload speeds — cable circuit throttled, upstream investigation",
        "description": (
            "Customer reports upload speeds consistently at 10% of contracted tier. Download is unaffected. "
            "NOC remotely confirmed upstream power levels are marginal on the cable plant. On-site technician "
            "to inspect cable modem signal levels, inspect coax splitters and terminations at demarc, replace "
            "suspect splitter, and re-run speed tests before and after each change to isolate root cause."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-09", 13, 30),
    },

    # Friday April 10
    {
        "short_description": "Network loop causing broadcast storm — access layer switch",
        "description": (
            "NOC alerted to a broadcast storm condition originating from the customer's access layer. "
            "Spanning tree is not converging on one segment. Customer staff report intermittent connectivity. "
            "On-site technician to identify the loop source (likely a rogue hub or patch error), disable the "
            "offending port, verify STP root bridge config, and enable BPDU Guard on all access ports."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-10", 8, 30),
    },
    {
        "short_description": "VoIP system deployment — 12-phone Poly setup and provisioning",
        "description": (
            "Customer is migrating from legacy PBX to hosted VoIP. Twelve Poly Edge E400 phones have been "
            "shipped to site. On-site technician to unbox and stage phones, connect each to PoE switch drop, "
            "provision via provisioning server URL, validate extension dial plan and SIP trunk registration, "
            "and walk customer through basic phone operation before completing work order."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-10", 13, 0),
    },

    # ══ Week of April 13 ═════════════════════════════════════════════════════

    # Monday April 13
    {
        "short_description": "CPE replacement — cable modem hardware failure confirmed by NOC",
        "description": (
            "NOC has confirmed the customer's cable modem is no longer provisioning after repeated "
            "reboot attempts. Replacement unit has been pre-provisioned and is ready to swap. On-site "
            "technician to swap modem, re-terminate coax at the demarc, confirm DOCSIS provisioning "
            "with NOC, and validate internet connectivity before closing the work order."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-13", 8, 0),
    },
    {
        "short_description": "Outdoor wireless AP installation — parking lot coverage expansion",
        "description": (
            "Customer requires outdoor Wi-Fi coverage for the vehicle lot and loading dock. Two Cisco "
            "Catalyst 9124 outdoor APs have been approved and staged. On-site work to mount APs on poles "
            "per survey diagram, run conduit-protected Cat6 drops to nearest IDF, terminate and test PoE, "
            "and onboard to existing DNA Center managed WLC. Verify signal levels at the far lot edge."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-13", 13, 0),
    },

    # Tuesday April 14
    {
        "short_description": "SD-WAN edge appliance — secondary site failover configuration",
        "description": (
            "Second branch site is being brought under the SD-WAN umbrella for active-passive failover. "
            "Fortinet 60F edge appliance has been staged. On-site technician to rack and cable unit, apply "
            "NOC-provided SD-WAN policy template, validate ADVPN tunnel formation to hub, confirm policy "
            "routing and failover behavior with a manual primary-link-down test, and document site config."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-14", 9, 0),
    },
    {
        "short_description": "Intermittent packet loss — fiber hand-off investigation",
        "description": (
            "Customer is experiencing intermittent packet loss (2–8%) throughout the business day. NOC "
            "monitoring shows periodic drops on the fiber circuit. On-site technician to inspect SFP "
            "transceivers and patch cables at the CPE and hand-off point, clean fiber connectors, check "
            "for micro-bends in the interior fiber run, and coordinate an ISP loop test if plant is suspect."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-14", 14, 0),
    },

    # Wednesday April 15
    {
        "short_description": "Phone system offline — SIP trunk registration failure",
        "description": (
            "All outbound and inbound calls have been failing since early morning. SIP trunk is showing "
            "401 Unauthorized from the carrier. On-site technician to verify SIP credentials on the "
            "on-premise PBX, check for any recent firewall policy changes blocking SIP/RTP traffic, "
            "confirm NAT rules for the SIP ALG, and coordinate test calls with the SIP carrier."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-15", 8, 0),
    },
    {
        "short_description": "Cat6 drop installation — 10 new workstation positions",
        "description": (
            "Office expansion has added 10 new desks requiring data drops. Runs range from 40 to 180 feet "
            "from the IDF. On-site technician to pull Cat6 through existing conduit and ceiling space, "
            "terminate at keystone jacks at the desk and patch panel at the IDF, label per naming convention, "
            "test end-to-end continuity on all 10 drops, and update the physical plant documentation."
        ),
        "priority": "4",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-15", 13, 30),
    },

    # Thursday April 16
    {
        "short_description": "UPS installation — battery backup for server room critical equipment",
        "description": (
            "Customer has approved an APC Smart-UPS 3000VA for the server room to protect the core switch, "
            "firewall, and NAS from power events. Unit has been staged. On-site technician to rack the UPS, "
            "transfer power feeds for critical equipment, verify runtime with simulated load test, configure "
            "network management card for NOC SNMP monitoring, and document connected load inventory."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-16", 8, 30),
    },
    {
        "short_description": "DHCP scope exhausted — clients unable to obtain IP address",
        "description": (
            "Multiple workstations and mobile devices are getting APIPA addresses. Customer reports scope "
            "was sized for 50 hosts but headcount has grown. On-site technician to access the DHCP server "
            "(on-prem Windows Server), expand the scope range, reduce lease time to reclaim stale leases, "
            "and optionally split the LAN into two subnets if the customer approves future-proofing scope."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-16", 13, 0),
    },

    # Friday April 17
    {
        "short_description": "Switch port errors — high CRC count on core uplink, possible bad cable",
        "description": (
            "NOC SNMP monitoring alerted on elevated CRC errors on the uplink port between the access and "
            "core switches. Error rate is increasing over 24 hours. On-site technician to inspect the "
            "patch cable and SFP on both ends of the uplink, swap with a known-good cable, and re-check "
            "error counters after 30 minutes to confirm whether issue is physical or interface-related."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-17", 9, 0),
    },
    {
        "short_description": "Cable broadband activation — new service install, business class",
        "description": (
            "New customer onboarding for C Spire business cable broadband. DOCSIS modem has been "
            "pre-provisioned. On-site technician to locate demarc, install and terminate coax, connect "
            "modem and verify provisioning with NOC, install customer-premise router, and validate "
            "speed tier with download/upload test. Provide customer with support contact and account info."
        ),
        "priority": "4",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-17", 14, 0),
    },

    # ══ Week of April 20 ═════════════════════════════════════════════════════

    # Monday April 20
    {
        "short_description": "Complete office outage — power surge damaged CPE and switch",
        "description": (
            "Customer experienced a power surge over the weekend that has taken down the CPE and the "
            "access layer switch. No connectivity for approximately 40 staff. Replacement CPE and a "
            "loaner switch have been pre-staged by NOC. On-site technician to swap both units, re-terminate "
            "all cabling, confirm WAN provisioning, and validate internal LAN before restoring full service."
        ),
        "priority": "1",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-20", 8, 0),
    },
    {
        "short_description": "Network rack installation — new server room buildout",
        "description": (
            "Customer is building out a new server room as part of an office relocation. A 42U rack, "
            "patch panel, and horizontal cable management have been delivered. On-site technician to "
            "assemble and anchor the rack, install patch panel and management hardware, dress and label "
            "all cable runs to the rack, and confirm power receptacles are ready for equipment install "
            "by the customer's IT team."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-20", 13, 30),
    },

    # Tuesday April 21
    {
        "short_description": "4G LTE backup circuit installation — WAN failover redundancy",
        "description": (
            "Customer has approved addition of an LTE failover circuit to complement the primary fiber "
            "connection. Cradlepoint E3000 router with Sierra Wireless modem has been staged. On-site "
            "technician to install and activate SIM, mount unit, connect to SD-WAN appliance secondary "
            "WAN port, configure failover policy, and perform a manual failover test to confirm traffic "
            "shifts correctly when the primary fiber circuit is disabled."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-21", 9, 0),
    },
    {
        "short_description": "Wireless authentication failure — RADIUS server rejecting clients",
        "description": (
            "Corporate SSID clients are being rejected with 802.1X authentication failures. Guest SSID "
            "is unaffected. NOC has confirmed the WLC is reachable but the RADIUS server is returning "
            "Access-Reject. On-site technician to verify NPS/RADIUS server certificate validity, check "
            "Active Directory group membership for affected users, review RADIUS event logs, and test "
            "with a known-good domain account to isolate cert vs. policy issue."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-21", 14, 0),
    },

    # Wednesday April 22
    {
        "short_description": "Fiber cable damage — suspected rodent damage to underground run",
        "description": (
            "Customer is experiencing a fiber outage. NOC has ruled out plant issues at the head-end "
            "and suspects physical damage to the underground fiber run between the street vault and the "
            "building demarc. On-site technician to perform OTDR testing to locate the break, document "
            "findings, and coordinate with the fiber repair crew for splice or re-pull as needed."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-22", 8, 0),
    },
    {
        "short_description": "PoE switch upgrade — supporting new IP camera system expansion",
        "description": (
            "Existing switch does not have sufficient PoE budget for the planned IP camera expansion. "
            "Replacement Cisco SG350-28P (195W PoE budget) has been staged. On-site technician to "
            "backup existing config, swap the switch during approved window, verify all uplinks and "
            "access ports come up correctly, confirm PoE power delivery to cameras and phones, "
            "and validate VLAN segmentation before completing the work order."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-22", 13, 0),
    },

    # Thursday April 23
    {
        "short_description": "Point-to-point wireless bridge — building-to-building fiber alternative",
        "description": (
            "Customer needs connectivity between two buildings 300 meters apart without trenching for "
            "fiber. Ubiquiti airFiber 5XHD point-to-point bridge set has been approved and staged. "
            "On-site technician to mount radios on rooftop mounts at each building, align and optimize "
            "signal (target RSSI above -65 dBm), configure bridge mode, and validate throughput and "
            "latency are within agreed SLA before signing off."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-23", 8, 30),
    },
    {
        "short_description": "VoIP jitter and call quality issues — QoS misconfiguration suspected",
        "description": (
            "Customer reports poor call quality with audible jitter and occasional one-way audio. "
            "Issue began after a recent firewall firmware update. On-site technician to review DSCP "
            "markings on VoIP traffic end-to-end, verify QoS policies on the firewall and access "
            "switch have not been reset to default, check SIP ALG status, and run a jitter/MOS "
            "test using a softphone before and after applying correct QoS config."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-23", 14, 0),
    },

    # Friday April 24
    {
        "short_description": "DNS resolution failures — internal DNS server unreachable",
        "description": (
            "Workstations are unable to resolve internal hostnames. Internet works when using IP directly. "
            "The internal Windows DNS server appears to be online but unreachable from the LAN segment. "
            "On-site technician to check VLAN routing between the workstation and server VLANs, inspect "
            "any recent firewall ACL changes that may be blocking DNS (UDP/TCP 53), and verify the "
            "DNS service is running and listening on the correct interface."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-24", 8, 0),
    },
    {
        "short_description": "Smart hands — NOC-directed emergency router configuration",
        "description": (
            "NOC requires on-site smart hands to apply a corrected routing configuration to the customer "
            "edge router. Remote access is unavailable due to a management VLAN misconfiguration. "
            "On-site technician to connect via console cable, relay current running config to NOC, "
            "apply NOC-dictated commands, confirm management access is restored, and verify all traffic "
            "paths are functional before disconnecting."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-24", 13, 30),
    },

    # ══ Week of April 27 ═════════════════════════════════════════════════════

    # Monday April 27
    {
        "short_description": "Backup LTE circuit down — modem not re-establishing connection",
        "description": (
            "Customer's backup LTE circuit has been offline for two days. Primary fiber is up, but "
            "the LTE modem is stuck in a registration loop per NOC remote diagnostics. On-site "
            "technician to inspect SIM seating and antenna connections, perform factory reset if "
            "needed, re-provision the SIM with carrier, and confirm failover circuit is active "
            "and passing traffic before closing."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-27", 8, 0),
    },
    {
        "short_description": "Cisco Catalyst 9300 installation — core switch layer refresh",
        "description": (
            "Legacy core switch is being replaced with a Cisco Catalyst 9300-48P as part of a "
            "campus refresh. NOC has pre-staged the config. On-site technician to perform physical "
            "swap during approved maintenance window, re-terminate all uplinks and server connections, "
            "verify LACP port channels, confirm inter-VLAN routing and STP root placement, and "
            "validate full connectivity before returning the site to production."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-27", 13, 0),
    },

    # Tuesday April 28
    {
        "short_description": "New fiber circuit handoff — ISP provisioning confirmed, CPE install",
        "description": (
            "ISP has completed provisioning of a new 1Gbps dedicated fiber circuit. On-site "
            "technician to install CPE at the demarc, connect the fiber hand-off from the ONT, "
            "confirm IP assignment and routing with NOC, patch CPE WAN port to the customer "
            "firewall, and run speed tier validation tests. Customer IT contact will handle "
            "LAN-side routing changes after handoff is confirmed."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-28", 9, 0),
    },
    {
        "short_description": "Network performance degradation — duplex mismatch on uplink",
        "description": (
            "Customer reports sluggish network performance affecting all users. NOC has identified "
            "high input error rates on the uplink between the access switch and the router, consistent "
            "with a duplex mismatch. On-site technician to verify interface duplex and speed settings "
            "on both ends of the uplink, force full-duplex/1G where auto-negotiation appears to be "
            "failing, clear error counters, and monitor for 15 minutes to confirm resolution."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-28", 14, 0),
    },

    # Wednesday April 29
    {
        "short_description": "Firewall policy misconfiguration — business apps blocked after update",
        "description": (
            "Following a NOC-pushed firmware update, customer reports that Microsoft 365, Salesforce, "
            "and several other SaaS applications are unreachable. On-site technician to review the "
            "firewall policy changes introduced in the update, identify any application control or "
            "SSL inspection rules that may be incorrectly blocking traffic, apply corrective policy, "
            "and validate affected applications are fully accessible before completing the ticket."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-29", 8, 30),
    },
    {
        "short_description": "IP phone deployment — 8-unit expansion for new office wing",
        "description": (
            "Office expansion has added an 8-desk wing requiring phone service. Eight Poly Edge E350 "
            "phones have been staged and shipped. On-site technician to connect phones to existing "
            "PoE drops, provision via the hosted PBX provisioning server, assign extensions per "
            "customer-provided dial plan, confirm ring groups and voicemail are functioning, "
            "and walk the office manager through basic phone features before sign-off."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-29", 13, 30),
    },

    # Thursday April 30
    {
        "short_description": "Campus Wi-Fi expansion — 6 additional APs for new building wing",
        "description": (
            "New building wing has been added to the customer campus with no wireless coverage. "
            "Six Cisco Catalyst 9130 APs have been approved and shipped. On-site technician to "
            "mount APs per survey placement diagram, terminate Cat6 drops at each location and "
            "at the IDF patch panel, onboard APs to DNA Center, verify roaming overlap with "
            "the existing campus SSID, and confirm full signal coverage at all designated "
            "work areas before closing the work order."
        ),
        "priority": "3",
        "state": "1",
        "u_ticket_type": "install",
        "sched": ("2026-04-30", 8, 0),
    },
    {
        "short_description": "CPE firmware update — critical security patch, on-site required",
        "description": (
            "NOC has identified a critical CVE affecting the customer's CPE firmware. Remote update "
            "failed due to management interface instability. On-site technician to connect via console, "
            "perform manual firmware upgrade using USB/TFTP method per NOC runbook, verify device "
            "comes up on new firmware version, confirm WAN link and routing are stable, and notify "
            "NOC of completion so the security audit record can be updated."
        ),
        "priority": "2",
        "state": "1",
        "u_ticket_type": "repair",
        "sched": ("2026-04-30", 14, 0),
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def sn_get(table, query="", fields="", limit=50):
    url    = f"{SN_INSTANCE}/api/now/table/{table}"
    params = {"sysparm_limit": limit}
    if query:  params["sysparm_query"]  = query
    if fields: params["sysparm_fields"] = fields
    r = requests.get(url, auth=AUTH, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json().get("result", [])


def sn_post(table, payload):
    url = f"{SN_INSTANCE}/api/now/table/{table}"
    r   = requests.post(url, auth=AUTH, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()["result"]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    now_central = datetime.now(tz=_CENTRAL)
    print(f"\n-- Local time: {now_central.strftime('%Y-%m-%d %H:%M')} Central")

    # Look up test_fieldtech
    print("\n-- Looking up test_fieldtech user")
    users = sn_get("sys_user", "user_name=test_fieldtech", "sys_id,name")
    if not users:
        print("  ERROR: test_fieldtech not found. Run seed_test_user.py first.")
        return
    tech_id = users[0]["sys_id"]
    print(f"  OK  test_fieldtech  sys_id={tech_id}")

    # Fetch accounts
    print("\n-- Fetching accounts")
    accounts = sn_get("customer_account", "active=true^ORDERBYname", "sys_id,name,number", limit=20)
    if not accounts:
        print("  ERROR: No accounts found. Run seed_servicenow.py first.")
        return
    print(f"  OK  {len(accounts)} accounts found")

    # Fetch contacts and primary locations per account
    contacts_by_account  = {}
    locations_by_account = {}
    for acct in accounts:
        aid      = acct["sys_id"]
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
    print(f"\n-- Creating {len(CASES)} cases for April 6–30, 2026 (weekdays only)")
    created = []
    pri_label = ["", "Critical", "High", "Medium", "Low"]

    for i, tmpl in enumerate(CASES):
        acct       = accounts[i % len(accounts)]
        acct_id    = acct["sys_id"]
        contact_id = contacts_by_account.get(acct_id, "")
        loc_id     = locations_by_account.get(acct_id, "")

        sched_utc = sn_datetime_cst(*tmpl["sched"])
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
        label = pri_label[int(tmpl["priority"])]
        date  = tmpl["sched"][0]
        print(f"  OK  {rec.get('number','—'):<12} [{label:<8}]  [{tmpl['u_ticket_type'].upper():<7}]  {date}  {acct['name']}")
        created.append(rec.get("number", "—"))

    print(f"\n== Done =====================================================")
    print(f"Created {len(created)} cases: {', '.join(created)}")


if __name__ == "__main__":
    main()
