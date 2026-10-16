import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import SourceRegistryEntry
from app.models.schemas import SourceRegistryResponse

router = APIRouter(prefix="/sources", tags=["Source Registry"])

@router.get("", response_model=list[SourceRegistryResponse])
def get_source_registry(db: Session = Depends(get_db)):
    entries = db.query(SourceRegistryEntry).all()
    results = []
    for e in entries:
        results.append(SourceRegistryResponse(
            id=e.id,
            provider_name=e.provider_name,
            provider_type=e.provider_type,
            supported_fields=json.loads(e.supported_fields_json or "[]"),
            access_method=e.access_method,
            auth_requirement=e.auth_requirement,
            cost_status=e.cost_status,
            license_url=e.license_url,
            attribution_text=e.attribution_text,
            rate_limit_info=e.rate_limit_info,
            data_retention_rules=e.data_retention_rules,
            is_enabled=e.is_enabled,
            last_sync=e.last_sync,
            last_error=e.last_error,
            coverage_limitations=e.coverage_limitations
        ))
    return results
