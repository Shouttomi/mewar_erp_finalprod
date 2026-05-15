# Chatbot API Test Log
**Generated:** 2026-04-18 15:46:40  
**Endpoint:** `http://127.0.0.1:8000/chatbot/`  
**Total Tests:** 65  

---

## Summary
| Status | Count |
|--------|-------|
| PASS (auto-check) | 54 |
| FAIL (auto-check) | 0 |
| UNKNOWN (empty DB / unverifiable) | 11 |

---

## [PASS] TC-01 - Latest PO – Arawali (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Show me the latest purchase order for Arawali",
  "history": [],
  "ui_filters": {
    "limit": 1
  }
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00020/2026-2027",
      "supplier": "Arawali Minerals",
      "date": "2026-04-16",
      "total": 1.05,
      "advance": 0.0,
      "balance": 1.05,
      "status": "Completed"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "po_number": "MHEL/PO/00020/2026-2027",
  "total_amount": "1.05",
  "balance_amount": "1.05",
  "status": "Completed",
  "po_date": "2026-04-16",
  "supplier_name": "Arawali Minerals"
}
```

---

## [PASS] TC-02 - Inventory – bearing (Hinglish typo 'beerign')

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "beerign ka kitna stock hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 **Total Bearing Stock:** 48.00 units available hain."
    },
    {
      "type": "dropdown",
      "message": "Select item for details:",
      "items": [
        {
          "id": 2,
          "name": "BEARING 608 ZZ "
        },
        {
          "id": 3,
          "name": "BEARING 2216 "
        },
        {
          "id": 4,
          "name": "BEARING 6014 "
        },
        {
          "id": 5,
          "name": "BEARING 6019 "
        },
        {
          "id": 6,
          "name": "BEARING 6200 "
        },
        {
          "id": 7,
          "name": "BEARING 6201 "
        },
        {
          "id": 8,
          "name": "BEARING 6202 "
        },
        {
          "id": 9,
          "name": "BEARING 6206 "
        },
        {
          "id": 10,
          "name": "BEARING 6205 "
        },
        {
          "id": 11,
          "name": "BEARING 6208 "
        },
        {
          "id": 12,
          "name": "BEARING 6209 "
        },
        {
          "id": 13,
          "name": "BEARING 6210 "
        },
        {
          "id": 14,
          "name": "BEARING 6218 "
        },
        {
          "id": 15,
          "name": "BEARING 6303 "
        },
        {
          "id": 16,
          "name": "BEARING 6305 "
        },
        {
          "id": 17,
          "name": "BEARING 6306 "
        },
        {
          "id": 18,
          "name": "BEARING 6308 "
        },
        {
          "id": 19,
          "name": "BEARING 6309 "
        },
        {
          "id": 20,
          "name": "BEARING 6322 "
        },
        {
          "id": 21,
          "name": "BEARING 6312 "
        },
        {
          "id": 22,
          "name": "BEARING 6320 C3 "
        },
        {
          "id": 23,
          "name": "BEARING 7221 "
        },
        {
          "id": 24,
          "name": "BEARING 6215 "
        },
        {
          "id": 25,
          "name": "BEARING 6301 "
        },
        {
          "id": 26,
          "name": "BEARING 6304 "
        },
        {
          "id": 27,
          "name": "BEARING 6203 "
        },
        {
          "id": 28,
          "name": "BEARING 6212 "
        },
        {
          "id": 29,
          "name": "BEARING 30308 "
        },
        {
          "id": 30,
          "name": "BEARING 32211 "
        },
        {
          "id": 31,
          "name": "BEARING 32021 "
        }
      ]
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "BEARING 608 ZZ",
  "classification": "SEMI_FINISH",
  "placement": "Store MHEL"
}
```

---

## [PASS] TC-03 - Supplier profile – Adinath (Hinglish)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Adinath supplier ki details batao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 Mujhe 5 suppliers mile hain:"
    },
    {
      "type": "dropdown",
      "message": "Select a supplier for details:",
      "items": [
        {
          "id": "Adinath Automobiles , Udaipur (Raj.)",
          "name": "Adinath Automobiles , Udaipur (Raj.)"
        },
        {
          "id": "Adinath Enterprises, Udaipur (Raj.)",
          "name": "Adinath Enterprises, Udaipur (Raj.)"
        },
        {
          "id": "Adinath Equipments Pvt. Ltd.",
          "name": "Adinath Equipments Pvt. Ltd."
        },
        {
          "id": "Adinath Export , Udaipur (Raj.)",
          "name": "Adinath Export , Udaipur (Raj.)"
        },
        {
          "id": "Adinath Petrochemicals, Udaipur (Raj.)",
          "name": "Adinath Petrochemicals, Udaipur (Raj.)"
        }
      ]
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Adinath Automobiles , Udaipur (Raj.)",
  "mobile": "+919928446250"
}
```

---

## [PASS] TC-04 - All pending/draft POs

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "saare pending orders dikhao",
  "history": [],
  "ui_filters": {
    "limit": 5
  }
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **21 orders** mile hain. Inka total pending balance **₹5,683,445.48** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00025/2026-2027",
      "supplier": "Adinath Enterprises, Udaipur (Raj.)",
      "date": "2026-04-18",
      "total": 1062.0,
      "advance": 0.0,
      "balance": 1062.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00024/2026-2027",
      "supplier": "Rishabh International",
      "date": "2026-04-17",
      "total": 104076.0,
      "advance": 0.0,
      "balance": 104076.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00023/2026-2027",
      "supplier": "Trad Industries",
      "date": "2026-04-17",
      "total": 58705.0,
      "advance": 0.0,
      "balance": 58705.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00022/2026-2027",
      "supplier": "Rishabh International",
      "date": "2026-04-16",
      "total": 25311.0,
      "advance": 0.0,
      "balance": 25311.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00021/2026-2027",
      "supplier": "Max Spare Limited, Thane (M.H.)",
      "date": "2026-04-16",
      "total": 56581.0,
      "advance": 0.0,
      "balance": 56581.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00019/2026-2027",
      "supplier": "RVM Enterprises, Faridabad (H.R.)",
      "date": "2026-04-15",
      "total": 44604.0,
      "advance": 0.0,
      "balance": 44604.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00018/2026-2027",
      "supplier": "Mehta Automobiles, Udaipur (Raj.)",
      "date": "2026-04-15",
      "total": 19470.0,
      "advance": 0.0,
      "balance": 19470.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00017/2026-2027",
      "supplier": "Adinath Enterprises, Udaipur (Raj.)",
      "date": "2026-04-15",
      "total": 3540.0,
      "advance": 0.0,
      "balance": 3540.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MTPL/PO/00001/2026-2027",
      "supplier": "Paroliya Metals & Alloys",
      "date": "2026-04-13",
      "total": 122130.0,
      "advance": 0.0,
      "balance": 122130.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00015/2026-2027",
      "supplier": "DCL Enterprises , Faridabad (H.R.)",
      "date": "2026-04-13",
      "total": 17700.0,
      "advance": 0.0,
      "balance": 18500.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00014/2026-2027",
      "supplier": "Unitech Solutions and Services",
      "date": "2026-04-13",
      "total": 230170.8,
      "advance": 0.0,
      "balance": 230170.8,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00013/2026-2027",
      "supplier": "Shree G.K.Steels",
      "date": "2026-04-13",
      "total": 40320.6,
      "advance": 0.0,
      "balance": 40320.6,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00012/2026-2027",
      "supplier": "Ikon rubber",
      "date": "2026-04-11",
      "total": 27562.5,
      "advance": 5000.0,
      "balance": 25562.5,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00011/2026-2027",
      "supplier": "Eastern Bearings Pvt. Ltd.",
      "date": "2026-04-09",
      "total": 10232.58,
      "advance": 0.0,
      "balance": 10232.58,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00007/2026-2027",
      "supplier": "M B Enterprisess , Ajmer (Raj.)",
      "date": "2026-04-06",
      "total": 133723.5,
      "advance": 0.0,
      "balance": 133723.5,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00010/2026-2027",
      "supplier": "Ram Bilas Narinder Kumar",
      "date": "2026-04-04",
      "total": 84075.0,
      "advance": 0.0,
      "balance": 84075.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00009/2026-2027",
      "supplier": "JSR CUTTING & WELDING SOLUTIONS, FARIDABAD (H.R.)",
      "date": "2026-04-04",
      "total": 7434.0,
      "advance": 0.0,
      "balance": 7434.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00008/2026-2027",
      "supplier": "Chhavi Enterprises, Udaipur (Raj.)",
      "date": "2026-04-04",
      "total": 6726.0,
      "advance": 0.0,
      "balance": 6726.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00006/2026-2027",
      "supplier": "Bhilwara Sales Corporation, Bhilwara (Raj.)",
      "date": "2026-04-03",
      "total": 38409.0,
      "advance": 0.0,
      "balance": 38409.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00005/2026-2027",
      "supplier": "Shreya Seals",
      "date": "2026-04-01",
      "total": 16962.5,
      "advance": 16962.5,
      "balance": 0.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00004/2025-2026",
      "supplier": "Aastha Engineering, Faridabad (G.J.)",
      "date": "2026-03-14",
      "total": 4652812.5,
      "advance": 0.0,
      "balance": 4652812.5,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00025/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00023/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00024/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00021/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00022/2026-2027",
    "status": "Draft"
  }
]
```

---

## [PASS] TC-05 - Boss Mode – Highest pending balance

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "sabse jyada balance kiska hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "💸 **Payment Alert:** Sabse zyada pending balance **Aastha Engineering, Faridabad (G.J.)** ka hai.\n\n💰 Total Pending: **₹4,652,812.50**\n📄 Orders: **1 pending**\n📞 Contact: +919953563097"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Aastha Engineering, Faridabad (G.J.)",
  "total_bal": "4652812.50",
  "mobile": "+919953563097"
}
```

---

## [PASS] TC-06 - Boss Mode – Lowest pending balance

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "sabse kam balance kiska pending hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "💸 **Payment Alert:** Sabse kam pending balance **Adinath Enterprises, Udaipur (Raj.)** ka hai.\n\n💰 Total Pending: **₹4,602.00**\n📄 Orders: **2 pending**\n📞 Contact: +919829450941"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Adinath Enterprises, Udaipur (Raj.)",
  "total_bal": "4602.00"
}
```

---

## [PASS] TC-07 - Boss Mode – Highest PO

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "sabse bada po kaun sa hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "🏆 **Highest Order:** Poore system mein sabse bada Purchase Order **Aastha Engineering, Faridabad (G.J.)** ka hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00004/2025-2026",
      "supplier": "Aastha Engineering, Faridabad (G.J.)",
      "date": "2026-03-14",
      "total": 4652812.5,
      "advance": 0.0,
      "balance": 4652812.5,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "po_number": "MHEL/PO/00004/2025-2026",
  "supplier_name": "Aastha Engineering, Faridabad (G.J.)",
  "total_amount": "4652812.50"
}
```

---

## [PASS] TC-08 - Boss Mode – Lowest PO

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "sabse chhota purchase order dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📉 **Lowest Order:** Poore system mein sabse chhota Purchase Order **Arawali Minerals** ka hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00020/2026-2027",
      "supplier": "Arawali Minerals",
      "date": "2026-04-16",
      "total": 1.05,
      "advance": 0.0,
      "balance": 1.05,
      "status": "Completed"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "po_number": "MHEL/PO/00020/2026-2027",
  "supplier_name": "Arawali Minerals",
  "total_amount": "1.05"
}
```

---

## [PASS] TC-09 - Boss Mode – Total GST

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "total gst kitna bana hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "🧾 **Tax (GST) Report:**\n\n**Total Gst Kitna Bana Hai** ke **23 orders** par total **₹378,791.85** ka Tax/GST bana hai."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "total_tax": "378791.85",
  "po_count": 23
}
```

---

## [UNKNOWN] TC-10 - Project search – running projects

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "konse projects chal rahe hain abhi",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "lagta hai 'konse projects chal rahe hain abhi' wala koi project abhi nahi chal raha. 🧐"
    }
  ]
}
```

### DB Ground Truth
```json
[]
```

---

## [PASS] TC-11 - Aggregation – count suppliers

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "system mein kitne suppliers hain",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "👥 Hamare system mein total **6091 suppliers** registered hain."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "total": 6091
}
```

---

## [PASS] TC-12 - Aggregation – lowest stock item

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "sabse kam stock wala item kaun sa hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📉 Sabse kam stock wala item **Test Inventory** hai — sirf **0.00 units** bache hain. (Location: Main Gate)"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "Test Inventory",
  "placement": "Main Gate",
  "stock": "0.00"
}
```

---

## [PASS] TC-13 - Supplier – mobile query (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "What is the contact number of Adinath?",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 Mujhe 5 suppliers mile hain:"
    },
    {
      "type": "dropdown",
      "message": "Select a supplier for details:",
      "items": [
        {
          "id": "Adinath Automobiles , Udaipur (Raj.)",
          "name": "Adinath Automobiles , Udaipur (Raj.)"
        },
        {
          "id": "Adinath Enterprises, Udaipur (Raj.)",
          "name": "Adinath Enterprises, Udaipur (Raj.)"
        },
        {
          "id": "Adinath Equipments Pvt. Ltd.",
          "name": "Adinath Equipments Pvt. Ltd."
        },
        {
          "id": "Adinath Export , Udaipur (Raj.)",
          "name": "Adinath Export , Udaipur (Raj.)"
        },
        {
          "id": "Adinath Petrochemicals, Udaipur (Raj.)",
          "name": "Adinath Petrochemicals, Udaipur (Raj.)"
        }
      ]
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Adinath Automobiles , Udaipur (Raj.)",
  "mobile": "+919928446250"
}
```

---

## [UNKNOWN] TC-14 - Inventory – fast-track numeric ID

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "1",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "Bhai, ye item mere system mein nahi mila. 🧐 Thoda spelling check karoge?"
    }
  ]
}
```

### DB Ground Truth
```json
null
```

---

## [PASS] TC-15 - Multi-intent – Arawali profile + last 3 orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Show me Arawali's profile and their last 3 orders",
  "history": [],
  "ui_filters": {
    "limit": 3
  }
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **2 orders** mile hain."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00020/2026-2027",
      "supplier": "Arawali Minerals",
      "date": "2026-04-16",
      "total": 1.05,
      "advance": 0.0,
      "balance": 1.05,
      "status": "Completed"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00001/2025-2026",
      "supplier": "Arawali Minerals",
      "date": "2026-03-13",
      "total": 1610.5,
      "advance": 500.0,
      "balance": 1110.5,
      "status": "Completed"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier": {
    "supplier_name": "Arawali Minerals",
    "mobile": "09610092299"
  },
  "orders": [
    {
      "po_number": "MHEL/PO/00020/2026-2027",
      "total_amount": "1.05",
      "status": "Completed"
    },
    {
      "po_number": "MHEL/PO/00001/2025-2026",
      "total_amount": "1610.50",
      "status": "Completed"
    }
  ]
}
```

---

## [UNKNOWN] TC-16 - Inventory – V belt stock (Hinglish)

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "v belt ka stock kitna hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "Bhai, mujhe **V Belt** system mein mil gaye hain."
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **V Belt** ka profile mil gaya hai:"
    },
    {
      "type": "result",
      "supplier": {
        "id": 6524,
        "name": "V Belt",
        "code": "5843",
        "mobile": "N/A",
        "city": "N/A",
        "email": "N/A",
        "gstin": "N/A"
      },
      "items": []
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "V Belt B-74"
}
```

---

## [PASS] TC-17 - Inventory – oil seal stock

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "oil seal kitna pada hai godown mein",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 **Total Oil Seal Stock:** 184.00 units available hain."
    },
    {
      "type": "dropdown",
      "message": "Select item for details:",
      "items": [
        {
          "id": 227,
          "name": "OIL SEAL 58x70x10 "
        },
        {
          "id": 228,
          "name": "OIL SEAL 95x115x13 "
        },
        {
          "id": 229,
          "name": "OIL SEAL 80x100x10 "
        },
        {
          "id": 230,
          "name": "OIL SEAL 120x160x13 "
        },
        {
          "id": 231,
          "name": "OIL SEAL 260X300X15 "
        },
        {
          "id": 232,
          "name": "OIL SEAL 200X230X15 "
        },
        {
          "id": 233,
          "name": "OIL SEAL 120X140X13 "
        },
        {
          "id": 234,
          "name": "OIL SEAL 115X150X12 "
        },
        {
          "id": 235,
          "name": "OIL SEAL 120X150X13 "
        },
        {
          "id": 236,
          "name": "OIL SEAL 120X160x12 "
        },
        {
          "id": 237,
          "name": "OIL SEAL 140X160X13 "
        },
        {
          "id": 238,
          "name": "OIL SEAL 110X135X13 "
        },
        {
          "id": 239,
          "name": "OIL SEAL 180X210X13 "
        },
        {
          "id": 240,
          "name": "OIL SEAL 180X210X15 "
        },
        {
          "id": 241,
          "name": "OIL SEAL 110X130X13 "
        },
        {
          "id": 242,
          "name": "OIL SEAL 115X140X13 "
        },
        {
          "id": 243,
          "name": "OIL SEAL 80X110X10 "
        },
        {
          "id": 244,
          "name": "OIL SEAL 48X70X10 "
        },
        {
          "id": 245,
          "name": "OIL SEAL 50X70X10 "
        },
        {
          "id": 246,
          "name": "OIL SEAL 40X60X10 "
        },
        {
          "id": 247,
          "name": "OIL SEAL 82x105x10 "
        },
        {
          "id": 248,
          "name": "OIL SEAL 110X140X13 "
        },
        {
          "id": 249,
          "name": "OIL SEAL 125X160X13 "
        },
        {
          "id": 250,
          "name": "OIL SEAL 120X160X13 "
        },
        {
          "id": 251,
          "name": "OIL SEAL 108X130X13 "
        },
        {
          "id": 252,
          "name": "OIL SEAL 60X80X10 "
        },
        {
          "id": 253,
          "name": "OIL SEAL 30X45X10 "
        },
        {
          "id": 254,
          "name": "OIL SEAL 55X90X10 "
        },
        {
          "id": 255,
          "name": "OIL SEAL 85X105X13 "
        },
        {
          "id": 256,
          "name": "OIL SEAL 100x130x13 "
        }
      ]
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "OIL SEAL 58x70x10"
}
```

---

## [PASS] TC-18 - Inventory – round bar (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "How much round bar is in stock?",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 **Total Round Bar Stock:** 1.00 units available hain."
    },
    {
      "type": "dropdown",
      "message": "Select item for details:",
      "items": [
        {
          "id": 978,
          "name": "Round Bar EN-24 All Size "
        },
        {
          "id": 1092,
          "name": "Round Bar 25mm "
        },
        {
          "id": 1093,
          "name": "Round Bar 30mm "
        },
        {
          "id": 1094,
          "name": "Round Bar 40mm "
        },
        {
          "id": 1095,
          "name": "Round Bar 50mm "
        },
        {
          "id": 1096,
          "name": "Round Bar 60mm "
        },
        {
          "id": 1097,
          "name": "Round Bar 65mm "
        },
        {
          "id": 1098,
          "name": "Round Bar 70mm "
        },
        {
          "id": 1159,
          "name": "Round Bar EN-8 25mm"
        },
        {
          "id": 1160,
          "name": "Round Bar EN-8 40mm"
        },
        {
          "id": 1161,
          "name": "Round Bar EN-8 50mm"
        },
        {
          "id": 1214,
          "name": "Round Bar EN-24 350x2320"
        },
        {
          "id": 1384,
          "name": "Main Shaft Round bar en24 forged "
        },
        {
          "id": 1414,
          "name": "Round Bar EN-8 OD:32mm"
        },
        {
          "id": 1415,
          "name": "Round Bar EN-8 OD:40mm"
        },
        {
          "id": 1416,
          "name": "Round Bar EN-8 45mm"
        },
        {
          "id": 1417,
          "name": "Round Bar EN-8 OD:50mm"
        },
        {
          "id": 1418,
          "name": "Round Bar EN-8 OD:56mm"
        },
        {
          "id": 1419,
          "name": "Round Bar EN-8 OD:63mm"
        },
        {
          "id": 1420,
          "name": "Round Bar EN-8 OD:70mm"
        },
        {
          "id": 1436,
          "name": "Round Bar 50mm"
        },
        {
          "id": 1474,
          "name": "Round Bar EN-8 120x1730"
        },
        {
          "id": 1475,
          "name": "Round Bar EN-8 140x1800"
        },
        {
          "id": 1510,
          "name": "Round Bar EN-9 315x2350mm"
        },
        {
          "id": 1532,
          "name": "En-8 Round Bar 2026"
        }
      ]
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "Round Bar EN-24 All Size"
}
```

---

## [PASS] TC-19 - Inventory – bearing 6205 specific

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "bearing 6205 ka stock dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **BEARING 6205** ka data mil gaya:"
    },
    {
      "type": "result",
      "inventory": {
        "id": 10,
        "name": "BEARING 6205 ",
        "category": "Raw Material",
        "placement": "Store MHEL"
      },
      "total_stock": 0.0,
      "finish_stock": 0.0,
      "semi_finish_stock": 0,
      "machining_stock": 0
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "BEARING 6205",
  "classification": ""
}
```

---

## [PASS] TC-20 - Inventory – chain stock

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "chain ka kitna maal hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **Steel Chain** ka data mil gaya:"
    },
    {
      "type": "result",
      "inventory": {
        "id": 1496,
        "name": "Steel Chain 8mm",
        "category": "Raw Material",
        "placement": "Store MHEL"
      },
      "total_stock": 0.0,
      "finish_stock": 0.0,
      "semi_finish_stock": 0,
      "machining_stock": 0
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "Steel Chain"
}
```

---

## [UNKNOWN] TC-21 - Inventory – hydraulic oil

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "hydraulic oil stock check karo",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 **Total Hydraulic Cylinder Stock:** 0.00 units available hain."
    },
    {
      "type": "dropdown",
      "message": "Select item for details:",
      "items": [
        {
          "id": 1100,
          "name": "Hydraulic Cylinder 275mm Stroke "
        },
        {
          "id": 1423,
          "name": "Hydraulic Cylinder OD:220"
        }
      ]
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "Hydraulics Block MB9 X D6K X 3/8''  (Manyfold) "
}
```

---

## [UNKNOWN] TC-22 - Inventory – welding electrode

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "welding electrode kitne hain",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "Bhai, mujhe **Mig Welding Machines** system mein mil gaye hain."
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **Mig Welding Machines** ka profile mil gaya hai:"
    },
    {
      "type": "result",
      "supplier": {
        "id": 3400,
        "name": "Mig Welding Machines",
        "code": "2719",
        "mobile": "N/A",
        "city": "N/A",
        "email": "N/A",
        "gstin": "N/A"
      },
      "items": []
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "Welding Rod 10 No."
}
```

---

## [UNKNOWN] TC-23 - Inventory – hex nut

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "hex nut ka stock batao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **HT Nut** ka data mil gaya:"
    },
    {
      "type": "result",
      "inventory": {
        "id": 1528,
        "name": "HT Nut 20mm",
        "category": "Raw Material",
        "placement": "Store MHEL"
      },
      "total_stock": 0.0,
      "finish_stock": 0.0,
      "semi_finish_stock": 0,
      "machining_stock": 0
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "CHECK NUT KM 10"
}
```

---

## [PASS] TC-24 - Inventory – bearing 6308 specific

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "bearing 6308 ka stock",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **BEARING 6308** ka data mil gaya:"
    },
    {
      "type": "result",
      "inventory": {
        "id": 18,
        "name": "BEARING 6308 ",
        "category": "Raw Material",
        "placement": "Store MHEL"
      },
      "total_stock": 0.0,
      "finish_stock": 0.0,
      "semi_finish_stock": 0,
      "machining_stock": 0
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "BEARING 6308",
  "classification": "",
  "placement": "Store MHEL"
}
```

---

## [PASS] TC-25 - Inventory – highest stock item (aggregation)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "sabse zyada stock wala item kaun sa hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📈 Sabse zyada stock wala item **HR Plate 10mm 1500x6300mm= 1 Nos** hai — **9850.00 units** available hain. (Location: 2 Unit CNC M/C Ke Pass)"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "HR Plate 10mm 1500x6300mm= 1 Nos",
  "stock": "9850.00"
}
```

---

## [PASS] TC-26 - Supplier – DCL details (Hinglish)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "DCL Enterprises ki details batao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **DCL Enterprises , Faridabad (H.R.)** ka profile mil gaya hai:"
    },
    {
      "type": "result",
      "supplier": {
        "id": 1513,
        "name": "DCL Enterprises , Faridabad (H.R.)",
        "code": "832",
        "mobile": "+919891397350",
        "city": "N/A",
        "email": "dclent1970@gmail.com",
        "gstin": "06AGNPD6771C1ZH"
      },
      "items": []
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "DCL Enterprises , Faridabad (H.R.)",
  "mobile": "+919891397350",
  "city": ""
}
```

---

## [PASS] TC-27 - Supplier – Rishabh International GST

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Rishabh International ka GST number kya hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📞 **Rishabh International** ka contact: **+919829706543**  \n🏢 GST: **08AAEFR8162L1ZP**"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Rishabh International",
  "gstin": "08AAEFR8162L1ZP"
}
```

---

## [PASS] TC-28 - Supplier – Ikon rubber mobile

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Ikon rubber ka mobile number",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📞 **Ikon rubber** ka contact number **8179327753** hai."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Ikon rubber",
  "mobile": "8179327753"
}
```

---

## [PASS] TC-29 - Supplier – Eastern Bearings profile (city fallback)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Eastern Bearings kahan se hain",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "Bhai, mujhe **Eastern Bearings Pvt. Ltd.** system mein mil gaye hain."
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **Eastern Bearings Pvt. Ltd.** ka profile mil gaya hai:"
    },
    {
      "type": "result",
      "supplier": {
        "id": 1665,
        "name": "Eastern Bearings Pvt. Ltd.",
        "code": "984",
        "mobile": "09991111843",
        "city": "N/A",
        "email": "arb@easternbearings.in",
        "gstin": "06AABCE1150B1ZI"
      },
      "items": []
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Eastern Bearings Pvt. Ltd.",
  "mobile": "09991111843",
  "gstin": "06AABCE1150B1ZI"
}
```

---

## [PASS] TC-30 - Supplier – Shreya Seals profile

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Shreya Seals supplier details dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **Shreya Seals** ka profile mil gaya hai:"
    },
    {
      "type": "result",
      "supplier": {
        "id": 6870,
        "name": "Shreya Seals",
        "code": "6189",
        "mobile": "9684707477",
        "city": "Pune",
        "email": "shriyaseals@gmail.com",
        "gstin": "27ADOFS2497N1Z2"
      },
      "items": []
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Shreya Seals",
  "gstin": "27ADOFS2497N1Z2"
}
```

---

## [PASS] TC-31 - Supplier – Ram Bilas contact (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "What is the contact number of Ram Bilas?",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📞 **Ram Bilas Narinder Kumar** ka contact number **+9198116312849810101284** hai."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Ram Bilas Narinder Kumar",
  "mobile": "+9198116312849810101284"
}
```

---

## [UNKNOWN] TC-32 - Supplier – Trad Industries info

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "Trad Industries ka profile batao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **Trad Industries** ka profile mil gaya hai:"
    },
    {
      "type": "result",
      "supplier": {
        "id": 6322,
        "name": "Trad Industries",
        "code": "5641",
        "mobile": "+919829054313",
        "city": "N/A",
        "email": "mogra.dilip@gmail.com",
        "gstin": "08ABFPM0798R1ZS"
      },
      "items": []
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Aagaaz Wold Trade Pvt Ltd",
  "mobile": ""
}
```

---

## [PASS] TC-33 - Supplier – Mehta Automobiles details

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Mehta Automobiles supplier details",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📞 **Mehta Automobiles, Udaipur (Raj.)** ka contact number **N/A** hai."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Mehta Automobiles, Udaipur (Raj.)",
  "gstin": "08ABRPM5006A1ZW"
}
```

---

## [PASS] TC-34 - Supplier – Paroliya Metals GST (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "What is the GST number of Paroliya Metals?",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📞 **Paroliya Metals & Alloys** ka contact: **+919460870144**  \n🏢 GST: **N/A**"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Paroliya Metals & Alloys",
  "gstin": ""
}
```

---

## [UNKNOWN] TC-35 - Supplier – all suppliers list

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "saare suppliers ki list dikhao",
  "history": [],
  "ui_filters": {
    "limit": 5
  }
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 Mujhe 5 suppliers mile hain:"
    },
    {
      "type": "dropdown",
      "message": "Select a supplier for details:",
      "items": [
        {
          "id": "Annapurna Suppliers-Balangir (Odisha)",
          "name": "Annapurna Suppliers-Balangir (Odisha)"
        },
        {
          "id": "Attri Industrial Suppliers",
          "name": "Attri Industrial Suppliers"
        },
        {
          "id": "Bhagya Shree Cement Suppliers",
          "name": "Bhagya Shree Cement Suppliers"
        },
        {
          "id": "Friends Suppliers Co.",
          "name": "Friends Suppliers Co."
        },
        {
          "id": "GANESH SAND SUPPLIERS (Co Neeta Munji)",
          "name": "GANESH SAND SUPPLIERS (Co Neeta Munji)"
        }
      ]
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "supplier_name": "Ikon rubber"
  },
  {
    "supplier_name": "Shreya Seals"
  },
  {
    "supplier_name": "Z & Z Infrastructure, Ratlam (M.P.)"
  },
  {
    "supplier_name": "Zoho Technologies Private Limited"
  },
  {
    "supplier_name": "Ziya Engineers"
  }
]
```

---

## [PASS] TC-36 - PO – Rishabh International orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Rishabh International ke orders dikhao",
  "history": [],
  "ui_filters": {
    "limit": 5
  }
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **2 orders** mile hain. Inka total pending balance **₹129,387.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00024/2026-2027",
      "supplier": "Rishabh International",
      "date": "2026-04-17",
      "total": 104076.0,
      "advance": 0.0,
      "balance": 104076.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00022/2026-2027",
      "supplier": "Rishabh International",
      "date": "2026-04-16",
      "total": 25311.0,
      "advance": 0.0,
      "balance": 25311.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00024/2026-2027",
    "total_amount": "104076.00",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00022/2026-2027",
    "total_amount": "25311.00",
    "status": "Draft"
  }
]
```

---

## [PASS] TC-37 - PO – last 5 orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "last 5 orders dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **5 orders** mile hain. Inka total pending balance **₹245,735.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00025/2026-2027",
      "supplier": "Adinath Enterprises, Udaipur (Raj.)",
      "date": "2026-04-18",
      "total": 1062.0,
      "advance": 0.0,
      "balance": 1062.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00024/2026-2027",
      "supplier": "Rishabh International",
      "date": "2026-04-17",
      "total": 104076.0,
      "advance": 0.0,
      "balance": 104076.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00023/2026-2027",
      "supplier": "Trad Industries",
      "date": "2026-04-17",
      "total": 58705.0,
      "advance": 0.0,
      "balance": 58705.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00022/2026-2027",
      "supplier": "Rishabh International",
      "date": "2026-04-16",
      "total": 25311.0,
      "advance": 0.0,
      "balance": 25311.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00021/2026-2027",
      "supplier": "Max Spare Limited, Thane (M.H.)",
      "date": "2026-04-16",
      "total": 56581.0,
      "advance": 0.0,
      "balance": 56581.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00025/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00024/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00023/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00022/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00021/2026-2027",
    "status": "Draft"
  }
]
```

---

## [PASS] TC-38 - PO – DCL Enterprises orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "DCL ke orders",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹18,500.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00015/2026-2027",
      "supplier": "DCL Enterprises , Faridabad (H.R.)",
      "date": "2026-04-13",
      "total": 17700.0,
      "advance": 0.0,
      "balance": 18500.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00015/2026-2027",
    "status": "Draft"
  }
]
```

---

## [PASS] TC-39 - PO – search by PO number

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "MHEL/PO/00022/2026-2027 dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹25,311.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00022/2026-2027",
      "supplier": "Rishabh International",
      "date": "2026-04-16",
      "total": 25311.0,
      "advance": 0.0,
      "balance": 25311.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "po_number": "MHEL/PO/00022/2026-2027",
  "total_amount": "25311.00",
  "status": "Draft"
}
```

---

## [PASS] TC-40 - PO – Max Spare pending orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Max Spare ke pending orders",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹56,581.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00021/2026-2027",
      "supplier": "Max Spare Limited, Thane (M.H.)",
      "date": "2026-04-16",
      "total": 56581.0,
      "advance": 0.0,
      "balance": 56581.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00021/2026-2027",
    "status": "Draft",
    "balance_amount": "56581.00"
  }
]
```

---

## [PASS] TC-41 - PO – RVM Enterprises orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "RVM Enterprises ke orders batao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹44,604.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00019/2026-2027",
      "supplier": "RVM Enterprises, Faridabad (H.R.)",
      "date": "2026-04-15",
      "total": 44604.0,
      "advance": 0.0,
      "balance": 44604.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00019/2026-2027",
    "total_amount": "44604.00"
  }
]
```

---

## [PASS] TC-42 - PO – Ikon rubber orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Ikon rubber ke orders dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹25,562.50** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00012/2026-2027",
      "supplier": "Ikon rubber",
      "date": "2026-04-11",
      "total": 27562.5,
      "advance": 5000.0,
      "balance": 25562.5,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00012/2026-2027",
    "total_amount": "27562.50"
  }
]
```

---

## [PASS] TC-43 - PO – Unitech Solutions orders (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Show orders for Unitech Solutions",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹230,170.80** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00014/2026-2027",
      "supplier": "Unitech Solutions and Services",
      "date": "2026-04-13",
      "total": 230170.8,
      "advance": 0.0,
      "balance": 230170.8,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00014/2026-2027",
    "total_amount": "230170.80"
  }
]
```

---

## [PASS] TC-44 - PO – balance pending total (Hinglish)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "total pending balance kitna hai sabka",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "💰 **Total Pending Balance (Sabka):**\n\n📊 Total Outstanding: **₹5,684,557.03**\n📄 Orders with balance: **22**\n🟡 Draft/Pending amount: **₹5,683,445.48**"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "total_bal": "5684557.03"
}
```

---

## [PASS] TC-45 - PO – Adinath Enterprises orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Adinath Enterprises ke saare orders",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **2 orders** mile hain. Inka total pending balance **₹4,602.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00025/2026-2027",
      "supplier": "Adinath Enterprises, Udaipur (Raj.)",
      "date": "2026-04-18",
      "total": 1062.0,
      "advance": 0.0,
      "balance": 1062.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00017/2026-2027",
      "supplier": "Adinath Enterprises, Udaipur (Raj.)",
      "date": "2026-04-15",
      "total": 3540.0,
      "advance": 0.0,
      "balance": 3540.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00025/2026-2027",
    "status": "Draft"
  },
  {
    "po_number": "MHEL/PO/00017/2026-2027",
    "status": "Draft"
  }
]
```

---

## [UNKNOWN] TC-46 - Project – completed projects

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "completed projects dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 Mujhe **5 projects** mile hain:"
    },
    {
      "type": "project",
      "project_name": "Madhav Minetech, Kachchh",
      "category": "Refurbished | New",
      "amount": 13.0,
      "start_date": "2026-04-14",
      "end_date": "2026-04-22",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Uday Mines, Dewas",
      "category": "New Machine | New",
      "amount": 42.0,
      "start_date": "2026-04-06",
      "end_date": "2026-05-06",
      "comments": "With Structure",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Sidhi Vinayak Microns, Rajsamand",
      "category": "New Machine | New",
      "amount": 7.0,
      "start_date": "2026-04-04",
      "end_date": "2026-05-04",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Durgesh Crushing Plant, Savina",
      "category": "New Machine | New",
      "amount": 18.0,
      "start_date": "2026-03-31",
      "end_date": "2026-04-30",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Shree Mahadev Stone Crusher, Raniwara",
      "category": "New Machine | New",
      "amount": 155.0,
      "start_date": "2026-01-31",
      "end_date": "2026-03-31",
      "comments": "1. Vibro Feeder with Vibro Motor 1000 mm x 3000 mm- 1 Nos\r\n2. Vibro Pan Feeder with Vibro Motor 800 mmx2000 mm- 1 Nos\r\n3. Cone Crusher KCC 200- 1 Nos\r\n4. Vibrating Screen with doom chut and pillar 20x06 (41⁄2 Deck) Platemesh- 1 Nos\r\n5. Main Conveyor Belt Size 800 mm, MC 1 - 6 Mtr, MC 2 - 15 Mtr, MC 3- 18 Mtr, MC 4- 18 mtr\r\n6. Reverse Forwar Conveyor Belt Size 800 mm, RFC – 7.5 Mtr\r\n7. GSB Conveyor Belt Size 800 mm, GSBC - 18 Mtr\r\n8. Return Conveyor Belt Size 650 mm, RC 1 - 24 Mtr\r\n9. Product Conveyor Belt Size 500 mm, PC 1 - 15 Mtr, PC 2 - 15 Mtr, PC 3 - 15 Mtr, PC 4 - 15 Mtr, PC 5 - 15 Mtr\r\n10. Motor 327.5 HP For Complete Unit Make – ABB / Siemens / Equivalent (1440 RPM)\r\n11. Control Panel Board For Complete Unit - (Standard Make)\r\n12. Cable & Wiring ( RR Kable / Polycab / Equivalent)\r\n13. Metal Detector- 1 Nos\r\n14. Secondary Hopper - 1 Set\r\n15. Cone Crusher Structure- 1 Set\r\n16. Miscellaneous / Fabricated Items- V belt & Pulley, Vibrating Screen Walk Way with Railing, All Motor Stand, Primary\r\nCrusher Maintenance Platform, Wooden Sleeper, Feed, Transfer & Discharge Chutes, Foundation Nut & Bolts for entire\r\nunit, Foundation Templates.\r\n17. Erection & commissioning\r\nPrimary Hopper: यह पार्टी का रहेगा, लेकिन इसमें जो भी Repairing work होगा या कोई Extra item लगाने होंगे, वह मेवाड़ हाईटेक द्वारा\r\nकिया जाएगा।\r\n36x24 DTO & 75 HP Motor: यह पार्टी द्वारा उपलब्ध कराई जाएगी। इसके अलावा केबल, पैनल और बोल्ट आदि मेवाड़ हाईटेक देगी और\r\nइसकी पूरी फिटिंग का काम भी कंपनी का होगा।",
      "stage": "0%",
      "priority": "NORMAL"
    }
  ]
}
```

### DB Ground Truth
```json
[]
```

---

## [UNKNOWN] TC-47 - Project – high priority

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "high priority projects kaun se hain",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "lagta hai 'projects hain' wala koi project abhi nahi chal raha. 🧐"
    }
  ]
}
```

### DB Ground Truth
```json
[]
```

---

## [PASS] TC-48 - Project – refurbished projects

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "refurbished projects dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 Mujhe **5 projects** mile hain:"
    },
    {
      "type": "project",
      "project_name": "Madhav Minetech, Kachchh",
      "category": "Refurbished | New",
      "amount": 13.0,
      "start_date": "2026-04-14",
      "end_date": "2026-04-22",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Uday Mines, Dewas",
      "category": "New Machine | New",
      "amount": 42.0,
      "start_date": "2026-04-06",
      "end_date": "2026-05-06",
      "comments": "With Structure",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Sidhi Vinayak Microns, Rajsamand",
      "category": "New Machine | New",
      "amount": 7.0,
      "start_date": "2026-04-04",
      "end_date": "2026-05-04",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Durgesh Crushing Plant, Savina",
      "category": "New Machine | New",
      "amount": 18.0,
      "start_date": "2026-03-31",
      "end_date": "2026-04-30",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Shree Mahadev Stone Crusher, Raniwara",
      "category": "New Machine | New",
      "amount": 155.0,
      "start_date": "2026-01-31",
      "end_date": "2026-03-31",
      "comments": "1. Vibro Feeder with Vibro Motor 1000 mm x 3000 mm- 1 Nos\r\n2. Vibro Pan Feeder with Vibro Motor 800 mmx2000 mm- 1 Nos\r\n3. Cone Crusher KCC 200- 1 Nos\r\n4. Vibrating Screen with doom chut and pillar 20x06 (41⁄2 Deck) Platemesh- 1 Nos\r\n5. Main Conveyor Belt Size 800 mm, MC 1 - 6 Mtr, MC 2 - 15 Mtr, MC 3- 18 Mtr, MC 4- 18 mtr\r\n6. Reverse Forwar Conveyor Belt Size 800 mm, RFC – 7.5 Mtr\r\n7. GSB Conveyor Belt Size 800 mm, GSBC - 18 Mtr\r\n8. Return Conveyor Belt Size 650 mm, RC 1 - 24 Mtr\r\n9. Product Conveyor Belt Size 500 mm, PC 1 - 15 Mtr, PC 2 - 15 Mtr, PC 3 - 15 Mtr, PC 4 - 15 Mtr, PC 5 - 15 Mtr\r\n10. Motor 327.5 HP For Complete Unit Make – ABB / Siemens / Equivalent (1440 RPM)\r\n11. Control Panel Board For Complete Unit - (Standard Make)\r\n12. Cable & Wiring ( RR Kable / Polycab / Equivalent)\r\n13. Metal Detector- 1 Nos\r\n14. Secondary Hopper - 1 Set\r\n15. Cone Crusher Structure- 1 Set\r\n16. Miscellaneous / Fabricated Items- V belt & Pulley, Vibrating Screen Walk Way with Railing, All Motor Stand, Primary\r\nCrusher Maintenance Platform, Wooden Sleeper, Feed, Transfer & Discharge Chutes, Foundation Nut & Bolts for entire\r\nunit, Foundation Templates.\r\n17. Erection & commissioning\r\nPrimary Hopper: यह पार्टी का रहेगा, लेकिन इसमें जो भी Repairing work होगा या कोई Extra item लगाने होंगे, वह मेवाड़ हाईटेक द्वारा\r\nकिया जाएगा।\r\n36x24 DTO & 75 HP Motor: यह पार्टी द्वारा उपलब्ध कराई जाएगी। इसके अलावा केबल, पैनल और बोल्ट आदि मेवाड़ हाईटेक देगी और\r\nइसकी पूरी फिटिंग का काम भी कंपनी का होगा।",
      "stage": "0%",
      "priority": "NORMAL"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "name": "Jay Bajrang Stone, Indore",
    "status": "new"
  },
  {
    "name": "Maxstone Global India LLP, Asind",
    "status": "new"
  },
  {
    "name": "Madhav Minetech, Kachchh",
    "status": "new"
  }
]
```

---

## [PASS] TC-49 - Project – latest project

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "latest project batao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 Mujhe **5 projects** mile hain:"
    },
    {
      "type": "project",
      "project_name": "Madhav Minetech, Kachchh",
      "category": "Refurbished | New",
      "amount": 13.0,
      "start_date": "2026-04-14",
      "end_date": "2026-04-22",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Uday Mines, Dewas",
      "category": "New Machine | New",
      "amount": 42.0,
      "start_date": "2026-04-06",
      "end_date": "2026-05-06",
      "comments": "With Structure",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Sidhi Vinayak Microns, Rajsamand",
      "category": "New Machine | New",
      "amount": 7.0,
      "start_date": "2026-04-04",
      "end_date": "2026-05-04",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Durgesh Crushing Plant, Savina",
      "category": "New Machine | New",
      "amount": 18.0,
      "start_date": "2026-03-31",
      "end_date": "2026-04-30",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Shree Mahadev Stone Crusher, Raniwara",
      "category": "New Machine | New",
      "amount": 155.0,
      "start_date": "2026-01-31",
      "end_date": "2026-03-31",
      "comments": "1. Vibro Feeder with Vibro Motor 1000 mm x 3000 mm- 1 Nos\r\n2. Vibro Pan Feeder with Vibro Motor 800 mmx2000 mm- 1 Nos\r\n3. Cone Crusher KCC 200- 1 Nos\r\n4. Vibrating Screen with doom chut and pillar 20x06 (41⁄2 Deck) Platemesh- 1 Nos\r\n5. Main Conveyor Belt Size 800 mm, MC 1 - 6 Mtr, MC 2 - 15 Mtr, MC 3- 18 Mtr, MC 4- 18 mtr\r\n6. Reverse Forwar Conveyor Belt Size 800 mm, RFC – 7.5 Mtr\r\n7. GSB Conveyor Belt Size 800 mm, GSBC - 18 Mtr\r\n8. Return Conveyor Belt Size 650 mm, RC 1 - 24 Mtr\r\n9. Product Conveyor Belt Size 500 mm, PC 1 - 15 Mtr, PC 2 - 15 Mtr, PC 3 - 15 Mtr, PC 4 - 15 Mtr, PC 5 - 15 Mtr\r\n10. Motor 327.5 HP For Complete Unit Make – ABB / Siemens / Equivalent (1440 RPM)\r\n11. Control Panel Board For Complete Unit - (Standard Make)\r\n12. Cable & Wiring ( RR Kable / Polycab / Equivalent)\r\n13. Metal Detector- 1 Nos\r\n14. Secondary Hopper - 1 Set\r\n15. Cone Crusher Structure- 1 Set\r\n16. Miscellaneous / Fabricated Items- V belt & Pulley, Vibrating Screen Walk Way with Railing, All Motor Stand, Primary\r\nCrusher Maintenance Platform, Wooden Sleeper, Feed, Transfer & Discharge Chutes, Foundation Nut & Bolts for entire\r\nunit, Foundation Templates.\r\n17. Erection & commissioning\r\nPrimary Hopper: यह पार्टी का रहेगा, लेकिन इसमें जो भी Repairing work होगा या कोई Extra item लगाने होंगे, वह मेवाड़ हाईटेक द्वारा\r\nकिया जाएगा।\r\n36x24 DTO & 75 HP Motor: यह पार्टी द्वारा उपलब्ध कराई जाएगी। इसके अलावा केबल, पैनल और बोल्ट आदि मेवाड़ हाईटेक देगी और\r\nइसकी पूरी फिटिंग का काम भी कंपनी का होगा।",
      "stage": "0%",
      "priority": "NORMAL"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "Madhav Minetech, Kachchh",
  "status": "new",
  "priority": "NORMAL"
}
```

---

## [PASS] TC-50 - Project – list all projects (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Show me all projects",
  "history": [],
  "ui_filters": {
    "limit": 5
  }
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan mil gaya 👍 Mujhe **5 projects** mile hain:"
    },
    {
      "type": "project",
      "project_name": "Madhav Minetech, Kachchh",
      "category": "Refurbished | New",
      "amount": 13.0,
      "start_date": "2026-04-14",
      "end_date": "2026-04-22",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Uday Mines, Dewas",
      "category": "New Machine | New",
      "amount": 42.0,
      "start_date": "2026-04-06",
      "end_date": "2026-05-06",
      "comments": "With Structure",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Sidhi Vinayak Microns, Rajsamand",
      "category": "New Machine | New",
      "amount": 7.0,
      "start_date": "2026-04-04",
      "end_date": "2026-05-04",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Durgesh Crushing Plant, Savina",
      "category": "New Machine | New",
      "amount": 18.0,
      "start_date": "2026-03-31",
      "end_date": "2026-04-30",
      "comments": "",
      "stage": "0%",
      "priority": "NORMAL"
    },
    {
      "type": "project",
      "project_name": "Shree Mahadev Stone Crusher, Raniwara",
      "category": "New Machine | New",
      "amount": 155.0,
      "start_date": "2026-01-31",
      "end_date": "2026-03-31",
      "comments": "1. Vibro Feeder with Vibro Motor 1000 mm x 3000 mm- 1 Nos\r\n2. Vibro Pan Feeder with Vibro Motor 800 mmx2000 mm- 1 Nos\r\n3. Cone Crusher KCC 200- 1 Nos\r\n4. Vibrating Screen with doom chut and pillar 20x06 (41⁄2 Deck) Platemesh- 1 Nos\r\n5. Main Conveyor Belt Size 800 mm, MC 1 - 6 Mtr, MC 2 - 15 Mtr, MC 3- 18 Mtr, MC 4- 18 mtr\r\n6. Reverse Forwar Conveyor Belt Size 800 mm, RFC – 7.5 Mtr\r\n7. GSB Conveyor Belt Size 800 mm, GSBC - 18 Mtr\r\n8. Return Conveyor Belt Size 650 mm, RC 1 - 24 Mtr\r\n9. Product Conveyor Belt Size 500 mm, PC 1 - 15 Mtr, PC 2 - 15 Mtr, PC 3 - 15 Mtr, PC 4 - 15 Mtr, PC 5 - 15 Mtr\r\n10. Motor 327.5 HP For Complete Unit Make – ABB / Siemens / Equivalent (1440 RPM)\r\n11. Control Panel Board For Complete Unit - (Standard Make)\r\n12. Cable & Wiring ( RR Kable / Polycab / Equivalent)\r\n13. Metal Detector- 1 Nos\r\n14. Secondary Hopper - 1 Set\r\n15. Cone Crusher Structure- 1 Set\r\n16. Miscellaneous / Fabricated Items- V belt & Pulley, Vibrating Screen Walk Way with Railing, All Motor Stand, Primary\r\nCrusher Maintenance Platform, Wooden Sleeper, Feed, Transfer & Discharge Chutes, Foundation Nut & Bolts for entire\r\nunit, Foundation Templates.\r\n17. Erection & commissioning\r\nPrimary Hopper: यह पार्टी का रहेगा, लेकिन इसमें जो भी Repairing work होगा या कोई Extra item लगाने होंगे, वह मेवाड़ हाईटेक द्वारा\r\nकिया जाएगा।\r\n36x24 DTO & 75 HP Motor: यह पार्टी द्वारा उपलब्ध कराई जाएगी। इसके अलावा केबल, पैनल और बोल्ट आदि मेवाड़ हाईटेक देगी और\r\nइसकी पूरी फिटिंग का काम भी कंपनी का होगा।",
      "stage": "0%",
      "priority": "NORMAL"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "name": "Madhav Minetech, Kachchh",
    "status": "new"
  },
  {
    "name": "Uday Mines, Dewas",
    "status": "new"
  },
  {
    "name": "Sidhi Vinayak Microns, Rajsamand",
    "status": "new"
  },
  {
    "name": "Durgesh Crushing Plant, Savina",
    "status": "new"
  },
  {
    "name": "Shree Mahadev Stone Crusher, Raniwara",
    "status": "new"
  }
]
```

---

## [PASS] TC-51 - Aggregation – total items count

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "inventory mein kitne items hain total",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📦 Hamare inventory mein total **1556 unique items** hain."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "total": 1556
}
```

---

## [PASS] TC-52 - Aggregation – total projects count

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "kitne projects hain system mein",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "🏗️ Total **18 projects** hain system mein, jisme se **0 abhi active** hain."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "total": 18
}
```

---

## [PASS] TC-53 - Aggregation – total PO count (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "How many purchase orders are there in total?",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "🧾 System mein total **23 purchase orders** hain, jisme se **21 draft/pending** hain."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "total": 23
}
```

---

## [PASS] TC-54 - Aggregation – highest stock item (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "which item has the most stock?",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📈 Sabse zyada stock wala item **HR Plate 10mm 1500x6300mm= 1 Nos** hai — **9850.00 units** available hain. (Location: 2 Unit CNC M/C Ke Pass)"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "name": "HR Plate 10mm 1500x6300mm= 1 Nos",
  "stock": "9850.00"
}
```

---

## [PASS] TC-55 - Aggregation – GST of specific supplier

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Adinath Enterprises ka GST kitna bana hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "🧾 **Tax (GST) Report:**\n\n**Adinath Enterprises Ka Gst Kitna Bana Hai** ke **2 orders** par total **₹702.00** ka Tax/GST bana hai."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "total_tax": "702.00"
}
```

---

## [PASS] TC-56 - PO – Arawali balance (Hinglish)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Arawali ka balance kya hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **2 orders** mile hain. Total balance (sabka): **₹1,111.55**"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00020/2026-2027",
      "supplier": "Arawali Minerals",
      "date": "2026-04-16",
      "total": 1.05,
      "advance": 0.0,
      "balance": 1.05,
      "status": "Completed"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00001/2025-2026",
      "supplier": "Arawali Minerals",
      "date": "2026-03-13",
      "total": 1610.5,
      "advance": 500.0,
      "balance": 1110.5,
      "status": "Completed"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Arawali Minerals",
  "bal": "1111.55"
}
```

---

## [PASS] TC-57 - Supplier – typo 'Risabh' (FAISS tolerance)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Risabh International ka profile",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "haan ye raha 👍 **Rishabh International** ka profile mil gaya hai:"
    },
    {
      "type": "result",
      "supplier": {
        "id": 4725,
        "name": "Rishabh International",
        "code": "4044",
        "mobile": "+919829706543",
        "city": "N/A",
        "email": "rishabhntn@gmail.com",
        "gstin": "08AAEFR8162L1ZP"
      },
      "items": []
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Rishabh International",
  "mobile": "+919829706543",
  "gstin": "08AAEFR8162L1ZP"
}
```

---

## [PASS] TC-58 - Multi-intent – DCL details and orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "DCL ki details aur uske orders dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹18,500.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00015/2026-2027",
      "supplier": "DCL Enterprises , Faridabad (H.R.)",
      "date": "2026-04-13",
      "total": 17700.0,
      "advance": 0.0,
      "balance": 18500.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "DCL Enterprises , Faridabad (H.R.)",
  "gstin": "06AGNPD6771C1ZH"
}
```

---

## [PASS] TC-59 - PO – Shree GK Steels orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Shree GK Steels ke orders",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹40,320.60** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00013/2026-2027",
      "supplier": "Shree G.K.Steels",
      "date": "2026-04-13",
      "total": 40320.6,
      "advance": 0.0,
      "balance": 40320.6,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
[
  {
    "po_number": "MHEL/PO/00013/2026-2027",
    "total_amount": "40320.60"
  }
]
```

---

## [PASS] TC-60 - PO – Bhilwara Sales pending balance

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Bhilwara Sales ka pending balance",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Total balance (sabka): **₹38,409.00**"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00006/2026-2027",
      "supplier": "Bhilwara Sales Corporation, Bhilwara (Raj.)",
      "date": "2026-04-03",
      "total": 38409.0,
      "advance": 0.0,
      "balance": 38409.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Bhilwara Sales Corporation, Bhilwara (Raj.)",
  "bal": "38409.00"
}
```

---

## [PASS] TC-61 - PO – latest single purchase order (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Show me the latest purchase order",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **1 orders** mile hain. Inka total pending balance **₹1,062.00** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00025/2026-2027",
      "supplier": "Adinath Enterprises, Udaipur (Raj.)",
      "date": "2026-04-18",
      "total": 1062.0,
      "advance": 0.0,
      "balance": 1062.0,
      "status": "Draft"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "po_number": "MHEL/PO/00025/2026-2027",
  "status": "Draft"
}
```

---

## [UNKNOWN] TC-62 - Supplier – SUP code lookup

**HTTP Status:** `200`  
**Auto-check:** `None`

### Request
```json
{
  "query": "sup-146 ki details dikhao",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "Bhai, ye item mere system mein nahi mila. 🧐 Thoda spelling check karoge?"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Adinath Automobiles , Udaipur (Raj.)",
  "mobile": "+919928446250"
}
```

---

## [PASS] TC-63 - Supervisor role – PO blocked

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "latest purchase order dikhao",
  "history": [],
  "role": "supervisor",
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "🚫 Aapke paas Purchase Orders dekhne ki permission nahi hai. Kripya apne manager se contact karein."
    }
  ]
}
```

### DB Ground Truth
```json
{
  "blocked": true
}
```

---

## [PASS] TC-64 - PO – advance paid orders

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "jin orders mein advance diya gaya hai",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📄 Mujhe कुल **3 orders** mile hain. Inka total pending balance **₹25,562.50** hai."
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00012/2026-2027",
      "supplier": "Ikon rubber",
      "date": "2026-04-11",
      "total": 27562.5,
      "advance": 5000.0,
      "balance": 25562.5,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00005/2026-2027",
      "supplier": "Shreya Seals",
      "date": "2026-04-01",
      "total": 16962.5,
      "advance": 16962.5,
      "balance": 0.0,
      "status": "Draft"
    },
    {
      "type": "po",
      "po_no": "MHEL/PO/00001/2025-2026",
      "supplier": "Arawali Minerals",
      "date": "2026-03-13",
      "total": 1610.5,
      "advance": 500.0,
      "balance": 1110.5,
      "status": "Completed"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "po_number": "MHEL/PO/00012/2026-2027",
  "advance_amount": "5000.00"
}
```

---

## [PASS] TC-65 - Mixed – Adinath Petrochemicals contact + GSTIN (English)

**HTTP Status:** `200`  
**Auto-check:** `True`

### Request
```json
{
  "query": "Show me the contact and GST of Adinath Petrochemicals",
  "history": [],
  "ui_filters": {}
}
```

### Response
```json
{
  "results": [
    {
      "type": "chat",
      "message": "hmm ek sec... main check karta hoon 👍"
    },
    {
      "type": "chat",
      "message": "📞 **Adinath Petrochemicals, Udaipur (Raj.)** ka contact: **+919414316398**  \n🏢 GST: **08AASFA1893R1ZG**"
    }
  ]
}
```

### DB Ground Truth
```json
{
  "supplier_name": "Adinath Petrochemicals, Udaipur (Raj.)",
  "mobile": "+919414316398",
  "gstin": "08AASFA1893R1ZG"
}
```

---
