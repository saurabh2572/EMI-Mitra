from fastapi import APIRouter, HTTPException
from concepts import CONCEPTS

router = APIRouter()

@router.get("/explain-concept")
def explain_concept(term: str):

    key = term.lower().strip()

    concept = CONCEPTS.get(key)

    if not concept:
        raise HTTPException(
            status_code=404,
            detail="Concept not found"
        )

    return {
        "term": concept["term"],
        "explanation": concept["simple"],
        "voice_summary": concept["simple"]
    }


@router.get("/list-concepts")
def list_concepts():

    return {
        "concepts": list(CONCEPTS.keys())
    }