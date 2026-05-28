from fastapi import APIRouter, HTTPException
from schemas import BankCompareRequest
from bank_service import compare_banks
from database import BANKS

router = APIRouter()

@router.post("/compare-banks")
def compare_banks_tool(payload: BankCompareRequest):

    return compare_banks(
        loan_amount=payload.loan_amount,
        tenure_years=payload.tenure_years,
        cibil_score=payload.cibil_score,
        is_woman=payload.is_woman,
        bank_ids=payload.bank_ids,
    )


@router.get("/list-banks")
def list_banks():

    return {
        "banks": BANKS
    }


@router.get("/bank-detail/{bank_id}")
def bank_detail(bank_id: str):

    bank = next(
        (b for b in BANKS if b["id"] == bank_id),
        None,
    )

    if not bank:
        raise HTTPException(
            status_code=404,
            detail="Bank not found"
        )

    return bank