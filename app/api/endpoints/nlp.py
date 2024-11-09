# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.services.nlp_service import NLPService
# from app.db.database import get_db

# router = APIRouter()

# @router.post("/index/")
# def index_documents(db: Session = Depends(get_db)):
#     try:
#         NLPService.index_documents(db)
#         return {"message": "Documents indexed successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/query/")
# def query_documents(query: str):
#     try:
#         results = NLPService.query_index(query)
#         if not results:
#             raise HTTPException(status_code=404, detail="No results found")
        
#         # Format results if needed (e.g., convert to a list of dicts)
#         formatted_results = [{"text": doc.page_content, "metadata": doc.metadata} for doc in results]
        
#         return {"results": formatted_results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.nlp_service import NLPService
from app.db.database import get_db

router = APIRouter()

@router.post("/index/")
def index_documents(db: Session = Depends(get_db)):
    try:
        NLPService.index_documents(db)
        return {"message": "Documents indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query/")
def query_documents(query: str):
    try:
        # Use query_documents instead of query_index
        result = NLPService.query_documents(query)
        if not result:
            raise HTTPException(status_code=404, detail="No results found")
        
        # Assuming result is a single answer from the LLM, not multiple documents
        return {"answer": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))