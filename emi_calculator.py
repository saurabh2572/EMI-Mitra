"""
Core EMI calculation engine.

EMI Formula:
    EMI = P × r × (1+r)^n / ((1+r)^n - 1)
    where P = principal, r = monthly rate, n = months
"""

import math
from typing import List


def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> dict:
    """
    Calculate EMI and return full amortization summary.

    Args:
        principal:     Loan amount in ₹
        annual_rate:   Interest rate per annum (e.g. 8.5 for 8.5%)
        tenure_years:  Loan tenure in years

    Returns:
        dict with emi, total_payment, total_interest, amortization summary
    """
    r = annual_rate / 100 / 12           # monthly interest rate
    n = tenure_years * 12                # total months

    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

    total_payment = emi * n
    total_interest = total_payment - principal
    interest_to_principal_ratio = total_interest / principal

    # Year-wise breakup (useful for voice summary)
    yearly_breakup = _yearly_breakup(principal, r, emi, n)

    return {
        "monthly_emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "interest_to_principal_ratio": round(interest_to_principal_ratio, 2),
        "principal": principal,
        "annual_rate_pct": annual_rate,
        "tenure_years": tenure_years,
        "tenure_months": n,
        "yearly_breakup": yearly_breakup,
        "voice_summary": _emi_voice_summary(
            emi, principal, total_interest, total_payment, tenure_years, annual_rate
        ),
    }


def _yearly_breakup(principal: float, monthly_rate: float, emi: float, n: int) -> list:
    """Generate year-wise principal, interest, and balance summary."""
    balance = principal
    yearly = []
    year = 1
    year_principal = 0
    year_interest = 0

    for month in range(1, n + 1):
        interest_component = balance * monthly_rate
        principal_component = emi - interest_component
        balance -= principal_component

        year_principal += principal_component
        year_interest += interest_component

        if month % 12 == 0 or month == n:
            yearly.append({
                "year": year,
                "principal_paid": round(year_principal, 2),
                "interest_paid": round(year_interest, 2),
                "closing_balance": round(max(balance, 0), 2),
            })
            year += 1
            year_principal = 0
            year_interest = 0

    return yearly


def _emi_voice_summary(
    emi: float, principal: float, total_interest: float,
    total_payment: float, tenure: int, rate: float
) -> str:
    """Generate a natural language summary for VAPI to speak aloud."""
    emi_formatted = _format_inr(emi)
    interest_formatted = _format_inr(total_interest)
    total_formatted = _format_inr(total_payment)
    principal_formatted = _format_inr(principal)

    return (
        f"For a home loan of {principal_formatted} at {rate}% per annum for {tenure} years, "
        f"your monthly EMI will be {emi_formatted}. "
        f"Over the entire tenure, you will pay {interest_formatted} as interest, "
        f"making the total repayment {total_formatted}. "
        f"The interest amount is {round(total_interest/principal, 1)} times your loan amount."
    )


def _format_inr(amount: float) -> str:
    """Format amount in Indian number system (lakhs, crores)."""
    if amount >= 10_000_000:
        return f"₹{amount/10_000_000:.2f} crore"
    elif amount >= 100_000:
        return f"₹{amount/100_000:.2f} lakh"
    else:
        return f"₹{amount:,.0f}"


def get_amortization_schedule(
    principal: float, annual_rate: float, tenure_years: int
) -> List[dict]:
    """
    Full month-by-month amortization schedule.
    Returns first 12 months + year-end snapshots for brevity.
    """
    r = annual_rate / 100 / 12
    n = tenure_years * 12
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

    schedule = []
    balance = principal

    for month in range(1, n + 1):
        interest_component = balance * r
        principal_component = emi - interest_component
        balance = max(balance - principal_component, 0)

        # Include first 12 months + every 12th month thereafter
        if month <= 12 or month % 12 == 0:
            schedule.append({
                "month": month,
                "year": math.ceil(month / 12),
                "emi": round(emi, 2),
                "principal_component": round(principal_component, 2),
                "interest_component": round(interest_component, 2),
                "closing_balance": round(balance, 2),
            })

    return schedule

