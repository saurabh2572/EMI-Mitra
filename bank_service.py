"""
Bank service — fetch, filter, and compare bank rates.
Uses bank data from bank_data.db.
"""

import json

from sqlalchemy import create_engine, text

from emi_calculator import calculate_emi, _format_inr


DATABASE_URL = "sqlite:///./bank_data.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def get_banks_from_db() -> list[dict]:
    query = text("SELECT * FROM banks")

    with engine.connect() as connection:
        result = connection.execute(query)
        banks = []

        for row in result:
            bank = dict(row._mapping)

            bank["id"] = bank.pop("bank_id", None)
            bank["type"] = bank.pop("bank_type", None)

            if isinstance(bank.get("special_features"), str):
                bank["special_features"] = json.loads(bank["special_features"])

            if isinstance(bank.get("cibil_slabs"), str):
                bank["cibil_slabs"] = json.loads(bank["cibil_slabs"])

            banks.append(bank)

        return banks


def get_all_banks() -> list:
    """Return all banks with key info for listing."""
    banks = get_banks_from_db()

    return [
        {
            "id": b["id"],
            "name": b["name"],
            "short_name": b["short_name"],
            "type": b["type"],
            "rate_min": b["rate_min"],
            "rate_max": b["rate_max"],
            "processing_fee_note": b["processing_fee_note"],
        }
        for b in banks
    ]


def get_bank_detail(bank_id: str) -> dict | None:
    """Return full detail for a single bank."""
    banks = get_banks_from_db()
    return next((b for b in banks if b["id"] == bank_id), None)


def get_rate_for_cibil(bank: dict, cibil_score: int, is_woman: bool = False) -> float:
    """Determine applicable rate based on CIBIL score slab."""
    rate = bank["rate_max"]

    for slab in bank.get("cibil_slabs", []):
        if slab["min"] <= cibil_score <= slab["max"]:
            rate = slab["rate"]
            break

    if is_woman:
        rate -= bank.get("womens_concession", 0)

    return round(rate, 2)


def compare_banks(
    loan_amount: float,
    tenure_years: int,
    cibil_score: int = 750,
    is_woman: bool = False,
    bank_ids: list | None = None,
) -> dict:
    """
    Compare home loan options across banks for a given profile.

    Returns ranked list with EMI, total interest, and processing fee.
    """
    banks_to_compare = get_banks_from_db()

    if bank_ids:
        banks_to_compare = [
            b for b in banks_to_compare
            if b["id"] in bank_ids
        ]

    eligible_banks = [
        b for b in banks_to_compare
        if b["min_cibil"] <= cibil_score
    ]

    results = []

    for bank in eligible_banks:
        rate = get_rate_for_cibil(bank, cibil_score, is_woman)
        emi_data = calculate_emi(loan_amount, rate, tenure_years)

        fee = loan_amount * bank["processing_fee_pct"] / 100
        fee = max(fee, bank["processing_fee_min"])
        fee = min(fee, bank["processing_fee_max"])

        results.append({
            "bank_id": bank["id"],
            "bank_name": bank["name"],
            "bank_type": bank["type"],
            "applicable_rate": rate,
            "monthly_emi": emi_data["monthly_emi"],
            "total_interest": emi_data["total_interest"],
            "total_payment": emi_data["total_payment"],
            "processing_fee_estimate": round(fee, 2),
            "total_cost": round(emi_data["total_payment"] + fee, 2),
            "prepayment_penalty_floating": bank["prepayment_floating"],
            "min_cibil_required": bank["min_cibil"],
            "special_features": bank.get("special_features", [])[:2],
        })

    results.sort(key=lambda x: x["total_cost"])

    for index, result in enumerate(results):
        result["rank"] = index + 1

    best = results[0] if results else None

    return {
        "loan_amount": loan_amount,
        "tenure_years": tenure_years,
        "cibil_score": cibil_score,
        "is_woman_borrower": is_woman,
        "banks_compared": len(results),
        "results": results,
        "best_option": best,
        "voice_summary": _comparison_voice_summary(results, loan_amount, tenure_years),
    }


def _comparison_voice_summary(results: list, loan_amount: float, tenure: int) -> str:
    if not results:
        return "No eligible banks found for your profile."

    best = results[0]
    worst = results[-1]
    savings = worst["total_interest"] - best["total_interest"]

    lines = [
        f"I compared {len(results)} banks for a {_format_inr(loan_amount)} loan over {tenure} years.",
        f"The best option is {best['bank_name']} at {best['applicable_rate']}% per annum, "
        f"with an EMI of {_format_inr(best['monthly_emi'])} per month.",
    ]

    if len(results) > 1:
        lines.append(
            f"Compared to {worst['bank_name']}, you save {_format_inr(savings)} in interest "
            f"by choosing {best['bank_name']}."
        )

    return " ".join(lines)