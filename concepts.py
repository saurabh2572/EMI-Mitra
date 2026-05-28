"""
Concept explainer — answers "what is X?" questions about home loan terms.
VAPI can call this when a user asks about EMI, CIBIL, LTV, FOIR, etc.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()

CONCEPTS = {
    "emi": {
        "term": "EMI (Equated Monthly Instalment)",
        "simple": (
            "EMI is the fixed amount you pay every month to repay your home loan. "
            "It has two parts: principal (the actual loan amount) and interest. "
            "In early months, most of your EMI goes towards interest. "
            "As years pass, more goes towards reducing the principal."
        ),
        "formula": "EMI = P × r × (1+r)^n / ((1+r)^n - 1)",
        "example": (
            "For a ₹50 lakh loan at 8.5% for 20 years, "
            "your EMI is approximately ₹43,391 per month."
        ),
    },
    "cibil": {
        "term": "CIBIL Score (Credit Score)",
        "simple": (
            "CIBIL score is a 3-digit number between 300 and 900 that reflects your credit health. "
            "It is calculated by TransUnion CIBIL based on your loan repayment history. "
            "A score above 750 gets you the best home loan rates. "
            "Below 650, many banks may reject your application."
        ),
        "score_guide": {
            "750-900": "Excellent — best rates available",
            "700-749": "Good — slightly higher rates",
            "650-699": "Fair — limited bank options",
            "below-650": "Poor — most banks will reject",
        },
        "example": (
            "A CIBIL score of 800 can get you SBI's lowest rate of 7.25%, "
            "while a score of 680 may only qualify you for 8.25%."
        ),
    },
    "ltv": {
        "term": "LTV (Loan to Value Ratio)",
        "simple": (
            "LTV is the percentage of the property value that the bank will lend you. "
            "RBI mandates: for loans below ₹30 lakh, banks can lend up to 90%. "
            "For ₹30-75 lakh, up to 80%. Above ₹75 lakh, up to 75%. "
            "You must arrange the remaining amount as a down payment."
        ),
        "example": (
            "For a ₹1 crore property, the bank will lend up to ₹75 lakh. "
            "You need to arrange ₹25 lakh as down payment."
        ),
    },
    "foir": {
        "term": "FOIR (Fixed Obligation to Income Ratio)",
        "simple": (
            "FOIR is the percentage of your monthly income that goes towards all loan EMIs combined. "
            "Banks prefer FOIR below 40-50%. "
            "If your existing EMIs already consume 40% of your income, the bank may not give you a home loan."
        ),
        "example": (
            "If you earn ₹1 lakh per month and already pay ₹20,000 in car loan EMI, "
            "your FOIR is 20%. Banks will typically allow another ₹30,000 in home loan EMI."
        ),
    },
    "rllr": {
        "term": "RLLR / EBLR (External Benchmark Linked Lending Rate)",
        "simple": (
            "Since October 2019, all new home loans must be linked to an external benchmark, "
            "typically the RBI Repo Rate. This is called RLLR — Repo Linked Lending Rate. "
            "When RBI cuts or hikes the repo rate, your home loan rate changes automatically "
            "at the next reset date (usually quarterly). "
            "This protects borrowers from banks delaying rate cut benefits."
        ),
        "current_repo": "5.25% (as of February 2026)",
    },
    "prepayment": {
        "term": "Prepayment / Foreclosure",
        "simple": (
            "Prepayment means paying extra money beyond your EMI to reduce your outstanding loan. "
            "Part-prepayment reduces your balance, saving interest. "
            "Full prepayment (foreclosure) closes the loan before tenure ends. "
            "As per RBI rules, banks cannot charge prepayment penalty on floating rate home loans."
        ),
        "tip": "Prepaying in early years saves the most interest as that is when your outstanding is highest.",
    },
    "mclr": {
        "term": "MCLR (Marginal Cost of Funds Based Lending Rate)",
        "simple": (
            "MCLR is the older benchmark used by banks before RLLR was introduced in 2019. "
            "Some older home loans are still on MCLR. "
            "MCLR-linked loans are less transparent as banks control when to pass on RBI rate cuts. "
            "If you have an MCLR loan, consider switching to RLLR for better rate transmission."
        ),
    },
    "pmay": {
        "term": "PMAY (Pradhan Mantri Awas Yojana)",
        "simple": (
            "PMAY is a government scheme that provides interest subsidy on home loans "
            "for first-time buyers from economically weaker sections and middle income groups. "
            "The subsidy is credited upfront to your loan account, reducing your EMI."
        ),
        "subsidy": {
            "EWS/LIG": "Up to 6.5% subsidy on first ₹6 lakh",
            "MIG-1": "4% subsidy on first ₹9 lakh",
            "MIG-2": "3% subsidy on first ₹12 lakh",
        },
    },
    "fixed_vs_floating": {
        "term": "Fixed vs Floating Interest Rate",
        "simple": (
            "Fixed rate stays the same throughout the loan tenure, giving you payment certainty. "
            "Floating rate changes when RBI changes the repo rate — it can go up or down. "
            "Historically, floating rates have been cheaper over long tenures. "
            "For a 20-year home loan, most experts recommend floating rate."
        ),
        "recommendation": "For tenures above 10 years, floating rate is generally better.",
    },
}


@router.get("/explain-concept")
def explain_concept_tool(term: str):
    """
    VAPI Tool: Explain a home loan concept in simple language.

    Supported terms: emi, cibil, ltv, foir, rllr, prepayment, mclr, pmay, fixed_vs_floating
    """
    key = term.lower().strip().replace(" ", "_").replace("-", "_")

    # Handle common aliases
    aliases = {
        "credit_score": "cibil",
        "loan_to_value": "ltv",
        "repo_rate": "rllr",
        "rllr_rate": "rllr",
        "foreclosure": "prepayment",
        "part_payment": "prepayment",
        "fixed_rate": "fixed_vs_floating",
        "floating_rate": "fixed_vs_floating",
        "subsidy": "pmay",
        "pradhan_mantri": "pmay",
    }
    key = aliases.get(key, key)

    concept = CONCEPTS.get(key)
    if not concept:
        available = list(CONCEPTS.keys())
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Concept '{term}' not found.",
                "available_concepts": available,
            },
        )

    return {
        "term": concept["term"],
        "explanation": concept["simple"],
        "extra": {k: v for k, v in concept.items() if k not in ("term", "simple")},
        "voice_summary": concept["simple"],
    }


@router.get("/list-concepts")
def list_concepts_tool():
    """VAPI Tool: List all available home loan concepts that can be explained."""
    return {
        "concepts": [
            {"key": k, "term": v["term"]} for k, v in CONCEPTS.items()
        ]
    }
