from typing import Dict, List, Optional
from pydantic import BaseModel, Field, RootModel, model_validator
from datetime import datetime

class HistoryTable(BaseModel):
    from_: datetime = Field(..., alias="from", description="start date, ej. 2025-09-01T00:00:00Z")
    to: datetime = Field(..., description="end date, ej. 2025-09-01T00:00:00Z")
    mac_address: str = Field(..., description="MAC_Address of sensor")
    attributes: Optional[List[str]]= Field(..., description="sensor type")
    product_type: str = Field(..., description="sensor type")
    model_config = {
        "populate_by_name": True
    }

class ValueWindow(BaseModel):
    from_: datetime = Field(..., alias="start_timestamp")
    to: datetime = Field(..., alias="end_timestamp")
    min_value: float = Field(..., alias="min_val")
    max_value: float = Field(..., alias="max_val")
    median_value: float = Field(..., alias="median_val")

class MacAggregate(BaseModel):
    aggregation_level: str
    attributes: Dict[str, List[ValueWindow]]

class UsageAggWindow(BaseModel):
    start_timestamp: datetime
    end_timestamp: datetime
    min_val: float
    max_val: float
    consumption: float

class MixedUsageAttributes(BaseModel):
    aggregation_level: str
    attributes: Dict[str, List[UsageAggWindow]]

class AggPayload(BaseModel):
    agg_attributes: MacAggregate
    usage_attributes: MixedUsageAttributes

class TableResponse(RootModel):
    root: Dict[str, AggPayload]

#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#------------------------------------------Mode table models------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------

class ModeTable(BaseModel):
    from_: datetime = Field(..., alias="from", description="start date, ej. 2025-09-01T00:00:00Z")
    to: datetime = Field(..., description="end date, ej. 2025-09-01T00:00:00Z")
    mac_address: str = Field(..., description="MAC_Address of sensor")

class ModeValueWindow(BaseModel):
    mode_value: int
    start_timestamp: datetime
    end_timestamp: datetime
    window_duration_S: int
    HEATSETP_min: Optional[float] = Field(None)
    HEATSETP_max: Optional[float] = Field(None)
    HEATSETP_median: Optional[float] = Field(None)
    COOLSETP_min: Optional[float] = Field(None)
    COOLSETP_max: Optional[float] = Field(None)
    COOLSETP_median: Optional[float] = Field(None)
    SPT_min: Optional[float] = Field(None)
    SPT_max: Optional[float] = Field(None)
    SPT_median: Optional[float] = Field(None)


class SensorResponse(BaseModel):
    attributes: Dict[str, List[ModeValueWindow]]

class ModeResponse(RootModel[Dict[str, SensorResponse]]):
    root: Dict[str, SensorResponse]


#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#------------------------------------------Mixed response models------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------

class MixedAggWindow(BaseModel):
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    min_val: Optional[float] = Field(None)
    max_val: Optional[float] = None
    median_val: Optional[float] = None

class MixedAggAttributes(BaseModel):
    aggregation_level: Optional[str] = None
    attributes: Dict[str, List["MixedAggWindow"]] = Field(default_factory=dict)

class MixedModeWindow(BaseModel):
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    mode_value: Optional[int] = None
    window_duration_S: Optional[int] = None
    HEATSETP_min: Optional[float] = None
    HEATSETP_max: Optional[float] = None
    HEATSETP_median: Optional[float] = None
    COOLSETP_min: Optional[float] = None
    COOLSETP_max: Optional[float] = None
    COOLSETP_median: Optional[float] = None
    SPT_min: Optional[float] = None
    SPT_max: Optional[float] = None
    SPT_median: Optional[float] = None

class MixedModeAttributes(BaseModel):
    attributes: Dict[str, List["MixedModeWindow"]] = Field(default_factory=dict)

class MixedPayload(BaseModel):
    agg_attributes: MixedAggAttributes = Field(default_factory=MixedAggAttributes)
    mode_attributes: MixedModeAttributes = Field(default_factory=MixedModeAttributes)

class MixedResponse(RootModel[Dict[str, MixedPayload]]):
    root: Dict[str, MixedPayload]