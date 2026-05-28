from fastapi import APIRouter
from schemas import EligibilityRequest
from loan_service import estimate_eligibility

router = APIRouter()

@router.post("/check-eligibility")
def check_eligibility(payload: EligibilityRequest):

    return estimate_eligibility(
        monthly_income=payload.monthly_income,
        monthly_obligations=payload.monthly_obligations,
        cibil_score=payload.cibil_score,
        age=payload.age,
        tenure_years=payload.tenure_years,
        annual_rate=payload.annual_rate,
        is_woman=payload.is_woman,
    )