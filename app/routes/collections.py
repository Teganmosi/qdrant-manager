from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from ..config import settings
from ..schemas import CollectionCreateIn
from ..deps import get_current_user, require_role
from ..models import User  # Add this import
from ..audit import audit
from ..db import get_db

router = APIRouter(prefix="/collections", tags=["collections"])
client = QdrantClient(url=settings.QDRANT_URL, prefer_grpc=False)

@router.get("")
def list_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all Qdrant collections."""
    try:
        collections = client.get_collections().collections
        audit(db, current_user, "LIST_COLLECTIONS", "collections")
        return {"collections": [col.dict() for col in collections]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch collections: {str(e)}")

@router.post("")
def create_collection(
    data: CollectionCreateIn,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Create a new Qdrant collection."""
    try:
        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclid": Distance.EUCLID,
            "Dot": Distance.DOT,
            "Manhattan": Distance.MANHATTAN
        }
        
        client.create_collection(
            collection_name=data.name,
            vectors_config=VectorParams(
                size=data.vector_size,
                distance=distance_map[data.distance]
            )
        )
        audit(db, current_user, "CREATE_COLLECTION", data.name)
        return {"status": "success", "message": f"Collection '{data.name}' created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create collection: {str(e)}")

@router.delete("/{name}")
def delete_collection(
    name: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Delete a Qdrant collection."""
    try:
        client.delete_collection(name)
        audit(db, current_user, "DELETE_COLLECTION", name)
        return {"status": "success", "message": f"Collection '{name}' deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete collection: {str(e)}")