"""
llm_bench.py — Compare free OpenRouter models on hard ERP queries.
Tests 10 semantically complex queries, checks intent + entity correctness.
"""
import json, os, time, requests, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv(override=True)

OR_KEY = os.getenv("OPENROUTER_API_KEY", "")

MODELS = [
    "google/gemma-3-27b-it:free",
    "google/gemma-2-27b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "minimax/minimax-m2.5:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen3-8b:free",
    "qwen/qwen3-30b-a3b:free",
]

SYSTEM = """You are mewar erp chatbot. Output STRICT JSON only:
{"intents":["search"],"search_target":"","specific_items":[],"filters":{"status":null,"priority":null,"city":null,"machine":null,"category":null,"from_date":null,"to_date":null,"limit":5},"reasoning":"..."}

Intents: search=inventory/stock, supplier_search=supplier/vendor, po_search=purchase orders/balance/payments, project_search=project/site, general_chat=other
NAME SAFETY: Never shorten supplier/company names. Keep exactly as typed.
CLEANING: Remove noise words from search_target (ka, ki, ke, dikhao, batao, supplier, details, etc.)"""

TESTS = [
    ("English stock",        "how much bearing stock do we have",             "search",          "bearing"),
    ("Hindi aggregation",    "sabse zyada balance kiska hai",                 "po_search",       ""),
    ("Casual mobile query",  "Unitech ka number kya hai bhai",                "supplier_search", "Unitech"),
    ("Superlative PO",       "highest value PO dikhao",                       "po_search",       ""),
    ("Metaphor/synonym",     "bearing ka maal thoda kam lag raha hai",        "search",          "bearing"),
    ("Paisa baaki entity",   "DCL ka kitna paisa baaki hai abhi tak",         "po_search",       "DCL"),
    ("Tax aggregation",      "total tax kitna bana",                          "po_search",       ""),
    ("Low stock hint",       "low stock items batao",                         "search",          ""),
    ("City hint supplier",   "Rishabh kahan se hai",                          "supplier_search", "Rishabh"),
    ("Complete profile",     "Aastha ke bare mein complete details",          "supplier_search", "Aastha"),
    ("Hinglish PO synonym",  "orders ka hisab dikhao",                        "po_search",       ""),
    ("Udhar balance",        "kiska udhar baaki hai",                         "po_search",       ""),
]

def call_model(model, query):
    t0 = time.time()
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OR_KEY}",
                "HTTP-Referer": "https://mewar-erp.local",
                "X-OpenRouter-Title": "Mewar ERP Bench",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": query},
                ],
                "temperature": 0.0,
                "max_tokens": 300,
            },
            timeout=25,
        )
        ms = round((time.time() - t0) * 1000)
        if r.status_code in (402, 429, 404, 503):
            return None, ms, f"HTTP {r.status_code}"
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"].strip()
        s, e = raw.find("{"), raw.rfind("}") + 1
        parsed = json.loads(raw[s:e]) if s != -1 else {}
        return parsed, ms, None
    except Exception as ex:
        ms = round((time.time() - t0) * 1000)
        return None, ms, str(ex)[:60]

def score(parsed, expect_intent, expect_target):
    if not parsed:
        return 0, "no response"
    intents = parsed.get("intents", [])
    target  = parsed.get("search_target", "").lower()
    ok_intent = expect_intent in intents
    ok_target = (not expect_target) or (expect_target.lower() in target)
    pts = int(ok_intent) + int(ok_target)
    reason = f"intent={'OK' if ok_intent else 'FAIL'}({intents}) target={'OK' if ok_target else 'FAIL'}({target!r})"
    return pts, reason

print("=" * 110)
print("FREE LLM BENCHMARK — Mewar ERP Intent Classification")
print(f"Testing {len(MODELS)} models × {len(TESTS)} queries")
print("=" * 110)

totals = {}
for model in MODELS:
    short = model.split("/")[-1].replace(":free", "")[:30]
    print(f"\n>>> MODEL: {model}")
    score_sum = 0
    max_score = 0
    errors = 0
    for label, query, exp_intent, exp_target in TESTS:
        parsed, ms, err = call_model(model, query)
        pts, reason = score(parsed, exp_intent, exp_target)
        max_pts = 1 + int(bool(exp_target))
        score_sum += pts
        max_score += max_pts
        status = "OK " if pts == max_pts else ("PART" if pts > 0 else "FAIL")
        if err:
            errors += 1
            print(f"  [{status}] {label:<35} ERROR: {err}")
        else:
            print(f"  [{status}] {label:<35} {ms:>4}ms  {reason}")
    pct = round(score_sum * 100 / max_score) if max_score else 0
    totals[model] = (score_sum, max_score, pct, errors)
    print(f"  TOTAL: {score_sum}/{max_score} = {pct}%  ({errors} errors)")

print()
print("=" * 110)
print("FINAL LEADERBOARD")
print("=" * 110)
ranked = sorted(totals.items(), key=lambda x: x[1][2], reverse=True)
for rank, (model, (s, mx, pct, errs)) in enumerate(ranked, 1):
    short = model.split("/")[-1].replace(":free", "")[:35]
    print(f"  #{rank}  {pct:>3}%  {s:>2}/{mx}  errors={errs}  {short}")

print()
winner = ranked[0]
print(f"WINNER: {winner[0]}  ({winner[1][2]}% accuracy)")
