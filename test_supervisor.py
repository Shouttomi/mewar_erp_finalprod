#!/usr/bin/env python3
"""Test which queries bypass supervisor block"""

import requests
import json

BASE = "http://192.168.29.175:8000/chatbot/"

def test(query, role="supervisor"):
    r = requests.post(BASE, json={"query": query, "history": [], "ui_filters": {}, "role": role}, timeout=30)
    result = r.json()
    results = result.get("results", [])
    types = [x.get("type") for x in results]
    has_po = "po" in types
    msgs = [x.get("message","")[:60] for x in results if x.get("type") == "chat"]
    blocked = any("permission" in str(m).lower() or "nahi hai" in str(m).lower() for m in msgs)
    return {"query": query, "types": types, "has_po": has_po, "blocked": blocked, "msgs": msgs}

# PO-related queries to test supervisor blocking
po_queries = [
    "po list",
    "latest po",
    "pending po",
    "draft po",
    "purchase orders",
    "show me orders",
    "sabse jada balance",
    "total pending balance",
    "highest po",
    "po details",
    "last 5 orders",
    "order list",
    "kitne purchase orders hain",
]

print("="*70)
print("SUPERVISOR ROLE - PO ACCESS BLOCK TEST")
print("="*70)
print(f"{'Query':<35} {'Blocked?':<10} {'Types':<30}")
print("-"*70)

not_blocked = []
blocked_list = []

for q in po_queries:
    try:
        res = test(q)
        status = "BLOCKED" if res["blocked"] else "NOT BLOCKED"
        if not res["blocked"]:
            not_blocked.append(q)
        else:
            blocked_list.append(q)
        print(f"{q:<35} {status:<10} {str(res['types'])}")
    except Exception as e:
        print(f"{q:<35} ERROR: {e}")

print("\n" + "="*70)
print(f"NOT BLOCKED ({len(not_blocked)}):")
for q in not_blocked:
    print(f"  - {q}")

print(f"\nBLOCKED ({len(blocked_list)}):")
for q in blocked_list:
    print(f"  - {q}")
