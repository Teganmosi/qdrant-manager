from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from ..config import settings
from ..schemas import VectorSearchIn
from ..deps import get_current_user
from ..audit import audit
from ..db import get_db
from ..models import User  # Add this import

router = APIRouter(prefix="/search", tags=["search"])
client = QdrantClient(url=settings.QDRANT_URL, prefer_grpc=False)

@router.post("")
def vector_search(
    data: VectorSearchIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform vector search in a Qdrant collection."""
    try:
        result = client.search(
            collection_name=data.collection,
            query_vector=data.vector,
            limit=data.limit,
            with_payload=data.with_payload,
            score_threshold=data.score_threshold
        )
        audit(db, current_user, "VECTOR_SEARCH", data.collection, {"limit": data.limit})
        return {"results": [hit.dict() for hit in result]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search failed: {str(e)}")