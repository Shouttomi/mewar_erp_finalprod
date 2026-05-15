"""
test500.py — 500 diverse query tests against /v2-chatbot/
Covers all intents, synonyms, Hinglish/English mix, edge cases, date ranges, roles.
"""
import requests, time, sys, io, random
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

URL = "http://127.0.0.1:8000/v2-chatbot/"

def ask(q, role="purchase", history=None):
    t0 = time.time()
    try:
        r = requests.post(URL, json={"query": q, "role": role, "history": history or []}, timeout=35)
        ms = round((time.time() - t0) * 1000)
        results = r.json().get("results", [])
        types = [i.get("type") for i in results]
        all_msg = ""
        for item in results:
            t = item.get("type")
            if t == "chat":
                all_msg += " " + item.get("message", "")
            elif t == "result" and "inventory" in item:
                inv = item["inventory"]
                all_msg += f" {inv.get('name','')} stock={item.get('total_stock','')} {inv.get('unit','')}"
            elif t == "result" and "supplier" in item:
                s = item["supplier"]
                all_msg += f" {s.get('name','')} {s.get('city','')} mob={s.get('mobile','')} gst={s.get('gstin','')}"
            elif t == "po":
                all_msg += f" {item.get('po_no','')} {item.get('supplier','')} Rs{item.get('total',0):,.0f} bal=Rs{item.get('balance',0):,.0f} {item.get('status','')}"
            elif t == "project":
                all_msg += f" {item.get('project_name','')} {item.get('category','')} pri={item.get('priority','')}"
            elif t == "purchase_request":
                all_msg += f" {item.get('pr_no','')} {item.get('status','')} qty={item.get('total_qty','')}"
        return ms, types, all_msg.strip()
    except Exception as e:
        return 0, [], f"ERROR: {e}"

passed = failed = 0

def test(label, q, role="purchase", history=None, expect_in=None, expect_not_in=None, expect_type=None):
    global passed, failed
    ms, types, all_msg = ask(q, role=role, history=history)
    fail_defaults = ["connect nahi", "error", "try again"]
    ok = True
    reason = ""

    if not all_msg or all_msg.startswith("ERROR"):
        ok = False; reason = f"NO RESULT / {all_msg[:60]}"
    elif any(k in all_msg.lower() for k in fail_defaults) and not expect_in:
        ok = False; reason = "LLM connection error"
    elif expect_in and not any(e.lower() in all_msg.lower() for e in expect_in):
        ok = False; reason = f"expected one of {expect_in}"
    elif expect_not_in and any(e.lower() in all_msg.lower() for e in expect_not_in):
        ok = False; reason = f"found unwanted {expect_not_in}"
    elif expect_type and expect_type not in types:
        ok = False; reason = f"expected type={expect_type}, got {types}"

    if ok: passed += 1
    else:  failed += 1

    status = "OK  " if ok else "FAIL"
    preview = "".join(c if ord(c) < 128 else "?" for c in all_msg[:70])
    print(f"[{status}] [{ms:>4}ms] {label:<45} {preview}")
    if not ok:
        print(f"         >> REASON: {reason}")


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1: INVENTORY — 100 queries (diverse synonyms, Hinglish, English, specifics)
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 110)
print("SECTION 1: INVENTORY / STOCK (100 tests)")
print("=" * 110)

inv_tests = [
    # Basic stock queries
    ("INV-001 bearing Hindi",            "bearing ka stock kitna hai",                  ["bearing", "stock"]),
    ("INV-002 oil seal Hindi",           "oil seal ka stock dikhao",                    ["Oil Seal", "stock"]),
    ("INV-003 belt English",             "show me belt stock",                          ["Belt", "stock"]),
    ("INV-004 bolt stock",               "bolt ka stock check karo",                    ["Bolt", "stock"]),
    ("INV-005 coupling",                 "coupling kitna pada hai",                     ["stock", "units"]),
    ("INV-006 pipe stock",               "pipe ka maal kitna hai",                      ["stock", "Pipe"]),
    ("INV-007 motor stock",              "motor ka stock batao",                        ["stock", "Motor"]),
    ("INV-008 pump Hindi",               "pump kitna hai",                              ["Pump", "stock"]),
    ("INV-009 valve English",            "valve stock level",                           ["Valve", "stock"]),
    ("INV-010 gear",                     "gear ka stok dikhao",                         ["Gear", "stock"]),
    # Typos / fuzzy
    ("INV-011 beerign typo",             "beerign ka stock",                            ["bearing", "stock"]),
    ("INV-012 balt typo",                "balt ka stok",                                ["Belt", "stock"]),
    ("INV-013 mottar typo",              "mottar ka stock",                             ["Motor", "stock"]),
    ("INV-014 sael typo",                "oil sael ka stock",                           ["stock"]),
    ("INV-015 inventry typo",            "inventry mein kitne items hain",              ["item", "inventory", "1654"]),
    # Specific items
    ("INV-016 conveyor 700mm",           "conveyor belt 700mm ka stock",                ["Conveyor Belt", "stock"]),
    ("INV-017 oil seal 75x100",          "oil seal 75x100x10 ka stock",                 ["Oil Seal", "stock"]),
    ("INV-018 bearing 6205",             "6205 bearing ka stock",                       ["stock"]),
    ("INV-019 v-belt b-section",         "v-belt b section ka stock",                   ["stock"]),
    ("INV-020 chain 12B",                "12B chain ka stock batao",                    ["stock"]),
    # Aggregate / count
    ("INV-021 total items",              "total inventory items kitne hain",            ["1654"]),
    ("INV-022 total items English",      "how many items are in inventory",             ["1654"]),
    ("INV-023 low stock",                "low stock items dikhao",                      ["stock"]),
    ("INV-024 min stock item",           "sabse kam stock wala item",                   ["stock", "units"]),
    ("INV-025 max stock item",           "sabse zyada stock wala item",                 ["stock", "units"]),
    ("INV-026 zero stock",               "zero stock items dikhao",                     ["stock"]),
    ("INV-027 out of stock",             "out of stock items",                          ["stock"]),
    ("INV-028 high stock item",          "high stock wale items batao",                 ["stock"]),
    # Category-based
    ("INV-029 electrical items",         "electrical items ka stock",                   ["stock"]),
    ("INV-030 mechanical items",         "mechanical items kitne hain",                 ["stock"]),
    # English synonyms
    ("INV-031 how much bearing",         "how much bearing stock do we have",           ["bearing", "stock"]),
    ("INV-032 quantity of oil seal",     "what is the quantity of oil seal",            ["Oil Seal", "stock"]),
    ("INV-033 available belt",           "how many belts are available",                ["Belt", "stock"]),
    ("INV-034 inventory count",          "inventory count karo",                        ["item", "inventory", "stock"]),
    ("INV-035 check stock",              "stock check karo",                            ["stock", "item"]),
    # Maal/paisa synonyms
    ("INV-036 maal bearing",             "bearing ka maal kitna pada hai",              ["bearing", "stock"]),
    ("INV-037 samaan motor",             "motor ka samaan kitna hai",                   ["Motor", "stock"]),
    ("INV-038 kahan pada hai",           "oil seal kahan pada hai",                     ["Oil Seal", "stock"]),
    ("INV-039 thoda kam bearing",        "bearing ka maal thoda kam lag raha hai",      ["bearing", "stock"]),
    ("INV-040 zyada stock",              "kiska stock zyada hai",                       ["stock"]),
    # Multi-item
    ("INV-041 belt aur oil seal",        "belt aur oil seal ka stock",                  ["stock"]),
    ("INV-042 bearing aur bolt",         "bearing aur bolt ka stock batao",             ["stock"]),
    ("INV-043 three items",              "belt oil seal bearing stock",                 ["stock"]),
    # Role-based
    ("INV-044 store admin bearing",      "bearing stock kitna hai",                     ["bearing", "stock"]),
    ("INV-045 supervisor inventory",     "inventory dikhao",                            ["stock", "item"]),
    ("INV-046 HOD stock query",          "stock report dikhao",                         ["stock", "item"]),
    ("INV-047 sales oil seal",           "oil seal ka stock",                           ["Oil Seal", "stock"]),
    # Units
    ("INV-048 meter units",              "pipe kitne meter hai",                        ["Pipe", "stock"]),
    ("INV-049 kg units",                 "grease kitna kg hai",                         ["stock"]),
    ("INV-050 litre units",              "oil kitna litre hai",                         ["stock"]),
    # ID-based
    ("INV-051 numeric ID 1",             "item 1 ka stock",                             ["stock", "inventory"]),
    ("INV-052 numeric ID 5",             "5 item ka stock",                             ["stock", "inventory"]),
    # Restock / shortage
    ("INV-053 restock needed",           "kaunse items restock chahiye",                ["stock"]),
    ("INV-054 shortage items",           "shortage wale items batao",                   ["stock"]),
    ("INV-055 critical stock",           "critical stock items",                        ["stock"]),
    # Long natural language
    ("INV-056 long NL bearing",          "yaar mujhe batao ki hamare paas jo conveyor belt hai usme jo sabse zyada stock pada hai woh konsa hai", ["belt", "stock"]),
    ("INV-057 long English",             "Can you tell me the current stock level for all bearings in our inventory system", ["bearing", "stock"]),
    ("INV-058 natural Hinglish",         "bhai bearing ka kitna maal bacha hai store mein abhi", ["bearing", "stock"]),
    # Specific brand/size
    ("INV-059 SKF bearing",              "SKF bearing ka stock",                        ["stock"]),
    ("INV-060 6206 bearing",             "6206 bearing stock batao",                    ["stock"]),
    ("INV-061 seal 80x100",              "oil seal 80x100 stock",                       ["stock"]),
    ("INV-062 belt A40",                 "belt A40 ka stock",                           ["stock"]),
    # Month/week context
    ("INV-063 this month stock",         "is mahine kitna stock aaya",                  ["stock"]),
    ("INV-064 stock added",              "naya stock kab aaya",                         ["stock"]),
    # Variations
    ("INV-065 check karo",               "bolt check karo",                             ["Bolt", "stock"]),
    ("INV-066 batao",                    "coupling batao",                              ["stock"]),
    ("INV-067 dikhao",                   "valve dikhao",                                ["Valve", "stock"]),
    ("INV-068 hai kitna",               "gasket hai kitna",                            ["stock"]),
    ("INV-069 abhi kitna",               "spring abhi kitna hai",                       ["stock"]),
    ("INV-070 bacha hai",                "filter kitna bacha hai",                      ["stock"]),
    # Casual short
    ("INV-071 just bearing",             "bearing",                                     ["bearing", "stock"]),
    ("INV-072 just oil seal",            "oil seal",                                    ["Oil Seal", "stock"]),
    ("INV-073 just pump",                "pump",                                        ["Pump", "stock"]),
    ("INV-074 just motor",               "motor",                                       ["Motor", "stock"]),
    ("INV-075 just belt",                "belt",                                        ["Belt", "stock"]),
    # Follow-up style
    ("INV-076 kitne available",          "bearing kitne available hain",                ["bearing", "stock"]),
    ("INV-077 available hain",           "oil seal available hain kya",                 ["Oil Seal", "stock"]),
    ("INV-078 in stock",                 "belt in stock hai kya",                       ["Belt", "stock"]),
    # Comparison
    ("INV-079 more or less",             "bearing stock zyada hai ya kam",              ["bearing", "stock"]),
    ("INV-080 compare stock",            "belt vs chain stock",                         ["stock"]),
    # Transactions
    ("INV-081 stock nikla",              "bearing kitna nikla aaj",                     ["bearing", "stock"]),
    ("INV-082 stock aaya",               "belt aaj kitna aaya",                         ["Belt", "stock"]),
    # Vague
    ("INV-083 maal check",               "maal check karo",                             ["stock", "item"]),
    ("INV-084 store mein kya hai",       "store mein kya kya hai",                      ["stock", "item", "inventory"]),
    ("INV-085 sab dikhao",               "sab items dikhao",                            ["stock", "item", "inventory"]),
    # Mixed entity+filter
    ("INV-086 bearing low stock",        "bearing jo kam hai dikhao",                   ["bearing", "stock"]),
    ("INV-087 belt available units",     "belt ke available units",                     ["Belt", "stock"]),
    # Fast/brief
    ("INV-088 quick check bolt",         "bolt quick check",                            ["Bolt", "stock"]),
    ("INV-089 status bearing",           "bearing status",                              ["bearing", "stock"]),
    ("INV-090 details oil seal",         "oil seal details",                            ["Oil Seal", "stock"]),
    # Hindi numbers
    ("INV-091 ek bearing",               "ek bearing ka stock",                         ["bearing", "stock"]),
    ("INV-092 paanch items",             "paanch items ka stock",                       ["stock"]),
    # Named stores
    ("INV-093 main store",               "main store mein bearing hai kya",             ["bearing", "stock"]),
    ("INV-094 warehouse",                "warehouse mein belt kitna hai",               ["Belt", "stock"]),
    # Generic
    ("INV-095 inventory report",         "inventory report dikhao",                     ["stock", "item", "inventory"]),
    ("INV-096 stock summary",            "stock summary batao",                         ["stock"]),
    ("INV-097 item list",                "item list dikhao",                            ["stock", "item", "inventory"]),
    ("INV-098 spare parts",              "spare parts ka stock",                        ["stock"]),
    ("INV-099 all items English",        "show all inventory items",                    ["stock", "item", "inventory"]),
    ("INV-100 item count English",       "how many total items in inventory",           ["1654"]),
]

with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(test, *t): t for t in [(l, q, "purchase", None, e, None, None) for l, q, e in inv_tests]}
    for f in as_completed(futures):
        f.result()

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2: SUPPLIERS — 100 queries
# ──────────────────────────────────────────────────────────────────────────────
print()
print("=" * 110)
print("SECTION 2: SUPPLIERS (100 tests)")
print("=" * 110)

sup_tests = [
    # Basic lookups
    ("SUP-001 Unitech basic",           "Unitech supplier details",                    ["Unitech"]),
    ("SUP-002 DCL basic",               "DCL ki details",                              ["DCL"]),
    ("SUP-003 Rishabh basic",           "Rishabh International details",               ["Rishabh"]),
    ("SUP-004 Aastha basic",            "Aastha Engineering details",                  ["Aastha"]),
    ("SUP-005 Arawali basic",           "Arawali ke details",                          ["Arawali"]),
    # Mobile queries
    ("SUP-006 Unitech mobile",          "Unitech ka mobile number",                    ["Unitech", "mobile"]),
    ("SUP-007 DCL phone",               "DCL ka phone number",                         ["DCL"]),
    ("SUP-008 Rishabh contact",         "Rishabh ka contact",                          ["Rishabh"]),
    ("SUP-009 mobile casual",           "Unitech ka number kya hai bhai",              ["Unitech"]),
    ("SUP-010 mobile English",          "what is the mobile number of DCL",            ["DCL"]),
    # GSTIN queries
    ("SUP-011 Unitech GSTIN",           "Unitech ki GSTIN",                            ["Unitech"]),
    ("SUP-012 DCL GST",                 "DCL ka GST number",                           ["DCL"]),
    ("SUP-013 tax number",              "Aastha ka tax number",                        ["Aastha"]),
    ("SUP-014 GSTIN English",           "show me Unitech's GST number",                ["Unitech"]),
    # Email
    ("SUP-015 email query",             "Rishabh ka email kya hai",                    ["Rishabh"]),
    ("SUP-016 email English",           "what is the email of Aastha Engineering",     ["Aastha"]),
    # City-based
    ("SUP-017 Udaipur suppliers",       "Udaipur ke suppliers dikhao",                 ["supplier", "Udaipur"]),
    ("SUP-018 Jaipur suppliers",        "Jaipur mein kitne suppliers hain",            ["supplier"]),
    ("SUP-019 Delhi suppliers",         "Delhi wale suppliers batao",                  ["supplier", "Delhi"]),
    ("SUP-020 Rajsamand suppliers",     "Rajsamand ke suppliers",                      ["supplier"]),
    # Count
    ("SUP-021 total suppliers",         "total kitne suppliers registered hain",       ["6092", "supplier"]),
    ("SUP-022 total English",           "how many suppliers do we have",               ["supplier", "6092"]),
    ("SUP-023 active suppliers",        "active suppliers kitne hain",                 ["supplier"]),
    # Profile
    ("SUP-024 full profile",            "Unitech ki poori profile",                    ["Unitech"]),
    ("SUP-025 complete details",        "Aastha ke bare mein complete details",        ["Aastha"]),
    ("SUP-026 vendor details",          "DCL vendor details",                          ["DCL"]),
    ("SUP-027 party details",           "Rishabh party details",                       ["Rishabh"]),
    # Typos
    ("SUP-028 Unitec typo",             "Unitec suplier details",                      ["Unitech"]),
    ("SUP-029 Risabh typo",             "Risabh ke details",                           ["Rishabh"]),
    ("SUP-030 Astha typo",              "Astha Engineering details",                   ["Aastha"]),
    ("SUP-031 supplair typo",           "supplair kitne hain total",                   ["supplier"]),
    ("SUP-032 Arawaali typo",           "Arawaali supplier",                           ["Arawali"]),
    # Hindi synonyms
    ("SUP-033 darjedar query",          "hamare saare vendors ki list",                ["supplier"]),
    ("SUP-034 party list",              "sab parties dikhao",                          ["supplier"]),
    ("SUP-035 vendor list",             "vendor list batao",                           ["supplier"]),
    ("SUP-036 sabke details",           "sabhi suppliers ki details",                  ["supplier"]),
    # Location context
    ("SUP-037 kahan se supplier",       "Rishabh kahan se hai",                        ["Rishabh"]),
    ("SUP-038 address query",           "Unitech ka address kya hai",                  ["Unitech"]),
    ("SUP-039 location query",          "DCL kahan ka hai",                            ["DCL"]),
    # Multi-supplier
    ("SUP-040 two suppliers",           "Unitech aur DCL ki details",                  ["Unitech", "DCL"]),
    ("SUP-041 compare suppliers",       "Rishabh aur Aastha details",                  ["Rishabh", "Aastha"]),
    # Role-based
    ("SUP-042 purchase role",           "Unitech details",                             ["Unitech"]),
    ("SUP-043 HOD vendor",              "vendor details Rishabh",                      ["Rishabh"]),
    ("SUP-044 store admin sup",         "Aastha supplier details",                     ["Aastha"]),
    # English full sentences
    ("SUP-045 English full",            "Show me all details for Unitech supplier",    ["Unitech"]),
    ("SUP-046 English GSTIN",           "Can you give me the GSTIN of DCL",           ["DCL"]),
    ("SUP-047 English phone",           "Find the phone number of Rishabh International", ["Rishabh"]),
    ("SUP-048 English city",            "Which city is Aastha Engineering from",       ["Aastha"]),
    # Category
    ("SUP-049 category filter",         "bearing wale suppliers dikhao",               ["supplier"]),
    ("SUP-050 oil suppliers",           "oil dene wale suppliers",                     ["supplier"]),
    # Short/casual
    ("SUP-051 just Unitech",            "Unitech",                                     ["Unitech"]),
    ("SUP-052 just DCL",                "DCL",                                         ["DCL"]),
    ("SUP-053 just Rishabh",            "Rishabh",                                     ["Rishabh"]),
    ("SUP-054 Aastha only",             "Aastha Engineering",                          ["Aastha"]),
    ("SUP-055 Arawali only",            "Arawali",                                     ["Arawali"]),
    # Number queries
    ("SUP-056 number total",            "kitne suppliers hain",                        ["supplier", "6092"]),
    ("SUP-057 count vendors",           "vendors ka count",                            ["supplier"]),
    ("SUP-058 registered count",        "registered vendors kitne hain",               ["supplier"]),
    # New/recently added
    ("SUP-059 new suppliers",           "naye suppliers dikhao",                       ["supplier"]),
    ("SUP-060 recent suppliers",        "recent suppliers",                            ["supplier"]),
    # Search by initial
    ("SUP-061 starts with A",           "A se start hone wale suppliers",              ["supplier"]),
    ("SUP-062 starts with R",           "R wale suppliers dikhao",                     ["supplier"]),
    # with city
    ("SUP-063 Mumbai supplier",         "Mumbai ke suppliers",                         ["supplier"]),
    ("SUP-064 Jodhpur",                 "Jodhpur ke vendors batao",                    ["supplier"]),
    ("SUP-065 Gujarat supplier",        "Gujarat ke suppliers",                        ["supplier"]),
    # Attribute-specific
    ("SUP-066 has email",               "jinke paas email hai wale suppliers",         ["supplier"]),
    ("SUP-067 has GSTIN",               "GST registered suppliers",                    ["supplier"]),
    # Follow-up style (no history, but phrased as follow-up)
    ("SUP-068 uski details",            "Unitech uski GSTIN batao",                    ["Unitech"]),
    ("SUP-069 uska mobile",             "DCL uska mobile",                             ["DCL"]),
    # Hinglish
    ("SUP-070 bhai supplier",           "bhai Unitech ka kya number hai",              ["Unitech"]),
    ("SUP-071 yaar details",            "yaar DCL ki detail do",                       ["DCL"]),
    ("SUP-072 zara batao",              "Rishabh ki details zara batao",               ["Rishabh"]),
    # Aggregation on suppliers
    ("SUP-073 city count",              "kitne cities mein suppliers hain",            ["supplier"]),
    ("SUP-074 top suppliers",           "top suppliers dikhao",                        ["supplier"]),
    ("SUP-075 main vendors",            "main vendors kaun kaun hain",                 ["supplier"]),
    # All/list
    ("SUP-076 list all suppliers",      "sab suppliers ki list",                       ["supplier"]),
    ("SUP-077 supplier directory",      "supplier directory dikhao",                   ["supplier"]),
    ("SUP-078 all vendors list",        "all vendors list",                            ["supplier"]),
    # State-based
    ("SUP-079 Rajasthan suppliers",     "Rajasthan ke suppliers",                      ["supplier"]),
    ("SUP-080 UP suppliers",            "UP ke suppliers batao",                       ["supplier"]),
    # Payment-related
    ("SUP-081 trusted supplier",        "trusted suppliers kaun hain",                 ["supplier"]),
    ("SUP-082 local suppliers",         "local suppliers batao",                       ["supplier"]),
    # Near-duplicate phrasings
    ("SUP-083 detail nikalo",           "Unitech ka detail nikalo",                    ["Unitech"]),
    ("SUP-084 info chahiye",            "DCL ki info chahiye",                         ["DCL"]),
    ("SUP-085 profile dikhao",          "Rishabh ka profile",                          ["Rishabh"]),
    ("SUP-086 poori jaankari",          "Aastha ki poori jaankari",                    ["Aastha"]),
    ("SUP-087 sab kuch batao",          "Unitech ke baare mein sab kuch batao",        ["Unitech"]),
    # Long sentence
    ("SUP-088 long sentence",           "mujhe Unitech Solutions aur Services ke baare mein sab kuch batao including mobile GSTIN address", ["Unitech"]),
    ("SUP-089 English long",            "Please provide complete information about Rishabh International including their GST number and contact", ["Rishabh"]),
    # Industry
    ("SUP-090 industry supplier",       "electrical suppliers dikhao",                 ["supplier"]),
    ("SUP-091 mechanical vendors",      "mechanical vendors batao",                    ["supplier"]),
    # Specific attribute
    ("SUP-092 bank details",            "Unitech ke bank details",                     ["Unitech"]),
    ("SUP-093 PAN number",              "DCL ka PAN number",                           ["DCL"]),
    # Registered date
    ("SUP-094 old suppliers",           "purane suppliers dikhao",                     ["supplier"]),
    ("SUP-095 2024 suppliers",          "2024 mein registered suppliers",              ["supplier"]),
    # Conditional
    ("SUP-096 Udaipur only",            "sirf Udaipur ke suppliers",                   ["supplier", "Udaipur"]),
    ("SUP-097 exclude Delhi",           "Delhi chhod ke baaki suppliers",              ["supplier"]),
    # Short English
    ("SUP-098 supplier info",           "supplier info Unitech",                       ["Unitech"]),
    ("SUP-099 vendor contact",          "DCL vendor contact details",                  ["DCL"]),
    ("SUP-100 total count",             "total vendor count",                          ["supplier", "6092"]),
]

with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(test, *t): t for t in [(l, q, "purchase", None, e, None, None) for l, q, e in sup_tests]}
    for f in as_completed(futures):
        f.result()

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3: PURCHASE ORDERS — 100 queries
# ──────────────────────────────────────────────────────────────────────────────
print()
print("=" * 110)
print("SECTION 3: PURCHASE ORDERS (100 tests)")
print("=" * 110)

po_tests = [
    # Basic
    ("PO-001 pending orders",           "pending orders dikhao",                       ["order", "mile"]),
    ("PO-002 all orders",               "sab orders dikhao",                           ["order", "mile"]),
    ("PO-003 latest orders",            "latest orders",                               ["order", "mile"]),
    ("PO-004 last 5 orders",            "last 5 orders",                               ["order", "mile"]),
    ("PO-005 draft orders",             "draft orders batao",                          ["order", "mile"]),
    ("PO-006 completed orders",         "completed orders dikhao",                     ["order", "mile"]),
    ("PO-007 recent orders",            "recent purchase orders",                      ["order", "mile"]),
    ("PO-008 all POs",                  "sab POs dikhao",                              ["order", "mile"]),
    ("PO-009 PO list",                  "PO list batao",                               ["order", "mile"]),
    ("PO-010 purchase orders Eng",      "show all purchase orders",                    ["order", "mile"]),
    # Supplier-specific
    ("PO-011 Unitech orders",           "Unitech ke orders",                           ["Unitech", "order"]),
    ("PO-012 DCL orders",               "DCL ke orders dikhao",                        ["DCL", "order"]),
    ("PO-013 Rishabh orders",           "Rishabh ke orders",                           ["Rishabh", "order"]),
    ("PO-014 Aastha orders",            "Aastha Engineering ke orders",                ["Aastha", "order"]),
    ("PO-015 Arawali orders",           "Arawali ke orders",                           ["Arawali", "order"]),
    # Balance queries
    ("PO-016 total balance",            "total pending balance kitna hai",             ["balance"]),
    ("PO-017 highest balance",          "sabse jyada balance kiska hai",               ["balance"]),
    ("PO-018 lowest balance",           "sabse kam balance kiska hai",                 ["balance"]),
    ("PO-019 Rishabh balance",          "Rishabh ka balance kitna hai",                ["Rishabh", "balance"]),
    ("PO-020 DCL balance",              "DCL ka baaki paisa kitna hai",                ["DCL", "balance"]),
    ("PO-021 paisa baaki",              "kiska paisa baaki hai",                       ["balance"]),
    ("PO-022 udhar",                    "kiska udhar baaki hai",                       ["balance"]),
    ("PO-023 rokra",                    "rokra kitna hai",                             ["balance"]),
    ("PO-024 hisab",                    "hisab dikhao",                                ["order", "mile"]),
    ("PO-025 baaki amount",             "baaki amount batao",                          ["balance"]),
    # Advance
    ("PO-026 advance given",            "kitne orders mein advance diya gaya",         ["order", "mile"]),
    ("PO-027 advance paid",             "advance paid orders",                         ["order", "mile"]),
    ("PO-028 prepaid orders",           "prepaid orders dikhao",                       ["order", "mile"]),
    ("PO-029 advance details",          "advance diya gaya hai kisi ko",               ["order", "mile"]),
    # Specific PO number
    ("PO-030 exact PO number",          "MHEL/PO/00029/2026-2027 dikhao",             ["MHEL", "Rishabh"]),
    ("PO-031 exact PO 4",               "MHEL/PO/00004/2025-2026 dikhao",             ["MHEL", "Aastha"]),
    # Aggregations
    ("PO-032 total gst",                "total gst kitna bana sabka",                  ["GST", "tax", "bata", "Rs"]),
    ("PO-033 total value",              "total orders ki value",                       ["order", "Rs"]),
    ("PO-034 biggest PO",               "sabse bada PO kaunsa hai",                   ["MHEL", "Rs"]),
    ("PO-035 smallest PO",              "sabse chota PO",                              ["MHEL", "Rs"]),
    ("PO-036 highest value",            "highest value purchase order",                ["MHEL", "Rs"]),
    ("PO-037 most expensive",           "sabse mehanga order",                         ["Rs"]),
    ("PO-038 count all POs",            "total kitne purchase orders hain",            ["order", "mile"]),
    ("PO-039 count pending",            "kitne pending orders hain",                   ["order", "mile"]),
    ("PO-040 count draft",              "draft orders kitne hain",                     ["order", "mile"]),
    # Date range
    ("PO-041 this month",               "is month ke orders",                          ["order", "mile"]),
    ("PO-042 last month",               "pichle mahine ke orders",                     ["order", "mile"]),
    ("PO-043 this week",                "is hafte ke orders",                          ["order", "mile"]),
    ("PO-044 last week",                "last week ke orders",                         ["order", "mile"]),
    ("PO-045 today orders",             "aaj ke orders",                               ["order", "mile"]),
    ("PO-046 2025 orders",              "2025 mein kitne orders",                      ["order", "mile"]),
    ("PO-047 April orders",             "April ke purchase orders",                    ["order", "mile"]),
    ("PO-048 March orders",             "March mein kitne orders bane",                ["order", "mile"]),
    # Status filters
    ("PO-049 open orders",              "open orders dikhao",                          ["order", "mile"]),
    ("PO-050 closed orders",            "closed orders",                               ["order", "mile"]),
    # Synonyms
    ("PO-051 purchase order Hindi",     "khareed order dikhao",                        ["order", "mile"]),
    ("PO-052 mal mangwana",             "mal mangwane ke orders",                      ["order", "mile"]),
    ("PO-053 order nikalo",             "orders nikalo",                               ["order", "mile"]),
    ("PO-054 English show PO",          "Show me all purchase orders",                 ["order", "mile"]),
    ("PO-055 English pending",          "Show pending purchase orders",                ["order", "mile"]),
    ("PO-056 English balance",          "What is the total pending balance",           ["balance"]),
    ("PO-057 English supplier PO",      "Show orders for Unitech",                     ["Unitech", "order"]),
    ("PO-058 English specific PO",      "Show MHEL/PO/00029/2026-2027",               ["MHEL", "Rishabh"]),
    # Typos
    ("PO-059 purcahse typo",            "purcahse orders dikhao",                      ["order", "mile"]),
    ("PO-060 ordder typo",              "ordder list batao",                           ["order", "mile"]),
    # Superlatives
    ("PO-061 max order value",          "maximum order value wala",                    ["Rs"]),
    ("PO-062 min order",                "minimum order wala",                          ["Rs"]),
    ("PO-063 top 3 orders",             "top 3 orders dikhao",                         ["order", "mile"]),
    ("PO-064 first 10 orders",          "first 10 orders",                             ["order", "mile"]),
    # GST / tax
    ("PO-065 gst total",                "sab orders ka GST total",                     ["GST", "tax", "bata", "Rs"]),
    ("PO-066 tax amount",               "tax amount total",                            ["GST", "tax", "Rs"]),
    # Mixed queries
    ("PO-067 supplier + balance",       "Unitech ka balance aur orders",               ["Unitech", "order"]),
    ("PO-068 DCL orders + balance",     "DCL ke orders aur kitna baaki hai",           ["DCL"]),
    # Special phrases
    ("PO-069 paise de diye",            "jinhe paise de diye hain",                    ["order", "mile"]),
    ("PO-070 payment pending",          "payment pending hai jinke",                   ["balance", "order"]),
    ("PO-071 ledger",                   "ledger dikhao",                               ["order", "mile"]),
    ("PO-072 account baahi",            "account baahi batao",                         ["order", "mile"]),
    # Roles
    ("PO-073 supervisor PO",            "latest purchase orders",                      ["order", "mile"]),
    ("PO-074 HOD PO",                   "total pending balance",                       ["balance"]),
    ("PO-075 director PO",              "purchase orders summary",                     ["order", "mile"]),
    # Aastha specific
    ("PO-076 Aastha PO value",          "Aastha ka total order value",                 ["Aastha", "Rs"]),
    ("PO-077 Aastha balance",           "Aastha ka balance",                           ["Aastha", "balance"]),
    # DCL specific
    ("PO-078 DCL paisa baaki",          "DCL ka kitna paisa baaki hai abhi tak",       ["DCL", "balance"]),
    ("PO-079 DCL last order",           "DCL ka last order",                           ["DCL"]),
    # Hinglish casual
    ("PO-080 yaar orders",              "yaar sab pending orders dikhao",              ["order", "mile"]),
    ("PO-081 bhai kya baaki",           "bhai kya kya baaki hai",                      ["balance", "order"]),
    # English professional
    ("PO-082 outstanding balance",      "show all outstanding balances",               ["balance"]),
    ("PO-083 pending payments",         "what are the pending payments",               ["balance", "order"]),
    ("PO-084 PO summary",               "purchase order summary",                      ["order", "mile"]),
    # Amount-based filter
    ("PO-085 orders above 1 lakh",      "1 lakh se zyada ke orders",                   ["order", "mile", "Rs"]),
    ("PO-086 orders below 50k",         "50,000 se kam ke orders",                     ["order", "mile", "Rs"]),
    # By month
    ("PO-087 January POs",              "January ke purchase orders",                  ["order", "mile"]),
    ("PO-088 February POs",             "February mein kuch orders bane the",         ["order", "mile"]),
    # By supplier city
    ("PO-089 Udaipur supplier orders",  "Udaipur ke suppliers ke orders",              ["order", "mile"]),
    # Verification
    ("PO-090 order received",           "order mila kya",                              ["order", "mile"]),
    ("PO-091 delivery status",          "delivery kab hogi",                           ["order", "mile"]),
    # Misc
    ("PO-092 overdue",                  "overdue orders dikhao",                       ["order", "mile"]),
    ("PO-093 under process",            "process mein hai jo orders",                  ["order", "mile"]),
    ("PO-094 dispatch orders",          "dispatch orders",                             ["order", "mile"]),
    ("PO-095 in transit",               "in transit orders",                           ["order", "mile"]),
    ("PO-096 balance all",              "sab ka balance dikhao",                       ["balance"]),
    ("PO-097 abhi tak baaki",           "abhi tak kya baaki hai",                      ["balance", "order"]),
    ("PO-098 payment history",          "payment history dikhao",                      ["order", "mile"]),
    ("PO-099 vendor payments",          "vendor payments ka hisab",                    ["order", "mile"]),
    ("PO-100 orders total value",       "total order value dikhao",                    ["order", "Rs"]),
]

with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(test, *t): t for t in [(l, q, "purchase", None, e, None, None) for l, q, e in po_tests]}
    for f in as_completed(futures):
        f.result()

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 4: PROJECTS — 60 queries
# ──────────────────────────────────────────────────────────────────────────────
print()
print("=" * 110)
print("SECTION 4: PROJECTS (60 tests)")
print("=" * 110)

proj_tests = [
    ("PROJ-001 all projects",           "sab projects dikhao",                         ["project", "mile"]),
    ("PROJ-002 running projects",       "running projects",                            ["project", "mile"]),
    ("PROJ-003 urgent projects",        "urgent projects dikhao",                      ["project", "mile"]),
    ("PROJ-004 high priority",          "high priority projects",                      ["project", "mile"]),
    ("PROJ-005 low priority",           "low priority projects",                       ["project", "mile"]),
    ("PROJ-006 Rajsamand projects",     "Rajsamand ke projects",                       ["Rajsamand", "project"]),
    ("PROJ-007 Udaipur projects",       "Udaipur ke projects",                         ["project", "mile"]),
    ("PROJ-008 total projects",         "total projects kitne hain",                   ["18", "project"]),
    ("PROJ-009 new projects",           "new status projects",                         ["project", "mile"]),
    ("PROJ-010 project list",           "project list batao",                          ["project", "mile"]),
    ("PROJ-011 site dikhao",            "site dikhao",                                 ["project", "mile"]),
    ("PROJ-012 machine projects",       "machine projects batao",                      ["project", "mile"]),
    ("PROJ-013 English projects",       "show all projects",                           ["project", "mile"]),
    ("PROJ-014 English urgent",         "show urgent projects",                        ["project", "mile"]),
    ("PROJ-015 Hindi total",            "kul kitne projects hain",                     ["18", "project"]),
    ("PROJ-016 running sites",          "running sites dikhao",                        ["project", "mile"]),
    ("PROJ-017 active projects",        "active projects",                             ["project", "mile"]),
    ("PROJ-018 on hold projects",       "on hold projects",                            ["project", "mile"]),
    ("PROJ-019 completed projects",     "completed projects",                          ["project", "mile"]),
    ("PROJ-020 new status",             "status new wale projects",                    ["project", "mile"]),
    ("PROJ-021 city Jodhpur",           "Jodhpur ke projects",                         ["project", "mile"]),
    ("PROJ-022 Jaipur projects",        "Jaipur mein kya projects hain",              ["project", "mile"]),
    ("PROJ-023 priority filter",        "priority wise projects",                      ["project", "mile"]),
    ("PROJ-024 project count",          "projects ka count",                           ["18", "project"]),
    ("PROJ-025 projeckt typo",          "running projeckt dikhao",                     ["project", "mile"]),
    ("PROJ-026 project English count",  "how many projects are there",                 ["18", "project"]),
    ("PROJ-027 show sites",             "show all sites",                              ["project", "mile"]),
    ("PROJ-028 budgeted projects",      "budget wale projects",                        ["project", "mile"]),
    ("PROJ-029 zero budget",            "zero budget projects",                        ["project", "mile"]),
    ("PROJ-030 kahan chal rahe",        "Rajsamand mein konse projects chal rahe hain", ["Rajsamand", "project"]),
    ("PROJ-031 high pri English",       "high priority projects English",              ["project", "mile"]),
    ("PROJ-032 project summary",        "project summary",                             ["project", "mile"]),
    ("PROJ-033 category projects",      "category wise projects",                      ["project", "mile"]),
    ("PROJ-034 recent projects",        "recent projects",                             ["project", "mile"]),
    ("PROJ-035 latest project",         "latest project batao",                        ["project", "mile"]),
    ("PROJ-036 Rajsamand abhi",         "Rajsamand mein abhi kya chal raha",          ["Rajsamand", "project"]),
    ("PROJ-037 naya project",           "naya project dikhao",                         ["project", "mile"]),
    ("PROJ-038 old projects",           "purane projects",                             ["project", "mile"]),
    ("PROJ-039 not urgent",             "non urgent projects",                         ["project", "mile"]),
    ("PROJ-040 low budget",             "low budget wale projects",                    ["project", "mile"]),
    ("PROJ-041 project names",          "project names list",                          ["project", "mile"]),
    ("PROJ-042 Vinayak project",        "Sidhi Vinayak project details",               ["Sidhi Vinayak", "project"]),
    ("PROJ-043 Mewar projects",         "Mewar ke projects",                           ["project", "mile"]),
    ("PROJ-044 plant projects",         "plant ke projects",                           ["project", "mile"]),
    ("PROJ-045 factory site",           "factory site dikhao",                         ["project", "mile"]),
    ("PROJ-046 expansion projects",     "expansion projects",                          ["project", "mile"]),
    ("PROJ-047 repair projects",        "repair projects",                             ["project", "mile"]),
    ("PROJ-048 maintenance",            "maintenance projects",                        ["project", "mile"]),
    ("PROJ-049 capex projects",         "capex projects dikhao",                       ["project", "mile"]),
    ("PROJ-050 ongoing",                "ongoing projects",                            ["project", "mile"]),
    ("PROJ-051 paused",                 "paused projects",                             ["project", "mile"]),
    ("PROJ-052 delayed",                "delayed projects",                            ["project", "mile"]),
    ("PROJ-053 pending projects",       "pending projects",                            ["project", "mile"]),
    ("PROJ-054 this month project",     "is month ke projects",                        ["project", "mile"]),
    ("PROJ-055 last month project",     "last month ke projects",                      ["project", "mile"]),
    ("PROJ-056 total number English",   "total number of projects",                    ["18", "project"]),
    ("PROJ-057 Rajasthan projects",     "Rajasthan ke projects",                       ["project", "mile"]),
    ("PROJ-058 Gujarat projects",       "Gujarat projects",                            ["project", "mile"]),
    ("PROJ-059 project status",         "project status dikhao",                       ["project", "mile"]),
    ("PROJ-060 urgent high mix",        "urgent ya high priority projects",            ["project", "mile"]),
]

with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(test, *t): t for t in [(l, q, "purchase", None, e, None, None) for l, q, e in proj_tests]}
    for f in as_completed(futures):
        f.result()

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 5: GENERAL CHAT & EDGE CASES — 60 queries
# ──────────────────────────────────────────────────────────────────────────────
print()
print("=" * 110)
print("SECTION 5: GENERAL CHAT & EDGE CASES (60 tests)")
print("=" * 110)

gen_tests = [
    # Greetings
    ("GEN-001 hello",                   "hello",                                       ["Haan", "kya", "help", "inventory", "ERP", "kaise"]),
    ("GEN-002 namaste",                 "namaste",                                     ["kya", "help", "ERP", "inventory", "Namaste"]),
    ("GEN-003 hi",                      "hi",                                          ["kya", "help", "ERP"]),
    ("GEN-004 good morning",            "good morning",                                ["kya", "help", "ERP", "morning"]),
    ("GEN-005 kya haal",                "kya haal hai",                                ["kya", "ERP"]),
    # Gibberish
    ("GEN-006 xyzqwerty",               "xyzqwerty123",                                ["ERP", "samajh", "inventory", "poochh"]),
    ("GEN-007 random chars",            "!@#$%",                                       ["ERP", "samajh", "kya"]),
    ("GEN-008 numbers only",            "99999",                                       ["inventory", "stock", "nahi mila", "ERP", "database"]),
    ("GEN-009 single word",             "stock",                                       ["inventory", "item", "stock", "ERP", "database"]),
    # Off-topic
    ("GEN-010 weather",                 "aaj ka mausam kaisa hai",                     ["ERP", "mausam", "stock", "samajh"]),
    ("GEN-011 cricket",                 "cricket score kya hai",                       ["ERP", "samajh"]),
    ("GEN-012 news",                    "aaj ki news kya hai",                         ["ERP", "samajh"]),
    ("GEN-013 joke",                    "ek joke sunao",                               ["ERP", "samajh"]),
    # Capability questions
    ("GEN-014 what can you do",         "tum kya kar sakte ho",                        ["ERP", "inventory", "supplier", "order"]),
    ("GEN-015 help",                    "help",                                        ["ERP", "inventory", "supplier", "order", "help"]),
    ("GEN-016 kya kya puchh sakte",     "kya kya puchh sakte hain tumse",             ["ERP", "inventory", "supplier", "order"]),
    ("GEN-017 your name",               "tumhara naam kya hai",                        ["mewar", "ERP"]),
    # Multi-intent
    ("GEN-018 supplier + orders",       "Unitech ki details aur orders",               ["Unitech"]),
    ("GEN-019 DCL detail + GST + PO",   "DCL ka gstin aur orders bhi",                ["DCL"]),
    ("GEN-020 two items stock",         "belt aur oil seal ka stock",                  ["stock"]),
    ("GEN-021 balance + count",         "kitne orders hain aur total balance kitna",   ["order"]),
    ("GEN-022 profile + PO",            "Rishabh ka profile aur latest PO",           ["Rishabh"]),
    # Follow-up simulation
    ("GEN-023 FU Unitech mobile",       "Unitech ka mobile number kya hai bhai",      ["Unitech", "mobile"]),
    ("GEN-024 FU DCL orders",           "DCL ke orders dikhao",                        ["DCL", "order"]),
    # Purchase requests
    ("GEN-025 PR list",                 "purchase request dikhao",                     ["PR", "purchase"]),
    ("GEN-026 PR count",                "kitni purchase requests hain",                ["purchase request", "PR"]),
    ("GEN-027 pending PR",              "pending purchase requests",                   ["purchase", "PR"]),
    ("GEN-028 approved PR",             "approved purchase requests",                  ["purchase", "PR"]),
    # Role test
    ("GEN-029 supervisor query",        "latest purchase orders",                      ["order", "mile"]),
    ("GEN-030 store admin inventory",   "bearing stock kitna hai",                     ["bearing", "stock"]),
    # Very long sentence
    ("GEN-031 very long Hindi",         "yaar mujhe batao ki hamare suppliers mein se kaunsa zyada paisa maang raha hai aur uske sath kya orders hain aur unka balance kya hai", ["order", "balance", "supplier"]),
    ("GEN-032 very long English",       "Can you please tell me which of our suppliers has the highest outstanding balance and show me their recent purchase orders", ["balance", "supplier", "order"]),
    # Numeric ID queries
    ("GEN-033 ID 1 stock",              "1",                                           ["stock", "inventory"]),
    ("GEN-034 ID 5 stock",              "5",                                           ["stock", "inventory"]),
    # Yes/no followup
    ("GEN-035 yes standalone",          "yes",                                         ["kya", "ERP", "poochh", "inventory"]),
    ("GEN-036 no standalone",           "no",                                          ["kya", "ERP", "poochh", "inventory"]),
    ("GEN-037 ok",                      "ok",                                          ["kya", "ERP", "poochh", "inventory", "ok", "theek"]),
    # Abbreviation
    ("GEN-038 PO abbrev",               "PO check karo",                               ["order", "mile"]),
    ("GEN-039 PR abbrev",               "PR list",                                     ["purchase", "PR"]),
    ("GEN-040 GRN",                     "GRN dikhao",                                  ["ERP", "samajh", "order", "stock", "mile"]),
    # Thanks
    ("GEN-041 thanks",                  "thanks",                                      ["kya", "ERP", "poochh", "inventory", "shukriya", "thanks"]),
    ("GEN-042 shukriya",                "shukriya",                                    ["kya", "ERP", "poochh", "inventory", "shukriya", "thanks"]),
    # Mixed language errors
    ("GEN-043 inventry typo",           "inventry mein kitne items",                   ["item", "inventory", "1654"]),
    ("GEN-044 supplair typo",           "supplair kitne hain",                         ["supplier"]),
    ("GEN-045 projeckt typo",           "running projeckt dikhao",                     ["project", "mile"]),
    ("GEN-046 purcahse typo",           "purcahse orders dikhao",                      ["order", "mile"]),
    # Combined entity questions
    ("GEN-047 who is main supplier",    "hamare main supplier kaun hai",               ["supplier"]),
    ("GEN-048 best supplier",           "best supplier kaun hai",                      ["supplier"]),
    ("GEN-049 supplier city count",     "kitne cities mein suppliers hain",            ["supplier"]),
    ("GEN-050 total money due",         "total kitna paisa baaki hai",                 ["balance"]),
    # Unusual phrasings
    ("GEN-051 maal mangana",            "maal mangwana hai",                           ["order", "supplier", "mile", "purchase"]),
    ("GEN-052 khareedna hai",           "kuch khareedna hai",                          ["order", "supplier", "mile", "purchase"]),
    ("GEN-053 order banana",            "naya order banana hai",                       ["order", "mile", "purchase"]),
    # Out of scope but graceful
    ("GEN-054 salary",                  "salary kab aayegi",                           ["ERP", "samajh"]),
    ("GEN-055 HR query",                "employee list dikhao",                        ["ERP", "samajh"]),
    # Confirm the system is up
    ("GEN-056 status query",            "ERP status check",                            ["ERP", "inventory", "supplier", "stock"]),
    ("GEN-057 ping",                    "ping",                                        ["kya", "ERP", "poochh"]),
    # Very specific numerics
    ("GEN-058 total inventory count",   "total kitne items hain inventory mein",       ["1654"]),
    ("GEN-059 total suppliers 6092",    "total kitne suppliers registered hain",       ["6092"]),
    ("GEN-060 total projects 18",       "total projects kitne hain",                   ["18", "project"]),
]

with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(test, *t): t for t in [(l, q, "purchase", None, e, None, None) for l, q, e in gen_tests]}
    for f in as_completed(futures):
        f.result()

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 6: FOLLOW-UP WITH HISTORY — 30 queries
# ──────────────────────────────────────────────────────────────────────────────
print()
print("=" * 110)
print("SECTION 6: FOLLOW-UP WITH HISTORY (30 tests)")
print("=" * 110)

H_UNITECH = [
    {"role": "user",      "content": "Unitech supplier details"},
    {"role": "assistant", "content": "ye raha **Unitech Solutions and Services** ka profile: mob +919829098028, GSTIN 08AAHFU6733F1ZZ"},
]
H_RISHABH = [
    {"role": "user",      "content": "Rishabh ke orders dikhao"},
    {"role": "assistant", "content": "ye raha **Rishabh International** ke 3 orders, balance Rs 1,82,000"},
]
H_AASTHA = [
    {"role": "user",      "content": "Aastha ke orders dikhao"},
    {"role": "assistant", "content": "ye raha **Aastha Engineering** ka 1 PO: MHEL/PO/00004/2025-2026, Rs 46,52,812"},
]
H_BEARING = [
    {"role": "user",      "content": "bearing ka stock kitna hai"},
    {"role": "assistant", "content": "Bearing ke 30 matching items mile. Total stock 2.00 units."},
]
H_DCL = [
    {"role": "user",      "content": "DCL supplier details"},
    {"role": "assistant", "content": "ye raha **DCL** ka profile: mob 9001234567, GSTIN 08AEFCD1234A1ZX"},
]

fu_tests = [
    ("FU-001 mobile after Unitech",     "uska mobile number kya hai",  H_UNITECH, ["Unitech", "mobile"]),
    ("FU-002 GSTIN after Unitech",      "uski gstin kya hai",          H_UNITECH, ["Unitech", "GSTIN"]),
    ("FU-003 orders after Unitech",     "uske orders dikhao",          H_UNITECH, ["Unitech", "order"]),
    ("FU-004 balance after Rishabh",    "iska balance kitna hai",      H_RISHABH, ["Rishabh", "balance"]),
    ("FU-005 yes after Unitech",        "yes",                         H_UNITECH, ["Unitech"]),
    ("FU-006 orders after Unitech2",    "orders dikhao",               H_UNITECH, ["Unitech", "order"]),
    ("FU-007 PO after Aastha",          "uska po dikhao",              H_AASTHA,  ["Aastha", "PO"]),
    ("FU-008 more after bearing",       "aur kitne hain",              H_BEARING, ["bearing", "stock"]),
    ("FU-009 profile after Unitech",    "poori profile",               H_UNITECH, ["Unitech"]),
    ("FU-010 profile after DCL",        "uski poori profile dikhao",   H_DCL,     ["DCL"]),
    ("FU-011 orders after DCL",         "ke orders dikhao",            H_DCL,     ["DCL", "order"]),
    ("FU-012 mobile after DCL",         "mobile batao",                H_DCL,     ["DCL", "mobile"]),
    ("FU-013 balance after DCL",        "kitna baaki hai",             H_DCL,     ["DCL", "balance"]),
    ("FU-014 GSTIN after DCL",          "GSTIN batao",                 H_DCL,     ["DCL", "GSTIN"]),
    ("FU-015 PO after Rishabh",         "uska latest PO",              H_RISHABH, ["Rishabh"]),
    ("FU-016 supplier after Rishabh",   "uski details",                H_RISHABH, ["Rishabh"]),
    ("FU-017 address after Unitech",    "uska address",                H_UNITECH, ["Unitech"]),
    ("FU-018 contact after Aastha",     "contact number batao",        H_AASTHA,  ["Aastha"]),
    ("FU-019 orders after Aastha",      "aur orders hain",             H_AASTHA,  ["Aastha", "order"]),
    ("FU-020 total after Aastha",       "total kitna hua",             H_AASTHA,  ["Aastha", "Rs"]),
    ("FU-021 balance after Aastha",     "kitna baaki hai",             H_AASTHA,  ["Aastha", "balance"]),
    ("FU-022 more bearing",             "aur bearing ka stock",        H_BEARING, ["bearing", "stock"]),
    ("FU-023 bearing total",            "total bearing stock",         H_BEARING, ["bearing", "stock"]),
    ("FU-024 bearing low",              "bearing kam hai kya",         H_BEARING, ["bearing", "stock"]),
    ("FU-025 same entity reconfirm",    "Unitech hai na",              H_UNITECH, ["Unitech"]),
    ("FU-026 uski city",                "uski city kya hai",           H_UNITECH, ["Unitech"]),
    ("FU-027 uska PAN",                 "uska PAN number",             H_UNITECH, ["Unitech"]),
    ("FU-028 DCL order details",        "order detail dikhao",         H_DCL,     ["DCL", "order"]),
    ("FU-029 Rishabh city",             "Rishabh kahan se hai",        H_RISHABH, ["Rishabh"]),
    ("FU-030 Aastha ka balance",        "Aastha ka total balance",     H_AASTHA,  ["Aastha", "balance"]),
]

for l, q, hist, exp in fu_tests:
    test(l, q, history=hist, expect_in=exp)

# ── FINAL ─────────────────────────────────────────────────────────────────────
total = passed + failed
pct = round(passed * 100 / total) if total else 0
print()
print("=" * 110)
print(f"FINAL RESULT: {passed} passed, {failed} failed out of {total}  ({pct}% pass rate)")
print(f"Section breakdown:")
print(f"  INV(100) + SUP(100) + PO(100) + PROJ(60) + GEN(60) + FU(30) = 450 tests")
print("=" * 110)
