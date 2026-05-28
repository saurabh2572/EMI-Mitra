import datetime as dt

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///./bank_data.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


class Bank(Base):
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True, index=True)

    bank_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    short_name = Column(String, index=True)
    bank_type = Column(String)
    # logo = Column(String)

    rate_min = Column(Float)
    rate_max = Column(Float)
    rate_type = Column(String)
    benchmark = Column(String)

    min_loan_amount = Column(Integer)
    max_loan_amount = Column(Integer)

    min_tenure_years = Column(Integer)
    max_tenure_years = Column(Integer)

    processing_fee_pct = Column(Float)
    processing_fee_min = Column(Integer)
    processing_fee_max = Column(Integer)
    processing_fee_note = Column(String)

    prepayment_floating = Column(Float)
    prepayment_fixed = Column(Float)
    foreclosure_floating = Column(Float)
    foreclosure_fixed = Column(Float)

    min_cibil = Column(Integer)
    max_ltv = Column(Integer)

    min_age = Column(Integer)
    max_age = Column(Integer)

    womens_concession = Column(Float)

    special_features = Column(JSON)
    cibil_slabs = Column(JSON)

    created_at = Column(DateTime, default=dt.datetime.utcnow)
    last_updated = Column(
        DateTime,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
    )


BANKS = [
    {
        "id": "sbi",
        "name": "State Bank of India",
        "short_name": "SBI",
        "type": "public",
        # "logo": "🏦",
        "rate_min": 7.25,
        "rate_max": 8.70,
        "rate_type": "floating",
        "benchmark": "RLLR",
        "min_loan_amount": 500000,
        "max_loan_amount": 75000000,
        "min_tenure_years": 5,
        "max_tenure_years": 30,
        "processing_fee_pct": 0.35,
        "processing_fee_min": 2000,
        "processing_fee_max": 10000,
        "processing_fee_note": "0.35% (min ₹2,000, max ₹10,000). Waived in festive schemes.",
        "prepayment_floating": 0.0,
        "prepayment_fixed": 0.0,
        "foreclosure_floating": 0.0,
        "foreclosure_fixed": 0.0,
        "min_cibil": 650,
        "max_ltv": 90,
        "min_age": 18,
        "max_age": 70,
        "special_features": [
            "No prepayment penalty on floating rate",
            "PMAY subsidy eligible",
            "Special rate for women borrowers",
            "SBI MaxGain (OD facility) available",
        ],
        "womens_concession": 0.05,
        "cibil_slabs": [
            {"min": 750, "max": 900, "rate": 7.25},
            {"min": 700, "max": 749, "rate": 7.75},
            {"min": 650, "max": 699, "rate": 8.25},
            {"min": 0, "max": 649, "rate": 8.70},
        ],
    },

    {
        "id": "axis",
        "name": "Axis Bank",
        "short_name": "Axis",
        "type": "private",

        "rate_min": 7.60,
        "rate_max": 9.40,
        "rate_type": "floating",
        "benchmark": "RLLR",
        "min_loan_amount": 500000,
        "max_loan_amount": 50000000,
        "min_tenure_years": 5,
        "max_tenure_years": 30,
        "processing_fee_pct": 1.00,
        "processing_fee_min": 10000,
        "processing_fee_max": 75000,
        "processing_fee_note": "Up to 1% of loan amount (max ₹75,000) + GST",
        "prepayment_floating": 0.0,
        "prepayment_fixed": 2.0,
        "foreclosure_floating": 0.0,
        "foreclosure_fixed": 2.0,
        "min_cibil": 700,
        "max_ltv": 85,
        "min_age": 21,
        "max_age": 65,
        "special_features": [
            "Shubh Aarambh Home Loan - no EMI for 3 months",
            "Fast Forward - bi-monthly EMI option",
            "Asha Home Loan for informal income borrowers",
        ],
        "womens_concession": 0.05,
        "cibil_slabs": [
            {"min": 800, "max": 900, "rate": 7.60},
            {"min": 750, "max": 799, "rate": 8.00},
            {"min": 700, "max": 749, "rate": 8.60},
            {"min": 0,   "max": 699, "rate": 9.00},
        ],
    },
    {
        "id": "pnb",
        "name": "Punjab National Bank",
        "short_name": "PNB",
        "type": "public",
    
        "rate_min": 7.20,
        "rate_max": 10.00,
        "rate_type": "floating",
        "benchmark": "RLLR",
        "min_loan_amount": 500000,
        "max_loan_amount": 50000000,
        "min_tenure_years": 5,
        "max_tenure_years": 30,
        "processing_fee_pct": 0.35,
        "processing_fee_min": 2500,
        "processing_fee_max": 15000,
        "processing_fee_note": "0.35% (min ₹2,500, max ₹15,000) + GST. Occasional festive waivers.",
        "prepayment_floating": 0.0,
        "prepayment_fixed": 2.0,
        "foreclosure_floating": 0.0,
        "foreclosure_fixed": 2.0,
        "min_cibil": 650,
        "max_ltv": 90,
        "min_age": 18,
        "max_age": 70,
        "special_features": [
            "PNB Pride for government employees",
            "PNB Max Saver OD account",
            "No prepayment on floating",
            "PMAY eligible",
        ],
        "womens_concession": 0.05,
        "cibil_slabs": [
            {"min": 750, "max": 900, "rate": 7.20},
            {"min": 700, "max": 749, "rate": 7.70},
            {"min": 650, "max": 699, "rate": 8.30},
            {"min": 0,   "max": 649, "rate": 9.00},
        ],
    },
    {
        "id": "bob",
        "name": "Bank of Baroda",
        "short_name": "BoB",
        "type": "public",

        "rate_min": 7.45,
        "rate_max": 9.95,
        "rate_type": "floating",
        "benchmark": "RLLR",
        "min_loan_amount": 500000,
        "max_loan_amount": 100000000,
        "min_tenure_years": 5,
        "max_tenure_years": 30,
        "processing_fee_pct": 0.50,
        "processing_fee_min": 8500,
        "processing_fee_max": 25000,
        "processing_fee_note": "0.50% (min ₹8,500, max ₹25,000) + GST",
        "prepayment_floating": 0.0,
        "prepayment_fixed": 2.0,
        "foreclosure_floating": 0.0,
        "foreclosure_fixed": 2.0,
        "min_cibil": 675,
        "max_ltv": 90,
        "min_age": 21,
        "max_age": 70,
        "special_features": [
            "Baroda Home Loan Advantage",
            "Baroda CRE Home Loan for commercial RE",
            "Top-up loan facility",
        ],
        "womens_concession": 0.05,
        "cibil_slabs": [
            {"min": 750, "max": 900, "rate": 7.45},
            {"min": 700, "max": 749, "rate": 7.95},
            {"min": 675, "max": 699, "rate": 8.45},
            {"min": 0,   "max": 674, "rate": 9.00},
        ],
    },
    {
        "id": "kotak",
        "name": "Kotak Mahindra Bank",
        "short_name": "Kotak",
        "type": "private",

        "rate_min": 7.99,
        "rate_max": 9.50,
        "rate_type": "floating",
        "benchmark": "RLLR",
        "min_loan_amount": 1500000,
        "max_loan_amount": 50000000,
        "min_tenure_years": 5,
        "max_tenure_years": 20,
        "processing_fee_pct": 0.50,
        "processing_fee_min": 10000,
        "processing_fee_max": 50000,
        "processing_fee_note": "0.50% + GST (max ₹50,000)",
        "prepayment_floating": 0.0,
        "prepayment_fixed": 2.0,
        "foreclosure_floating": 0.0,
        "foreclosure_fixed": 2.0,
        "min_cibil": 720,
        "max_ltv": 85,
        "min_age": 21,
        "max_age": 60,
        "special_features": [
            "Digital approval in 10 minutes",
            "Balance transfer with top-up",
            "Kotak Home First for first-time buyers",
        ],
        "womens_concession": 0.05,
        "cibil_slabs": [
            {"min": 800, "max": 900, "rate": 7.99},
            {"min": 750, "max": 799, "rate": 8.40},
            {"min": 720, "max": 749, "rate": 8.90},
            {"min": 0,   "max": 719, "rate": 9.50},
        ],
    },
    {
        "id": "lichousing",
        "name": "LIC Housing Finance",
        "short_name": "LIC HFL",
        "type": "hfc",

        "rate_min": 7.50,
        "rate_max": 10.50,
        "rate_type": "floating",
        "benchmark": "PLR",
        "min_loan_amount": 500000,
        "max_loan_amount": 75000000,
        "min_tenure_years": 5,
        "max_tenure_years": 30,
        "processing_fee_pct": 0.50,
        "processing_fee_min": 10000,
        "processing_fee_max": 15000,
        "processing_fee_note": "0.50% (max ₹15,000) + GST",
        "prepayment_floating": 0.0,
        "prepayment_fixed": 2.0,
        "foreclosure_floating": 0.0,
        "foreclosure_fixed": 2.0,
        "min_cibil": 650,
        "max_ltv": 90,
        "min_age": 21,
        "max_age": 60,
        "special_features": [
            "LIC Griha Varishtha for senior citizens",
            "Plot + construction loan",
            "NRI home loans",
            "Home renovation loans",
        ],
        "womens_concession": 0.10,
        "cibil_slabs": [
            {"min": 750, "max": 900, "rate": 7.50},
            {"min": 700, "max": 749, "rate": 8.00},
            {"min": 650, "max": 699, "rate": 8.70},
            {"min": 0,   "max": 649, "rate": 9.50},
        ],
    },
]


def create_tables():
    Base.metadata.create_all(bind=engine)


def add_banks():
    db = SessionLocal()

    try:
        for bank in BANKS:
            existing_bank = (
                db.query(Bank)
                .filter(Bank.bank_id == bank["id"])
                .first()
            )

            if existing_bank:
                continue

            new_bank = Bank(
                bank_id=bank["id"],
                name=bank["name"],
                short_name=bank["short_name"],
                bank_type=bank["type"],
                rate_min=bank["rate_min"],
                rate_max=bank["rate_max"],
                rate_type=bank["rate_type"],
                benchmark=bank["benchmark"],
                min_loan_amount=bank["min_loan_amount"],
                max_loan_amount=bank["max_loan_amount"],
                min_tenure_years=bank["min_tenure_years"],
                max_tenure_years=bank["max_tenure_years"],
                processing_fee_pct=bank["processing_fee_pct"],
                processing_fee_min=bank["processing_fee_min"],
                processing_fee_max=bank["processing_fee_max"],
                processing_fee_note=bank["processing_fee_note"],
                prepayment_floating=bank["prepayment_floating"],
                prepayment_fixed=bank["prepayment_fixed"],
                foreclosure_floating=bank["foreclosure_floating"],
                foreclosure_fixed=bank["foreclosure_fixed"],
                min_cibil=bank["min_cibil"],
                max_ltv=bank["max_ltv"],
                min_age=bank["min_age"],
                max_age=bank["max_age"],
                womens_concession=bank["womens_concession"],
                special_features=bank["special_features"],
                cibil_slabs=bank["cibil_slabs"],
            )

            db.add(new_bank)

        db.commit()

    except Exception as error:
        db.rollback()
        print("Error adding banks:", error)

    finally:
        db.close()


def main():
    Base.metadata.drop_all(bind=engine)
    create_tables()
    add_banks()
    print("Banks added successfully!")


if __name__ == "__main__":
    main()