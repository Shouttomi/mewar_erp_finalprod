#!/usr/bin/env python3
"""
Comprehensive Chatbot Endpoint Testing Script
Tests: Inventory, Suppliers, PO, Projects with various filters and history
"""

import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
BASE_URL = "http://192.168.29.175:8000"
CHATBOT_ENDPOINT = f"{BASE_URL}/chatbot/"
LOG_FILE = Path("d:/mewar_erp/chatbot_comprehensive_test_log.md")

# Initialize log file
log_content = [
    "# Comprehensive Chatbot Endpoint Test Report",
    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "---\n",
]

def log(message: str, level: str = "INFO"):
    """Log messages to both console and file"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    # Remove emoji characters for console output
    console_msg = message.replace("✅", "[OK]").replace("❌", "[FAIL]").replace("⚠️", "[WARN]").replace("▄", "=")
    log_entry = f"[{timestamp}] {level}: {console_msg}"
    print(log_entry)
    log_content.append(log_entry)

def make_request(query: str, history=None, ui_filters=None, role="superadmin", test_name=""):
    """Make a request to the chatbot endpoint"""
    payload = {
        "query": query,
        "history": history or [],
        "ui_filters": ui_filters or {},
        "role": role
    }

    log(f"\n{'='*80}")
    log(f"TEST: {test_name}", "TEST")
    log(f"Query: {query}")
    log(f"Role: {role}")
    if history:
        log(f"History Count: {len(history)}")
    if ui_filters:
        log(f"Filters: {ui_filters}")

    try:
        response = requests.post(CHATBOT_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        log(f"Status: SUCCESS (200)", "SUCCESS")

        # Parse and log results
        if "results" in result:
            log(f"Results Count: {len(result['results'])}")
            for idx, res in enumerate(result['results']):
                res_type = res.get("type", "unknown")
                log(f"  [{idx+1}] Type: {res_type}")

                if res_type == "chat":
                    msg = res.get("message", "")
                    log(f"       Message: {msg[:100]}...")
                elif res_type == "result":
                    if "inventory" in res:
                        inv = res["inventory"]
                        log(f"       Inventory: {inv.get('name')} (ID: {inv.get('id')})")
                        log(f"       Stock: {res.get('total_stock')} units")
                    elif "supplier" in res:
                        sup = res["supplier"]
                        log(f"       Supplier: {sup.get('name')} | {sup.get('city')}")
                elif res_type == "po":
                    log(f"       PO: {res.get('po_no')} | {res.get('supplier')}")
                    log(f"       Total: Rs{res.get('total')} | Balance: Rs{res.get('balance')}")
                elif res_type == "project":
                    log(f"       Project: {res.get('project_name')}")
                    log(f"       Status: {res.get('category')}")
                elif res_type == "dropdown":
                    log(f"       Dropdown: {res.get('message')}")
                    log(f"       Items: {len(res.get('items', []))} options")

        # Save raw response for debugging
        log_content.append(f"\nRaw Response:\n```json\n{json.dumps(result, indent=2)}\n```")
        return result

    except requests.exceptions.Timeout:
        log(f"Status: TIMEOUT (>30s)", "ERROR")
        return None
    except requests.exceptions.ConnectionError as e:
        log(f"Status: CONNECTION ERROR: {str(e)}", "ERROR")
        return None
    except Exception as e:
        log(f"Status: ERROR: {str(e)}", "ERROR")
        return None

def test_inventory():
    """Test inventory-related queries"""
    log("\n" + "="*80, "SECTION")
    log("SECTION: INVENTORY TESTS", "SECTION")

    tests = [
        ("bearing", "Search for bearing item"),
        ("round bar", "Search for round bar"),
        ("oil seal", "Search for oil seal"),
        ("kitna bearing hai", "Hinglish: how much bearing"),
        ("bearing stock check karo", "Hinglish: check bearing stock"),
        ("stock details", "Generic stock search"),
        ("sabse kam stock wala item", "Lowest stock item"),
        ("sabse zyada stock", "Highest stock item"),
        ("total inventory", "Count of all items"),
    ]

    for query, name in tests:
        make_request(query, test_name=f"Inventory - {name}")
        time.sleep(1)

def test_suppliers():
    """Test supplier-related queries"""
    log("\n" + "="*80, "SECTION")
    log("SECTION: SUPPLIER TESTS", "SECTION")

    tests = [
        ("supplier list", "Show all suppliers"),
        ("supplier mobile contact", "Get supplier contact"),
        ("supplier gst", "Get supplier GST"),
        ("supplier details", "Full supplier profile"),
        ("vendor contact", "Vendor contact number"),
        ("party profile", "Party profile"),
        ("kitne suppliers hain", "Count suppliers"),
    ]

    for query, name in tests:
        make_request(query, test_name=f"Supplier - {name}")
        time.sleep(1)

def test_purchase_orders():
    """Test PO-related queries"""
    log("\n" + "="*80, "SECTION")
    log("SECTION: PURCHASE ORDER TESTS", "SECTION")

    tests = [
        ("latest po", "Show latest PO"),
        ("po list", "Show all POs"),
        ("po details", "PO details"),
        ("pending po", "Show pending POs"),
        ("draft po", "Show draft POs"),
        ("sabse jada balance", "Highest balance"),
        ("sabse kam balance", "Lowest balance"),
        ("highest po", "Biggest PO"),
        ("sabse chhota po", "Smallest PO"),
        ("total pending balance", "Total pending balance"),
        ("tax report", "Tax/GST report"),
        ("po with advance", "POs with advance payment"),
        ("last 5 orders", "Last 5 orders"),
        ("kitne purchase orders hain", "Count POs"),
    ]

    for query, name in tests:
        make_request(query, test_name=f"PO - {name}")
        time.sleep(1)

def test_projects():
    """Test project-related queries"""
    log("\n" + "="*80, "SECTION")
    log("SECTION: PROJECT TESTS", "SECTION")

    tests = [
        ("project list", "Show all projects"),
        ("active projects", "Active projects"),
        ("completed projects", "Completed projects"),
        ("project status", "Project status"),
        ("total projects", "Count projects"),
        ("running projects", "Running projects"),
    ]

    for query, name in tests:
        make_request(query, test_name=f"Project - {name}")
        time.sleep(1)

def test_with_history():
    """Test conversation history feature"""
    log("\n" + "="*80, "SECTION")
    log("SECTION: HISTORY & CONTEXT TESTS", "SECTION")

    # Test 1: Follow-up after supplier search
    log("\n--- Follow-up Test 1: Supplier Context ---", "TEST")

    history1 = []
    result1 = make_request(
        "supplier list",
        history=history1,
        test_name="History - Initial supplier search"
    )

    if result1:
        history1.append({"role": "assistant", "content": "Found suppliers"})
        history1.append({"role": "user", "content": "supplier list"})

        # Follow-up with history
        make_request(
            "uske mobile number",  # "their phone number"
            history=history1,
            test_name="History - Follow-up (phone)"
        )

    time.sleep(1)

    # Test 2: Multi-turn conversation
    log("\n--- Multi-turn Test ---", "TEST")
    history3 = [
        {"role": "user", "content": "show latest po"},
        {"role": "assistant", "content": "Found purchase order"},
        {"role": "user", "content": "uska supplier"}
    ]

    make_request(
        "uska balance kitna baaki hai",  # "what's the balance"
        history=history3,
        test_name="History - Multi-turn balance query"
    )

def test_with_filters():
    """Test UI filters"""
    log("\n" + "="*80, "SECTION")
    log("SECTION: FILTER TESTS", "SECTION")

    # Date range filter
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    filters_tests = [
        ({"status": "draft"}, "po list", "PO with draft status filter"),
        ({"status": "completed"}, "po list", "PO with completed status filter"),
        ({"from_date": start_date, "to_date": end_date}, "po list", "PO with date range"),
        ({"limit": 10}, "po list", "PO with limit filter"),
        ({"status": "in progress"}, "project list", "Project in progress"),
    ]

    for filters, query, name in filters_tests:
        make_request(query, ui_filters=filters, test_name=f"Filters - {name}")
        time.sleep(1)

def test_role_based_access():
    """Test role-based access control"""
    log("\n" + "="*80, "SECTION")
    log("SECTION: ROLE-BASED ACCESS TESTS", "SECTION")

    roles = ["superadmin", "admin", "manager", "supervisor"]

    for role in roles:
        make_request(
            "po list",
            role=role,
            test_name=f"Role-based - {role} accessing PO"
        )
        time.sleep(1)

def test_edge_cases():
    """Test edge cases and error handling"""
    log("\n" + "="*80, "SECTION")
    log("SECTION: EDGE CASE TESTS", "SECTION")

    edge_cases = [
        ("", "Empty query"),
        ("   ", "Whitespace only"),
        ("xyz123abc456", "Non-existent item"),
        ("a", "Single character"),
        ("bearing bearing bearing", "Repeated words"),
        ("po po po", "Repeated PO keyword"),
    ]

    for query, name in edge_cases:
        make_request(query, test_name=f"Edge Case - {name}")
        time.sleep(0.5)

def save_log():
    """Save log to file"""
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(log_content))
        log(f"\nLog saved to: {LOG_FILE}", "SUCCESS")
    except Exception as e:
        log(f"Failed to save log: {e}", "ERROR")

def main():
    """Run all tests"""
    log("Starting Comprehensive Chatbot Testing")
    log(f"Endpoint: {CHATBOT_ENDPOINT}")

    try:
        # Test connectivity
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        log("Server is reachable", "SUCCESS")
    except Exception as e:
        log(f"Cannot reach server: {e}", "ERROR")
        log("Please ensure the server is running at the specified IP and port", "ERROR")
        save_log()
        return

    # Run all test suites
    try:
        test_inventory()
        time.sleep(2)

        test_suppliers()
        time.sleep(2)

        test_purchase_orders()
        time.sleep(2)

        test_projects()
        time.sleep(2)

        test_with_history()
        time.sleep(2)

        test_with_filters()
        time.sleep(2)

        test_role_based_access()
        time.sleep(2)

        test_edge_cases()

        log("\n" + "="*80, "SUMMARY")
        log("All test suites completed", "SUCCESS")

    except KeyboardInterrupt:
        log("\nTesting interrupted by user", "WARNING")
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
    finally:
        save_log()

if __name__ == "__main__":
    main()
