"""
Mewar ERP Chatbot — Full Test Suite
Calls chatbot function IN-PROCESS with a fresh DB session per test.
No HTTP, no connection pool issues.
"""

import sys, os, json, time, io
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from app.db.database import SessionLocal
from app.schemas.chat import ChatRequest
from app.routers.chatbot_final_prod import chatbot as _chatbot

TESTS = [
    # ── STOCK / INVENTORY ─────────────────────────────────────────────────────
    {"id": "S01",  "cat": "Stock",      "q": "HR Plate 10mm ka stock kitna hai",                    "expect": "9850"},
    {"id": "S02",  "cat": "Stock",      "q": "BEARING 6204 ka stock batao",                         "expect": "2000"},
    {"id": "S03",  "cat": "Stock",      "q": "Channel 100x50 ka stock kitna hai",                   "expect": "1620"},
    {"id": "S04",  "cat": "Stock",      "q": "HR Plate 5mm ka stock",                               "expect": "8950"},
    {"id": "S05",  "cat": "Stock",      "q": "Bearing ka total stock batao",                        "expect": ""},
    {"id": "S06",  "cat": "Stock",      "q": "Bolt ka total stock kitna hai",                       "expect": ""},
    {"id": "S07",  "cat": "Stock",      "q": "Sabse zyada stock kis item ka hai",                   "expect": "HR Plate"},
    {"id": "S08",  "cat": "Stock",      "q": "Total kitne inventory items hain",                    "expect": "1704"},
    {"id": "S09",  "cat": "Stock",      "q": "Model wise bearing stock dikhao",                     "expect": ""},
    {"id": "S10",  "cat": "Stock",      "q": "HR Plate ke saare models dikhao model wise stock",    "expect": ""},
    {"id": "S11",  "cat": "Stock",      "q": "FINISH placement mein kitne items hain",              "expect": ""},
    {"id": "S12",  "cat": "Stock",      "q": "Bearing aur bolt ka stock ek saath batao",            "expect": "Bearing"},
    {"id": "S13",  "cat": "Stock",      "q": "Gear Box ka stock kitna hai",                         "expect": ""},
    {"id": "S14",  "cat": "Stock",      "q": "Kaunse items ka stock 0 hai",                         "expect": ""},
    {"id": "S15",  "cat": "Stock",      "q": "Min quantity se kam stock wale items batao",          "expect": ""},

    # ── SHORTAGE ──────────────────────────────────────────────────────────────
    {"id": "SH01", "cat": "Shortage",   "q": "BEARING 608 ZZ ki shortage batao",                   "expect": "16"},
    {"id": "SH02", "cat": "Shortage",   "q": "BEARING 2216 ki shortage",                           "expect": "12"},
    {"id": "SH03", "cat": "Shortage",   "q": "BEARING 32021 ki shortage",                          "expect": "8"},
    {"id": "SH04", "cat": "Shortage",   "q": "V Belt C-305 ki shortage",                           "expect": "42"},
    {"id": "SH05", "cat": "Shortage",   "q": "Tool Right 1 inch ki shortage",                      "expect": "22"},
    {"id": "SH06", "cat": "Shortage",   "q": "Kitne items ki shortage hai",                        "expect": ""},
    {"id": "SH07", "cat": "Shortage",   "q": "Sabse zyada shortage kisme hai",                     "expect": ""},
    {"id": "SH08", "cat": "Shortage",   "q": "Required vs available report dikhao",                "expect": "required"},

    # ── PROJECTS ──────────────────────────────────────────────────────────────
    {"id": "P01",  "cat": "Project",    "q": "Total kitne projects hain",                           "expect": "27"},
    {"id": "P02",  "cat": "Project",    "q": "RBL Minerals ki deadline kya hai",                   "expect": "2026-05-30"},
    {"id": "P03",  "cat": "Project",    "q": "RBL Minerals ka start date",                         "expect": "2026-04-28"},
    {"id": "P04",  "cat": "Project",    "q": "Mahakal Stone Crusher ki deadline kya hai",           "expect": "2026-07-15"},
    {"id": "P05",  "cat": "Project",    "q": "Shree Balaji Stone Crusher ki end date",              "expect": "2026-05-12"},
    {"id": "P06",  "cat": "Project",    "q": "warrgyizmorsch project ki end date",                  "expect": "2026-05-25"},
    {"id": "P07",  "cat": "Project",    "q": "In progress projects dikhao",                        "expect": ""},
    {"id": "P08",  "cat": "Project",    "q": "New status wale projects kitne hain",                "expect": ""},
    {"id": "P09",  "cat": "Project",    "q": "RBL Minerals ki inventory batao",                    "expect": "Motor"},
    {"id": "P10",  "cat": "Project",    "q": "Mahakal Stone Crusher ki inventory dikhao",          "expect": ""},
    {"id": "P11",  "cat": "Project",    "q": "Kaunse projects ki deadline nikal gayi hai",         "expect": ""},
    {"id": "P12",  "cat": "Project",    "q": "Bhagwati Construction Company Barmer ki inventory",  "expect": ""},
    {"id": "P13",  "cat": "Project",    "q": "Musale Construction Nagpur project ka status",       "expect": "new"},
    {"id": "P14",  "cat": "Project",    "q": "Jo projects abhi chal rahe hain unki list dikhao",   "expect": ""},
    {"id": "P15",  "cat": "Project",    "q": "Uday Mines Dewas ki deadline",                       "expect": "2026-05-06"},
    {"id": "P16",  "cat": "Project",    "q": "Madhav Minetech Kachchh ka end date kya hai",        "expect": "2026-04-22"},
    {"id": "P17",  "cat": "Project",    "q": "Normal priority projects dikhao",                    "expect": ""},
    {"id": "P18",  "cat": "Project",    "q": "April 2026 mein start hone wale projects",           "expect": ""},

    # ── GRN ───────────────────────────────────────────────────────────────────
    {"id": "G01",  "cat": "GRN",        "q": "Total kitne GRNs hain",                              "expect": "4"},
    {"id": "G02",  "cat": "GRN",        "q": "Sabse recent GRN kaunsa hai",                        "expect": "GRN-004"},
    {"id": "G03",  "cat": "GRN",        "q": "Arawali Minerals ke saare GRNs dikhao",              "expect": "GRN"},
    {"id": "G04",  "cat": "GRN",        "q": "GRN-004 mein kitna accept hua",                      "expect": "1"},
    {"id": "G05",  "cat": "GRN",        "q": "GRN-002 mein kitna accept hua",                      "expect": "0"},
    {"id": "G06",  "cat": "GRN",        "q": "Arawali Minerals ka total accepted qty sabhi GRNs mein", "expect": "7"},
    {"id": "G07",  "cat": "GRN",        "q": "April 2026 ke GRNs dikhao",                          "expect": "GRN-004"},
    {"id": "G08",  "cat": "GRN",        "q": "16 April 2026 ka GRN kaunsa tha",                    "expect": "GRN-004"},
    {"id": "G09",  "cat": "GRN",        "q": "March 2026 ke GRNs",                                 "expect": "GRN-003"},
    {"id": "G10",  "cat": "GRN",        "q": "Kaunsa GRN completed status mein hai",               "expect": "GRN-004"},

    # ── PURCHASE ORDERS ───────────────────────────────────────────────────────
    {"id": "PO01", "cat": "PO",         "q": "Total kitne purchase orders hain",                   "expect": "52"},
    {"id": "PO02", "cat": "PO",         "q": "Sabse latest PO kaunsa hai",                         "expect": "00044"},
    {"id": "PO03", "cat": "PO",         "q": "NMTG Mechtrans ka PO total kitna hai",               "expect": "57980"},
    {"id": "PO04", "cat": "PO",         "q": "Alloy Steel Traders ke kitne POs hain",              "expect": "2"},
    {"id": "PO05", "cat": "PO",         "q": "Bhagwati Lubricants ka PO total amount",             "expect": "168504"},
    {"id": "PO06", "cat": "PO",         "q": "DK Metal Alloys ka PO kitne ka tha",                 "expect": "767000"},
    {"id": "PO07", "cat": "PO",         "q": "11 May 2026 ke saare POs dikhao",                    "expect": ""},
    {"id": "PO08", "cat": "PO",         "q": "Draft status mein kitne POs hain",                   "expect": ""},
    {"id": "PO09", "cat": "PO",         "q": "Is mahine ke purchase orders dikhao",                "expect": ""},
    {"id": "PO10", "cat": "PO",         "q": "Sabse mehengi PO kaunsi hai",                        "expect": ""},
    {"id": "PO11", "cat": "PO",         "q": "Eastern Bearings ka PO total",                       "expect": "211769"},
    {"id": "PO12", "cat": "PO",         "q": "Maheshwari Agencies ka PO kitne ka hai",             "expect": "339037"},
    {"id": "PO13", "cat": "PO",         "q": "MEWAR HITECH firm ke saare POs dikhao",              "expect": ""},
    {"id": "PO14", "cat": "PO",         "q": "May 2026 ke POs mein total kitna kharcha hua",       "expect": ""},
    {"id": "PO15", "cat": "PO",         "q": "Hanny Enterprises ka PO",                            "expect": "128620"},

    # ── PURCHASE REQUESTS ─────────────────────────────────────────────────────
    {"id": "PR01", "cat": "PurchaseReq","q": "Total kitne purchase requests hain",                 "expect": "5"},
    {"id": "PR02", "cat": "PurchaseReq","q": "PR-103 ka status kya hai",                           "expect": "submitted"},
    {"id": "PR03", "cat": "PurchaseReq","q": "HIGH priority purchase requests dikhao",             "expect": "PR-102"},
    {"id": "PR04", "cat": "PurchaseReq","q": "Mewar Store ne kitne PRs banaye",                    "expect": "2"},
    {"id": "PR05", "cat": "PurchaseReq","q": "Ordered status mein kitne PRs hain",                 "expect": "2"},
    {"id": "PR06", "cat": "PurchaseReq","q": "PR-102 ki total qty kitni hai",                      "expect": "7"},
    {"id": "PR07", "cat": "PurchaseReq","q": "Super Admin ne kitne purchase requests banaye",      "expect": ""},
    {"id": "PR08", "cat": "PurchaseReq","q": "Approved purchase requests dikhao",                  "expect": "PR-100"},
    {"id": "PR09", "cat": "PurchaseReq","q": "Partially ordered PR kaunsi hai",                    "expect": "PR-102"},
    {"id": "PR10", "cat": "PurchaseReq","q": "PR-104 ka status kya hai",                           "expect": "ordered"},

    # ── REQUEST SLIPS ─────────────────────────────────────────────────────────
    {"id": "RS01", "cat": "ReqSlip",    "q": "Total kitne request slips hain",                     "expect": "13"},
    {"id": "RS02", "cat": "ReqSlip",    "q": "RS-00013 ka status kya hai",                         "expect": "Rejected"},
    {"id": "RS03", "cat": "ReqSlip",    "q": "Bhagwati Construction Company Barmer ke kitne request slips hain", "expect": ""},
    {"id": "RS04", "cat": "ReqSlip",    "q": "Pending request slips dikhao",                       "expect": "RS-00011"},
    {"id": "RS05", "cat": "ReqSlip",    "q": "Shree Mahadev Stone Crusher Raniwara ka RS kaunsa hai", "expect": "RS-00010"},
    {"id": "RS06", "cat": "ReqSlip",    "q": "Sonapur Cement ka RS status kya hai",                "expect": "Approved"},
    {"id": "RS07", "cat": "ReqSlip",    "q": "Gorakhnath Construction Company Barmer ka RS kab tha", "expect": "2026-03-13"},
    {"id": "RS08", "cat": "ReqSlip",    "q": "Approved status wale RS dikhao",                     "expect": "RS-00009"},
    {"id": "RS09", "cat": "ReqSlip",    "q": "RS-00010 kaunse project ka hai",                     "expect": "Shree Mahadev"},
    {"id": "RS10", "cat": "ReqSlip",    "q": "April 2026 ke request slips dikhao",                 "expect": ""},
    {"id": "RS11", "cat": "ReqSlip",    "q": "RS-00007 kaunse project ka tha",                     "expect": "Jay Bajrang"},
    {"id": "RS12", "cat": "ReqSlip",    "q": "Girish ne kitne request slips banaye",               "expect": ""},

    # ── ISSUE SLIPS ───────────────────────────────────────────────────────────
    {"id": "IS01", "cat": "IssueSlip",  "q": "Total kitne issue slips hain",                       "expect": "6"},
    {"id": "IS02", "cat": "IssueSlip",  "q": "IS-00006 ki detail batao",                           "expect": "Project A"},
    {"id": "IS03", "cat": "IssueSlip",  "q": "Project A ke kitne issue slips hain",                "expect": "4"},
    {"id": "IS04", "cat": "IssueSlip",  "q": "Bhagwati Construction ke issue slips",               "expect": "IS-00005"},
    {"id": "IS05", "cat": "IssueSlip",  "q": "Partially issued issue slips kaunse hain",           "expect": "IS-00005"},
    {"id": "IS06", "cat": "IssueSlip",  "q": "April 2026 ke issue slips dikhao",                   "expect": "IS-00006"},
    {"id": "IS07", "cat": "IssueSlip",  "q": "IS-00006 mein total issued qty kitni thi",           "expect": "1"},
    {"id": "IS08", "cat": "IssueSlip",  "q": "Issued status wale issue slips dikhao",              "expect": "IS-00006"},
    {"id": "IS09", "cat": "IssueSlip",  "q": "February 2026 ke issue slips",                       "expect": "IS-00001"},
    {"id": "IS10", "cat": "IssueSlip",  "q": "IS-00005 mein pending qty kitni hai",                "expect": "1"},

    # ── SUPPLIERS ─────────────────────────────────────────────────────────────
    {"id": "SUP01","cat": "Supplier",   "q": "Total kitne suppliers hain",                         "expect": ""},
    {"id": "SUP02","cat": "Supplier",   "q": "Arawali Minerals ka supplier code",                  "expect": "SUP-100"},
    {"id": "SUP03","cat": "Supplier",   "q": "Arawali Minerals ka GST number",                     "expect": "YANAGSTIN2004"},
    {"id": "SUP04","cat": "Supplier",   "q": "Aabh Engineering Services ka mobile number",         "expect": "9199925294480"},
    {"id": "SUP05","cat": "Supplier",   "q": "Rajasthan wale suppliers dikhao",                    "expect": "Arawali"},
    {"id": "SUP06","cat": "Supplier",   "q": "Gujarat wale suppliers dikhao",                      "expect": "3 DMAS"},
    {"id": "SUP07","cat": "Supplier",   "q": "Raw Material category ke suppliers kitne hain",      "expect": ""},
    {"id": "SUP08","cat": "Supplier",   "q": "Udaipur ke suppliers batao",                         "expect": "Arawali"},
    {"id": "SUP09","cat": "Supplier",   "q": "Arawali Minerals ka account number",                 "expect": "369625851236"},
    {"id": "SUP10","cat": "Supplier",   "q": "Arawali Minerals ka bank kaunsa hai",                "expect": "IDCF"},

    # ── USERS ─────────────────────────────────────────────────────────────────
    {"id": "U01",  "cat": "Users",      "q": "Total kitne users hain",                             "expect": ""},
    {"id": "U02",  "cat": "Users",      "q": "Store department mein kitne users hain",             "expect": ""},
    {"id": "U03",  "cat": "Users",      "q": "Active users dikhao",                                "expect": "Active"},
    {"id": "U04",  "cat": "Users",      "q": "Sonu Singh ki email kya hai",                        "expect": "hodmewar@gmail.com"},
    {"id": "U05",  "cat": "Users",      "q": "Production department mein kaun kaun hai",           "expect": ""},
    {"id": "U06",  "cat": "Users",      "q": "HOD role wale users dikhao",                        "expect": "Sonu"},
    {"id": "U07",  "cat": "Users",      "q": "store@warr.com email wala user kaunsa hai",          "expect": "store"},

    # ── MACHINES ──────────────────────────────────────────────────────────────
    {"id": "M01",  "cat": "Machine",    "q": "Total kitne machines hain",                          "expect": "50"},
    {"id": "M02",  "cat": "Machine",    "q": "30x15 STG machine ka status kya hai",               "expect": "Active"},
    {"id": "M03",  "cat": "Machine",    "q": "Deleted machines kaunse hain",                       "expect": "30x15 STG"},
    {"id": "M04",  "cat": "Machine",    "q": "Vibro Feeder machines dikhao",                       "expect": "Vibro"},
    {"id": "M05",  "cat": "Machine",    "q": "Stone Crusher machines kitne hain",                  "expect": ""},
    {"id": "M06",  "cat": "Machine",    "q": "30x15 STG machine mein kaunsa item lagta hai",      "expect": "Motor"},

    # ── VENDORS ───────────────────────────────────────────────────────────────
    {"id": "V01",  "cat": "Vendor",     "q": "Total kitne vendors hain",                           "expect": "2"},
    {"id": "V02",  "cat": "Vendor",     "q": "Bhagyashree Engineering Work ka email",              "expect": "Bhagyashree"},
    {"id": "V03",  "cat": "Vendor",     "q": "Manish Vendor ka city kya hai",                      "expect": "Udaipur"},
    {"id": "V04",  "cat": "Vendor",     "q": "Udaipur wale vendors dikhao",                        "expect": "Bhagyashree"},

    # ── FOLLOW-UP / PRONOUN RESOLUTION ───────────────────────────────────────
    {"id": "F01",  "cat": "FollowUp",   "q": "BEARING 608 ZZ ka stock batao",                      "expect": "",
     "followup": "Iski min quantity kitni hai"},
    {"id": "F02",  "cat": "FollowUp",   "q": "RBL Minerals ki detail batao",                       "expect": "",
     "followup": "Is project ki deadline kya hai",  "f_expect": "2026-05-30"},
    {"id": "F03",  "cat": "FollowUp",   "q": "Arawali Minerals ke GRNs dikhao",                   "expect": "",
     "followup": "Inme se kitne completed hain",    "f_expect": "1"},

    # ── HINGLISH FILTERS ──────────────────────────────────────────────────────
    {"id": "H01",  "cat": "Hinglish",   "q": "Sabse zyada paisa baaki kiske paas hai suppliers mein", "expect": ""},
    {"id": "H02",  "cat": "Hinglish",   "q": "Is mahine kitne GRNs aaye",                          "expect": ""},
    {"id": "H03",  "cat": "Hinglish",   "q": "Bearings ka model wise stock dikhao",                "expect": ""},
    {"id": "H04",  "cat": "Hinglish",   "q": "Kab tak chalega Mahakal Stone Crusher project",      "expect": "2026-07-15"},
    {"id": "H05",  "cat": "Hinglish",   "q": "Kitne projects new hain aur kitne in progress",      "expect": ""},
    {"id": "H06",  "cat": "Hinglish",   "q": "V Belt C-305 ki shortage kitni hai",                 "expect": "42"},
    {"id": "H07",  "cat": "Hinglish",   "q": "Saare approved request slips dikhao",                "expect": ""},
    {"id": "H08",  "cat": "Hinglish",   "q": "Rejected wale request slips kaun kaun se hain",      "expect": "RS-00013"},
    {"id": "H09",  "cat": "Hinglish",   "q": "Pichle mahine ke purchase orders",                   "expect": ""},
    {"id": "H10",  "cat": "Hinglish",   "q": "Shree Radhe Minerals Rajsamand ki end date",         "expect": "2026-05-22"},
]

LOG_FILE = "chatbot_full_test_results.json"


def extract_text(resp_dict: dict) -> str:
    """Pull all text out of the chatbot response dict."""
    parts = []
    for item in resp_dict.get("results", []):
        t = item.get("type", "")
        if t == "chat":
            parts.append(item.get("message", ""))
        elif t == "nl2sql_table":
            rows = item.get("rows", [])
            for row in rows:
                parts.append(" ".join(str(v) for v in row.values()))
        elif t == "result":
            parts.append(str(item.get("total_stock", "")))
            parts.append(str(item))
        else:
            parts.append(str(item))
    return " | ".join(p for p in parts if p)


def call_chatbot(query: str, history: list = None) -> tuple[str, dict]:
    """Call chatbot in-process with a fresh DB session. Returns (text, raw_resp)."""
    db = SessionLocal()
    try:
        req = ChatRequest(query=query, role="Super Admin", history=history or [])
        resp = _chatbot(req, db)
        text = extract_text(resp)
        return text, resp
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        # Invalidate the connection so SQLAlchemy doesn't try to rollback a dead socket
        try:
            db.invalidate()
        except Exception:
            pass
        return f"EXCEPTION: {e}\n{tb[:300]}", {}
    finally:
        try:
            db.close()
        except Exception:
            pass  # connection already dead — ignore rollback error


def check(answer: str, expect: str) -> str:
    if not expect:
        return "REVIEW"
    a = answer.lower().replace(",", "").replace(".", "")
    e = expect.lower().replace(",", "").replace(".", "")
    return "PASS" if e in a else "FAIL"


def run_tests():
    results = []
    cats: dict = {}
    total = pass_ = fail = review = 0

    log_f = open(LOG_FILE, "w", encoding="utf-8")
    log_f.write("[\n")
    first_entry = True

    print(f"\n{'='*80}")
    print(f"  MEWAR ERP CHATBOT - FULL TEST SUITE  ({len(TESTS)} tests)")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: in-process (fresh DB session per test)")
    print(f"  Log: {LOG_FILE}")
    print(f"{'='*80}\n")
    sys.stdout.flush()

    for i, t in enumerate(TESTS, 1):
        tid     = t["id"]
        cat     = t["cat"]
        q       = t["q"]
        expect  = t.get("expect", "")
        followup= t.get("followup")
        f_exp   = t.get("f_expect", "")

        print(f"[{i:03d}/{len(TESTS)}] {tid} ({cat})")
        print(f"  Q : {q}")
        sys.stdout.flush()

        t0 = time.time()
        # Retry once on connection error
        for attempt in range(2):
            ans, raw = call_chatbot(q)
            if not ans.startswith("EXCEPTION:") or "MySQL server has gone away" not in ans:
                break
            print(f"  [retry {attempt+1}] DB connection dropped, waiting 5s...")
            time.sleep(5)
        elapsed = time.time() - t0

        history = []
        f_ans = ""
        if followup:
            history = [
                {"role": "user",      "content": q},
                {"role": "assistant", "content": ans},
            ]
            f_ans, _ = call_chatbot(followup, history)
            print(f"  A : {ans[:180]}")
            print(f"  Q2: {followup}")
            print(f"  A2: {f_ans[:180]}")
        else:
            print(f"  A : {ans[:180]}")

        # Determine status
        if followup:
            status = check(f_ans, f_exp) if f_exp else ("REVIEW" if not expect else check(ans, expect))
        else:
            status = check(ans, expect)

        tag = f"[{status}]"
        if expect:
            print(f"  {tag} expect '{expect}' in answer   ({elapsed:.1f}s)")
        else:
            print(f"  {tag} (no expected value, manual review)   ({elapsed:.1f}s)")
        sys.stdout.flush()

        total += 1
        if status == "PASS":   pass_  += 1
        elif status == "FAIL": fail   += 1
        else:                  review += 1

        cats.setdefault(cat, {"pass": 0, "fail": 0, "review": 0})
        cats[cat]["pass" if status=="PASS" else "fail" if status=="FAIL" else "review"] += 1

        entry = {
            "id": tid, "cat": cat,
            "question": q,
            "answer": ans,
            "followup_q": followup or "",
            "followup_a": f_ans,
            "expected": expect,
            "status": status,
            "elapsed_s": round(elapsed, 1),
            "ts": datetime.now().strftime("%H:%M:%S"),
        }
        results.append(entry)

        if not first_entry:
            log_f.write(",\n")
        log_f.write(json.dumps(entry, ensure_ascii=False))
        log_f.flush()
        first_entry = False
        print()
        time.sleep(2)  # give remote DB breathing room between tests

    log_f.write("\n]\n")
    log_f.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*80}")
    print(f"  Total : {total}")
    print(f"  PASS  : {pass_}  ({100*pass_//total if total else 0}%)")
    print(f"  FAIL  : {fail}")
    print(f"  REVIEW: {review}  (no expected value — manual check)")
    print(f"\n  Per Category:")
    for c, s in sorted(cats.items()):
        bar = "P"*s["pass"] + "F"*s["fail"] + "?"*s["review"]
        print(f"    {c:14s}  PASS:{s['pass']:2d}  FAIL:{s['fail']:2d}  REVIEW:{s['review']:2d}  [{bar}]")

    print(f"\n  FAILURES:")
    any_fail = False
    for r in results:
        if r["status"] == "FAIL":
            any_fail = True
            print(f"    [{r['id']}] {r['question']}")
            print(f"           Expected : '{r['expected']}'")
            a_short = r["answer"][:180]
            print(f"           Got      : {a_short}")
            print()
    if not any_fail:
        print("    None! All expected-value tests passed.")

    print(f"\n  Full results: {LOG_FILE}")
    print(f"{'='*80}\n")
    sys.stdout.flush()


if __name__ == "__main__":
    run_tests()
