"""Pydantic request/response models for all VAPI tool endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class EMIRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan amount in ₹")
    annual_rate: float = Field(..., gt=0, lt=30, description="Annual interest rate %")
    tenure_years: int = Field(..., ge=1, le=30, description="Loan tenure in years")
    include_schedule: bool = Field(False, description="Include month-wise amortization")

    model_config = {
        "json_schema_extra": {
            "example": {
                "principal": 5000000,
                "annual_rate": 8.5,
                "tenure_years": 20,
                "include_schedule": False,
            }
        }
    }


class EligibilityRequest(BaseModel):
    monthly_income: float = Field(..., gt=0, description="Gross monthly income in ₹")
    monthly_obligations: float = Field(0, ge=0, description="Existing EMIs/obligations ₹")
    cibil_score: int = Field(750, ge=300, le=900, description="CIBIL credit score")
    age: int = Field(30, ge=18, le=65, description="Applicant age in years")
    tenure_years: int = Field(20, ge=5, le=30)
    annual_rate: float = Field(8.5, gt=0, lt=20)
    is_woman: bool = Field(False, description="Women borrowers get 5bps concession")

    model_config = {
        "json_schema_extra": {
            "example": {
                "monthly_income": 100000,
                "monthly_obligations": 15000,
                "cibil_score": 750,
                "age": 32,
                "tenure_years": 20,
                "annual_rate": 8.5,
                "is_woman": False,
            }
        }
    }


class BankCompareRequest(BaseModel):
    loan_amount: float = Field(..., gt=0)
    tenure_years: int = Field(20, ge=5, le=30)
    cibil_score: int = Field(750, ge=300, le=900)
    is_woman: bool = Field(False)
    bank_ids: Optional[List[str]] = Field(None, description="Filter to specific banks. Omit for all.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "loan_amount": 5000000,
                "tenure_years": 20,
                "cibil_score": 750,
                "is_woman": False,
            }
        }
    }


class PrepaymentRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Original loan amount ₹")
    annual_rate: float = Field(..., gt=0, lt=30)
    tenure_years: int = Field(..., ge=1, le=30)
    prepayment_amount: float = Field(..., gt=0, description="Lump sum prepayment amount ₹")
    prepayment_at_month: int = Field(..., ge=1, description="Month number at which prepayment is made")
    prepayment_mode: Literal["reduce_tenure", "reduce_emi"] = Field(
        "reduce_tenure",
        description="reduce_tenure saves more interest; reduce_emi improves cash flow"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "principal": 5000000,
                "annual_rate": 8.5,
                "tenure_years": 20,
                "prepayment_amount": 500000,
                "prepayment_at_month": 36,
                "prepayment_mode": "reduce_tenure",
            }
        }
    }
