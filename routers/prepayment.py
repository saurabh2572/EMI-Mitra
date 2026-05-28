from fastapi import APIRouter
from schemas import PrepaymentRequest
from loan_service import simulate_prepayment

router = APIRouter()

@router.post("/simulate-prepayment")
def simulate_prepayment_tool(payload: PrepaymentRequest):

    return simulate_prepayment(
        principal=payload.principal,
        annual_rate=payload.annual_rate,
        tenure_years=payload.tenure_years,
        prepayment_at_month=payload.prepayment_at_month,
        prepayment_amount=payload.prepayment_amount,
        prepayment_mode=payload.prepayment_mode,
    )