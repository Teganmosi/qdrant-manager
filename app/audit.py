from sqlalchemy.orm import Session
from .models import AuditLog, User
from fastapi import HTTPException
from typing import Optional, Dict, Any

def audit(db: Session, actor: User, action: str, resource: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an audit event for a user action.
    """
    if not action or len(action) > 128 or not resource or len(resource) > 255:
        raise HTTPException(status_code=400, detail="Invalid action or resource")
    try:
        log = AuditLog(user_id=actor.id, action=action, resource=resource, payload=payload)
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Audit logging failed")