"""
seed_servicenow.py
Populates ServiceNow dev instance with ~12 generated customer accounts,
locations (cmn_location + account_address_relationship), and contacts.

Usage:
    python seed_servicenow.py

Set SN_USER and SN_PASS env vars or edit the credentials below.
"""

import requests
from requests.auth import HTTPBasicAuth

# ─── Config ───────────────────────────────────────────────────────────────────
SN_INSTANCE = "https://dev183548.service-now.com"
SN_USER     = "admin"
SN_PASS     = "5cO*3QL$rRon"

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
AUTH    = HTTPBasicAuth(SN_USER, SN_PASS)

# ─── Account data ─────────────────────────────────────────────────────────────
ACCOUNTS = [
    {
        "name": "Meridian Health Partners",
        "number": "ACC0100",
        "account_type": "Healthcare",
        "street": "4210 Wellness Blvd",
        "city": "Birmingham", "state": "AL", "zip": "35203",
        "phone": "(205) 334-8800",
        "locations": [
            {"name": "Meridian – Main Campus",      "street": "4210 Wellness Blvd",   "city": "Birmingham",  "state": "AL", "zip": "35203", "primary": True},
            {"name": "Meridian – Southside Clinic", "street": "812 Southside Ave",    "city": "Birmingham",  "state": "AL", "zip": "35205", "primary": False},
            {"name": "Meridian – Hoover Satellite", "street": "3301 Lorna Rd",        "city": "Hoover",      "state": "AL", "zip": "35216", "primary": False},
        ],
        "contacts": [
            {"first": "Patricia", "last": "Holloway",  "title": "IT Director",          "email": "p.holloway@meridianhealth.com",  "phone": "(205) 334-8801", "mobile": "(205) 512-0011"},
            {"first": "James",    "last": "Okafor",    "title": "Network Engineer",      "email": "j.okafor@meridianhealth.com",    "phone": "(205) 334-8802", "mobile": "(205) 512-0022"},
            {"first": "Sandra",   "last": "Liu",       "title": "Help Desk Manager",     "email": "s.liu@meridianhealth.com",       "phone": "(205) 334-8803", "mobile": "(205) 512-0033"},
        ],
    },
    {
        "name": "Coastal Logistics Group",
        "number": "ACC0101",
        "account_type": "Logistics",
        "street": "1050 Port Terminal Dr",
        "city": "Mobile", "state": "AL", "zip": "36602",
        "phone": "(251) 441-7700",
        "locations": [
            {"name": "CLG – Port Terminal",      "street": "1050 Port Terminal Dr", "city": "Mobile",    "state": "AL", "zip": "36602", "primary": True},
            {"name": "CLG – Warehouse North",    "street": "2800 Craft Hwy",        "city": "Mobile",    "state": "AL", "zip": "36610", "primary": False},
        ],
        "contacts": [
            {"first": "Derek",  "last": "Marsh",    "title": "VP of Operations",     "email": "d.marsh@coastallogistics.com",    "phone": "(251) 441-7701", "mobile": "(251) 600-1100"},
            {"first": "Tamara", "last": "Nguyen",   "title": "Systems Administrator", "email": "t.nguyen@coastallogistics.com",   "phone": "(251) 441-7702", "mobile": "(251) 600-1101"},
        ],
    },
    {
        "name": "Pinnacle Financial Services",
        "number": "ACC0102",
        "account_type": "Finance",
        "street": "700 Commerce St Suite 1800",
        "city": "Nashville", "state": "TN", "zip": "37203",
        "phone": "(615) 255-9400",
        "locations": [
            {"name": "Pinnacle – HQ Downtown",    "street": "700 Commerce St Suite 1800", "city": "Nashville",  "state": "TN", "zip": "37203", "primary": True},
            {"name": "Pinnacle – Green Hills",    "street": "4015 Hillsboro Pike",        "city": "Nashville",  "state": "TN", "zip": "37215", "primary": False},
            {"name": "Pinnacle – Brentwood",      "street": "1801 Westgate Pkwy",         "city": "Brentwood",  "state": "TN", "zip": "37027", "primary": False},
        ],
        "contacts": [
            {"first": "Marcus",  "last": "Caldwell",  "title": "Chief Information Officer", "email": "m.caldwell@pinnaclefs.com",   "phone": "(615) 255-9401", "mobile": "(615) 330-4400"},
            {"first": "Helen",   "last": "Reyes",     "title": "IT Security Analyst",        "email": "h.reyes@pinnaclefs.com",     "phone": "(615) 255-9402", "mobile": "(615) 330-4401"},
        ],
    },
    {
        "name": "Redstone Manufacturing LLC",
        "number": "ACC0103",
        "account_type": "Manufacturing",
        "street": "500 Industrial Park Rd",
        "city": "Huntsville", "state": "AL", "zip": "35811",
        "phone": "(256) 772-5300",
        "locations": [
            {"name": "Redstone – Plant A",        "street": "500 Industrial Park Rd", "city": "Huntsville",  "state": "AL", "zip": "35811", "primary": True},
            {"name": "Redstone – Plant B",        "street": "620 Industrial Park Rd", "city": "Huntsville",  "state": "AL", "zip": "35811", "primary": False},
        ],
        "contacts": [
            {"first": "Gary",    "last": "Thornton",  "title": "Plant IT Manager",     "email": "g.thornton@redstonemanuf.com",  "phone": "(256) 772-5301", "mobile": "(256) 655-8800"},
            {"first": "Brenda",  "last": "Kim",       "title": "Network Technician",   "email": "b.kim@redstonemanuf.com",       "phone": "(256) 772-5302", "mobile": "(256) 655-8801"},
            {"first": "Troy",    "last": "Patel",     "title": "IT Support Specialist","email": "t.patel@redstonemanuf.com",     "phone": "(256) 772-5303", "mobile": "(256) 655-8802"},
        ],
    },
    {
        "name": "Gulf South Hospitality Group",
        "number": "ACC0104",
        "account_type": "Hospitality",
        "street": "2 Royal St",
        "city": "New Orleans", "state": "LA", "zip": "70130",
        "phone": "(504) 581-4200",
        "locations": [
            {"name": "GSHG – French Quarter Hotel", "street": "2 Royal St",           "city": "New Orleans", "state": "LA", "zip": "70130", "primary": True},
            {"name": "GSHG – Metairie Property",    "street": "3441 Veterans Blvd",   "city": "Metairie",    "state": "LA", "zip": "70002", "primary": False},
            {"name": "GSHG – Baton Rouge Inn",      "street": "9919 Airline Hwy",     "city": "Baton Rouge", "state": "LA", "zip": "70816", "primary": False},
        ],
        "contacts": [
            {"first": "Cecilia",  "last": "Fontaine",  "title": "Corporate IT Director","email": "c.fontaine@gulfsouthhospitality.com", "phone": "(504) 581-4201", "mobile": "(504) 430-7700"},
            {"first": "Reggie",   "last": "Washington","title": "AV & Network Lead",    "email": "r.washington@gulfsouthhospitality.com","phone": "(504) 581-4202", "mobile": "(504) 430-7701"},
        ],
    },
    {
        "name": "Atlas Energy Solutions",
        "number": "ACC0105",
        "account_type": "Energy",
        "street": "1919 Midland Dr",
        "city": "Midland", "state": "TX", "zip": "79701",
        "phone": "(432) 683-5100",
        "locations": [
            {"name": "Atlas – HQ Midland",       "street": "1919 Midland Dr",        "city": "Midland",    "state": "TX", "zip": "79701", "primary": True},
            {"name": "Atlas – Odessa Field Office","street": "550 W 8th St",          "city": "Odessa",     "state": "TX", "zip": "79761", "primary": False},
        ],
        "contacts": [
            {"first": "Blake",   "last": "Norris",    "title": "IT Infrastructure Lead","email": "b.norris@atlasenergysoln.com",   "phone": "(432) 683-5101", "mobile": "(432) 200-9900"},
            {"first": "Valerie", "last": "Escobedo",  "title": "Systems Administrator", "email": "v.escobedo@atlasenergysoln.com", "phone": "(432) 683-5102", "mobile": "(432) 200-9901"},
        ],
    },
    {
        "name": "Lakeview Education District",
        "number": "ACC0106",
        "account_type": "Education",
        "street": "400 School Board Dr",
        "city": "Jackson", "state": "MS", "zip": "39201",
        "phone": "(601) 960-8700",
        "locations": [
            {"name": "LED – District Office",     "street": "400 School Board Dr",   "city": "Jackson",    "state": "MS", "zip": "39201", "primary": True},
            {"name": "LED – North High School",   "street": "1800 Hanging Moss Rd",  "city": "Jackson",    "state": "MS", "zip": "39213", "primary": False},
            {"name": "LED – South Elementary",    "street": "320 Terry Rd",          "city": "Jackson",    "state": "MS", "zip": "39212", "primary": False},
        ],
        "contacts": [
            {"first": "Dorothy",  "last": "Simmons",  "title": "Technology Coordinator", "email": "d.simmons@lakeviewedu.org",   "phone": "(601) 960-8701", "mobile": "(601) 550-3300"},
            {"first": "Calvin",   "last": "Bright",   "title": "Network Administrator",  "email": "c.bright@lakeviewedu.org",   "phone": "(601) 960-8702", "mobile": "(601) 550-3301"},
            {"first": "Monique",  "last": "Tran",     "title": "IT Support Specialist",  "email": "m.tran@lakeviewedu.org",     "phone": "(601) 960-8703", "mobile": "(601) 550-3302"},
        ],
    },
    {
        "name": "Summit Retail Partners",
        "number": "ACC0107",
        "account_type": "Retail",
        "street": "8100 Mall Ring Rd",
        "city": "Chattanooga", "state": "TN", "zip": "37421",
        "phone": "(423) 894-5500",
        "locations": [
            {"name": "Summit – Chattanooga DC",   "street": "8100 Mall Ring Rd",     "city": "Chattanooga", "state": "TN", "zip": "37421", "primary": True},
            {"name": "Summit – Cleveland Store",  "street": "2200 Ocoee St N",       "city": "Cleveland",   "state": "TN", "zip": "37311", "primary": False},
        ],
        "contacts": [
            {"first": "Russell",  "last": "Hines",    "title": "Director of IT",       "email": "r.hines@summitretail.com",    "phone": "(423) 894-5501", "mobile": "(423) 760-2200"},
            {"first": "Amber",    "last": "Castillo",  "title": "POS Systems Analyst",  "email": "a.castillo@summitretail.com", "phone": "(423) 894-5502", "mobile": "(423) 760-2201"},
        ],
    },
    {
        "name": "Keystone Agriculture Co.",
        "number": "ACC0108",
        "account_type": "Agriculture",
        "street": "1201 Farm Bureau Rd",
        "city": "Tupelo", "state": "MS", "zip": "38804",
        "phone": "(662) 841-3300",
        "locations": [
            {"name": "Keystone – Tupelo HQ",      "street": "1201 Farm Bureau Rd",   "city": "Tupelo",      "state": "MS", "zip": "38804", "primary": True},
            {"name": "Keystone – Corinth Depot",  "street": "802 Highway 72 W",      "city": "Corinth",     "state": "MS", "zip": "38834", "primary": False},
        ],
        "contacts": [
            {"first": "Earl",    "last": "Hutchins",  "title": "IT Manager",           "email": "e.hutchins@keystoneagco.com",  "phone": "(662) 841-3301", "mobile": "(662) 255-4400"},
            {"first": "Kayla",   "last": "Stanton",   "title": "Network Technician",   "email": "k.stanton@keystoneagco.com",   "phone": "(662) 841-3302", "mobile": "(662) 255-4401"},
            {"first": "Justin",  "last": "Evers",     "title": "Help Desk Technician", "email": "j.evers@keystoneagco.com",     "phone": "(662) 841-3303", "mobile": "(662) 255-4402"},
        ],
    },
    {
        "name": "Crescent City Law Group",
        "number": "ACC0109",
        "account_type": "Legal",
        "street": "909 Poydras St Floor 22",
        "city": "New Orleans", "state": "LA", "zip": "70112",
        "phone": "(504) 523-8800",
        "locations": [
            {"name": "CCLG – Downtown Office",    "street": "909 Poydras St Floor 22","city": "New Orleans", "state": "LA", "zip": "70112", "primary": True},
            {"name": "CCLG – Covington Branch",   "street": "501 N Columbia St",      "city": "Covington",   "state": "LA", "zip": "70433", "primary": False},
        ],
        "contacts": [
            {"first": "Naomi",   "last": "Arceneaux", "title": "IT Operations Manager","email": "n.arceneaux@crescentlawgroup.com","phone": "(504) 523-8801", "mobile": "(504) 319-6600"},
            {"first": "Felix",   "last": "Guidry",    "title": "Systems Analyst",      "email": "f.guidry@crescentlawgroup.com",   "phone": "(504) 523-8802", "mobile": "(504) 319-6601"},
        ],
    },
    {
        "name": "TerraPath Civil Engineering",
        "number": "ACC0110",
        "account_type": "Engineering",
        "street": "3300 Perimeter Hill Dr",
        "city": "Nashville", "state": "TN", "zip": "37211",
        "phone": "(615) 833-6200",
        "locations": [
            {"name": "TerraPath – Nashville HQ",  "street": "3300 Perimeter Hill Dr", "city": "Nashville",  "state": "TN", "zip": "37211", "primary": True},
            {"name": "TerraPath – Knoxville Branch","street": "9111 Cross Park Dr",   "city": "Knoxville",  "state": "TN", "zip": "37923", "primary": False},
            {"name": "TerraPath – Memphis Office", "street": "6750 Poplar Ave",       "city": "Memphis",    "state": "TN", "zip": "38138", "primary": False},
        ],
        "contacts": [
            {"first": "Aaron",   "last": "Mercer",    "title": "CTO",                  "email": "a.mercer@terrapath.com",     "phone": "(615) 833-6201", "mobile": "(615) 477-5500"},
            {"first": "Ingrid",  "last": "Santos",    "title": "Senior IT Analyst",    "email": "i.santos@terrapath.com",     "phone": "(615) 833-6202", "mobile": "(615) 477-5501"},
        ],
    },
    {
        "name": "Magnolia Media Group",
        "number": "ACC0111",
        "account_type": "Media",
        "street": "1600 Broadcast Plaza",
        "city": "Memphis", "state": "TN", "zip": "38103",
        "phone": "(901) 726-4400",
        "locations": [
            {"name": "MMG – Broadcast Center",    "street": "1600 Broadcast Plaza",  "city": "Memphis",    "state": "TN", "zip": "38103", "primary": True},
            {"name": "MMG – East Memphis Studio", "street": "5100 Poplar Ave",       "city": "Memphis",    "state": "TN", "zip": "38137", "primary": False},
        ],
        "contacts": [
            {"first": "Danielle","last": "Pryor",    "title": "Director of Technology","email": "d.pryor@magnoliamediagroup.com","phone": "(901) 726-4401", "mobile": "(901) 545-3300"},
            {"first": "Isaiah",  "last": "Coleman",  "title": "Broadcast IT Engineer", "email": "i.coleman@magnoliamediagroup.com","phone": "(901) 726-4402","mobile": "(901) 545-3301"},
            {"first": "Alexis",  "last": "Chen",     "title": "Network Administrator", "email": "a.chen@magnoliamediagroup.com",  "phone": "(901) 726-4403","mobile": "(901) 545-3302"},
        ],
    },
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def sn_post(table: str, payload: dict) -> dict:
    url = f"{SN_INSTANCE}/api/now/table/{table}"
    resp = requests.post(url, auth=AUTH, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()["result"]


def sn_query(table: str, query: str) -> list:
    url = f"{SN_INSTANCE}/api/now/table/{table}"
    resp = requests.get(url, auth=AUTH, headers=HEADERS,
                        params={"sysparm_query": query, "sysparm_limit": 10})
    resp.raise_for_status()
    return resp.json().get("result", [])


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not SN_PASS:
        print("ERROR: SN_PASS is not set. Set it as an environment variable or edit the script.")
        return

    created_accounts = []

    for acct in ACCOUNTS:
        print(f"\n── {acct['name']} ──────────────────────")

        # 1. Create customer_account
        acct_payload = {
            "name":         acct["name"],
            "number":       acct["number"],
            "account_type": acct["account_type"],
            "street":       acct["street"],
            "city":         acct["city"],
            "state":        acct["state"],
            "zip":          acct["zip"],
            "phone":        acct["phone"],
        }
        acct_rec = sn_post("customer_account", acct_payload)
        acct_sys_id = acct_rec["sys_id"]
        print(f"  ✓ Account created  sys_id={acct_sys_id}")

        # 2. Create locations + address relationships
        for loc in acct["locations"]:
            loc_payload = {
                "name":    loc["name"],
                "street":  loc["street"],
                "city":    loc["city"],
                "state":   loc["state"],
                "zip":     loc["zip"],
                "country": "United States",
            }
            loc_rec = sn_post("cmn_location", loc_payload)
            loc_sys_id = loc_rec["sys_id"]

            rel_payload = {
                "account":   acct_sys_id,
                "location":  loc_sys_id,
                "is_primary": "true" if loc["primary"] else "false",
            }
            sn_post("account_address_relationship", rel_payload)
            flag = " (primary)" if loc["primary"] else ""
            print(f"  ✓ Location: {loc['name']}{flag}")

        # 3. Create contacts
        for con in acct["contacts"]:
            con_payload = {
                "first_name":   con["first"],
                "last_name":    con["last"],
                "title":        con["title"],
                "email":        con["email"],
                "phone":        con["phone"],
                "mobile_phone": con["mobile"],
                "account":      acct_sys_id,
            }
            sn_post("customer_contact", con_payload)
            print(f"  ✓ Contact: {con['first']} {con['last']} – {con['title']}")

        created_accounts.append({"name": acct["name"], "sys_id": acct_sys_id})

    print("\n\n══ All done ══════════════════════════════════════")
    print(f"Created {len(created_accounts)} accounts:\n")
    for a in created_accounts:
        print(f"  {a['name']:<40}  {a['sys_id']}")


if __name__ == "__main__":
    main()
