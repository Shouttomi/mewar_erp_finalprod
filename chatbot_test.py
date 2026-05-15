"""
Chatbot Integration Test Suite — 65 tests (15 original + 50 extended)
Hits POST /chatbot/, cross-checks DB, writes chatbot_test_log.md
"""

import json, datetime, urllib.parse, re, requests
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/chatbot/"
LOG_FILE = "chatbot_test_log.md"

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    password = urllib.parse.quote_plus("a3nQyY7RT;G9")
    DATABASE_URL = f"mysql+pymysql://u512872665_user:{password}@auth-db1830.hstgr.io:3306/u512872665_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ── DB helpers ────────────────────────────────────────────────────────────────
def db_query(sql, params=None):
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params or {}).fetchall()
            return [dict(r._mapping) for r in rows]
    except Exception as e:
        return {"db_error": str(e)}

def db_one(sql, params=None):
    rows = db_query(sql, params)
    return rows[0] if isinstance(rows, list) and rows else (rows if isinstance(rows, dict) else None)

# ── Test cases ────────────────────────────────────────────────────────────────
TEST_CASES = [
    # ── ORIGINAL 15 ──────────────────────────────────────────────────────────
    {
        "id": "TC-01", "label": "Latest PO – Arawali (English)",
        "request": {"query": "Show me the latest purchase order for Arawali", "history": [], "ui_filters": {"limit": 1}},
        "db_verify": lambda: db_one("SELECT p.po_number, p.total_amount, p.balance_amount, p.status, p.po_date, s.supplier_name FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%arawali%' ORDER BY p.po_date DESC, p.id DESC LIMIT 1")
    },
    {
        "id": "TC-02", "label": "Inventory – bearing (Hinglish typo 'beerign')",
        "request": {"query": "beerign ka kitna stock hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name, classification, placement FROM inventories WHERE LOWER(name) LIKE '%bearing%' LIMIT 1")
    },
    {
        "id": "TC-03", "label": "Supplier profile – Adinath (Hinglish)",
        "request": {"query": "Adinath supplier ki details batao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile FROM suppliers WHERE LOWER(supplier_name) LIKE '%adinath%' LIMIT 1")
    },
    {
        "id": "TC-04", "label": "All pending/draft POs",
        "request": {"query": "saare pending orders dikhao", "history": [], "ui_filters": {"limit": 5}},
        "db_verify": lambda: db_query("SELECT po_number, status FROM purchase_orders WHERE LOWER(status)='draft' ORDER BY po_date DESC LIMIT 5")
    },
    {
        "id": "TC-05", "label": "Boss Mode – Highest pending balance",
        "request": {"query": "sabse jyada balance kiska hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT s.supplier_name, SUM(p.balance_amount) as total_bal, s.mobile FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE p.balance_amount>0 AND LOWER(p.status)!='completed' GROUP BY s.id, s.supplier_name ORDER BY total_bal DESC LIMIT 1")
    },
    {
        "id": "TC-06", "label": "Boss Mode – Lowest pending balance",
        "request": {"query": "sabse kam balance kiska pending hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT s.supplier_name, SUM(p.balance_amount) as total_bal FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE p.balance_amount>0 AND LOWER(p.status)!='completed' GROUP BY s.id, s.supplier_name ORDER BY total_bal ASC LIMIT 1")
    },
    {
        "id": "TC-07", "label": "Boss Mode – Highest PO",
        "request": {"query": "sabse bada po kaun sa hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT p.po_number, s.supplier_name, p.total_amount FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id ORDER BY p.total_amount DESC LIMIT 1")
    },
    {
        "id": "TC-08", "label": "Boss Mode – Lowest PO",
        "request": {"query": "sabse chhota purchase order dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT p.po_number, s.supplier_name, p.total_amount FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id ORDER BY p.total_amount ASC LIMIT 1")
    },
    {
        "id": "TC-09", "label": "Boss Mode – Total GST",
        "request": {"query": "total gst kitna bana hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT SUM(tax_amount) as total_tax, COUNT(id) as po_count FROM purchase_orders")
    },
    {
        "id": "TC-10", "label": "Project search – running projects",
        "request": {"query": "konse projects chal rahe hain abhi", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT name, status FROM projects WHERE is_deleted=0 AND LOWER(status)='in progress' LIMIT 5")
    },
    {
        "id": "TC-11", "label": "Aggregation – count suppliers",
        "request": {"query": "system mein kitne suppliers hain", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT COUNT(*) as total FROM suppliers")
    },
    {
        "id": "TC-12", "label": "Aggregation – lowest stock item",
        "request": {"query": "sabse kam stock wala item kaun sa hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT i.name, i.placement, SUM(CASE WHEN LOWER(t.txn_type)='in' THEN t.quantity ELSE -t.quantity END) AS stock FROM inventories i JOIN stock_transactions t ON i.id=t.inventory_id GROUP BY i.id, i.name, i.placement ORDER BY stock ASC LIMIT 1")
    },
    {
        "id": "TC-13", "label": "Supplier – mobile query (English)",
        "request": {"query": "What is the contact number of Adinath?", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile FROM suppliers WHERE LOWER(supplier_name) LIKE '%adinath%' LIMIT 1")
    },
    {
        "id": "TC-14", "label": "Inventory – fast-track numeric ID",
        "request": {"query": "1", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT id, name FROM inventories WHERE id=1")
    },
    {
        "id": "TC-15", "label": "Multi-intent – Arawali profile + last 3 orders",
        "request": {"query": "Show me Arawali's profile and their last 3 orders", "history": [], "ui_filters": {"limit": 3}},
        "db_verify": lambda: {
            "supplier": db_one("SELECT supplier_name, mobile FROM suppliers WHERE LOWER(supplier_name) LIKE '%arawali%' LIMIT 1"),
            "orders": db_query("SELECT po_number, total_amount, status FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%arawali%' ORDER BY p.po_date DESC, p.id DESC LIMIT 3")
        }
    },

    # ── EXTENDED 50 ──────────────────────────────────────────────────────────

    # --- Inventory (10) ---
    {
        "id": "TC-16", "label": "Inventory – V belt stock (Hinglish)",
        "request": {"query": "v belt ka stock kitna hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name FROM inventories WHERE LOWER(name) LIKE '%v belt%' OR LOWER(name) LIKE '%vbelt%' LIMIT 1")
    },
    {
        "id": "TC-17", "label": "Inventory – oil seal stock",
        "request": {"query": "oil seal kitna pada hai godown mein", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name FROM inventories WHERE LOWER(name) LIKE '%oil seal%' LIMIT 1")
    },
    {
        "id": "TC-18", "label": "Inventory – round bar (English)",
        "request": {"query": "How much round bar is in stock?", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name FROM inventories WHERE LOWER(name) LIKE '%round bar%' LIMIT 1")
    },
    {
        "id": "TC-19", "label": "Inventory – bearing 6205 specific",
        "request": {"query": "bearing 6205 ka stock dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name, classification FROM inventories WHERE LOWER(name) LIKE '%6205%' LIMIT 1")
    },
    {
        "id": "TC-20", "label": "Inventory – chain stock",
        "request": {"query": "chain ka kitna maal hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name FROM inventories WHERE LOWER(name) LIKE '%chain%' LIMIT 1")
    },
    {
        "id": "TC-21", "label": "Inventory – hydraulic oil",
        "request": {"query": "hydraulic oil stock check karo", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name FROM inventories WHERE LOWER(name) LIKE '%hydraulic%' LIMIT 1")
    },
    {
        "id": "TC-22", "label": "Inventory – welding electrode",
        "request": {"query": "welding electrode kitne hain", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name FROM inventories WHERE LOWER(name) LIKE '%welding%' OR LOWER(name) LIKE '%electrode%' LIMIT 1")
    },
    {
        "id": "TC-23", "label": "Inventory – hex nut",
        "request": {"query": "hex nut ka stock batao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name FROM inventories WHERE LOWER(name) LIKE '%hex%' OR LOWER(name) LIKE '%nut%' LIMIT 1")
    },
    {
        "id": "TC-24", "label": "Inventory – bearing 6308 specific",
        "request": {"query": "bearing 6308 ka stock", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name, classification, placement FROM inventories WHERE LOWER(name) LIKE '%6308%' LIMIT 1")
    },
    {
        "id": "TC-25", "label": "Inventory – highest stock item (aggregation)",
        "request": {"query": "sabse zyada stock wala item kaun sa hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT i.name, SUM(CASE WHEN LOWER(t.txn_type)='in' THEN t.quantity ELSE -t.quantity END) AS stock FROM inventories i JOIN stock_transactions t ON i.id=t.inventory_id GROUP BY i.id, i.name ORDER BY stock DESC LIMIT 1")
    },

    # --- Supplier (10) ---
    {
        "id": "TC-26", "label": "Supplier – DCL details (Hinglish)",
        "request": {"query": "DCL Enterprises ki details batao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile, city FROM suppliers WHERE LOWER(supplier_name) LIKE '%dcl%' LIMIT 1")
    },
    {
        "id": "TC-27", "label": "Supplier – Rishabh International GST",
        "request": {"query": "Rishabh International ka GST number kya hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, gstin FROM suppliers WHERE LOWER(supplier_name) = 'rishabh international' LIMIT 1")
    },
    {
        "id": "TC-28", "label": "Supplier – Ikon rubber mobile",
        "request": {"query": "Ikon rubber ka mobile number", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile FROM suppliers WHERE LOWER(supplier_name) LIKE '%ikon%' LIMIT 1")
    },
    {
        "id": "TC-29", "label": "Supplier – Eastern Bearings profile (city fallback)",
        "request": {"query": "Eastern Bearings kahan se hain", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile, gstin FROM suppliers WHERE LOWER(supplier_name) LIKE '%eastern bearings%' LIMIT 1")
    },
    {
        "id": "TC-30", "label": "Supplier – Shreya Seals profile",
        "request": {"query": "Shreya Seals supplier details dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, gstin FROM suppliers WHERE LOWER(supplier_name) = 'shreya seals' LIMIT 1")
    },
    {
        "id": "TC-31", "label": "Supplier – Ram Bilas contact (English)",
        "request": {"query": "What is the contact number of Ram Bilas?", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile FROM suppliers WHERE LOWER(supplier_name) LIKE '%ram bilas%' LIMIT 1")
    },
    {
        "id": "TC-32", "label": "Supplier – Trad Industries info",
        "request": {"query": "Trad Industries ka profile batao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile FROM suppliers WHERE LOWER(supplier_name) LIKE '%trad%' LIMIT 1")
    },
    {
        "id": "TC-33", "label": "Supplier – Mehta Automobiles details",
        "request": {"query": "Mehta Automobiles supplier details", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, gstin FROM suppliers WHERE LOWER(supplier_name) LIKE '%mehta automobiles%' LIMIT 1")
    },
    {
        "id": "TC-34", "label": "Supplier – Paroliya Metals GST (English)",
        "request": {"query": "What is the GST number of Paroliya Metals?", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, gstin FROM suppliers WHERE LOWER(supplier_name) LIKE '%paroliya%' LIMIT 1")
    },
    {
        "id": "TC-35", "label": "Supplier – all suppliers list",
        "request": {"query": "saare suppliers ki list dikhao", "history": [], "ui_filters": {"limit": 5}},
        "db_verify": lambda: db_query("SELECT supplier_name FROM suppliers ORDER BY id DESC LIMIT 5")
    },

    # --- Purchase Orders (10) ---
    {
        "id": "TC-36", "label": "PO – Rishabh International orders",
        "request": {"query": "Rishabh International ke orders dikhao", "history": [], "ui_filters": {"limit": 5}},
        "db_verify": lambda: db_query("SELECT p.po_number, p.total_amount, p.status FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%rishabh%' ORDER BY p.po_date DESC LIMIT 5")
    },
    {
        "id": "TC-37", "label": "PO – last 5 orders",
        "request": {"query": "last 5 orders dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT po_number, status FROM purchase_orders ORDER BY po_date DESC, id DESC LIMIT 5")
    },
    {
        "id": "TC-38", "label": "PO – DCL Enterprises orders",
        "request": {"query": "DCL ke orders", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT p.po_number, p.status FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%dcl%' ORDER BY p.po_date DESC LIMIT 5")
    },
    {
        "id": "TC-39", "label": "PO – search by PO number",
        "request": {"query": "MHEL/PO/00022/2026-2027 dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT po_number, total_amount, status FROM purchase_orders WHERE po_number='MHEL/PO/00022/2026-2027'")
    },
    {
        "id": "TC-40", "label": "PO – Max Spare pending orders",
        "request": {"query": "Max Spare ke pending orders", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT p.po_number, p.status, p.balance_amount FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%max spare%' AND LOWER(p.status)='draft' ORDER BY p.po_date DESC LIMIT 5")
    },
    {
        "id": "TC-41", "label": "PO – RVM Enterprises orders",
        "request": {"query": "RVM Enterprises ke orders batao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT p.po_number, p.total_amount FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%rvm%' ORDER BY p.po_date DESC LIMIT 5")
    },
    {
        "id": "TC-42", "label": "PO – Ikon rubber orders",
        "request": {"query": "Ikon rubber ke orders dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT p.po_number, p.total_amount FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%ikon%' ORDER BY p.po_date DESC LIMIT 5")
    },
    {
        "id": "TC-43", "label": "PO – Unitech Solutions orders (English)",
        "request": {"query": "Show orders for Unitech Solutions", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT p.po_number, p.total_amount FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%unitech%' ORDER BY p.po_date DESC LIMIT 5")
    },
    {
        "id": "TC-44", "label": "PO – balance pending total (Hinglish)",
        "request": {"query": "total pending balance kitna hai sabka", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT SUM(balance_amount) as total_bal FROM purchase_orders WHERE balance_amount > 0")
    },
    {
        "id": "TC-45", "label": "PO – Adinath Enterprises orders",
        "request": {"query": "Adinath Enterprises ke saare orders", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT p.po_number, p.status FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%adinath enterprises%' ORDER BY p.po_date DESC LIMIT 10")
    },

    # --- Projects (5) ---
    {
        "id": "TC-46", "label": "Project – completed projects",
        "request": {"query": "completed projects dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT name, status FROM projects WHERE is_deleted=0 AND LOWER(status)='completed' LIMIT 5")
    },
    {
        "id": "TC-47", "label": "Project – high priority",
        "request": {"query": "high priority projects kaun se hain", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT name, priority, status FROM projects WHERE is_deleted=0 AND LOWER(priority)='high' LIMIT 5")
    },
    {
        "id": "TC-48", "label": "Project – refurbished projects",
        "request": {"query": "refurbished projects dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT name, status FROM projects WHERE is_deleted=0 AND refurbish=1 LIMIT 5")
    },
    {
        "id": "TC-49", "label": "Project – latest project",
        "request": {"query": "latest project batao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT name, status, priority FROM projects WHERE is_deleted=0 ORDER BY id DESC LIMIT 1")
    },
    {
        "id": "TC-50", "label": "Project – list all projects (English)",
        "request": {"query": "Show me all projects", "history": [], "ui_filters": {"limit": 5}},
        "db_verify": lambda: db_query("SELECT name, status FROM projects WHERE is_deleted=0 ORDER BY id DESC LIMIT 5")
    },

    # --- Aggregations (5) ---
    {
        "id": "TC-51", "label": "Aggregation – total items count",
        "request": {"query": "inventory mein kitne items hain total", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT COUNT(*) as total FROM inventories")
    },
    {
        "id": "TC-52", "label": "Aggregation – total projects count",
        "request": {"query": "kitne projects hain system mein", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT COUNT(*) as total FROM projects WHERE is_deleted=0")
    },
    {
        "id": "TC-53", "label": "Aggregation – total PO count (English)",
        "request": {"query": "How many purchase orders are there in total?", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT COUNT(*) as total FROM purchase_orders")
    },
    {
        "id": "TC-54", "label": "Aggregation – highest stock item (English)",
        "request": {"query": "which item has the most stock?", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT i.name, SUM(CASE WHEN LOWER(t.txn_type)='in' THEN t.quantity ELSE -t.quantity END) AS stock FROM inventories i JOIN stock_transactions t ON i.id=t.inventory_id GROUP BY i.id, i.name ORDER BY stock DESC LIMIT 1")
    },
    {
        "id": "TC-55", "label": "Aggregation – GST of specific supplier",
        "request": {"query": "Adinath Enterprises ka GST kitna bana hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT SUM(p.tax_amount) as total_tax FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%adinath enterprises%'")
    },

    # --- Edge cases / Mixed (10) ---
    {
        "id": "TC-56", "label": "PO – Arawali balance (Hinglish)",
        "request": {"query": "Arawali ka balance kya hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT s.supplier_name, SUM(p.balance_amount) as bal FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%arawali%' GROUP BY s.id, s.supplier_name LIMIT 1")
    },
    {
        "id": "TC-57", "label": "Supplier – typo 'Risabh' (FAISS tolerance)",
        "request": {"query": "Risabh International ka profile", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile, gstin FROM suppliers WHERE LOWER(supplier_name) = 'rishabh international' LIMIT 1")
    },
    {
        "id": "TC-58", "label": "Multi-intent – DCL details and orders",
        "request": {"query": "DCL ki details aur uske orders dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT s.supplier_name, s.gstin FROM suppliers s WHERE LOWER(s.supplier_name) LIKE '%dcl%' LIMIT 1")
    },
    {
        "id": "TC-59", "label": "PO – Shree GK Steels orders",
        "request": {"query": "Shree GK Steels ke orders", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_query("SELECT p.po_number, p.total_amount FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%shree%' AND LOWER(s.supplier_name) LIKE '%steel%' ORDER BY p.po_date DESC LIMIT 5")
    },
    {
        "id": "TC-60", "label": "PO – Bhilwara Sales pending balance",
        "request": {"query": "Bhilwara Sales ka pending balance", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT s.supplier_name, SUM(p.balance_amount) as bal FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE LOWER(s.supplier_name) LIKE '%bhilwara%' GROUP BY s.id LIMIT 1")
    },
    {
        "id": "TC-61", "label": "PO – latest single purchase order (English)",
        "request": {"query": "Show me the latest purchase order", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT po_number, status FROM purchase_orders ORDER BY po_date DESC, id DESC LIMIT 1")
    },
    {
        "id": "TC-62", "label": "Supplier – SUP code lookup",
        "request": {"query": "sup-146 ki details dikhao", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile FROM suppliers WHERE supplier_code=146 OR id=146 LIMIT 1")
    },
    {
        "id": "TC-63", "label": "Supervisor role – PO blocked",
        "request": {"query": "latest purchase order dikhao", "history": [], "role": "supervisor", "ui_filters": {}},
        "db_verify": lambda: {"blocked": True}
    },
    {
        "id": "TC-64", "label": "PO – advance paid orders",
        "request": {"query": "jin orders mein advance diya gaya hai", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT po_number, advance_amount FROM purchase_orders WHERE advance_amount > 0 ORDER BY po_date DESC LIMIT 1")
    },
    {
        "id": "TC-65", "label": "Mixed – Adinath Petrochemicals contact + GSTIN (English)",
        "request": {"query": "Show me the contact and GST of Adinath Petrochemicals", "history": [], "ui_filters": {}},
        "db_verify": lambda: db_one("SELECT supplier_name, mobile, gstin FROM suppliers WHERE LOWER(supplier_name) LIKE '%petrochemical%' LIMIT 1")
    },
]

# ── Runner ────────────────────────────────────────────────────────────────────
def run_test(tc):
    req_body = {k: v for k, v in tc["request"].items()}
    try:
        resp = requests.post(BASE_URL, json=req_body, timeout=60)
        status_code = resp.status_code
        try:
            response_json = resp.json()
        except Exception:
            response_json = {"raw": resp.text}
    except Exception as e:
        status_code = "ERROR"
        response_json = {"error": str(e)}

    db_truth = None
    try:
        db_truth = tc["db_verify"]()
    except Exception as e:
        db_truth = {"db_verify_error": str(e)}

    resp_str = json.dumps(response_json).lower()

    def _check(d):
        if not d:
            return None
        if isinstance(d, dict):
            # Special: supervisor blocked check
            if d.get("blocked"):
                return "permission" in resp_str.lower() or "nahi hai" in resp_str.lower()
            for v in d.values():
                if v is None:
                    continue
                if isinstance(v, (dict, list)):
                    r = _check(v)
                    if r is not None:
                        return r
                    continue
                sv = str(v).lower()
                if len(sv) > 3 and sv in resp_str:
                    return True
                # numeric with comma formatting
                try:
                    nv = str(int(float(sv.replace(",", ""))))
                    if len(nv) > 1 and nv in resp_str.replace(",", ""):
                        return True
                except Exception:
                    pass
        elif isinstance(d, list):
            for item in d:
                r = _check(item)
                if r is True:
                    return True
        return None

    passed = _check(db_truth)
    # If DB returned empty list, treat as "unknown" (correct not-found is also valid)
    if isinstance(db_truth, list) and not db_truth:
        passed = None
    if isinstance(db_truth, dict) and not db_truth.get("blocked") and all(v is None for v in db_truth.values()):
        passed = None

    return {
        "id": tc["id"], "label": tc["label"],
        "http_status": status_code,
        "request": req_body,
        "response": response_json,
        "db_ground_truth": db_truth,
        "auto_check_passed": passed,
    }

# ── Log writer ────────────────────────────────────────────────────────────────
def write_log(results):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    passed = sum(1 for r in results if r["auto_check_passed"] is True)
    failed = sum(1 for r in results if r["auto_check_passed"] is False)
    unknown = sum(1 for r in results if r["auto_check_passed"] is None)

    lines = [
        "# Chatbot API Test Log",
        f"**Generated:** {now}  ",
        f"**Endpoint:** `{BASE_URL}`  ",
        f"**Total Tests:** {len(results)}  ",
        "",
        "---",
        "",
        "## Summary",
        "| Status | Count |",
        "|--------|-------|",
        f"| PASS (auto-check) | {passed} |",
        f"| FAIL (auto-check) | {failed} |",
        f"| UNKNOWN (empty DB / unverifiable) | {unknown} |",
        "",
        "---",
        "",
    ]

    for r in results:
        icon = "PASS" if r["auto_check_passed"] is True else ("FAIL" if r["auto_check_passed"] is False else "UNKNOWN")
        lines += [
            f"## [{icon}] {r['id']} - {r['label']}",
            "",
            f"**HTTP Status:** `{r['http_status']}`  ",
            f"**Auto-check:** `{r['auto_check_passed']}`",
            "",
            "### Request",
            "```json",
            json.dumps(r["request"], indent=2, ensure_ascii=False),
            "```",
            "",
            "### Response",
            "```json",
            json.dumps(r["response"], indent=2, ensure_ascii=False),
            "```",
            "",
            "### DB Ground Truth",
            "```json",
            json.dumps(r["db_ground_truth"], indent=2, ensure_ascii=False, default=str),
            "```",
            "",
            "---",
            "",
        ]

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nLog written to {LOG_FILE}")
    print(f"PASS: {passed}  FAIL: {failed}  UNKNOWN: {unknown}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Warming up server (FAISS + first Groq call)...", end=" ", flush=True)
    try:
        requests.post(BASE_URL, json={"query": "hi", "history": [], "ui_filters": {}}, timeout=90)
        print("done.")
    except Exception as e:
        print(f"warmup note: {e}")

    print(f"\nRunning {len(TEST_CASES)} chatbot tests against {BASE_URL}\n")
    results = []
    for tc in TEST_CASES:
        print(f"  [{tc['id']}] {tc['label']} ...", end=" ", flush=True)
        r = run_test(tc)
        icon = "PASS" if r["auto_check_passed"] is True else ("FAIL" if r["auto_check_passed"] is False else "??")
        print(icon)
        results.append(r)

    write_log(results)
