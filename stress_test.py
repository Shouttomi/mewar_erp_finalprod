"""
Chatbot stress test — fires many queries, logs every result to stress_test.log
Run: python stress_test.py
"""
import requests, json, time, datetime, sys, os, textwrap

BASE    = "http://127.0.0.1:8000/v2-chatbot/"
LOG     = "d:/mewar_erp/stress_test.log"
TIMEOUT = 45   # seconds — LLM calls can take 4-8s

QUERIES = [
    # ── Greetings / general ──────────────────────────────────────────
    ("general_chat",  "hi"),
    ("general_chat",  "hello bhai kya haal hai"),
    ("general_chat",  "help"),
    ("general_chat",  "tum kya kar sakte ho"),
    ("general_chat",  ""),                                    # empty
    ("general_chat",  "   "),                                 # whitespace
    ("general_chat",  "😊"),                                  # emoji only

    # ── Inventory / stock ────────────────────────────────────────────
    ("search",        "bearing ka stock dikhao"),
    ("search",        "belt stock kitna hai"),
    ("search",        "oil seal stock check karo"),
    ("search",        "nut bolt"),
    ("search",        "saare items list karo"),
    ("search",        "filter ka stock"),
    ("search",        "V-belt stock"),
    ("search",        "pump ka stock"),
    ("search",        "gear box stock"),
    ("search",        "hydraulic oil"),
    ("search",        "grease"),
    ("search",        "chain"),
    ("search",        "sprocket stock"),
    ("search",        "cylinder stock"),
    ("search",        "valve"),
    ("search",        "seal kit"),
    ("search",        "bearing 6205 stock"),           # specific bearing number
    ("search",        "motor"),
    ("search",        "cable wire stock"),
    ("search",        "paint"),
    ("search",        "fasteners"),

    # ── Typos / phonetic ────────────────────────────────────────────
    ("search",        "bering ka stock"),              # typo
    ("search",        "beering"),                      # double typo
    ("search",        "seel"),                         # typo for seal
    ("search",        "natt bolt"),                    # typo
    ("search",        "hydrualic oil"),                # typo

    # ── PO / orders ──────────────────────────────────────────────────
    ("po_search",     "pending orders dikhao"),
    ("po_search",     "saare pending po"),
    ("po_search",     "last 5 orders"),
    ("po_search",     "last order dikhao"),
    ("po_search",     "aaj ke orders"),
    ("po_search",     "is mahine ke orders"),
    ("po_search",     "top 5 suppliers by spend"),
    ("po_search",     "total pending balance kitna hai"),
    ("po_search",     "Rishabh International ke orders"),
    ("po_search",     "Paroliya ka balance"),
    ("po_search",     "Adinath Enterprises ke pending orders"),
    ("po_search",     "advance diya hua kitna hai"),
    ("po_search",     "draft orders dikhao"),
    ("po_search",     "50000 se zyada ke orders"),
    ("po_search",     "1 lakh se zyada"),
    ("po_search",     "MHEL orders"),
    ("po_search",     "MTPL orders"),
    ("po_search",     "April ke orders"),
    ("po_search",     "supplier wise order count"),
    ("po_search",     "sabse bada order"),
    ("po_search",     "gst kitna laga total"),

    # ── Supplier search ──────────────────────────────────────────────
    ("supplier_search","Adinath Enterprises details"),
    ("supplier_search","Rishabh International mobile number"),
    ("supplier_search","Paroliya Metals address"),
    ("supplier_search","saare suppliers ki city batao"),
    ("supplier_search","saare suppliers list karo"),
    ("supplier_search","Udaipur ke suppliers"),
    ("supplier_search","Faridabad suppliers"),
    ("supplier_search","Unitech Solutions email"),
    ("supplier_search","Bhilwara Sales gstin"),
    ("supplier_search","DCL Enterprises contact"),
    ("supplier_search","Eastern Bearings details"),
    ("supplier_search","xyz abc nonexistent supplier"),   # not found
    ("supplier_search","sup-001"),                        # code lookup
    ("supplier_search","supplier kitne hain total"),
    ("supplier_search","Ram Bilas address kya hai"),

    # ── Project search ───────────────────────────────────────────────
    ("project_search", "chalu projects dikhao"),
    ("project_search", "running projects"),
    ("project_search", "completed projects"),
    ("project_search", "urgent projects"),
    ("project_search", "sabse bada project"),
    ("project_search", "hold par kaunse projects hain"),
    ("project_search", "overdue projects"),

    # ── Multi-intent / ambiguous ─────────────────────────────────────
    ("multi",         "bearing aur oil seal ka stock"),
    ("multi",         "Rishabh International ke orders aur details"),
    ("multi",         "pending orders aur supplier balance"),

    # ── Follow-up / context ──────────────────────────────────────────
    ("context",       "uska number kya hai",
                      [{"role":"user","content":"Adinath Enterprises details batao"},
                       {"role":"assistant","content":"Adinath Enterprises, Udaipur mil gaye"}]),
    ("context",       "unke orders dikhao",
                      [{"role":"user","content":"Rishabh International"},
                       {"role":"assistant","content":"Rishabh International details"}]),

    # ── Aggregation / analytics ──────────────────────────────────────
    ("aggregation",   "kitne suppliers hain total"),
    ("aggregation",   "city wise supplier count"),
    ("aggregation",   "supplier by city"),
    ("aggregation",   "month wise orders"),
    ("aggregation",   "total order value"),

    # ── Edge / stress ────────────────────────────────────────────────
    ("edge",          "a"),                             # single char
    ("edge",          "1234567890"),                    # numbers only
    ("edge",          "!@#$%"),                         # special chars
    ("edge",          "SELECT * FROM suppliers"),       # SQL injection attempt
    ("edge",          "x" * 500),                       # very long input
    ("edge",          "kuch bhi random baat"),
    ("edge",          "haha lol bhai"),
    ("edge",          "order order order order"),       # repetition

    # ── Date/Time fixes ──────────────────────────────────────────────
    ("po_search",     "aaj ke orders"),                 # today
    ("po_search",     "kal ke orders"),                 # yesterday
    ("po_search",     "April ke orders"),               # named month
    ("po_search",     "January ke orders"),
    ("po_search",     "pichle 3 mahine ke orders"),     # last N months
    ("po_search",     "is saal ke orders"),             # this year
    ("po_search",     "last year orders"),

    # ── PO threshold filters ─────────────────────────────────────────
    ("po_search",     "50000 se zyada ke orders"),
    ("po_search",     "1 lakh se zyada ke orders"),
    ("po_search",     "50000 se kam ke orders"),

    # ── PO advance total ─────────────────────────────────────────────
    ("po_search",     "advance diya hua kitna hai"),
    ("po_search",     "total advance kitna hai"),

    # ── PO pending vs draft ──────────────────────────────────────────
    ("po_search",     "pending orders dikhao"),         # should match draft+pending
    ("po_search",     "draft orders"),

    # ── City-wise supplier ───────────────────────────────────────────
    ("aggregation",   "city wise supplier count"),
    ("aggregation",   "supplier by city"),
    ("supplier_search","saare suppliers ki city batao"),
    ("supplier_search","Udaipur ke suppliers"),         # city from target
    ("supplier_search","Faridabad ke suppliers"),

    # ── Project overdue / hold / urgent ──────────────────────────────
    ("project_search", "overdue projects"),
    ("project_search", "hold par kaunse projects hain"),
    ("project_search", "urgent projects"),
    ("project_search", "high priority projects"),

    # ── Confirm token edge cases ─────────────────────────────────────
    ("edge",          "👍"),                            # thumbs up with no pending
    ("edge",          "👎"),                            # thumbs down with no pending
    ("edge",          "nahi koi nahi"),                 # fuzzy deny phrase

    # ── General chat intent ──────────────────────────────────────────
    ("general_chat",  "weather kaisa hai"),             # non-ERP — should get help msg
    ("general_chat",  "joke sunao"),

    # ── Purchase requests ─────────────────────────────────────────────
    ("po_search",     "purchase request dikhao"),
    ("po_search",     "PR-001 status"),
]


def call(query, history=None):
    payload = {
        "query": query,
        "history": history or [],
        "role": None,
        "ui_filters": {}
    }
    t0 = time.time()
    r  = requests.post(BASE, json=payload, timeout=TIMEOUT)
    ms = int((time.time() - t0) * 1000)
    return r.json(), ms


def classify(results):
    """Return PASS/FAIL/WARN and a short reason."""
    if not results:
        return "FAIL", "empty results list"
    for item in results:
        t = item.get("type", "")
        m = item.get("message", "")
        if t == "error":
            return "FAIL", f"error: {m[:80]}"
        if "traceback" in m.lower() or "500 internal server error" in m.lower():
            return "FAIL", "server error in message"
        if t == "chat" and len(m) < 3:
            return "WARN", "suspiciously short reply"
    types = [i.get("type") for i in results]
    return "PASS", "+".join(dict.fromkeys(types))


def fmt_result(results):
    out = []
    for item in results:
        t = item.get("type", "?")
        m = item.get("message", "")[:120]
        if t in ("po", "po_summary"):
            out.append(f"  [{t}] {item.get('po_no','') or item.get('grp','')} ...")
        elif t == "dropdown":
            cnt = len(item.get("items", []))
            out.append(f"  [dropdown] {cnt} items")
        elif t == "confirm_resolution":
            cands = item.get("candidates", [])
            out.append(f"  [disambig] {len(cands)} candidates: {cands[:3]}")
        else:
            out.append(f"  [{t}] {m}")
    return "\n".join(out)


def run():
    ts   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log  = open(LOG, "w", encoding="utf-8")

    def w(*args, **kwargs):
        line = " ".join(str(a) for a in args)
        try:
            print(line, **kwargs)
        except UnicodeEncodeError:
            print(line.encode("ascii", "replace").decode(), **kwargs)
        print(line, file=log)

    w("=" * 72)
    w(f"CHATBOT STRESS TEST  --  {ts}")
    w(f"Total queries: {len(QUERIES)}")
    w("=" * 72)

    passed = failed = warned = 0
    slow   = []
    failures = []

    for entry in QUERIES:
        category = entry[0]
        query    = entry[1]
        history  = entry[2] if len(entry) > 2 else []

        display_q = (query[:70] + "…") if len(query) > 70 else query
        w(f"\n{'-'*60}")
        w(f"[{category.upper()}]  \"{display_q}\"")

        time.sleep(1)   # avoid overloading the server between queries
        try:
            data, ms = call(query, history)
        except Exception as e:
            w(f"  STATUS  : FAIL  ({str(e)[:80]})")
            failed += 1
            failures.append((category, query, str(e)))
            continue

        results  = data.get("results", [])
        status, reason = classify(results)
        req_id   = data.get("request_id", "?")

        w("  STATUS  : " + status + "  (" + str(ms) + "ms)  [" + reason + "]  req=" + req_id)
        w(fmt_result(results))

        if status == "PASS":
            passed += 1
        elif status == "WARN":
            warned += 1
            failures.append((category, query, f"WARN: {reason}"))
        else:
            failed += 1
            failures.append((category, query, "FAIL: " + reason))

        if ms > 8000:
            slow.append((ms, category, query))

    w("\n" + "=" * 72)
    w(f"SUMMARY  —  PASS:{passed}  WARN:{warned}  FAIL:{failed}  Total:{len(QUERIES)}")
    w(f"Pass rate: {passed/len(QUERIES)*100:.1f}%")
    w("=" * 72)

    if slow:
        w(f"\nSLOW QUERIES (>8s):")
        for ms, cat, q in sorted(slow, reverse=True):
            w(f"  {ms}ms  [{cat}]  \"{q[:60]}\"")

    if failures:
        w(f"\nFAILURES / WARNINGS:")
        for cat, q, reason in failures:
            w(f"  [{cat}]  \"{q[:60]}\"  →  {reason}")

    log.close()
    print(f"\nLog saved -> {LOG}")


if __name__ == "__main__":
    run()
