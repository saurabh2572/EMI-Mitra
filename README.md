# EMI Mitra Backend

FastAPI backend for EMI Mitra, a home loan assistant that can be connected to VAPI as tool endpoints. The backend supports EMI calculation, eligibility estimation, bank comparison, prepayment simulation, and home loan concept explanations.

## Features

- Calculate monthly EMI for a loan amount, rate, and tenure
- Estimate home loan eligibility using income, obligations, age, and CIBIL score
- Compare bank offers using data stored in `bank_data.db`
- Fetch bank list and individual bank details
- Simulate prepayment impact on tenure, EMI, and interest savings
- Explain common home loan terms like EMI, CIBIL, FOIR, LTV, RLLR, PMAY, and prepayment

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

## Project Structure

```text
.
├── main.py
├── database.py
├── bank_data.db
├── emi_calculator.py
├── services.py
├── bank_service.py
└── requirements.txt
```

## Setup

Install dependencies:

```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

If you use `uv`:

```bash
uv add fastapi uvicorn sqlalchemy pydantic
```

Create and seed the database:

```bash
python database.py
```

Run the API server:

```bash
uvicorn main:app --reload
```

Default local server:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

## API Endpoints

### Root

```http
GET /
```

Returns service status and available tools.

### Calculate EMI

```http
POST /tools/calculate-emi
```

Request:

```json
{
  "principal": 5000000,
  "annual_rate": 8.5,
  "tenure_years": 20,
  "include_schedule": false
}
```

### Check Eligibility

```http
POST /tools/check-eligibility
```

Request:

```json
{
  "monthly_income": 100000,
  "monthly_obligations": 15000,
  "cibil_score": 760,
  "age": 30,
  "tenure_years": 20,
  "annual_rate": 8.5,
  "is_woman": false
}
```

### Compare Banks

```http
POST /tools/compare-banks
```

Request:

```json
{
  "loan_amount": 5000000,
  "tenure_years": 20,
  "cibil_score": 750,
  "is_woman": false,
  "bank_ids": null
}
```

To compare selected banks:

```json
{
  "loan_amount": 5000000,
  "tenure_years": 20,
  "cibil_score": 750,
  "is_woman": false,
  "bank_ids": ["sbi", "hdfc", "icici"]
}
```

### Simulate Prepayment

```http
POST /tools/simulate-prepayment
```

Request:

```json
{
  "principal": 5000000,
  "annual_rate": 8.5,
  "tenure_years": 20,
  "prepayment_amount": 500000,
  "prepayment_at_month": 36,
  "prepayment_mode": "reduce_tenure"
}
```

`prepayment_mode` can be:

- `reduce_tenure`
- `reduce_emi`

### List Banks

```http
GET /tools/list-banks
```

### Bank Detail

```http
GET /tools/bank-detail/{bank_id}
```

Example:

```http
GET /tools/bank-detail/sbi
```

### Explain Concept

```http
GET /tools/explain-concept?term=cibil
```

Supported terms:

- `emi`
- `cibil`
- `ltv`
- `foir`
- `rllr`
- `prepayment`
- `mclr`
- `pmay`
- `fixed_vs_floating`

### List Concepts

```http
GET /tools/list-concepts
```

## VAPI Tool Integration

Use these backend endpoints as VAPI tools:

- `POST /tools/check-eligibility`
- `POST /tools/compare-banks`
- `POST /tools/calculate-emi`
- `POST /tools/simulate-prepayment`
- `GET /tools/explain-concept`
- `GET /tools/list-banks`
- `GET /tools/bank-detail/{bank_id}`

Recommended VAPI flow:

1. Collect loan amount and tenure.
2. Ask age, monthly income, existing EMIs, and CIBIL score.
3. Call eligibility API.
4. If eligible, call bank comparison API.
5. Use the best bank rate to calculate EMI.
6. Use prepayment API only if the user asks about part-payment or foreclosure.

## Notes

- Bank data is stored in SQLite database `bank_data.db`.
- Loan and bank data is for demo use only.
- Final loan approval depends on bank policy, documents, property valuation, and verification.
