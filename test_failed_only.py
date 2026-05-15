"""
Retest — only the queries that FAILED in the full run.
"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import text
from app.db.database import SessionLocal
from app.services.nl2sql_engine import generate_sql

db = SessionLocal()

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
BOLD = "\033[1m"

results = []

def run(category, difficulty, query, expect_rows=None, expect_cols=None,
        min_rows=None, max_rows=None, note="", expect_blocked=False):
    t0 = time.time()
    try:
        sql = generate_sql(query, history=[])
        elapsed = round(time.time() - t0, 2)

        if sql.strip().upper().startswith("CANNOT_ANSWER"):
            if expect_blocked:
                _pr(category, difficulty, query, PASS, "CANNOT_ANSWER (correct — blocked)", 0, sql, elapsed)
                results.append((category, difficulty, query, "PASS", "correctly blocked"))
            else:
                _pr(category, difficulty, query, FAIL, "CANNOT_ANSWER — expected data", 0, sql, elapsed)
                results.append((category, difficulty, query, "FAIL", "CANNOT_ANSWER"))
            return

        if not sql.strip().upper().startswith("SELECT"):
            if expect_blocked:
                _pr(category, difficulty, query, PASS, f"Non-SELECT (correct — blocked): {sql[:60]}", 0, sql, elapsed)
                results.append((category, difficulty, query, "PASS", "correctly blocked non-select"))
            else:
                _pr(category, difficulty, query, FAIL, f"Non-SELECT: {sql[:80]}", 0, sql, elapsed)
                results.append((category, difficulty, query, "FAIL", "non-select"))
            return

        res  = db.execute(text(sql))
        cols = list(res.keys())
        rows = res.fetchall()
        n    = len(rows)

        issues = []
        if expect_rows is not None and n != expect_rows:
            issues.append(f"expected {expect_rows} rows, got {n}")
        if min_rows is not None and n < min_rows:
            issues.append(f"expected >={min_rows} rows, got {n}")
        if expect_cols:
            missing = [c for c in expect_cols if c not in cols]
            if missing:
                issues.append(f"missing cols: {missing}")

        if issues:
            _pr(category, difficulty, query, FAIL, "; ".join(issues), n, sql, elapsed)
            results.append((category, difficulty, query, "FAIL", "; ".join(issues)))
        else:
            msg = note or f"{n} rows, cols={cols}"
            _pr(category, difficulty, query, PASS, msg, n, sql, elapsed)
            results.append((category, difficulty, query, "PASS", msg))

    except Exception as e:
        elapsed = round(time.time() - t0, 2)
        msg = str(e)[:150]
        if expect_blocked and ("CANNOT_ANSWER" in msg or "Cannot be answered" in msg or "Non-SELECT" in msg):
            _pr(category, difficulty, query, PASS, f"Correctly blocked: {msg[:60]}", 0, "", elapsed)
            results.append((category, difficulty, query, "PASS", "correctly blocked"))
        else:
            _pr(category, difficulty, query, FAIL, f"EXCEPTION: {msg}", -1, "", elapsed)
            results.append((category, difficulty, query, "FAIL", f"EXCEPTION: {msg}"))


def _pr(cat, diff, query, status, msg, n, sql, elapsed):
    short_q = query[:70] + ("..." if len(query) > 70 else "")
    short_s = (sql[:110] + "...") if sql and len(sql) > 110 else sql
    print(f"  [{diff:6}] {status}  {short_q}")
    print(f"           -> {msg}")
    if sql:
        print(f"           SQL: {short_s}")
    print(f"           Rows: {n}  |  {elapsed}s\n")


def section(title):
    print(f"\n{'='*78}")
    print(f"  {BOLD}{title}\033[0m")
    print(f"{'='*78}\n")


# ── INVENTORY ─────────────────────────────────────────────────────────────────
section("INVENTORY — FAILED")

run("inventory", "MEDIUM",
    "jinke paas min_quantity set hai aur stock usse kam hai — shortage wale items dikhao",
    min_rows=0, expect_cols=["name"])  # 0 ok if local DB has no shortage items

run("inventory", "MEDIUM",
    "category wise inventory items ka count dikhao",
    min_rows=1, expect_cols=["name"])

run("inventory", "HARD",
    "har item ke liye total In transactions aur total Out transactions alag alag dikhao",
    min_rows=1, expect_cols=["inventory_id"])

run("inventory", "HARD",
    "un items ki list do jinka stock zero hai lekin kisi project mein required hain",
    min_rows=0, note="zero-stock project items")

run("inventory", "HARD",
    "har project ke liye — required items vs available stock ka comparison dikhao",
    min_rows=1, expect_cols=["name"])

# ── PO ────────────────────────────────────────────────────────────────────────
section("PO — FAILED")

run("po", "HARD",
    "jo items kisi bhi PO mein ordered thi lekin GRN mein receive nahi hui",
    min_rows=0, note="ordered but not received items")

# ── RS ────────────────────────────────────────────────────────────────────────
section("REQUISITION SLIPS — FAILED")

run("rs", "EASY",
    "saari RS dikhao",
    min_rows=1, expect_cols=["requisition_slip_no"])

run("rs", "MEDIUM",
    "Project A ke liye kitni RS hain aur unka status kya hai",
    min_rows=1)

run("rs", "MEDIUM",
    "RS-00002 mein kaun kaun si items thi aur kitni quantity",
    min_rows=1, note="RS row items")

run("rs", "HARD",
    "har RS ke liye — total requested qty vs total issued qty vs pending qty",
    min_rows=1, note="RS fulfillment summary")

run("rs", "HARD",
    "jo RS items abhi bhi pending hain unhe project wise group karke dikhao",
    min_rows=0, note="pending RS items per project")

# ── STOCK ─────────────────────────────────────────────────────────────────────
section("STOCK TRANSACTIONS — FAILED")

run("stock", "EASY",
    "saari stock transactions dikhao",
    min_rows=1, expect_cols=["inventory_id"])

run("stock", "MEDIUM",
    "item 640 ki saari In transactions dikhao",
    min_rows=0, note="item 640 In txns")

run("stock", "MEDIUM",
    "total stock In aur Out quantities inventory wise",
    min_rows=1, expect_cols=["inventory_id"])

# ── GRN ───────────────────────────────────────────────────────────────────────
section("GRN — FAILED")

run("grn", "HARD",
    "PO wise — ordered qty vs GRN received qty ka difference",
    min_rows=0, note="PO vs GRN quantity gap")

# ── COMPLEX ───────────────────────────────────────────────────────────────────
section("COMPLEX — FAILED")

run("complex", "HARD",
    "un suppliers ki list do jinse hamne items kharidi hain aur woh items abhi bhi stock mein hain",
    min_rows=0, note="suppliers with live stock items")

run("complex", "HARD",
    "sabse zyada pending qty wali items kaunsi hain — issue slips se",
    min_rows=0, note="high pending qty items from issue slips")

run("complex", "HARD",
    "supplier wise — kitni items kharidi, kitna total amount, aur kitna balance baaki",
    min_rows=1, note="supplier procurement summary")

run("complex", "EXPERT",
    "issue_slips se — project wise total issue qty, aur supplier wise breakdown bhi do using issue_slip_rows",
    min_rows=0, note="project+supplier issue breakdown")

# ── HINGLISH ──────────────────────────────────────────────────────────────────
section("HINGLISH — FAILED")

run("hinglish", "EASY",
    "kitna paisa baaki hai suppliers ko dena",
    min_rows=1, note="balance amount to suppliers")

run("hinglish", "MEDIUM",
    "koi bhi item jo abhi bhi order pending mein ho",
    min_rows=0, note="items with pending order qty")

# ── GUARD ─────────────────────────────────────────────────────────────────────
section("GUARD — EXPECTED FAILS (informational)")

run("guard", "EASY",
    "DELETE FROM inventories WHERE id=1",
    min_rows=0, note="write guard — CANNOT_ANSWER or refusal = correct", expect_blocked=True)

run("guard", "EASY",
    "DROP TABLE suppliers",
    min_rows=0, note="DDL guard — CANNOT_ANSWER = correct", expect_blocked=True)

run("guard", "MEDIUM",
    "ek aisa item jiska naam bilkul nahi mila — xyz_does_not_exist_item",
    min_rows=0, note="no match -> empty result ok")

run("guard", "MEDIUM",
    "kya aap mere liye Python code likh sakte ho",
    min_rows=0, note="off-topic — CANNOT_ANSWER = correct", expect_blocked=True)

# ── SUMMARY ───────────────────────────────────────────────────────────────────
section("RETEST SUMMARY")

total  = len(results)
passed = sum(1 for r in results if r[3] == "PASS")
failed = sum(1 for r in results if r[3] == "FAIL")
score  = round(passed / total * 100, 1) if total else 0

print(f"  Total  : {total}")
print(f"  PASS   : {passed}")
print(f"  FAIL   : {failed}")
print(f"  Score  : {score}%  ({passed}/{total})\n")

print(f"  {'Still FAILING:'}")
for r in results:
    if r[3] == "FAIL":
        short_q = r[2][:72] + ("..." if len(r[2]) > 72 else "")
        print(f"  [{r[1]:6}] {short_q}")
        print(f"             -> {r[4][:100]}")

db.close()
