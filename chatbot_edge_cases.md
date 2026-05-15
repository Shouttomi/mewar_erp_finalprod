# Chatbot Edge Case Test Questions
**Total:** 30 cases | **New focus:** history chains, ambiguous entities, multi-item, date ranges, junk input, aggregation+entity, role edge cases, zero stock

---

## CATEGORY A: History / Follow-up Chains

### TC-H01 — Supplier found → ask different field next turn
**Risk:** Sticky context fails if previous bot message doesn't bold the name correctly.
```json
// Turn 1
{ "query": "DCL ka mobile number batao", "history": [] }

// Turn 2
{
  "query": "aur inka GST?",
  "history": [
    { "role": "user",      "content": "DCL ka mobile number batao" },
    { "role": "assistant", "content": "📞 **DCL Enterprises** ka number **9876XXXXXX** hai." }
  ]
}
```

---

### TC-H02 — Dropdown shown → user picks one by name
**Risk:** Bot returns full list again instead of drilling into the selected supplier.
```json
// Turn 1
{ "query": "Adinath details", "history": [] }

// Turn 2
{
  "query": "Adinath Enterprises wala dikhao",
  "history": [
    { "role": "user",      "content": "Adinath details" },
    { "role": "assistant", "content": "haan mil gaya 👍 5 suppliers mile: **Adinath Automobiles**, **Adinath Enterprises**..." }
  ]
}
```

---

### TC-H03 — 3-turn chain: supplier → orders → balance
**Risk:** By turn 3, sticky extractor may grab "3 orders" bold text instead of "Rishabh International".
```json
// Turn 1
{ "query": "Rishabh International ki details", "history": [] }

// Turn 2
{
  "query": "uske orders dikhao",
  "history": [
    { "role": "user",      "content": "Rishabh International ki details" },
    { "role": "assistant", "content": "ye raha 👍 **Rishabh International** ka profile mil gaya." }
  ]
}

// Turn 3
{
  "query": "inka pending balance kitna hai",
  "history": [
    { "role": "user",      "content": "Rishabh International ki details" },
    { "role": "assistant", "content": "ye raha 👍 **Rishabh International** ka profile." },
    { "role": "user",      "content": "uske orders dikhao" },
    { "role": "assistant", "content": "📄 **3 orders** mile. Pending balance: **₹1,04,076**" }
  ]
}
```

---

### TC-H04 — Topic switch: old entity must NOT bleed into new query
**Risk:** "bearing" is short (≤2 words), follow-up detector fires, sticky pulls "DCL Enterprises" → wrong intent.
```json
// Turn 1
{ "query": "DCL ke orders batao", "history": [] }

// Turn 2 — completely different topic
{
  "query": "bearing ka stock kitna hai",
  "history": [
    { "role": "user",      "content": "DCL ke orders batao" },
    { "role": "assistant", "content": "📄 **2 orders** mile for **DCL Enterprises**." }
  ]
}
```

---

### TC-H05 — "haa" / "yes" follow-up after supplier found
**Risk:** Bot may return generic fallback instead of supplier profile.
```json
{
  "query": "haa",
  "history": [
    { "role": "user",      "content": "Arawali supplier hai?" },
    { "role": "assistant", "content": "Bhai, mujhe **Arawali Minerals** system mein mil gaye hain." }
  ]
}
```

---

### TC-H06 — "aur" continuation — ambiguous follow-up
**Risk:** "aur iske projects?" after a PO result — should not search all projects globally.
```json
{
  "query": "aur iske projects?",
  "history": [
    { "role": "user",      "content": "Arawali Minerals ke orders dikhao" },
    { "role": "assistant", "content": "📄 **1 orders** mile for **Arawali Minerals**." }
  ]
}
```

---

## CATEGORY B: Ambiguous Entity (supplier vs inventory name conflict)

### TC-A01 — "Eastern Bearings" — supplier name or bearing inventory?
**Risk:** "Bearings" keyword keeps intent as `search`, bot searches inventory instead of supplier profile.
```json
{ "query": "Eastern Bearings ka stock kitna hai", "history": [] }
```

---

### TC-A02 — Numeric bearing model vs inventory ID fast-track
**Risk:** "6205" triggers numeric ID fast-track (id=6205), returns wrong item instead of BEARING 6205.
```json
{ "query": "6205 ka stock batao", "history": [] }
```

---

### TC-A03 — Short name that partially matches both supplier and inventory
**Risk:** LLM routes to `search` instead of `supplier_search` for "Ikon".
```json
{ "query": "Ikon ka details batao", "history": [] }
```

---

## CATEGORY C: Multi-item Inventory in One Query

### TC-M01 — Two inventory items
**Risk:** LLM only puts one in `search_target`, second item silently dropped.
```json
{ "query": "oil seal aur v belt dono ka stock batao", "history": [] }
```

---

### TC-M02 — Three inventory items
**Risk:** `specific_items` list has 3 entries; `clean_noise` may strip "bar" or "round" from one.
```json
{ "query": "bearing 6205, oil seal aur round bar ka stock", "history": [] }
```

---

### TC-M03 — Specific model + generic category mixed
**Risk:** Loop must produce both a single-item result AND a dropdown in the same response.
```json
{ "query": "bearing 6308 aur saare oil seal ka stock kitna hai", "history": [] }
```

---

## CATEGORY D: Date Range Queries

### TC-D01 — Current month in Hinglish
**Risk:** LLM returns `null` dates, filter skipped, all orders returned unfiltered.
```json
{ "query": "is mahine ke purchase orders dikhao", "history": [] }
```

---

### TC-D02 — Last week (English)
**Risk:** LLM computes wrong dates or returns null; date format mismatch (MM/DD vs YYYY-MM-DD).
```json
{ "query": "show me purchase orders from last week", "history": [] }
```

---

### TC-D03 — Inventory stock added in a specific month
**Risk:** `from_date`/`to_date` null → `date_cond` skipped → returns all-time stock instead of April stock.
```json
{ "query": "April mein kitna bearing stock aaya tha", "history": [] }
```

---

## CATEGORY E: Off-topic / Junk Input

### TC-E01 — Non-ERP question
**Risk:** LLM routes to `search` with `search_target: "mausam"` → inventory query for "mausam" → bad UX.
```json
{ "query": "bhai aaj ka mausam kaisa hai", "history": [] }
```

---

### TC-E02 — Gibberish
**Risk:** LLM hallucinates an intent rather than returning a graceful fallback.
```json
{ "query": "asdfghjkl qwerty", "history": [] }
```

---

### TC-E03 — Large number not in ID range
**Risk:** Fast-track fires for `id=999999`, returns nothing, then LLM guesses wrong intent on retry.
```json
{ "query": "999999", "history": [] }
```

---

### TC-E04 — Greeting with no ERP intent
**Risk:** Empty `search_target` after noise removal → inventory query runs wide open, random results.
```json
{ "query": "hello bhai kya haal hai", "history": [] }
```

---

## CATEGORY F: Aggregation + Specific Entity (untested combo)

### TC-F01 — Total pending balance for ONE supplier
**Risk:** `_agg_pending_bal` fast-path fires and returns ALL suppliers' balance, ignoring "Arawali".
```json
{ "query": "Arawali ka total pending balance kitna hai", "history": [] }
```

---

### TC-F02 — Specific supplier's biggest PO
**Risk:** Boss Mode 3 fires globally — ignores supplier filter, returns globally biggest PO.
```json
{ "query": "Rishabh International ka sabse bada order kaun sa hai", "history": [] }
```

---

### TC-F03 — Count of POs for one supplier
**Risk:** `_AGG_COUNT` fast-path on "kitne" + "orders" returns total count for ALL suppliers, not DCL.
```json
{ "query": "DCL ke kitne orders hain", "history": [] }
```

---

## CATEGORY G: Case & Format Edge Cases

### TC-G01 — All lowercase supplier name
**Risk:** Regression check — `clean_noise` must not strip "minerals"; LOWER() DB query should handle it.
```json
{ "query": "arawali minerals ka gst number", "history": [] }
```

---

### TC-G02 — ALL CAPS query
**Risk:** LLM reasoning language detection may break; `search_target` extraction may fail on all-caps.
```json
{ "query": "ARAWALI KE ORDERS DIKHAO", "history": [] }
```

---

### TC-G03 — Supplier name with special characters typed verbatim
**Risk:** `clean_noise` strips brackets and comma → cleaned target breaks LIKE match.
```json
{ "query": "Adinath Automobiles , Udaipur (Raj.) ka GST", "history": [] }
```

---

## CATEGORY H: Partial PO Number

### TC-P01 — PO number without year suffix
**Risk:** LIKE `%mhel/po/00020%` should still match even without `/2026-2027` — verify regex captures partial.
```json
{ "query": "MHEL/PO/00020 wala order dikhao", "history": [] }
```

---

### TC-P02 — Just the sequence number
**Risk:** "00025" alone won't match PO regex (needs letter prefix); falls to supplier LIKE → no results.
```json
{ "query": "00025 number ka PO dikhao", "history": [] }
```

---

## CATEGORY I: Supervisor Role Edge Cases

### TC-R01 — Supervisor asks multi-intent with PO
**Risk:** Role block strips `po_search`, keeps `supplier_search` — verify response doesn't crash and shows PO-restricted notice.
```json
{
  "query": "DCL ki details aur orders",
  "history": [],
  "role": "supervisor"
}
```

---

### TC-R02 — Supervisor follow-up triggers PO intent from sticky context
**Risk:** Sticky fires → target=DCL → intents=`["po_search"]` → role block removes all intents → empty intents array → must return "no permission" without crashing.
```json
{
  "query": "uske pending orders?",
  "history": [
    { "role": "user",      "content": "DCL ki details dikhao" },
    { "role": "assistant", "content": "ye raha **DCL Enterprises** ka profile." }
  ],
  "role": "supervisor"
}
```

---

## CATEGORY J: Zero / Negative Stock Edge Cases

### TC-Z01 — Item with zero or negative stock
**Risk:** `SUM()` returns 0 or negative — bot must say "0 units", not "not found".
```json
{ "query": "hydraulic oil ka stock kitna hai", "history": [] }
```

---

### TC-Z02 — Supplier with no inventory transactions (empty items array)
**Risk:** Profile card returns `items: []` — verify frontend and response shape handle empty array without error.
```json
{ "query": "Paroliya Metals ki detail batao", "history": [] }
```

---

## Risk Summary

| Category | Cases | Top failure mode |
|----------|-------|-----------------|
| History / Follow-ups | H01–H06 | Sticky grabs wrong bold text (numbers vs names) |
| Ambiguous entities | A01–A03 | Numeric fast-track hijacks bearing model search |
| Multi-item inventory | M01–M03 | Second/third item silently dropped |
| Date ranges | D01–D03 | LLM returns null dates, filter silently skipped |
| Off-topic / junk | E01–E04 | Greeting → empty target → wide inventory scan |
| Aggregation + entity | F01–F03 | Fast-paths ignore supplier name in query |
| Case / format | G01–G03 | Special chars stripped → LIKE match breaks |
| Partial PO number | P01–P02 | Sequence-only number misses PO regex |
| Role edge cases | R01–R02 | Empty intents after role block → potential crash |
| Zero stock | Z01–Z02 | Zero stock misread as item not found |
