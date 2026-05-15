# ═══════════════════════════════════════════════════════════════════════════════
# MEWAR ERP — FINAL PRODUCTION CHATBOT
#
# Two-layer architecture:
#   Layer 1 — V2 Intent Engine  : structured queries → rich card UI
#             (SupplierCard, POCard, InventoryCard, RS Form, Project cards)
#   Layer 2 — NL2SQL AI Engine  : anything V2 couldn't answer → AI writes SQL
#             (SambaNova DeepSeek V3.1 → Gemini 2.5 Flash → Groq fallback)
#
# Route prefix: /v2-chatbot  (Chat.jsx connects here)
# ═══════════════════════════════════════════════════════════════════════════════

import re
import time
import json
import os
import difflib
import datetime

from fastapi import APIRouter, Depends, Query as _Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db, SessionLocal
from app.schemas.chat import ChatRequest
from app.services.ollama_engine import ask_ollama
from app.services.nl2sql_engine import generate_sql, format_answer
from apscheduler.schedulers.background import BackgroundScheduler

router = APIRouter(prefix="/v2-chatbot", tags=["Chatbot Final"])


# ── Role permissions ──────────────────────────────────────────────────────────
ROLE_PERMISSIONS = {
    "supervisor":     ["inventory", "project", "general_chat"],
    "sales":          ["inventory", "general_chat"],
    "purchase":       ["inventory", "supplier", "po", "general_chat"],
    "purchase admin": ["inventory", "supplier", "po", "financials", "general_chat"],
    "store admin":    ["inventory", "po", "project", "general_chat"],
    "store department": ["inventory", "general_chat"],
    "hod":            ["inventory", "project", "supplier", "po", "financials", "general_chat"],
    "hr":             ["general_chat"],
}

# ── Off-topic guard ───────────────────────────────────────────────────────────
_ERP_KEYWORDS = {
    "supplier", "vendor", "party", "sup",
    "po", "order", "purchase", "transit", "delivery", "grn", "dispatch",
    "stock", "maal", "item", "inventory", "qty", "quantity",
    "project", "site", "crusher",
    "balance", "payment", "invoice", "gst", "tax", "cgst", "sgst",
    "rokra", "paisa", "kharcha", "hisab",
    "mewar", "erp", "sale", "sales", "report", "employee", "account",
    # Hindi query verbs & RS form keywords
    "slip", "request", "banao", "batao", "dikhao", "milao", "details",
    "kitna", "kitne", "kahan", "kaisa", "kab", "lagao", "nikalo",
    # general — if user is asking a "how many / total / list" ERP question
    "total", "list", "count", "kitni", "sabhi", "saare",
    # query action words — any sentence starting with these is likely ERP
    "show", "find", "get", "check", "all", "mere", "mera",
    # ── Item nouns (factory/inventory items) ──
    "bearing", "bearings", "bolt", "bolts", "plate", "plates", "motor", "motors",
    "screw", "screws", "nut", "nuts", "washer", "washers", "pipe", "pipes",
    "valve", "valves", "pump", "pumps", "tool", "tools", "rod", "rods",
    "belt", "belts", "gear", "gears", "channel", "channels", "sleeve", "sleeves",
    "spring", "springs", "shaft", "shafts", "ring", "rings", "seal", "seals",
    "wire", "cable", "sheet", "angle", "beam", "flange", "coupling", "machine",
    "machines", "feeder", "conveyor", "hopper", "crusher",
    # ── English question/quantity words ──
    "have", "much", "many", "how", "when", "where", "which", "what", "who",
    "deadline", "due", "date", "available", "running", "pending", "completed",
    "approved", "rejected", "issued", "ordered", "draft",
    # ── Hinglish helpers ──
    "banata", "bana", "bani", "kya", "konsa", "kaunsa", "kaunsi", "konsi",
    "wala", "wali", "wale", "hain", "hai", "ho",
}

_POOR_SIGNALS = [
    "theek se samajh nahi", "maaf kijiye", "clear batao", "clearly batao",
    "kripya", "naam batao", "couldn't understand", "i'm sorry",
    "it seems you", "please provide", "thoda clear",
    # item / supplier not found → try NL2SQL
    "nahi mila", "nahi mili", "nahi mile", "spelling check karoge",
    "koi supplier nahi", "koi project nahi",
    # Ollama reasoning fillers with no actual data — let NL2SQL answer instead
    "ek sec", "check karta hoon", "dekh raha hoon", "dhundh raha hoon",
    "data entry nahi hui",
]


_CLEARLY_OFFTOPIC = {
    "poem", "poetry", "joke", "weather", "recipe", "cook", "song", "lyrics",
    "translate", "movie", "cricket", "football", "game", "news", "capital of",
    "who is the president", "write a story", "tell me a story",
}

def _is_off_topic(query: str) -> bool:
    q = query.lower()
    # Short queries (≤3 words) are almost always item/name lookups — always allow
    if len(q.split()) <= 3:
        return False
    # Block only if the query matches a clearly non-ERP pattern
    if any(kw in q for kw in _CLEARLY_OFFTOPIC):
        return True
    # Block longer queries that have zero ERP keywords
    return not any(kw in q for kw in _ERP_KEYWORDS)


def _is_poor_result(response: dict) -> bool:
    results = response.get("results", [])
    data_types = {
        "result", "po", "dropdown", "project",
        "po_list", "po_summary", "project_list",
        "supplier_list", "supplier_items", "supplier_payments",
    }
    if any(r.get("type") in data_types for r in results):
        return False
    chat_text = " ".join(
        r.get("message", "") for r in results if r.get("type") == "chat"
    ).lower()
    return any(sig in chat_text for sig in _POOR_SIGNALS)


# ── FAISS disabled stubs ──────────────────────────────────────────────────────
def load_faiss_once(db: Session):
    pass


def smart_match(query_text, category="inventory"):
    return query_text


# ── Slang translation ─────────────────────────────────────────────────────────
def translate_slang(text: str):
    slang_map = {
        r'\bmaal\b':   'inventory',
        r'\bstock\b':  'inventory',
        r'\bkharcha\b': 'budget',
        r'\brokra\b':  'balance_amount',
        r'\bpaisa\b':  'amount',
        r'\bkitna\b':  'total_stock',
        r'\bitem\b':   'inventory',
    }
    for slang, official in slang_map.items():
        text = re.sub(slang, official, text, flags=re.IGNORECASE)
    return text


# ── Intent detection ──────────────────────────────────────────────────────────
def advanced_intent_detector(query: str):
    q = query.lower()
    score = {"po_search": 0, "supplier_search": 0, "project_search": 0, "search": 0}

    po_words  = ["po", "order", "orders", "purchase", "transit", "raste", "pending", "dispatch", "delivery"]
    sup_words = ["supplier", "vendor", "party", "contact", "mobile", "number", "account", "details", "profile"]
    proj_words = ["project", "site", "crusher", "running", "urgent", "completed", "refurbish"]
    inv_words  = ["stock", "maal", "item", "inventory", "quantity", "kitna", "qty", "available"]
    for w in po_words:   score["po_search"]      += 2 if w in q else 0
    for w in sup_words:  score["supplier_search"] += 2 if w in q else 0
    for w in proj_words: score["project_search"]  += 2 if w in q else 0
    for w in inv_words:  score["search"]          += 2 if w in q else 0

    if any(w in q for w in ["stock", "maal", "kitna"]) and any(w in q for w in ["supplier", "party"]):
        score["search"] += 3

    best = max(score, key=score.get)
    return best if score[best] > 0 else "search"


def clean_target_ultimate(target: str):
    noise = ["dikhao", "batao", "check", "ka", "ki", "ke", "mein", "inventory",
             "stock", "orders", "po", "list", "mujhe", "hai", "bhai", "details", "contact"]
    words   = target.split()
    cleaned = [w for w in words if w.lower() not in noise]
    return " ".join(cleaned) if cleaned else target


# ── Logger ────────────────────────────────────────────────────────────────────
def log_query_pro(user_role, query, intents, final_results, process_time):
    bot_reply = "No Response"
    if isinstance(final_results, dict) and "results" in final_results:
        bot_reply = final_results["results"]

    is_fail = any(w in str(bot_reply).lower()
                  for w in ["nahi mila", "error", "samajh nahi", "maaf kijiye", "permission nahi"])

    log_entry = {
        "date_time":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "role":         user_role,
        "user_query":   query,
        "intent":       str(intents),
        "bot_response": bot_reply,
        "time_taken_sec": round(process_time, 2),
        "status":       "Fail" if is_fail else "Success",
    }
    try:
        with open("chat_history.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + "\n")
    except Exception as e:
        print(f"Log error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN UNIFIED ENDPOINT
# ══════════════════════════════════════════════════════════════════════════════
@router.post("")
def chatbot(request: ChatRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    raw_q  = request.query.strip()
    low_q  = raw_q.lower()

    # ── Off-topic guard ───────────────────────────────────────────────────────
    # Skip guard if user has prior conversation history (follow-up questions
    # like "why are they best" don't contain ERP keywords but are valid follow-ups)
    _has_history = bool(request.history)
    if _is_off_topic(raw_q) and not _has_history:
        return {"results": [{"type": "chat", "message": (
            "Bhai, main sirf Mewar ERP ke sawaalon mein help kar sakta hoon — "
            "Suppliers, Purchase Orders, Inventory, aur Projects. "
            "In topics par kuch poochho! 😊"
        )}]}

    # ── Role ──────────────────────────────────────────────────────────────────
    user_role = (getattr(request, "role", "guest") or "guest").lower().strip()

    # ── Fast-track: bare numeric ID → inventory lookup ────────────────────────
    if low_q.isdigit() and len(low_q) < 8:
        allowed = ROLE_PERMISSIONS.get(user_role, [])
        if user_role in ("superadmin", "super admin") or "inventory" in allowed:
            try:
                inv = db.execute(
                    text("SELECT id, name, classification, placement FROM inventories WHERE id = :id"),
                    {"id": int(low_q)},
                ).fetchone()
                if inv:
                    stock = float(db.execute(
                        text("SELECT SUM(CASE WHEN LOWER(txn_type)='in' THEN quantity ELSE -quantity END) "
                             "FROM stock_transactions WHERE inventory_id = :id"),
                        {"id": inv.id},
                    ).scalar() or 0)
                    cls = str(inv.classification or "").lower()
                    m = stock if "machining" in cls else 0
                    sf = stock if "semi" in cls else 0
                    f  = 0 if ("machining" in cls or "semi" in cls) else stock
                    return {"results": [{"type": "result",
                        "inventory": {"id": inv.id, "name": inv.name,
                                      "category": cls.upper(), "placement": inv.placement or "N/A"},
                        "total_stock": stock, "finish_stock": f,
                        "semi_finish_stock": sf, "machining_stock": m}]}
            except Exception:
                pass
        else:
            return {"results": [{"type": "chat", "message":
                f"Aapka role '{user_role.title()}' hai. Aapko Item Codes se search karne ki permission nahi hai."}]}

    # ── All queries go directly to NL2SQL ────────────────────────────────────
    intents = ["nl2sql"]
    nl2_resp = _nl2sql_response(raw_q, db, history=request.history or [])
    if nl2_resp:
        process_time = time.time() - start_time
        try:
            log_query_pro(user_role, raw_q, intents, nl2_resp, process_time)
        except Exception as e:
            print(f"Logger error: {e}")
        return nl2_resp

    return {"results": [{"type": "chat", "message": (
        "Maaf kijiye, main theek se samajh nahi paaya. "
        "Kripya dobara poochho."
    )}]}


_WRITE_PATTERN = re.compile(
    r'^\s*(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE|MERGE|CALL|EXEC)\b',
    re.IGNORECASE,
)

# ── NL2SQL helper ─────────────────────────────────────────────────────────────
def _nl2sql_response(raw_q: str, db, history: list = None) -> dict | None:
    """Run NL2SQL pipeline. Returns formatted response or None on failure."""
    history = history or []
    try:
        sql = generate_sql(raw_q, history=history)
        if _WRITE_PATTERN.match(sql):
            print(f"[NL2SQL] BLOCKED write SQL: {sql[:120]}")
            return {"results": [{"type": "chat", "message":
                "Yeh action allowed nahi hai. Main sirf data read kar sakta hoon — koi bhi changes karne ki permission nahi hai."}]}
        try:
            result  = db.execute(text(sql))
        except Exception as exec_err:
            print(f"[NL2SQL] failed: {exec_err}\n[SQL: {sql}]")
            sql = generate_sql(raw_q, previous_sql=sql, sql_error=str(exec_err), history=history)
            if _WRITE_PATTERN.match(sql):
                print(f"[NL2SQL] BLOCKED write SQL (retry): {sql[:120]}")
                return {"results": [{"type": "chat", "message":
                    "Yeh action allowed nahi hai. Main sirf data read kar sakta hoon — koi bhi changes karne ki permission nahi hai."}]}
            print(f"[NL2SQL] retry SQL: {sql[:120]}")
            result  = db.execute(text(sql))
        columns      = list(result.keys())
        rows         = [list(row) for row in result.fetchall()]
        answer       = format_answer(raw_q, rows, columns, history=history)
        parts        = [{"type": "chat", "message": answer}]
        if rows:
            rows_as_dicts = [dict(zip(columns, row)) for row in rows]
            parts.append({"type": "nl2sql_table", "rows": rows_as_dicts, "columns": columns})
        return {"results": parts}
    except Exception as e:
        print(f"[NL2SQL] failed: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# AUXILIARY ENDPOINTS — Supplier / PO / Inventory card buttons
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/select")
def handle_select(payload: dict, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    name = payload.get("selected", "")
    s = db.execute(_t("SELECT * FROM suppliers WHERE supplier_name=:n LIMIT 1"), {"n": name}).fetchone()
    if not s:
        return {"results": [{"type": "chat", "message": f"'{name}' nahi mila."}]}
    inv_items = db.execute(_t(
        "SELECT i.name, SUM(CASE WHEN LOWER(t.txn_type)='in' THEN t.quantity ELSE -t.quantity END) as stock "
        "FROM inventories i JOIN stock_transactions t ON i.id=t.inventory_id "
        "WHERE t.supplier_id=:sid GROUP BY i.id,i.name HAVING stock!=0"
    ), {"sid": s.id}).fetchall()
    return {"results": [
        {"type": "chat", "message": f"ye raha **{s.supplier_name}** ka profile:"},
        {"type": "result", "supplier": {
            "id": int(s.id), "name": str(s.supplier_name or ""),
            "code":   str(getattr(s, "supplier_code", "") or ""),
            "mobile": str(getattr(s, "mobile", "")        or ""),
            "city":   str(getattr(s, "city", "")          or ""),
            "email":  str(getattr(s, "email", "")         or ""),
            "gstin":  str(getattr(s, "gstin", "")         or ""),
        }, "items": [{"name": r.name, "stock": float(r.stock)} for r in inv_items]},
    ]}


@router.get("/inventory/{inventory_id}/details")
def inventory_details(inventory_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    inv = db.execute(_t("SELECT * FROM inventories WHERE id=:id LIMIT 1"), {"id": inventory_id}).fetchone()
    if not inv:
        return {"results": [{"type": "chat", "message": "Item nahi mila."}]}
    stock = float(db.execute(_t(
        "SELECT COALESCE(SUM(CASE WHEN LOWER(txn_type)='in' THEN quantity ELSE -quantity END),0) "
        "FROM stock_transactions WHERE inventory_id=:id"
    ), {"id": inventory_id}).scalar() or 0)
    cls       = (getattr(inv, "classification", "") or "").lower()
    finish    = 0 if ("machining" in cls or "semi" in cls) else stock
    semi      = stock if "semi"      in cls else 0
    machining = stock if "machining" in cls else 0
    return {"results": [
        {"type": "chat", "message": f"ye raha **{inv.name}** ka stock:"},
        {"type": "result",
         "inventory": {"id": int(inv.id), "name": str(inv.name or ""),
                       "category": cls.upper(), "placement": str(getattr(inv, "placement", "") or ""),
                       "unit": str(getattr(inv, "unit", "") or ""), "model": str(getattr(inv, "model", "") or ""),
                       "grade": str(getattr(inv, "grade", "") or "")},
         "total_stock": stock, "finish_stock": finish,
         "semi_finish_stock": semi, "machining_stock": machining},
    ]}


@router.get("/inventory/{inventory_id}/po-history")
def inventory_po_history(inventory_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    rows = db.execute(_t("""
        SELECT po.po_number, po.po_date, s.supplier_name,
               poi.ordered_qty, poi.unit_price, po.status
        FROM purchase_order_items poi
        JOIN purchase_orders po ON poi.purchase_order_id=po.id
        JOIN suppliers s ON po.supplier_id=s.id
        WHERE poi.inventory_id=:iid ORDER BY po.po_date DESC LIMIT 20
    """), {"iid": inventory_id}).fetchall()
    return {"rows": [{"po": str(r.po_number), "date": str(r.po_date)[:10],
                      "supplier": str(r.supplier_name), "qty": float(r.ordered_qty or 0),
                      "price": float(r.unit_price or 0), "status": str(r.status)} for r in rows]}


@router.get("/inventory/{inventory_id}/suppliers")
def inventory_suppliers(inventory_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    rows = db.execute(_t("""
        SELECT DISTINCT s.id, s.supplier_name, s.mobile, s.city
        FROM stock_transactions st JOIN suppliers s ON st.supplier_id=s.id
        WHERE st.inventory_id=:iid
    """), {"iid": inventory_id}).fetchall()
    return {"rows": [{"id": int(r.id), "name": str(r.supplier_name or ""),
                      "mobile": str(r.mobile or ""), "city": str(r.city or "")} for r in rows]}


@router.get("/supplier/{supplier_id}/card")
def supplier_card(supplier_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    s = db.execute(_t("SELECT * FROM suppliers WHERE id=:id LIMIT 1"), {"id": supplier_id}).fetchone()
    if not s:
        return {"results": [{"type": "chat", "message": "Supplier nahi mila."}]}
    inv_items = db.execute(_t(
        "SELECT i.name, SUM(CASE WHEN LOWER(t.txn_type)='in' THEN t.quantity ELSE -t.quantity END) AS stock "
        "FROM inventories i JOIN stock_transactions t ON i.id=t.inventory_id "
        "WHERE t.supplier_id=:sid GROUP BY i.id,i.name HAVING stock!=0"
    ), {"sid": supplier_id}).fetchall()
    return {"results": [
        {"type": "chat", "message": f"ye raha **{s.supplier_name}** ka profile:"},
        {"type": "result", "supplier": {
            "id": int(s.id), "name": str(s.supplier_name or ""),
            "code":   str(getattr(s, "supplier_code", "") or ""),
            "mobile": str(getattr(s, "mobile", "")        or ""),
            "city":   str(getattr(s, "city", "")          or ""),
            "email":  str(getattr(s, "email", "")         or ""),
            "gstin":  str(getattr(s, "gstin", "")         or ""),
        }, "items": [{"name": r.name, "stock": float(r.stock)} for r in inv_items]},
    ]}


@router.get("/supplier/{supplier_id}/pos")
def supplier_pos(supplier_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    rows = db.execute(_t(
        "SELECT p.id, p.po_number, p.po_date, p.total_amount, p.balance_amount, p.status "
        "FROM purchase_orders p WHERE p.supplier_id=:sid ORDER BY p.po_date DESC LIMIT 50"
    ), {"sid": supplier_id}).fetchall()
    return {"rows": [{"type": "po", "id": int(r.id), "po_no": str(r.po_number),
                      "date": str(r.po_date), "total": float(r.total_amount or 0),
                      "balance": float(r.balance_amount or 0), "status": str(r.status)} for r in rows]}


@router.get("/supplier/{supplier_id}/balance")
def supplier_balance(supplier_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    r = db.execute(_t(
        "SELECT COALESCE(SUM(balance_amount),0) as bal, COUNT(id) as cnt "
        "FROM purchase_orders WHERE supplier_id=:sid AND LOWER(status)!='completed'"
    ), {"sid": supplier_id}).fetchone()
    s = db.execute(_t("SELECT supplier_name FROM suppliers WHERE id=:id"), {"sid": supplier_id}).fetchone()
    name = s.supplier_name if s else "Supplier"
    return {"balance": float(r.bal or 0), "order_count": int(r.cnt or 0),
            "message": f"**{name}** ka total pending balance: **₹{float(r.bal or 0):,.2f}** ({r.cnt} orders)"}


@router.get("/supplier/{supplier_id}/items")
def supplier_items(supplier_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    rows = db.execute(_t("""
        SELECT i.id, i.name,
               SUM(CASE WHEN LOWER(t.txn_type)='in' THEN t.quantity ELSE -t.quantity END) AS stock
        FROM inventories i JOIN stock_transactions t ON i.id=t.inventory_id
        WHERE t.supplier_id=:sid GROUP BY i.id,i.name HAVING stock>0
    """), {"sid": supplier_id}).fetchall()
    return {"rows": [{"id": int(r.id), "name": str(r.name), "stock": float(r.stock)} for r in rows]}


@router.get("/supplier/{supplier_id}/payments")
def supplier_payments(supplier_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    rows = db.execute(_t("""
        SELECT pt.pay_amount, pt.transaction_date, po.po_number
        FROM po_transactions pt JOIN purchase_orders po ON pt.po_id=po.id
        WHERE po.supplier_id=:sid ORDER BY pt.transaction_date DESC LIMIT 30
    """), {"sid": supplier_id}).fetchall()
    total = sum(float(r.pay_amount) for r in rows)
    return {"total_paid": total,
            "rows": [{"amount": float(r.pay_amount), "date": str(r.transaction_date)[:10],
                      "po": str(r.po_number)} for r in rows]}


@router.get("/po/{po_id}/items")
def po_items(po_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    rows = db.execute(_t("""
        SELECT i.name, i.unit, poi.hsn, poi.ordered_qty, poi.received_qty,
               poi.unit_price, poi.discount, poi.tax_percent, poi.tax_amount, poi.line_total
        FROM purchase_order_items poi JOIN inventories i ON poi.inventory_id=i.id
        WHERE poi.purchase_order_id=:pid ORDER BY poi.id
    """), {"pid": po_id}).fetchall()
    return {"rows": [{"name": str(r.name), "unit": str(r.unit or ""), "hsn": str(r.hsn or ""),
                      "ordered": float(r.ordered_qty or 0), "received": float(r.received_qty or 0),
                      "unit_price": float(r.unit_price or 0), "discount": float(r.discount or 0),
                      "tax_percent": float(r.tax_percent or 0), "tax_amount": float(r.tax_amount or 0),
                      "line_total": float(r.line_total or 0)} for r in rows]}


@router.get("/po/{po_id}/payments")
def po_payments(po_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    rows  = db.execute(_t("SELECT pay_amount, transaction_date FROM po_transactions WHERE po_id=:pid ORDER BY transaction_date DESC"), {"pid": po_id}).fetchall()
    total = sum(float(r.pay_amount) for r in rows)
    return {"total_paid": total, "rows": [{"amount": float(r.pay_amount), "date": str(r.transaction_date)[:10]} for r in rows]}


@router.get("/po/{po_id}/status-log")
def po_status_log(po_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    rows = db.execute(_t("SELECT status, changed_at, remarks FROM po_status_logs WHERE purchase_order_id=:pid ORDER BY changed_at DESC"), {"pid": po_id}).fetchall()
    return {"rows": [{"status": str(r.status or ""), "date": str(r.changed_at)[:16], "remarks": str(r.remarks or "")} for r in rows]}


@router.get("/po/{po_id}/supplier")
def po_supplier(po_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    row = db.execute(_t("SELECT s.* FROM purchase_orders p JOIN suppliers s ON p.supplier_id=s.id WHERE p.id=:id LIMIT 1"), {"id": po_id}).fetchone()
    if not row:
        return {"error": "Supplier not found"}
    return {"supplier": {"id": int(row.id), "name": str(row.supplier_name or ""),
                         "code": str(getattr(row,"supplier_code","N/A") or "N/A"),
                         "mobile": str(getattr(row,"mobile","N/A") or "N/A"),
                         "city":   str(getattr(row,"city","N/A")   or "N/A"),
                         "email":  str(getattr(row,"email","N/A")  or "N/A"),
                         "gstin":  str(getattr(row,"gstin","N/A")  or "N/A")}}


@router.get("/po/{po_id}/card")
def po_card(po_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    row = db.execute(_t("SELECT p.*, s.supplier_name FROM purchase_orders p LEFT JOIN suppliers s ON p.supplier_id=s.id WHERE p.id=:id LIMIT 1"), {"id": po_id}).fetchone()
    if not row:
        return {"results": [{"type": "chat", "message": "PO nahi mila."}]}
    return {"results": [
        {"type": "chat", "message": f"ye raha **{row.po_number}** ka detail:"},
        {"type": "po", "id": int(row.id), "po_no": str(row.po_number), "supplier": str(row.supplier_name or ""),
         "date": str(row.po_date), "total": float(row.total_amount or 0),
         "advance": float(row.advance_amount or 0), "balance": float(row.balance_amount or 0),
         "status": str(row.status).capitalize()},
    ]}


# ── Quick search ──────────────────────────────────────────────────────────────

@router.get("/quick-search/supplier")
def quick_search_supplier(q: str = "", limit: int = 60, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    if not q.strip():
        rows = db.execute(_t("SELECT id, supplier_name, city, mobile FROM suppliers ORDER BY id DESC LIMIT :l"), {"l": limit}).fetchall()
    else:
        words = q.strip().lower().split()
        cond  = " AND ".join(f"(LOWER(supplier_name) LIKE :w{i} OR LOWER(COALESCE(city,'')) LIKE :w{i} OR COALESCE(mobile,'') LIKE :w{i})" for i in range(len(words)))
        params = {f"w{i}": f"%{w}%" for i, w in enumerate(words)}
        params["l"] = limit
        rows = db.execute(_t(f"SELECT id, supplier_name, city, mobile FROM suppliers WHERE {cond} ORDER BY supplier_name LIMIT :l"), params).fetchall()
    return {"rows": [{"id": int(r.id), "name": str(r.supplier_name or ""), "city": str(r.city or ""), "mobile": str(r.mobile or "")} for r in rows]}


@router.get("/quick-search/po")
def quick_search_po(q: str = "", limit: int = 60, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    base = "SELECT p.id, p.po_number, p.po_date, p.total_amount, p.status, s.supplier_name FROM purchase_orders p LEFT JOIN suppliers s ON p.supplier_id=s.id "
    if not q.strip():
        rows = db.execute(_t(base + "ORDER BY p.id DESC LIMIT :l"), {"l": limit}).fetchall()
    else:
        words  = q.strip().lower().split()
        cond   = " AND ".join(f"(LOWER(p.po_number) LIKE :w{i} OR LOWER(COALESCE(s.supplier_name,'')) LIKE :w{i} OR LOWER(COALESCE(p.status,'')) LIKE :w{i})" for i in range(len(words)))
        params = {f"w{i}": f"%{w}%" for i, w in enumerate(words)}
        params["l"] = limit
        rows = db.execute(_t(base + f"WHERE {cond} ORDER BY p.po_date DESC LIMIT :l"), params).fetchall()
    return {"rows": [{"id": int(r.id), "po_number": str(r.po_number or ""), "date": str(r.po_date or ""),
                      "total": float(r.total_amount or 0), "status": str(r.status or ""),
                      "supplier": str(r.supplier_name or "")} for r in rows]}


@router.get("/quick-search/inventory")
def quick_search_inventory(q: str = "", limit: int = 60, db: Session = Depends(get_db)):
    from sqlalchemy import text as _t
    base = ("SELECT i.id, i.name, i.unit, COALESCE(SUM(CASE WHEN LOWER(st.txn_type)='in' THEN st.quantity ELSE -st.quantity END),0) AS stock "
            "FROM inventories i LEFT JOIN stock_transactions st ON st.inventory_id=i.id WHERE i.is_deleted=0 ")
    if not q.strip():
        rows = db.execute(_t(base + "GROUP BY i.id,i.name,i.unit ORDER BY i.id DESC LIMIT :l"), {"l": limit}).fetchall()
    else:
        words  = q.strip().lower().split()
        cond   = " AND ".join(f"LOWER(i.name) LIKE :w{i}" for i in range(len(words)))
        params = {f"w{i}": f"%{w}%" for i, w in enumerate(words)}
        params["l"] = limit
        rows = db.execute(_t(base + f"AND {cond} GROUP BY i.id,i.name,i.unit ORDER BY i.name LIMIT :l"), params).fetchall()
    return {"rows": [{"id": int(r.id), "name": str(r.name or ""), "unit": str(r.unit or ""), "stock": float(r.stock or 0)} for r in rows]}


# ── Feedback & Logs ───────────────────────────────────────────────────────────

@router.post("/feedback")
def chatbot_feedback(payload: dict, db: Session = Depends(get_db)):
    try:
        with open("chat_history.json", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "type":       "feedback",
                "request_id": payload.get("request_id"),
                "query":      payload.get("query"),
                "rating":     payload.get("rating"),
                "summary":    payload.get("summary"),
                "timestamp":  datetime.datetime.now().isoformat(),
            }, ensure_ascii=False) + "\n")
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/logs")
def view_logs():
    log_file = "chat_history.json"
    if not os.path.exists(log_file):
        return {"message": "Abhi tak koi chat nahi hui."}
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = [json.loads(line) for line in f if line.strip()]
        return {"total_chats": len(logs), "latest_logs": logs[::-1]}
    except Exception as e:
        return {"error": str(e)}


@router.delete("/logs/clear")
def clear_logs(secret_key: str = "mewar123"):
    if secret_key != "mewar@12345":
        return {"error": "Galat password. Permission nahi hai."}
    try:
        open("chat_history.json", "w", encoding="utf-8").close()
        return {"success": True, "message": "Logs clear ho gaye."}
    except Exception as e:
        return {"error": str(e)}


# ── Morning briefing (called by APScheduler in main.py) ──────────────────────

def generate_morning_briefing():
    db = SessionLocal()
    try:
        po_res      = db.execute(text("SELECT COUNT(id), SUM(balance_amount) FROM purchase_orders WHERE balance_amount>0 AND LOWER(status)!='completed'")).fetchone()
        proj_res    = db.execute(text("SELECT COUNT(id) FROM projects WHERE is_deleted=0 AND (end_date < CURRENT_DATE OR deadline < CURRENT_DATE) AND LOWER(status)!='completed'")).fetchone()
        pending_pos = po_res[0] or 0
        pending_amt = po_res[1] or 0.0
        overdue     = proj_res[0] or 0
        msg = (f"Good Morning! Mewar ERP Daily Briefing:\n"
               f"Pending POs: {pending_pos} (Due: Rs {float(pending_amt):,.2f})\n" +
               (f"ALERT: {overdue} projects are overdue!\n" if overdue > 0 else "All projects on time.\n"))
        print(msg)
    except Exception as e:
        print(f"Morning briefing error: {e}")
    finally:
        db.close()
