#!/usr/bin/env python3
"""Quick Chatbot Endpoint Test with JSON Logging"""

import requests
import json
from datetime import datetime
from pathlib import Path

BASE_URL = "http://192.168.29.175:8000"
CHATBOT_ENDPOINT = f"{BASE_URL}/chatbot/"
LOG_FILE = Path("d:/mewar_erp/chatbot_test_results.json")

# Store all results
test_results = {
    "timestamp": datetime.now().isoformat(),
    "endpoint": CHATBOT_ENDPOINT,
    "tests": []
}

def test_query(query: str, history=None, ui_filters=None, role="superadmin", test_name=""):
    """Test a single query"""
    payload = {
        "query": query,
        "history": history or [],
        "ui_filters": ui_filters or {},
        "role": role
    }

    test_entry = {
        "name": test_name,
        "query": query,
        "role": role,
        "filters": ui_filters or {},
        "history_count": len(history or []),
        "status": "ERROR",
        "response": None,
        "error": None,
    }

    try:
        response = requests.post(CHATBOT_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        test_entry["status"] = "SUCCESS"
        test_entry["response"] = result

        # Extract summary
        if "results" in result:
            test_entry["results_count"] = len(result["results"])
            test_entry["result_types"] = [r.get("type") for r in result["results"]]

    except Exception as e:
        test_entry["status"] = "ERROR"
        test_entry["error"] = str(e)

    test_results["tests"].append(test_entry)
    print(f"[{test_entry['status']}] {test_name}: {query}")

    return test_entry

# INVENTORY TESTS
print("\n=== INVENTORY TESTS ===")
test_query("bearing", test_name="Inventory - Search bearing")
test_query("round bar", test_name="Inventory - Search round bar")
test_query("sabse kam stock wala item", test_name="Inventory - Lowest stock")
test_query("sabse zyada stock", test_name="Inventory - Highest stock")
test_query("total inventory", test_name="Inventory - Count all items")

# SUPPLIER TESTS
print("\n=== SUPPLIER TESTS ===")
test_query("supplier list", test_name="Supplier - List all")
test_query("supplier mobile contact", test_name="Supplier - Contact details")
test_query("supplier gst", test_name="Supplier - GST info")
test_query("kitne suppliers hain", test_name="Supplier - Count")

# PURCHASE ORDER TESTS
print("\n=== PURCHASE ORDER TESTS ===")
test_query("latest po", test_name="PO - Latest")
test_query("po list", test_name="PO - List all")
test_query("pending po", test_name="PO - Pending")
test_query("draft po", test_name="PO - Draft")
test_query("sabse jada balance", test_name="PO - Highest balance")
test_query("sabse kam balance", test_name="PO - Lowest balance")
test_query("highest po", test_name="PO - Biggest order")
test_query("sabse chhota po", test_name="PO - Smallest order")
test_query("total pending balance", test_name="PO - Total pending balance")
test_query("tax report", test_name="PO - Tax/GST report")
test_query("po with advance", test_name="PO - With advance payment")
test_query("last 5 orders", test_name="PO - Last 5 orders")
test_query("kitne purchase orders hain", test_name="PO - Count all")

# PROJECT TESTS
print("\n=== PROJECT TESTS ===")
test_query("project list", test_name="Project - List all")
test_query("active projects", test_name="Project - Active")
test_query("completed projects", test_name="Project - Completed")
test_query("total projects", test_name="Project - Count")
test_query("running projects", test_name="Project - Running")

# HISTORY TESTS
print("\n=== HISTORY & CONTEXT TESTS ===")
history1 = [
    {"role": "user", "content": "supplier list"},
    {"role": "assistant", "content": "Found suppliers"}
]
test_query("uske mobile number", history=history1, test_name="History - Follow-up phone")

history2 = [
    {"role": "user", "content": "latest po"},
    {"role": "assistant", "content": "Found PO"},
    {"role": "user", "content": "uska supplier"}
]
test_query("uska balance kitna", history=history2, test_name="History - Multi-turn balance")

# FILTER TESTS
print("\n=== FILTER TESTS ===")
test_query("po list", ui_filters={"status": "draft"}, test_name="Filter - PO draft status")
test_query("po list", ui_filters={"status": "completed"}, test_name="Filter - PO completed status")
test_query("po list", ui_filters={"limit": 10}, test_name="Filter - PO limit 10")

# ROLE TESTS
print("\n=== ROLE-BASED ACCESS TESTS ===")
test_query("po list", role="superadmin", test_name="Role - Superadmin PO access")
test_query("po list", role="supervisor", test_name="Role - Supervisor PO access (blocked?)")
test_query("po list", role="manager", test_name="Role - Manager PO access")

# EDGE CASES
print("\n=== EDGE CASE TESTS ===")
test_query("", test_name="Edge - Empty query")
test_query("   ", test_name="Edge - Whitespace only")
test_query("xyz123abc", test_name="Edge - Non-existent item")
test_query("a", test_name="Edge - Single character")
test_query("bearing bearing bearing", test_name="Edge - Repeated word")

# Save results
print("\n=== SAVING RESULTS ===")
try:
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Test results saved to: {LOG_FILE}")
    print(f"[INFO] Total tests: {len(test_results['tests'])}")
    print(f"[INFO] Passed: {sum(1 for t in test_results['tests'] if t['status']=='SUCCESS')}")
    print(f"[INFO] Failed: {sum(1 for t in test_results['tests'] if t['status']=='ERROR')}")
except Exception as e:
    print(f"[ERROR] Failed to save results: {e}")

# Print summary
print("\n=== TEST SUMMARY ===")
print(f"Total Tests: {len(test_results['tests'])}")
for test in test_results['tests']:
    status_icon = "[OK]" if test['status'] == 'SUCCESS' else "[FAIL]"
    result_count = test.get('results_count', 'N/A')
    print(f"{status_icon} {test['name']}: {result_count} results")
