# EMI Mitra — FastAPI Backend
**Home Loan AI Voice Assistant · VAPI Tool Server**

> Demo-grade backend. All 8 banks use real 2026 interest rate data sourced from
> Paisabazaar, GoodReturns, and Business Standard (Jan–Feb 2026).

---

## Project Structure

```
emi_mitra/
├── app/
│   ├── main.py                  ← FastAPI app + CORS + router registration
│   ├── models/
│   │   └── schemas.py           ← Pydantic request models
│   ├── routers/
│   │   ├── emi.py               ← POST /tools/calculate-emi
│   │   ├── eligibility.py       ← POST /tools/check-eligibility
│   │   ├── banks.py             ← GET/POST /tools/list-banks, compare-banks
│   │   ├── prepayment.py        ← POST /tools/simulate-prepayment
│   │   └── concepts.py          ← GET /tools/explain-concept
│   └── services/
│       ├── emi_service.py       ← Core EMI math engine
│       ├── bank_service.py      ← Bank data + comparison logic
│       └── loan_service.py      ← Eligibility + prepayment simulation
└── data/
    └── banks.py                 ← Real 2026 bank data (8 banks)
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server (from emi_mitra/ directory)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Open interactive docs
# http://localhost:8000/docs
```

For public access during VAPI testing, expose via ngrok:
```bash
ngrok http 8000
# Copy the https://xxxx.ngrok.io URL → use as VAPI Server URL base
```

---

## VAPI Tool Configuration

Add each tool below in your VAPI Agent → Tools section.
Set **Server URL** = `https://YOUR_NGROK_URL/tools/<endpoint>`

---

### Tool 1: calculate-emi

**Purpose:** Calculate monthly EMI, total interest, total repayment

```json
{
  "type": "function",
  "function": {
    "name": "calculate_emi",
    "description": "Calculate the monthly EMI, total interest, and total repayment for a home loan. Call this when the user gives a loan amount, interest rate, and tenure.",
    "parameters": {
      "type": "object",
      "properties": {
        "principal": {
          "type": "number",
          "description": "Home loan amount in Indian Rupees (e.g. 5000000 for 50 lakhs)"
        },
        "annual_rate": {
          "type": "number",
          "description": "Annual interest rate as a percentage (e.g. 8.5 for 8.5%)"
        },
        "tenure_years": {
          "type": "integer",
          "description": "Loan repayment period in years (e.g. 20)"
        }
      },
      "required": ["principal", "annual_rate", "tenure_years"]
    }
  },
  "server": {
    "url": "https://YOUR_URL/tools/calculate-emi",
    "method": "POST"
  }
}
```

---

### Tool 2: check-eligibility

**Purpose:** Estimate max loan amount a user qualifies for

```json
{
  "type": "function",
  "function": {
    "name": "check_eligibility",
    "description": "Estimate the maximum home loan amount a person is eligible for based on their income, existing obligations, and CIBIL score.",
    "parameters": {
      "type": "object",
      "properties": {
        "monthly_income": {
          "type": "number",
          "description": "Gross monthly income in rupees"
        },
        "monthly_obligations": {
          "type": "number",
          "description": "Total existing EMIs and loan obligations per month. Use 0 if none.",
          "default": 0
        },
        "cibil_score": {
          "type": "integer",
          "description": "CIBIL credit score between 300 and 900",
          "default": 750
        },
        "age": {
          "type": "integer",
          "description": "Applicant's current age in years",
          "default": 30
        },
        "tenure_years": {
          "type": "integer",
          "description": "Desired loan tenure in years",
          "default": 20
        },
        "annual_rate": {
          "type": "number",
          "description": "Expected interest rate (use 8.5 as default)",
          "default": 8.5
        },
        "is_woman": {
          "type": "boolean",
          "description": "Is the primary applicant a woman? Women get 0.05% concession.",
          "default": false
        }
      },
      "required": ["monthly_income"]
    }
  },
  "server": {
    "url": "https://YOUR_URL/tools/check-eligibility",
    "method": "POST"
  }
}
```

---

### Tool 3: compare-banks

**Purpose:** Compare home loan rates across all banks for a user's profile

```json
{
  "type": "function",
  "function": {
    "name": "compare_banks",
    "description": "Compare home loan interest rates, EMIs, processing fees, and total cost across Indian banks (SBI, HDFC, ICICI, Axis, PNB, BoB, Kotak, LIC HFL). Returns ranked results with the cheapest option first.",
    "parameters": {
      "type": "object",
      "properties": {
        "loan_amount": {
          "type": "number",
          "description": "Loan amount in rupees"
        },
        "tenure_years": {
          "type": "integer",
          "description": "Loan tenure in years",
          "default": 20
        },
        "cibil_score": {
          "type": "integer",
          "description": "CIBIL credit score",
          "default": 750
        },
        "is_woman": {
          "type": "boolean",
          "description": "Woman borrower gets 5 bps concession at most banks",
          "default": false
        }
      },
      "required": ["loan_amount"]
    }
  },
  "server": {
    "url": "https://YOUR_URL/tools/compare-banks",
    "method": "POST"
  }
}
```

---

### Tool 4: simulate-prepayment

**Purpose:** Show how much interest is saved by making a lump-sum prepayment

```json
{
  "type": "function",
  "function": {
    "name": "simulate_prepayment",
    "description": "Simulate the savings from a lump-sum home loan prepayment. Shows interest saved and time saved. Two modes: reduce_tenure (closes loan earlier, saves more) or reduce_emi (lowers monthly payment).",
    "parameters": {
      "type": "object",
      "properties": {
        "principal": {
          "type": "number",
          "description": "Original loan amount in rupees"
        },
        "annual_rate": {
          "type": "number",
          "description": "Annual interest rate as percentage"
        },
        "tenure_years": {
          "type": "integer",
          "description": "Original loan tenure in years"
        },
        "prepayment_amount": {
          "type": "number",
          "description": "Lump sum amount to prepay in rupees"
        },
        "prepayment_at_month": {
          "type": "integer",
          "description": "The month number at which the prepayment is made (e.g. 36 for 3 years into loan)"
        },
        "prepayment_mode": {
          "type": "string",
          "enum": ["reduce_tenure", "reduce_emi"],
          "description": "reduce_tenure: keep EMI same, close loan early. reduce_emi: keep tenure same, reduce EMI.",
          "default": "reduce_tenure"
        }
      },
      "required": ["principal", "annual_rate", "tenure_years", "prepayment_amount", "prepayment_at_month"]
    }
  },
  "server": {
    "url": "https://YOUR_URL/tools/simulate-prepayment",
    "method": "POST"
  }
}
```

---

### Tool 5: explain-concept

**Purpose:** Explain home loan terms in simple language

```json
{
  "type": "function",
  "function": {
    "name": "explain_concept",
    "description": "Explain a home loan concept in simple language. Use this when the user asks 'what is EMI', 'what is CIBIL', 'what is LTV', etc.",
    "parameters": {
      "type": "object",
      "properties": {
        "term": {
          "type": "string",
          "description": "The concept to explain. Supported: emi, cibil, ltv, foir, rllr, prepayment, mclr, pmay, fixed_vs_floating"
        }
      },
      "required": ["term"]
    }
  },
  "server": {
    "url": "https://YOUR_URL/tools/explain-concept",
    "method": "GET"
  }
}
```

---

## Bank Data Summary (2026)

| Bank       | Type    | Rate Range    | Processing Fee              | Prepayment (Float) |
|------------|---------|---------------|-----------------------------|---------------------|
| SBI        | Public  | 7.25–8.70%    | 0.35% (max ₹10,000)         | Nil                 |
| HDFC       | Private | 7.20–13.20%   | Up to 0.50% (max ₹45,000)   | Nil                 |
| ICICI      | Private | 7.65–9.80%    | Up to 0.30% (max ₹50,000)   | Nil                 |
| Axis       | Private | 7.60–9.40%    | Up to 1.00% (max ₹75,000)   | Nil                 |
| PNB        | Public  | 7.20–10.00%   | 0.35% (max ₹15,000)         | Nil                 |
| BoB        | Public  | 7.45–9.95%    | 0.50% (max ₹25,000)         | Nil                 |
| Kotak      | Private | 7.99–9.50%    | 0.50% (max ₹50,000)         | Nil                 |
| LIC HFL    | HFC     | 7.50–10.50%   | 0.50% (max ₹15,000)         | Nil                 |

> All floating-rate loans: zero prepayment penalty (RBI mandated since 2012)
> RBI Repo Rate: 5.25% (February 2026)

---

## VAPI System Prompt Snippet

Add this to your VAPI agent's system prompt:

```
You are EMI Mitra, an intelligent home loan assistant. You speak naturally and explain
financial concepts in simple language. You support Hindi, English, Tamil, Telugu, and Marathi.

When a user asks about EMI, loan eligibility, bank comparison, or prepayment:
1. Ask for the information you need (loan amount, tenure, income, etc.)
2. Call the appropriate tool
3. Read out the voice_summary field from the response naturally
4. Offer to explain further or compare banks

Always use Indian number format: say "50 lakh" not "5,000,000", "1 crore" not "10,000,000".
Never give investment advice. Always suggest users verify rates directly with banks before applying.
```
