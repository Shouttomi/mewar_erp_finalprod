import requests, time, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

URL = 'http://127.0.0.1:8000/v2-chatbot/'

def ask(q, role='purchase', history=None):
    t0 = time.time()
    r = requests.post(URL, json={'query': q, 'role': role, 'history': history or []}, timeout=40)
    ms = round((time.time()-t0)*1000)
    out = []
    for item in r.json().get('results', []):
        t = item.get('type')
        if t == 'chat':
            out.append(('CHAT', item.get('message', '')))
        elif t == 'result' and 'inventory' in item:
            inv = item['inventory']
            out.append(('INV', f"{inv['name']} | stock={item['total_stock']} {inv.get('unit','')}"))
        elif t == 'result' and 'supplier' in item:
            s = item['supplier']
            out.append(('SUP', f"{s['name']} | {s['city']} | mob={s['mobile']} | gst={s['gstin']}"))
        elif t == 'po':
            out.append(('PO', f"{item['po_no']} | {item['supplier']} | Rs{item['total']:,.0f} | bal=Rs{item['balance']:,.0f} | {item['status']}"))
        elif t == 'project':
            out.append(('PROJ', f"{item['project_name']} | {item['category']} | pri={item['priority']}"))
        elif t == 'dropdown':
            names = [i.get('name', '')[:25] for i in item.get('items', [])[:4]]
            out.append(('DROP', f"{len(item.get('items', []))} opts: {names}"))
        elif t == 'purchase_request':
            out.append(('PR', f"{item.get('pr_no')} | {item.get('status')} | qty={item.get('total_qty')}"))
    return ms, out

passed = failed = 0

def test(label, q, role='purchase', history=None, expect_in=None, expect_not_in=None):
    global passed, failed
    ms, out = ask(q, role=role, history=history)
    first_type = out[0][0] if out else 'NONE'
    all_msg = ' | '.join(m for _, m in out)

    ok = True
    reason = ''
    fail_defaults = ['connect nahi']
    if not out:
        ok = False; reason = 'NO RESULT'
    elif any(k in all_msg.lower() for k in fail_defaults) and not expect_in:
        ok = False; reason = 'LLM connection error'
    elif expect_in and not any(e.lower() in all_msg.lower() for e in expect_in):
        ok = False; reason = f'expected one of {expect_in}'
    elif expect_not_in and any(e.lower() in all_msg.lower() for e in expect_not_in):
        ok = False; reason = f'found unwanted: {expect_not_in}'

    if ok: passed += 1
    else:  failed += 1

    status = 'OK  ' if ok else 'FAIL'
    preview = ''.join(c if ord(c) < 128 else '?' for c in (out[0][1] if out else 'NO RESULT'))[:65]
    print(f'[{status}] [{ms:>4}ms] {label:<40} {preview}')
    if not ok:
        print(f'         >> REASON: {reason}')
        detail = ''.join(c if ord(c) < 128 else '?' for c in all_msg[:120])
        print(f'         >> GOT: {detail}')


# ── HISTORY HELPERS ──────────────────────────────────────────────────────────
hist_unitech = [
    {'role': 'user',      'content': 'Unitech supplier details'},
    {'role': 'assistant', 'content': 'ye raha **Unitech Solutions and Services** ka profile: mob +919829098028, GSTIN 08AAHFU6733F1ZZ'},
]
hist_rishabh = [
    {'role': 'user',      'content': 'Rishabh ke orders dikhao'},
    {'role': 'assistant', 'content': 'ye raha **Rishabh International** ke 3 orders, balance Rs 1,82,000'},
]
hist_aastha = [
    {'role': 'user',      'content': 'Aastha ke orders dikhao'},
    {'role': 'assistant', 'content': 'ye raha **Aastha Engineering** ka 1 PO: MHEL/PO/00004/2025-2026, Rs 46,52,812'},
]
hist_bearing = [
    {'role': 'user',      'content': 'bearing ka stock kitna hai'},
    {'role': 'assistant', 'content': 'Bearing ke 30 matching items mile. Total stock 2.00 units.'},
]
hist_project = [
    {'role': 'user',      'content': 'Rajsamand ke projects dikhao'},
    {'role': 'assistant', 'content': 'ye raha **Sidhi Vinayak Microns, Rajsamand** project details, status: new, budget 0'},
]

print('='*100)
print('EDGE CASE TEST SUITE - 50 TESTS')
print('='*100)
print()

# ── SECTION 1: FOLLOW-UP WITH HISTORY (10) ───────────────────────────────────
print('--- SECTION 1: FOLLOW-UP WITH HISTORY ---')
test('FU-01: uska mobile after Unitech',       'uska mobile number kya hai',    history=hist_unitech, expect_in=['+919829098028', 'mobile'])
test('FU-02: uski gstin after Unitech',        'uski gstin kya hai',            history=hist_unitech, expect_in=['08AAHFU6733F1ZZ', 'GSTIN'])
test('FU-03: uske orders after Unitech',       'uske orders dikhao',            history=hist_unitech, expect_in=['Unitech', 'order'])
test('FU-04: iska balance after Rishabh',      'iska balance kitna hai',        history=hist_rishabh, expect_in=['Rishabh', 'balance'])
test('FU-05: yes after Unitech',               'yes',                           history=hist_unitech, expect_in=['Unitech'])
test('FU-06: orders dikhao after Unitech',     'orders dikhao',                 history=hist_unitech, expect_in=['Unitech', 'order'])
test('FU-07: uska po after Aastha',            'uska po dikhao',                history=hist_aastha,  expect_in=['Aastha', 'PO'])
test('FU-08: aur kitne after bearing',         'aur kitne hain',                history=hist_bearing, expect_in=['bearing', 'stock'])
test('FU-09: poori profile after Unitech',     'poori profile',                 history=hist_unitech, expect_in=['Unitech'])
test('FU-10: iske baare mein after project',   'iske baare mein batao',         history=hist_project, expect_in=['Rajsamand', 'project'])

print()
print('--- SECTION 2: TYPOS / SPELLING ERRORS ---')
test('TYPO-01: beerign (bearing)',             'beerign ka stock kitna hai',    expect_not_in=['samajh nahi'])
test('TYPO-02: Unitec (Unitech)',              'Unitec suplier details',        expect_in=['Unitech'])
test('TYPO-03: Risabh (Rishabh)',             'Risabh ke orders',              expect_in=['order', 'Rishabh'])
test('TYPO-04: projeckt (project)',            'running projeckt dikhao',       expect_in=['project', 'mile'])
test('TYPO-05: supplair (supplier)',           'supplair kitne hain',           expect_in=['supplier'])
test('TYPO-06: balt (belt)',                   'balt ka stock dikhao',          expect_in=['belt', 'stock'])
test('TYPO-07: purcahse order',               'purcahse orders dikhao',        expect_in=['order', 'mile'])
test('TYPO-08: inventry count',               'inventry mein kitne items',     expect_in=['item', 'inventory'])

print()
print('--- SECTION 3: MULTI-INTENT QUERIES ---')
test('MULTI-01: supplier + orders',            'Unitech ki details aur orders', expect_in=['Unitech'])
test('MULTI-02: DCL gstin + orders',           'DCL ka gstin aur orders bhi',  expect_in=['DCL'])
test('MULTI-03: two items stock',              'belt aur oil seal ka stock',   expect_in=['stock'])
test('MULTI-04: balance + count query',        'kitne orders hain aur total balance kitna', expect_in=['order'])
test('MULTI-05: supplier profile + PO',        'Rishabh ka profile aur latest PO', expect_in=['Rishabh'])

print()
print('--- SECTION 4: AGGREGATIONS & ANALYTICS ---')
test('AGG-01: highest balance supplier',       'sabse jyada balance kiska hai', expect_in=['balance', 'pending'])
test('AGG-02: lowest balance supplier',        'sabse kam balance kiska hai',   expect_in=['balance'])
test('AGG-03: biggest PO value',               'sabse bada po kaunsa hai',      expect_in=['MHEL', 'Rs'])
test('AGG-04: smallest PO',                    'sabse chota po dikhao',         expect_in=['MHEL', 'Rs'])
test('AGG-05: total inventory items',          'total kitne items hain inventory mein', expect_in=['1654'])
test('AGG-06: total suppliers registered',     'total kitne suppliers registered hain', expect_in=['6092'])
test('AGG-07: min stock item',                 'sabse kam stock wala item',     expect_in=['stock', 'units'])
test('AGG-08: max stock item',                 'sabse zyada stock wala item',   expect_in=['stock', 'units'])
test('AGG-09: total projects',                 'total projects kitne hain',     expect_in=['18', 'project'])
test('AGG-10: count draft orders',             'kitne draft orders pending hain', expect_in=['order'])
test('AGG-11: total gst all POs',              'total gst kitna bana sabka',    expect_in=['GST', 'tax', 'bata'])
test('AGG-12: highest PO advance',             'kitne orders mein advance diya gaya', expect_in=['order', 'mile'])

print()
print('--- SECTION 5: DATE RANGE QUERIES ---')
test('DATE-01: this month orders',             'is month ke purchase orders',   expect_in=['order', 'mile'])
test('DATE-02: last week orders',              'last week ke orders dikhao',    expect_in=['order', 'mile'])
test('DATE-03: this week orders',              'this week ke orders',           expect_in=['order'])
test('DATE-04: last month orders',             'pichle mahine ke orders',       expect_in=['order'])
test('DATE-05: is hafte ke orders',            'is hafte ke orders dikhao',     expect_in=['order'])

print()
print('--- SECTION 6: SPECIFIC ENTITY LOOKUPS ---')
test('ENT-01: PO number exact',                'MHEL/PO/00029/2026-2027 dikhao', expect_in=['MHEL', 'Rishabh'])
test('ENT-02: numeric item ID',                '1',                              expect_in=['stock', 'inventory'])
test('ENT-03: purchase request list',          'purchase request dikhao',        expect_in=['PR', 'purchase'])
test('ENT-04: PR count',                       'kitni purchase requests hain',   expect_in=['purchase request'])
test('ENT-05: city-based supplier Udaipur',    'Udaipur ke suppliers dikhao',    expect_in=['supplier'])
test('ENT-06: Aastha full orders',             'Aastha Engineering ke orders',   expect_in=['Aastha', 'PO'])
test('ENT-07: conveyor belt 700mm specific',   'conveyor belt 700mm ka stock',   expect_in=['Conveyor Belt', 'stock'])
test('ENT-08: oil seal 75x100 specific',       'oil seal 75x100x10 ka stock',    expect_in=['Oil Seal', 'stock'])

print()
print('--- SECTION 7: ROLE-BASED PERMISSIONS ---')
test('ROLE-01: supervisor PO query',           'latest purchase orders',         'supervisor', expect_in=['order', 'mile'])
test('ROLE-02: store admin inventory',         'bearing stock kitna hai',        'store admin', expect_in=['bearing', 'stock'])
test('ROLE-03: HOD balance query',             'total pending balance',          'hod',         expect_in=['balance'])
test('ROLE-04: sales inventory',               'oil seal stock',                 'sales',       expect_in=['oil', 'stock'])

print()
print('--- SECTION 8: ROBUSTNESS / EDGE CASES ---')
test('EDGE-01: single word stock',             'stock',                          expect_in=['inventory', 'item', 'stock', 'ERP', 'database'])
test('EDGE-02: gibberish input',               'xyzqwerty123',                   expect_in=['ERP', 'samajh', 'inventory', 'poochh'])
test('EDGE-03: number only 99999',             '99999',                          expect_in=['inventory', 'stock', 'nahi mila', 'ERP', 'database'])
test('EDGE-04: long natural sentence',         'yaar mujhe batao ki hamare paas jo conveyor belt hai usme jo sabse zyada stock pada hai woh konsa hai store mein', expect_in=['belt', 'stock', 'Conveyor'])
test('EDGE-05: English full sentence',         'Show me all pending purchase orders with their supplier names', expect_in=['order', 'mile', 'supplier', 'Rs'])
test('EDGE-06: very specific Hindi',           'Rajsamand mein konse projects chal rahe hain abhi', expect_in=['Rajsamand', 'project'])

print()
print('='*100)
print(f'FINAL RESULT: {passed} passed, {failed} failed out of {passed+failed}  ({round(passed*100/(passed+failed))}% pass rate)')
print('='*100)
