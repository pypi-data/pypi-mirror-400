from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
class ApiDataModel(BaseModel):
    @classmethod
    def parse_tz_aware_datetime_to_iso_string(cls, v: datetime | str) -> str:
        if v is None:
            return None
        
        if isinstance(v, str):
            return v
        
        if isinstance(v, datetime):
            if v.tzinfo is None:
                raise ValueError("Datetime must be timezone-aware")
            dt_utc = v.astimezone(timezone.utc)
            return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        raise ValueError("Invalid datetime")
    
class ResourceBase(ApiDataModel):
    id: int = Field(description="ID")
    at: datetime = Field(description="When was last modified")
    
    
class QueryBase(BaseModel):
    pass

