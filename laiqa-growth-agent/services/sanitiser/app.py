"""
PII Sanitiser Service
Redacts emails, phone numbers, names, addresses before sending to LLM.
"""
import os
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

app = FastAPI(title="Laiqa Sanitiser")

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

async def verify_key(x_api_key: str = Header(...)):
    if INTERNAL_API_KEY and x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Entities to redact - conservative for health brand
REDACT_ENTITIES = [
    "EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON",
    "LOCATION", "IP_ADDRESS", "URL", "CREDIT_CARD",
    "IBAN_CODE", "MEDICAL_LICENSE", "NRP"
]

class SanitiseRequest(BaseModel):
    text: str
    language: str = "en"

class SanitiseResponse(BaseModel):
    sanitised: str
    redacted_count: int

@app.post("/sanitise", response_model=SanitiseResponse, dependencies=[Depends(verify_key)])
def sanitise(req: SanitiseRequest):
    results = analyzer.analyze(
        text=req.text,
        entities=REDACT_ENTITIES,
        language=req.language
    )
    anonymised = anonymizer.anonymize(text=req.text, analyzer_results=results)
    return SanitiseResponse(
        sanitised=anonymised.text,
        redacted_count=len(results)
    )

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8001)))
