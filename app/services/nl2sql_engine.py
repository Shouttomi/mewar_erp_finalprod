import os
import re
import time
import datetime
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Keys (all from env vars) ──────────────────────────────────────────────────
# SambaNova: comma-separated list of up to 7 keys for rate-limit rotation.
# Example: SAMBANOVA_API_KEYS=key1,key2,key3
SAMBANOVA_KEYS = [
    k.strip() for k in os.getenv("SAMBANOVA_API_KEYS", "").split(",")
    if k.strip()
]
# Backward compat: also accept the single-key form
_single_sb = os.getenv("SAMBANOVA_API_KEY", "").strip()
if _single_sb and _single_sb not in SAMBANOVA_KEYS:
    SAMBANOVA_KEYS.insert(0, _single_sb)
SAMBANOVA_KEY = SAMBANOVA_KEYS[0] if SAMBANOVA_KEYS else ""

# Gemini: comma-separated list of up to 2 keys for rotation
GEMINI_KEYS = [
    k.strip() for k in os.getenv("GEMINI_API_KEYS", "").split(",")
    if k.strip()
]
_single_gm = os.getenv("GEMINI_API_KEY", "").strip()
if _single_gm and _single_gm not in GEMINI_KEYS:
    GEMINI_KEYS.insert(0, _single_gm)
GEMINI_KEY = GEMINI_KEYS[0] if GEMINI_KEYS else ""

# Groq: two named env vars
GROQ_KEYS = list(filter(None, [
    os.getenv("GROQ_API_KEY_1"),
    os.getenv("GROQ_API_KEY_2"),
]))

SAMBANOVA_MODELS = [
    "DeepSeek-V3.1",                 # strongest coding/SQL model on SambaNova
    "Meta-Llama-3.3-70B-Instruct",   # fallback
]
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]
GROQ_MODELS   = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

# ── Schema cache (used by get_db_schema / invalidate_schema_cache) ───────────
_schema_full    : str = ""
_schema_compact : str = ""

SAMPLE_ROWS  = 3
MAX_CELL_LEN = 50


def _cell(v) -> str:
    if v is None:
        return "NULL"
    s = str(v)
    return s[:MAX_CELL_LEN] + "…" if len(s) > MAX_CELL_LEN else s


def _build_schemas(db):
    global _schema_full, _schema_compact
    from sqlalchemy import text
    tables = db.execute(text("SHOW TABLES")).fetchall()
    full_parts    = []
    compact_parts = []

    for (table,) in tables:
        cols      = db.execute(text(f"DESCRIBE `{table}`")).fetchall()
        col_names = [c[0] for c in cols]
        col_defs  = ", ".join(f"{c[0]} ({c[1]})" for c in cols)

        compact_parts.append(f"Table `{table}`: {col_defs}")

        try:
            sample = db.execute(text(f"SELECT * FROM `{table}` LIMIT {SAMPLE_ROWS}")).fetchall()
        except Exception:
            sample = []

        block = [f"Table `{table}`:"]
        block.append(f"  Columns: {col_defs}")
        if sample:
            block.append("  Sample rows:")
            block.append("    " + " | ".join(col_names))
            for row in sample:
                block.append("    " + " | ".join(_cell(v) for v in row))
        full_parts.append("\n".join(block))

    _schema_full    = "\n\n".join(full_parts)
    _schema_compact = "\n".join(compact_parts)


def get_db_schema(db, compact: bool = False) -> str:
    if not _schema_full:
        _build_schemas(db)
    return _schema_compact if compact else _schema_full


def invalidate_schema_cache():
    global _schema_full, _schema_compact
    _schema_full = _schema_compact = ""


# ── Prompts ───────────────────────────────────────────────────────────────────

_SQL_SYSTEM = """\
You are an expert MySQL query writer for Mewar ERP — a business management system.

DATABASE SCHEMA (exact column names — do NOT guess):

categories: id, name, is_delete, deleted_at, created_at, updated_at
consumptions: id, request_slips_id, transaction_date, created_by(->users), rs_row_id, inventory_id(->inventories), machine_id, unit, quantity, height, width, project_id(->projects), remark
departments: id, department_name, status, created_at, updated_at
firms: id, name, phone, address, email, website, gst_no, pan, logo, created_at, updated_at
grns: id, grn_number, purchase_order_id(->purchase_orders), grn_date, invoice_no, remarks, created_at, updated_at
grn_items: id, grn_id(->grns), inventory_id(->inventories), received_qty, accepted_qty, rejected_qty, placement, created_at, updated_at
inventories: id, name, opening_quantity, min_quantity, unit_id(->units), unit, model, category_id(->categories), grade, height, width, length, thikness, is_deleted, opening_stock, type, classification, placement, composition, outer_diameter, inner_diameter, no_of_coil, created_at, updated_at
issue_slips: id, issue_slip_no, project_id(->projects), requisition_slip_id(->requisition_slips), transaction_date, department_id(->departments), employee_id(->users), total_req_qty, total_issue_qty, total_pending_qty, comment, status, flag, created_by, edited_by, created_on, edited_on
issue_slip_rows: id, issue_slip_id(->issue_slips), requisition_slip_row_id, item_id(->inventories), quantity, description, status, pr_status, machine_id, order_qty, issue_qty, pending_qty, pr_machining_status, supplier_id(->suppliers)
job_cards: id, transaction_date, job_card_no, priority, status, vendor_id(->vendors), employee_id(->users), created_by, total_qty, pending_qty, total_received_qty, completion_date, created_at, completed_at
job_card_rows: id, job_card_id(->job_cards), issue_slip_row_id, item_id(->inventories), qty, item_pending_qty, received_qty, completion_date, status, description, supplier_id(->suppliers)
placements: id, name, created_at, updated_at
po_status_logs: id, purchase_order_id(->purchase_orders), status, changed_by(->users), changed_at, remarks
po_transactions: id, po_id(->purchase_orders), pay_amount, transaction_date
products: id, name, is_deleted, estimation_budget, estimation_duration, start_date, created_at, updated_at
product_items: id, product_id(->products), inventory_id(->inventories), quantity, is_deleted, created_at, updated_at
projects: id, name, status, priority, deadline, start_date, end_date, created_by(->users), is_deleted, completion_date, budget, comment, refurbish, created_at, updated_at
project_item: id, project_id(->projects), inventory_id(->inventories), quantity, length, created_at, updated_at
project_products: id, project_id(->projects), product_id(->products), quantity, status, is_deleted, created_at, updated_at
purchase_orders: id, po_number, supplier_id(->suppliers), po_date, expected_delivery, total_qty, subtotal, tax_amount, total_amount, subtotal_discount_amount, final_discount, loading_cutting_charges, freight_charges, advance_amount, balance_amount, remaining_amount, status, delivery_status, firm(->firms), remarks, terms_and_conditions, created_by(->users), approved_by(->users), created_at, completed_at
purchase_order_items: id, purchase_order_id(->purchase_orders), pr_item_id(->purchase_request_items), inventory_id(->inventories), hsn, ordered_qty, received_qty, unit_price, discount, discount_amount, tax_type, tax_percent, tax_amount, taxable_total, line_total, item_not, created_at
purchase_requests: id, pr_no, request_date, requested_by(->users), department_id(->departments), priority, status, remarks, total_qty, approved_by(->users), approved_at, created_at, updated_at
purchase_request_approvals: id, purchase_request_id(->purchase_requests), approver_id(->users), approval_level, status, remarks, action_date
purchase_request_items: id, purchase_request_id(->purchase_requests), issue_slip_row_id, item_id(->inventories), description, requested_qty, approved_qty, ordered_qty, uom, required_date, status, exited_qty, created_at
purchase_request_po_map: id, purchase_request_item_id(->purchase_request_items), purchase_order_item_id(->purchase_order_items), created_at
request_slip_histories: id, request_slip_id, action_by(->users), action, status, remarks, hold_by, created_at, updated_at
requisition_slips: id, rs_id, requisition_slip_no, store_rs, transaction_date, employee_id(->users), project_id(->projects), machine_id, lot_no, batch_no, department_id(->departments), purpose, total_qty, comment, status, approved_by(->users), rejected_by(->users), admin_id(->users), approved_date, rejected_date, admin_action_date, approve_comment, rejected_reason, admin_action_remark, admin_approve_status, po_flag, issue_completed, flag, is_exited, hold_by, created_by, edited_by, created_on, edited_on
requisition_slip_rows: id, requisition_slip_id(->requisition_slips), machine_id, item_id(->inventories), unit_id(->units), quantity, order_qty, issue_qty, pending_qty, order_pending_qty, issued_qty, consumed_qty, issued_height, issued_width, consumed_height, consumed_width, description, status, exited_qty, is_completed, unit
requisition_slip_row_pieces: id, item_id(->inventories), requisition_slip_row_id(->requisition_slip_rows), issued_height, issued_width, issued_qty, consumed_height, consumed_width, consumed_qty, shape, is_completed, send_hod
roles: id, name, deleted_at, created_at, updated_at
stock_transactions: id, project_id(->projects), machine_id, inventory_id(->inventories), txn_date, txn_type(enum: In/Out), quantity, ref_type, ref_no, issued_to(->users), issue_by(->users), requision_id(->requisition_slips), issue_slip_id(->issue_slips), supplier_id(->suppliers), vendor_id(->vendors), remarks
suppliers: id, category, registration_date, supplier_name, supplier_code, contact_person, email, state, city, mobile, gst_registered, gstin, pan, supplier_address, bank_name, branch_address, ifsc, account_number, created_at, updated_at
supplier_inventories: id, supplier_id(->suppliers), inventory_id(->inventories), quantity, created_at, updated_at
units: id, name, is_deleted, created_at, updated_at
users: id, name, email, status, date, is_delete, password, address, role_id(->roles), country_code, mobile, department_id(->departments), authority_id, image, created_at, updated_at
vendors: id, name, mobile_no, email, address, city, created_at, updated_at
vendor_payments: id, vendor_id(->vendors), purchase_order_id(->purchase_orders), amount, payment_date, payment_mode, reference_no, created_at

OUTPUT RULES — MUST FOLLOW:
1. Output ONLY a raw MySQL SELECT query. No explanation. No markdown. No code fences.
2. Never write INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, or any write operation.
3. Do NOT add any LIMIT clause. Return all rows unless the user explicitly asks for a top-N.
4. For ANY name or text search, ALWAYS use fuzzy matching:
   WHERE (col LIKE '%term%' OR col SOUNDS LIKE 'term' OR col LIKE '%word1%' OR col LIKE '%word2%')
5. If the question truly cannot be answered from this schema, output exactly: CANNOT_ANSWER
6. For vague/analytical questions ("best", "worst", "recommend"), fetch relevant metrics so the answer step can give a real recommendation.

CRITICAL RULES (never violate):
- suppliers name column: `supplier_name` — NEVER write s.name or suppliers.name
- purchase_order_items FK to purchase_orders: column is `purchase_order_id` — NEVER write `po_id`
- purchase_order_items has NO supplier_id — FK is on purchase_orders.supplier_id
- purchase_order_items amount columns: `line_total`, `taxable_total` only — NO total_amount/balance_amount
- purchase_order_items has NO name/description/item_name — item name is in inventories.name via inventory_id
- When aggregating per supplier: GROUP BY s.id, s.supplier_name ONLY — never include purchase_orders columns in GROUP BY
- purchase_orders has NO project_id — no direct join between purchase_orders and projects
- requisition_slips = request slips (rs) — same table; alias it `rs` NOT `is` (that's reserved for issue_slips)
- issue_slips alias must be `isl` or `islip` — NEVER use alias `is` (reserved SQL keyword)
- issue_slip_rows FK to issue_slips: column is `issue_slip_id` — join: isl.id = isr.issue_slip_id
- issue_slip_rows item column: `item_id` (-> inventories) — NEVER write `inventory_id` on this table
- requisition_slips has NO total_issue_qty / total_pending_qty columns — those are on issue_slips (total_issue_qty, total_pending_qty). To get issued/pending per RS, join: requisition_slips -> issue_slips via issue_slips.requisition_slip_id
- When the question asks for "issued qty" or "pending qty" per RS, use issue_slips.total_issue_qty and issue_slips.total_pending_qty
- COLUMN NAMING: always SELECT and GROUP BY the raw FK id column alongside the name — e.g. SELECT st.inventory_id, i.name, SUM(...) ... GROUP BY st.inventory_id, i.name. Never drop inventory_id from the SELECT.
- inventories has NO columns named `current_stock` or `shortage` — never reference them directly; always compute inline with COALESCE/SUM subquery
- stock_transactions join to inventories: st.inventory_id = i.id (NOT i.inventory_id)
- project_item table alias: use `pi` — but NEVER use `pi.name`; project name comes from projects.name via pi.project_id = p.id
- grn_items FK to grns: column is `grn_id` — join: g.id = gi.grn_id
- grn_items has NO `po_id` — to link GRN to PO: grn_items -> grns.purchase_order_id -> purchase_orders
- requisition_slip_rows has NO `project_id` — get project via: rsr -> requisition_slips.project_id -> projects
- stock_transactions `txn_type` values are exactly: 'In' and 'Out' (capital first letter)
- inventories has NO `current_stock` column — compute it: COALESCE(opening_quantity,0) + COALESCE(net_txn,0)
- inventories has NO `quantity` column — use `opening_quantity` or compute from stock_transactions
- purchase_orders `status` values: 'Draft', 'Approved', 'Completed' (capital first letter)
- When joining purchase_orders with grns: purchase_orders.id = grns.purchase_order_id
- projects `status` values are exactly: 'new' and 'in_progress' (lowercase with underscore) — NEVER use 'In Progress', 'inprogress', 'active', or any other variant
- "in progress projects", "jo projects chal rahe hain", "current projects" means WHERE status='in_progress' — apply this filter strictly, do NOT return all projects
- projects table date columns: `start_date` = project start, `end_date` = project end/deadline, `deadline` column is usually NULL — ALWAYS use `end_date` when asked for deadline, due date, end date, or "kab tak chalega"
- PROJECT PROGRESS / STAGE PERCENTAGE: the projects table has NO progress/stage/percent column. When user asks about project progress, "kitna percent complete", "stage", "X% se upper", "X% se kam", compute progress from dates:
    progress_pct =
      CASE
        WHEN end_date <= CURDATE() THEN 100
        WHEN start_date >= CURDATE() THEN 0
        WHEN DATEDIFF(end_date, start_date) = 0 THEN 100
        ELSE ROUND(DATEDIFF(CURDATE(), start_date) * 100.0 / DATEDIFF(end_date, start_date))
      END
  Use this formula whenever the user asks anything about project progress, stage, or completion percentage. Filter with WHERE is_deleted=0.
  Example for "kitne projects 25% se upper ho gaye hain":
    SELECT id, name, start_date, end_date,
      CASE WHEN end_date <= CURDATE() THEN 100
           WHEN start_date >= CURDATE() THEN 0
           WHEN DATEDIFF(end_date, start_date) = 0 THEN 100
           ELSE ROUND(DATEDIFF(CURDATE(), start_date) * 100.0 / DATEDIFF(end_date, start_date))
      END AS progress_pct
    FROM projects
    WHERE is_deleted=0
    HAVING progress_pct > 25
    ORDER BY progress_pct DESC
- PROJECT NAME SEARCH: when user asks about a specific company/client name (e.g. "RBL Minerals ki detail", "RBL Minerals ki inventory"), ALWAYS search in `projects` table first (projects.name LIKE '%term%'), NOT in suppliers. A client/customer is a project, not a supplier. Only search suppliers when user explicitly says "supplier" or "vendor".
- PROJECT INVENTORY ITEMS: a project's inventory comes from TWO sources — always include BOTH:
  (1) BOM chain: project_products -> product_items -> inventories (pp.project_id=p.id, pit.product_id=pp.product_id, i.id=pit.inventory_id)
  (2) Direct: project_item -> inventories (pi.project_id=p.id, i.id=pi.inventory_id)
  When asked "X project ki inventory batao", use:
  SELECT i.id, i.name, i.model, SUM(pp.quantity * pit.quantity) AS required_qty, 'BOM' AS source
  FROM projects p JOIN project_products pp ON pp.project_id=p.id AND pp.is_deleted=0
  JOIN product_items pit ON pit.product_id=pp.product_id AND pit.is_deleted=0
  JOIN inventories i ON i.id=pit.inventory_id
  WHERE p.name LIKE '%term%'
  GROUP BY i.id, i.name, i.model
  UNION ALL
  SELECT i.id, i.name, i.model, SUM(pi.quantity) AS required_qty, 'Direct' AS source
  FROM projects p JOIN project_item pi ON pi.project_id=p.id
  JOIN inventories i ON i.id=pi.inventory_id
  WHERE p.name LIKE '%term%'
  GROUP BY i.id, i.name, i.model
  CRITICAL: For project name search, use the FULL company name in a single LIKE '%full name%' — NEVER split into individual words (e.g. '%RBL%' OR '%Minerals%') as that matches unrelated projects. Do NOT use SOUNDS LIKE for project names.
  CRITICAL: Always GROUP BY i.id, i.name, i.model in the BOM branch to avoid duplicate rows when multiple products in the same project share the same inventory item.
- Hindi/Hinglish list words: "sarii", "saari", "saare", "sari", "sabhi", "sab", "sare" all mean "all" — fetch ALL rows with NO date or status filter unless the user also specifies one
- Date day filter: "13 date wali", "13 tarikh wali", "only 13 date" means DAY(transaction_date) = 13 — use DAY() function
- "X month wali" or "X mahine wali" means MONTH(transaction_date) = X
- INVENTORY SHORTAGE IN PROJECTS: "kis project mein X ki shortage hai", "which projects need X", "kin kin projects me bolts ki kami hai":
  A project needs item X if its required_qty for X (from BOM + direct) is greater than the item's current stock.
  Required comes from TWO sources — always union both:
    (1) BOM chain: project_products -> product_items -> inventories
    (2) Direct: project_item -> inventories
  Use derived subqueries so each row already has aggregated required_qty + current_stock — avoids MySQL "Unknown column in HAVING" errors that happen when you mix GROUP BY with non-aggregated columns in HAVING.
  Use this EXACT SQL pattern (replace 'X' with the item search term, e.g. 'bolt'):

  SELECT t.project_id, t.project_name, t.inventory_id, t.item_name, t.item_model,
    SUM(t.required_qty) AS required_qty,
    t.current_stock,
    SUM(t.required_qty) - t.current_stock AS shortage
  FROM (
    SELECT p.id AS project_id, p.name AS project_name,
      i.id AS inventory_id, i.name AS item_name, i.model AS item_model,
      pp.quantity * pit.quantity AS required_qty,
      COALESCE(i.opening_quantity,0) + COALESCE((SELECT SUM(CASE WHEN txn_type='In' THEN quantity ELSE -quantity END) FROM stock_transactions WHERE inventory_id=i.id),0) AS current_stock
    FROM projects p
    JOIN project_products pp ON pp.project_id=p.id AND pp.is_deleted=0
    JOIN product_items pit ON pit.product_id=pp.product_id AND pit.is_deleted=0
    JOIN inventories i ON i.id=pit.inventory_id
    WHERE p.is_deleted=0 AND i.name LIKE '%X%'
    UNION ALL
    SELECT p.id, p.name, i.id, i.name, i.model,
      pi.quantity,
      COALESCE(i.opening_quantity,0) + COALESCE((SELECT SUM(CASE WHEN txn_type='In' THEN quantity ELSE -quantity END) FROM stock_transactions WHERE inventory_id=i.id),0)
    FROM projects p
    JOIN project_item pi ON pi.project_id=p.id
    JOIN inventories i ON i.id=pi.inventory_id
    WHERE p.is_deleted=0 AND i.name LIKE '%X%'
  ) t
  GROUP BY t.project_id, t.project_name, t.inventory_id, t.item_name, t.item_model, t.current_stock
  HAVING SUM(t.required_qty) > t.current_stock
  ORDER BY shortage DESC

  CRITICAL: NEVER reference i.opening_quantity directly in HAVING — that causes "Unknown column" errors in MySQL. Always pre-compute current_stock in the inner subquery and use the alias in HAVING.
- GLOBAL INVENTORY SHORTAGE: "inventory items ki shortage" (without project context) means items where
  current_stock < inventories.min_quantity. shortage = min_quantity - current_stock.
  current_stock for global shortage = COALESCE(opening_quantity, 0) + net stock_transactions (In minus Out).
  Simpler formula used in practice: shortage = min_quantity - opening_quantity when opening_quantity < min_quantity.
- "paisa baaki" or "rokra" for suppliers means purchase_orders.balance_amount — SUM(balance_amount) per supplier
- ITEM TYPE STOCK QUERY ("bearing ka stock", "bolt ka stock", "how much bearings do we have"):
  These ask for the TOTAL combined stock of ALL items whose name contains that word.
  ALWAYS use: SELECT SUM(COALESCE(i.opening_quantity,0) + COALESCE((SELECT SUM(CASE WHEN txn_type='In' THEN quantity ELSE -quantity END) FROM stock_transactions WHERE inventory_id=i.id),0)) AS total_stock FROM inventories i WHERE i.name LIKE '%word%'
  Return a SINGLE row with total_stock. Do NOT list individual items — aggregate them.
- MULTI-TYPE STOCK ("bolts and bearings ka stock", "how much X and Y do we have"):
  Search by item name, NOT by categories table — categories has generic names like 'Raw Material', not 'Bearings'/'Bolts'.
  Use UNION ALL to show each type as a labeled group. Example for bolt+bearing:
  SELECT 'Bolt' AS item_type, SUM(COALESCE(i.opening_quantity,0)+COALESCE((SELECT SUM(CASE WHEN txn_type='In' THEN quantity ELSE -quantity END) FROM stock_transactions WHERE inventory_id=i.id),0)) AS total_stock FROM inventories i WHERE i.name LIKE '%bolt%'
  UNION ALL
  SELECT 'Bearing' AS item_type, SUM(...) FROM inventories i WHERE i.name LIKE '%bearing%'
  Always label each row with a human-readable item_type, not a model number or id.
- MODEL-WISE STOCK BREAKDOWN ("model wise stock", "X ke saare models dikhao", "model wise breakdown"):
  Show each individual item row (not aggregated). Use this exact pattern:
  SELECT i.name, i.model,
    COALESCE(i.opening_quantity,0) + COALESCE((SELECT SUM(CASE WHEN txn_type='In' THEN quantity ELSE -quantity END) FROM stock_transactions st WHERE st.inventory_id=i.id),0) AS current_stock
  FROM inventories i
  WHERE (i.name LIKE '%bolt%' OR i.name LIKE '%bearing%' OR i.name LIKE '%spring%' OR i.name LIKE '%cutting rod%')
  ORDER BY i.name, i.model
  NEVER select `model` as a stock value. `model` is a text descriptor column on inventories. `current_stock` must always be computed from opening_quantity + stock_transactions SUM.
- Pronouns "iski", "iska", "is item ki", "is cheez ki" in a follow-up refer to the item mentioned in the previous turn — resolve them from conversation context.
- REQUIRED VS AVAILABLE STOCK ("required vs available", "project ke liye kitna chahiye vs kitna hai", "shortage in active projects"):
  Business logic (matches the PHP requiredVsAvailable report):
  - Required = BOM (project_products->product_items) + direct project_item quantities for active projects
  - Active projects = status NOT IN ('completed','hold') AND is_deleted=0
  - Machining = Out transactions with ref_type='Machining' (items sent for machining — consumed)
  - Finish = In transactions with ref_type='Finish' (items finished/processed — available)
  - Semi Finish = In transactions with ref_type='Semi Finish' (partially finished — available)
  - Available Total = Finish qty + Semi Finish qty (items in the production pipeline ready to use)
  - Short/Extra = Available Total - Required (negative = short, positive = extra)
  Use this exact SQL pattern:
  SELECT i.id, i.name, i.model,
    COALESCE(bom.req,0)+COALESCE(direct.req,0) AS required_qty,
    COALESCE(mach.qty,0) AS machining,
    COALESCE(fin.qty,0) AS finish,
    COALESCE(semifin.qty,0) AS semi_finish,
    COALESCE(fin.qty,0)+COALESCE(semifin.qty,0) AS available_total,
    (COALESCE(fin.qty,0)+COALESCE(semifin.qty,0)) - (COALESCE(bom.req,0)+COALESCE(direct.req,0)) AS short_extra
  FROM inventories i
  LEFT JOIN (SELECT pit.inventory_id, SUM(pp.quantity*pit.quantity) AS req FROM projects p JOIN project_products pp ON pp.project_id=p.id AND pp.is_deleted=0 JOIN product_items pit ON pit.product_id=pp.product_id AND pit.is_deleted=0 WHERE p.status NOT IN ('completed','hold') AND p.is_deleted=0 GROUP BY pit.inventory_id) bom ON bom.inventory_id=i.id
  LEFT JOIN (SELECT pi.inventory_id, SUM(pi.quantity) AS req FROM projects p JOIN project_item pi ON pi.project_id=p.id WHERE p.status NOT IN ('completed','hold') AND p.is_deleted=0 GROUP BY pi.inventory_id) direct ON direct.inventory_id=i.id
  LEFT JOIN (SELECT inventory_id, SUM(quantity) AS qty FROM stock_transactions WHERE txn_type='Out' AND ref_type='Machining' GROUP BY inventory_id) mach ON mach.inventory_id=i.id
  LEFT JOIN (SELECT inventory_id, SUM(quantity) AS qty FROM stock_transactions WHERE txn_type='In' AND ref_type='Finish' GROUP BY inventory_id) fin ON fin.inventory_id=i.id
  LEFT JOIN (SELECT inventory_id, SUM(quantity) AS qty FROM stock_transactions WHERE txn_type='In' AND ref_type='Semi Finish' GROUP BY inventory_id) semifin ON semifin.inventory_id=i.id
  WHERE bom.req IS NOT NULL OR direct.req IS NOT NULL
  ORDER BY short_extra ASC
"""

_FIX_PROMPT = """\
Original question: {question}

Your previous SQL failed:
SQL: {sql}
Error: {error}

Fix it and return ONLY the corrected SQL. No explanation.
"""

_ANSWER_SYSTEM = """\
You are a smart business assistant for Mewar ERP. Keep replies SHORT — 1 to 3 sentences max.

LANGUAGE: Always reply in Hinglish (Hindi + English mix). Use English for numbers, names, dates.
Examples: "Total 6 suppliers hain.", "Arawali Minerals ne sabse zyada orders diye — 18 POs."

- Factual queries: give the key number/name directly, skip preamble.
- Analytical queries ("best", "recommend"): 1 sentence insight + 1 sentence reason.
- If no data: say so in 1 line.
- NEVER mention SQL, database, tables, or technical terms.
- Today is {today}.
"""


# ── Provider calls ────────────────────────────────────────────────────────────

def _call_sambanova(system: str, user: str) -> str:
    if not SAMBANOVA_KEYS:
        raise RuntimeError("No SAMBANOVA_API_KEY")
    from openai import OpenAI
    last_err = None
    for api_key in SAMBANOVA_KEYS:
        for model in SAMBANOVA_MODELS:
            try:
                client = OpenAI(
                    base_url="https://api.sambanova.ai/v1",
                    api_key=api_key,
                    timeout=30.0,
                )
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                    temperature=0.0,
                    max_tokens=1500,
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                err_str = str(e)
                last_err = e
                if "429" in err_str or "rate limit" in err_str.lower():
                    print(f"[NL2SQL] SambaNova key ...{api_key[-8:]} 429 — trying next key")
                    break  # try next key immediately on rate limit
    raise RuntimeError(f"SambaNova failed: {last_err}")


def _call_gemini(system: str, user: str, retries: int = 1) -> str:
    if not GEMINI_KEYS:
        raise RuntimeError("No GEMINI_API_KEY")
    last_err = None
    for api_key in GEMINI_KEYS:
        for model in GEMINI_MODELS:
            for attempt in range(retries):
                try:
                    resp = requests.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                        params={"key": api_key},
                        headers={"Content-Type": "application/json"},
                        json={
                            "contents":          [{"role": "user", "parts": [{"text": user}]}],
                            "systemInstruction": {"parts": [{"text": system}]},
                            "generationConfig":  {"temperature": 0.0, "maxOutputTokens": 2048},
                        },
                        timeout=25,
                    )
                    if resp.status_code == 429:
                        print(f"[NL2SQL] Gemini key ...{api_key[-8:]} {model} 429 — trying next key/model")
                        last_err = f"429 rate limit on {model}"
                        break  # try next model / next key immediately
                    resp.raise_for_status()
                    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                except requests.HTTPError as e:
                    last_err = e
                    break
                except Exception as e:
                    last_err = e
                    break
    raise RuntimeError(f"Gemini failed: {last_err}")


def _call_groq(system: str, user: str) -> str:
    from openai import OpenAI
    last_err = None
    for key in GROQ_KEYS:
        for model in GROQ_MODELS:
            try:
                client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=key.strip(),
                    timeout=20.0,
                )
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                    temperature=0.0,
                    max_tokens=1500,
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                last_err = e
    raise RuntimeError(f"Groq failed: {last_err}")


def _call_ai(system_full: str, system_compact: str, user: str) -> str:
    """
    Provider chain — most capable first.
    SambaNova and Gemini get full schema + sample data.
    Groq gets compact schema (columns only) to avoid 413.
    """
    for name, fn, sys in [
        ("SambaNova (DeepSeek V3.1 / Llama 70B)", _call_sambanova, system_full),
        ("Gemini 2.5 Flash",                       _call_gemini,    system_full),
    ]:
        try:
            result = fn(sys, user)
            print(f"[NL2SQL] answered by {name}")
            return result
        except Exception as e:
            print(f"[NL2SQL] {name} failed: {str(e)[:120]}")

    try:
        result = _call_groq(system_compact, user)
        print("[NL2SQL] answered by Groq (compact schema)")
        return result
    except Exception as e:
        print(f"[NL2SQL] Groq failed: {str(e)[:120]}")

    raise RuntimeError("All AI providers failed")


# ── SQL generation ────────────────────────────────────────────────────────────

def _clean_sql(raw: str) -> str:
    raw = re.sub(r"^```(?:sql)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw).strip()
    return raw


def _validate(raw: str) -> str:
    if raw.upper().startswith("CANNOT_ANSWER"):
        raise ValueError("Cannot be answered from the schema")
    if not re.match(r"^\s*SELECT\b", raw, re.IGNORECASE):
        raise ValueError(f"Non-SELECT output: {raw[:80]}")
    if raw.count("(") != raw.count(")"):
        raise ValueError(f"Truncated SQL (unbalanced parentheses): {raw[-60:]}")
    return raw


def _history_context(history: list) -> str:
    """Build a compact conversation context string from the last 4 turns."""
    if not history:
        return ""
    turns = history[-4:]
    lines = []
    for h in turns:
        role    = str(h.get("role", "")).lower()
        content = str(h.get("content", "")).strip()[:300]
        if role == "user":
            lines.append(f"User previously asked: {content}")
        elif role in ("assistant", "bot"):
            lines.append(f"Assistant previously answered: {content}")
    if not lines:
        return ""
    return (
        "CONVERSATION CONTEXT:\n"
        + "\n".join(lines)
        + "\n"
        "FOLLOW-UP RULES: If the new query is a filter/refinement on the previous one (e.g. 'only 13 date wali', 'sirf approved wali', 'project 5 wali'), "
        "apply that filter to the SAME table from the previous query. "
        "A bare number + 'date'/'tarikh' means DAY(date_column) = that number. "
        "Resolve 'unhe', 'unka', 'woh', 'those', 'them', 'iski', 'iska', 'is item ki' to refer to the specific item/entity mentioned in the previous turn. "
        "If the previous answer mentioned a specific inventory item name (e.g. 'Hard Facing Mig Roll'), "
        "use that exact item name in a LIKE '%name%' filter on inventories.name in the new query.\n\n"
    )


def generate_sql(user_query: str, schema_full: str = "", schema_compact: str = "",
                 previous_sql: str = None, sql_error: str = None,
                 history: list = None) -> str:
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    system = _SQL_SYSTEM + f"\nToday's date: {today}. Use this to resolve partial dates (e.g. '23 feb' = '2026-02-23', 'April' = month 4).\n"
    ctx = _history_context(history or [])
    if previous_sql and sql_error:
        user = ctx + _FIX_PROMPT.format(question=user_query, sql=previous_sql, error=sql_error)
    else:
        user = ctx + user_query
    raw = _call_ai(
        system_full=system,
        system_compact=system,
        user=user,
    )
    sql = _validate(_clean_sql(raw))
    print(f"[NL2SQL] SQL: {sql[:200]}")
    return sql


# ── Answer formatting ─────────────────────────────────────────────────────────

def format_answer(user_query: str, rows: list, columns: list,
                  history: list = None) -> str:
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    if not rows:
        data_text = "No data found."
        null_warning = ""
    else:
        header = " | ".join(columns)
        body   = "\n".join(" | ".join(str(v) for v in row) for row in rows[:50])
        data_text = f"{header}\n{body}"

        null_cols = [
            col for col, val in zip(columns, rows[0])
            if val is None or str(val).strip() in ("", "None", "NULL", "N/A")
        ]
        null_warning = (
            f"\nWARNING: The following columns have NULL/empty values in the data: {', '.join(null_cols)}. "
            "Do NOT invent or guess values for these fields. Say the info is not available.\n"
        ) if null_cols else ""

    ctx  = _history_context(history or [])
    user = f"{ctx}User asked: {user_query}\n\nData returned:\n{data_text}\n{null_warning}\nGive a clear friendly answer."
    system = _ANSWER_SYSTEM.format(today=today)

    try:
        return _call_ai(system_full=system, system_compact=system, user=user)
    except Exception:
        return data_text if rows else "Koi data nahi mila."
