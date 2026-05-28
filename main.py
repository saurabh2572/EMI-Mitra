from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    emi,
    eligibility,
    prepayment,
    banks,
    concepts
)

BASE_URL= "http://127.0.0.1:8000/tools"

app = FastAPI(
    title="EMI Mitra API",
    description="Home Loan AI Assistant Backend for VAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(
    emi.router,
    prefix="/tools",
    tags=["EMI"]
)

app.include_router(
    eligibility.router,
    prefix="/tools",
    tags=["Eligibility"]
)

app.include_router(
    prepayment.router,
    prefix="/tools",
    tags=["Prepayment"]
)

app.include_router(
    banks.router,
    prefix="/tools",
    tags=["Banks"]
)

app.include_router(
    concepts.router,
    prefix="/tools",
    tags=["Concepts"]
)

@app.get("/")
def root():
    return {
        "service": "EMI Mitra API",
        "status": "running",
    }