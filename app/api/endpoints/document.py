
# app/api/endpoints/document.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException , Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.document_service import DocumentService
from app.utils.auth import get_current_user

router = APIRouter()

@router.post("/upload/")
async def upload_document(
    file: UploadFile = File(...),
    token: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if file.content_type not in ["application/pdf", "application/vnd.ms-powerpoint", "text/csv"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, PPT, or CSV files.")

    document = DocumentService.upload_and_parse(file, db, current_user.id)
    return {"message": "File uploaded successfully", "document_id": document.id}
