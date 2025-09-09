from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from ..config import settings
from ..schemas import PointUpsertIn, PointsDeleteIn
from ..deps import get_current_user
from ..audit import audit
from ..db import get_db
from ..models import User  # Add this import

router = APIRouter(prefix="/points", tags=["points"])
client = QdrantClient(url=settings.QDRANT_URL, prefer_grpc=False)

@router.post("")
def upsert_point(
    data: PointUpsertIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upsert a point into a Qdrant collection."""
    try:
        client.upsert(
            collection_name=data.collection,
            points=[PointStruct(id=data.id, vector=data.vector, payload=data.payload)]
        )
        audit(db, current_user, "UPSERT_POINT", data.collection, {"point_id": data.id})
        return {"status": "success", "message": f"Point {data.id} upserted into '{data.collection}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to upsert point: {str(e)}")

@router.get("/{collection}")
def get_points(
    collection: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve points from a Qdrant collection."""
    try:
        result = client.scroll(collection_name=collection, limit=limit)
        points = [point.dict() for point in result[0]]
        audit(db, current_user, "GET_POINTS", collection, {"limit": limit})
        return {"points": points, "count": len(points)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch points: {str(e)}")

@router.delete("")
def delete_points(
    data: PointsDeleteIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete points from a Qdrant collection."""
    try:
        client.delete(
            collection_name=data.collection,
            points_selector={"points": data.ids}
        )
        audit(db, current_user, "DELETE_POINTS", data.collection, {"point_ids": data.ids})
        return {"status": "success", "message": f"Deleted points {data.ids} from '{data.collection}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete points: {str(e)}")