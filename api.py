from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from main import handle_email_processing  # Import the function from app.py

router = APIRouter()

class EmailRequest(BaseModel):
    email: str

class EntityItem(BaseModel):
    position: List[int]
    classification: str
    entity: str

class EmailResponse(BaseModel):
    input_email_body: str
    list_of_masked_entities: List[EntityItem]
    masked_email: str
    category_of_the_email: str

@router.post("/process-email", response_model=EmailResponse)
def process_email(request: EmailRequest):
    try:
        response = handle_email_processing(request.email)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
