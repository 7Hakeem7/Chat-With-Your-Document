# app/services/document_service.py
import os
from uuid import uuid4
from fastapi import HTTPException
from app.utils.s3_utils import upload_file_to_s3
from unstructured.partition.auto import partition
from sqlalchemy.orm import Session
from app.models.document import Document
import magic

class DocumentService:
    # Define a custom temporary directory path
    TEMP_DIR = os.path.join(os.getcwd(), "temp")
    
    # Ensure the temporary directory exists
    os.makedirs(TEMP_DIR, exist_ok=True)

    @staticmethod
    def save_document(db: Session, title: str, content: str, user_id: int) -> Document:
        document = Document(title=title, content=content, user_id=user_id)
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def upload_and_parse(file, db: Session, user_id: int):
        file_id = str(uuid4())
        file_path = os.path.join(DocumentService.TEMP_DIR, f"{file_id}_{file.filename}")

        # Save the file locally for parsing
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

         # Detect file type using python-magic after saving the file
        file_type = magic.from_file(file_path, mime=True)
        if file_type not in ["application/pdf", "application/vnd.ms-powerpoint", "text/csv"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, PPT, or CSV files.")
        # Upload the file to S3
        upload_file_to_s3(file_path)

        # Parse the document content
        try:
            elements = partition(filename=file_path)
            content = ' '.join([element.text for element in elements if element.text])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during parsing: {str(e)}")

        # Clean up the local file
        os.remove(file_path)

        # Save parsed content to database
        return DocumentService.save_document(db, file.filename, content, user_id)