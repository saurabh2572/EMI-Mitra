from fastapi import APIRouter
from schemas import EMIRequest
from emi_calculator import calculate_emi, get_amortization_schedule

router = APIRouter()

@router.post("/calculate-emi")
def calculate_emi_tool(payload: EMIRequest):

    response = calculate_emi(
        payload.principal,
        payload.annual_rate,
        payload.tenure_years,
    )

    if payload.include_schedule:
        response["schedule"] = get_amortization_schedule(
            payload.principal,
            payload.annual_rate,
            payload.tenure_years,
        )

    return response