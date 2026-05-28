"""
Eligibility estimation and prepayment simulation services.
"""

from app.services.emi_service import calculate_emi, _format_inr
from data.banks import BANKS


# ──────────────────────────────────────────────
# ELIGIBILITY SERVICE
# ──────────────────────────────────────────────

def estimate_eligibility(
    monthly_income: float,
    monthly_obligations: float,   # existing EMIs, credit card minimums, etc.
    cibil_score: int,
    age: int,
    tenure_years: int = 20,
    annual_rate: float = 8.5,
    is_woman: bool = False,
) -> dict:
    """
    Estimate maximum eligible loan amount using FOIR (Fixed Obligation to Income Ratio).

    RBI/bank guidelines:
      - FOIR limit: 40-50% of gross monthly income
      - LTV: up to 90% for loans < ₹30L, 80% for ₹30L-75L, 75% for >₹75L
      - Credit score must meet bank minimums
    """
    # FOIR caps by credit score
    if cibil_score >= 750:
        foir_cap = 0.50
    elif cibil_score >= 700:
        foir_cap = 0.45
    else:
        foir_cap = 0.40

    # Max EMI allowed = (income × FOIR) - existing obligations
    max_emi = (monthly_income * foir_cap) - monthly_obligations

    if max_emi <= 0:
        return {
            "eligible": False,
            "reason": "Existing obligations exceed FOIR limit. Reduce obligations to improve eligibility.",
            "max_emi_allowed": 0,
            "estimated_loan_amount": 0,
            "voice_summary": (
                "Based on your current obligations, you may not be eligible for a home loan. "
                "Your existing EMIs consume too much of your income. Try reducing existing debt first."
            ),
        }

    # Back-calculate principal from max EMI
    r = annual_rate / 100 / 12
    n = tenure_years * 12
    max_principal = max_emi * ((1 + r) ** n - 1) / (r * (1 + r) ** n)

    # Max tenure limited by retirement age (assume retire at 60 for salaried)
    max_tenure_by_age = max(5, 60 - age)
    effective_tenure = min(tenure_years, max_tenure_by_age)

    # Recalculate if tenure was reduced
    if effective_tenure < tenure_years:
        n2 = effective_tenure * 12
        max_principal = max_emi * ((1 + r) ** n2 - 1) / (r * (1 + r) ** n2)

    # Find eligible banks
    eligible_banks = []
    for bank in BANKS:
        if bank["min_cibil"] <= cibil_score and age <= bank["max_age"]:
            eligible_banks.append({
                "bank": bank["short_name"],
                "min_rate": bank["rate_min"],
                "max_ltv": bank["max_ltv"],
            })

    return {
        "eligible": True,
        "monthly_income": monthly_income,
        "monthly_obligations": monthly_obligations,
        "foir_applied_pct": round(foir_cap * 100, 1),
        "max_emi_allowed": round(max_emi, 2),
        "estimated_loan_amount": round(max_principal, 2),
        "effective_tenure_years": effective_tenure,
        "annual_rate_used": annual_rate,
        "cibil_score": cibil_score,
        "eligible_banks_count": len(eligible_banks),
        "eligible_banks": eligible_banks[:3],   # top 3 for voice
        "tips": _eligibility_tips(cibil_score, monthly_obligations, monthly_income),
        "voice_summary": _eligibility_voice_summary(
            max_principal, max_emi, effective_tenure, annual_rate,
            cibil_score, eligible_banks, monthly_income
        ),
    }


def _eligibility_voice_summary(
    principal, max_emi, tenure, rate, cibil, banks, income
) -> str:
    return (
        f"Based on your income and obligations, you are eligible for a home loan of up to "
        f"{_format_inr(principal)} at approximately {rate}% interest. "
        f"Your maximum EMI capacity is {_format_inr(max_emi)} per month. "
        f"You are eligible at {len(banks)} banks including "
        f"{', '.join(b['bank'] for b in banks[:3])}. "
        f"Your CIBIL score of {cibil} {'qualifies you for the best rates.' if cibil >= 750 else 'is acceptable. Improving it above 750 can get you better rates.'}"
    )


def _eligibility_tips(cibil: int, obligations: float, income: float) -> list:
    tips = []
    if cibil < 750:
        tips.append("Improve CIBIL score above 750 to access lowest interest rates.")
    if obligations / income > 0.3:
        tips.append("Reduce existing EMIs — high obligations reduce your eligible loan amount.")
    tips.append("Adding a co-applicant with income can increase your loan eligibility.")
    tips.append("A longer tenure reduces EMI but increases total interest paid.")
    return tips


# ──────────────────────────────────────────────
# PREPAYMENT SERVICE
# ──────────────────────────────────────────────

def simulate_prepayment(
    principal: float,
    annual_rate: float,
    tenure_years: int,
    prepayment_amount: float,
    prepayment_at_month: int,
    prepayment_mode: str = "reduce_tenure",  # or "reduce_emi"
) -> dict:
    """
    Simulate the effect of a lump-sum prepayment on a home loan.

    prepayment_mode:
      "reduce_tenure" → keep EMI same, finish loan earlier (saves more)
      "reduce_emi"    → keep tenure same, reduce monthly EMI
    """
    r = annual_rate / 100 / 12
    n = tenure_years * 12
    original_emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

    # Simulate WITHOUT prepayment
    original_total = original_emi * n
    original_interest = original_total - principal

    # Simulate WITH prepayment
    # Walk month by month to the prepayment point
    balance = principal
    interest_paid_before = 0
    for month in range(1, prepayment_at_month + 1):
        interest_this_month = balance * r
        principal_this_month = original_emi - interest_this_month
        interest_paid_before += interest_this_month
        balance -= principal_this_month

    balance_at_prepayment = max(balance, 0)
    new_principal = balance_at_prepayment - prepayment_amount

    if new_principal <= 0:
        # Prepayment closes the loan
        return {
            "prepayment_closes_loan": True,
            "months_completed": prepayment_at_month,
            "interest_saved": round(original_interest - interest_paid_before, 2),
            "voice_summary": (
                f"Great news! A prepayment of {_format_inr(prepayment_amount)} at month "
                f"{prepayment_at_month} will close your loan entirely. "
                f"You save {_format_inr(original_interest - interest_paid_before)} in interest."
            ),
        }

    remaining_months_original = n - prepayment_at_month

    if prepayment_mode == "reduce_tenure":
        # Keep same EMI, calculate new shorter tenure
        if r == 0:
            new_months = new_principal / original_emi
        else:
            import math
            new_months = math.log(original_emi / (original_emi - new_principal * r)) / math.log(1 + r)
        new_months = round(new_months)
        new_emi = original_emi

        months_saved = remaining_months_original - new_months
        new_interest_after = (new_emi * new_months) - new_principal
    else:
        # Keep same tenure, recalculate lower EMI
        new_months = remaining_months_original
        new_emi = new_principal * r * (1 + r) ** new_months / ((1 + r) ** new_months - 1)
        months_saved = 0
        new_interest_after = (new_emi * new_months) - new_principal

    total_interest_with_prepayment = interest_paid_before + new_interest_after
    interest_saved = original_interest - total_interest_with_prepayment

    new_total_tenure_months = prepayment_at_month + new_months
    years_saved = months_saved // 12
    months_rem = months_saved % 12

    return {
        "original_loan": {
            "emi": round(original_emi, 2),
            "tenure_months": n,
            "total_interest": round(original_interest, 2),
        },
        "prepayment": {
            "amount": prepayment_amount,
            "at_month": prepayment_at_month,
            "mode": prepayment_mode,
            "balance_before": round(balance_at_prepayment, 2),
            "balance_after": round(new_principal, 2),
        },
        "after_prepayment": {
            "new_emi": round(new_emi, 2),
            "remaining_months": new_months,
            "total_tenure_months": new_total_tenure_months,
            "months_saved": months_saved,
            "years_saved": years_saved,
            "total_interest_paid": round(total_interest_with_prepayment, 2),
        },
        "savings": {
            "interest_saved": round(interest_saved, 2),
            "time_saved_months": months_saved,
        },
        "voice_summary": _prepayment_voice_summary(
            prepayment_amount, prepayment_at_month, interest_saved,
            years_saved, months_rem, new_emi, original_emi, prepayment_mode
        ),
    }


def _prepayment_voice_summary(
    amount, month, interest_saved, years_saved, months_rem,
    new_emi, old_emi, mode
) -> str:
    amount_str = _format_inr(amount)
    saved_str = _format_inr(interest_saved)

    if mode == "reduce_tenure":
        time_str = ""
        if years_saved > 0:
            time_str += f"{years_saved} year{'s' if years_saved > 1 else ''}"
        if months_rem > 0:
            time_str += f" and {months_rem} month{'s' if months_rem > 1 else ''}"
        return (
            f"By making a prepayment of {amount_str} at month {month}, "
            f"you will save {saved_str} in total interest "
            f"and close your loan {time_str} earlier. "
            f"Your EMI stays the same at {_format_inr(new_emi)}."
        )
    else:
        emi_reduction = old_emi - new_emi
        return (
            f"By making a prepayment of {amount_str} at month {month}, "
            f"your monthly EMI reduces by {_format_inr(emi_reduction)} "
            f"to {_format_inr(new_emi)}. "
            f"You save {saved_str} in total interest."
        )
