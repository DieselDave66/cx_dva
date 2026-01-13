import os
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from config.settings import Settings, get_settings
from errors.exceptions import ConfigurationError
from models.tables import HistoryTable, TableResponse, ModeResponse, MixedResponse
from services.db.connector import   query
from typing import List, Dict, Any, Union, Optional
from datetime import datetime, timezone
from .utils.utils import calculate_aggregation_level
from .utils.utils import is_valid_mac_address

from .utils.queries import AGG_QUERY_WITH_ATTR, AGG_QUERY_NO_ATTR, USAGE_QUERY_WITH_ATTR, USAGE_QUERY_NO_ATTR, MODE_QUERY_WITH_ATTR, MODE_QUERY_NO_ATTR

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter(tags=["tables"])

logger = logging.getLogger(__name__)            

CATALOG = os.getenv("DATABRICKS_CATALOG")
SCHEMA = os.getenv("DATABRICKS_SCHEMA")
DBPATH = f"{CATALOG}.{SCHEMA}"
MODETABLE = os.getenv("DATABRICKS_TABLE_MODE")
USAGETABLE = os.getenv("DATABRICKS_TABLE_USAGE")

usage_list = ["TOTALKWH", "CHE_GASU", "GAS_KBTU", "CHE_GALS", "WTR_USED"]
agg_list = ["UPHTRTMP", "LOHTRTMP", "TEMP__IN", "TEMP_OUT", "SUB_COOL", "TEMP_OST","TEMP_SST", "TEMP_OLT","OAT_TEMP", "FLOW_GPM", "PRES_SUC", "PRES_LIQ", "ISACINPC","ISCSPEED", "INVSPEED"]
mode_list = ["HVACMODE","STATMODE"]

@router.get("/deviceHistory")
async def table(
    mac_address: str = Query(..., description="MAC Address of device"),
    product_type: str = Query(..., description="Device type, ex: heatpumpWaterHeaterGen5, econetControlCenter"),
    from_: datetime = Query(..., alias="from", description="start date, ej. 2025-09-01T00:00:00Z"),
    to: datetime = Query(..., description="end date, ej. 2025-09-01T00:00:00Z"),
    attributes: Optional[List[str]] = Query(None, description="One or more attributes, ex: LOHTRTMP, UPHTRTMP"),
    settings: Settings = Depends(get_settings),
):

    #if not is_valid_mac_address(mac_address):
    #    raise HTTPException(status_code=422, detail="Invalid MAC address format")
    
    if from_ > to:
        raise HTTPException(status_code=400, detail="The FROM date must be earlier than TO date")
        
    params = HistoryTable(
        from_=from_,
        to=to,
        mac_address=mac_address,
        attributes=attributes,
        product_type=product_type,
    )

    warehouse_id = settings.databricks_warehouse_id
    if not warehouse_id:
        raise ConfigurationError(
            message="SQL warehouse ID not configured",
            details={"setting": "databricks_warehouse_id"},
        )

    mode_types = "econetZoneController"
    mixed_types = "econetControlCenter"
    if params.attributes != None and params.attributes != [] and params.attributes != "":
        in_placeholders = ",".join(["?"] * len(params.attributes))

    if params.product_type == mode_types :

        table_path = f"{DBPATH}.{MODETABLE}"

        if params.attributes != None and params.attributes != [] and params.attributes != "":

            q= MODE_QUERY_WITH_ATTR.format(table_path=table_path, in_placeholders=in_placeholders)
            
            params = (
                params.mac_address,
                *params.attributes,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )

        else:

            q= MODE_QUERY_NO_ATTR.format(table_path=table_path)
            
            params = (
                params.mac_address,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )
        
        try:
            q_results : List[Dict[str, Any]] = query(q, warehouse_id, params)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while reading database: {e}")
        
        grouped: Dict[str, List[Dict[str, Any]]] = {}

        for row in q_results:
            key = row["mode_attr"]
            item = dict(row)
            item.pop("mac_address")
            item.pop("mode_attr")
            grouped.setdefault(key, []).append(item)

        result = {
            mac_address: {
                "attributes": grouped
            }
        }

        payload = jsonable_encoder(
            result, by_alias=True, custom_encoder={}
        )

        return ModeResponse(root=result)

    elif params.product_type == mixed_types:

        mac_address = str(mac_address)

        env_table, level = calculate_aggregation_level(from_, to)
        TABLE = os.getenv(env_table)

        table_path1 = f"{DBPATH}.{TABLE}"
        table_path3 = f"{DBPATH}.{MODETABLE}"

        common = []
        common3 = []

        if params.attributes != None and params.attributes != [] and params.attributes != "":

            common = any(att in params.attributes for att in agg_list)

            q = AGG_QUERY_WITH_ATTR.format(table_path=table_path1, in_placeholders=in_placeholders)

            params1 = (
                params.mac_address,
                *params.attributes,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )
        else:

            common = agg_list

            q = AGG_QUERY_NO_ATTR.format(table_path=table_path1)

            params1 = (
                params.mac_address,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )

        if common:

            try:
                q_results : List[Dict[str, Any]] = query(q, warehouse_id, params1)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error while reading database: {e}")

            grouped1: Dict[str, List[Dict[str, Any]]] = {}

            for row in q_results:
                key = row["attribute"]
                item = dict(row)
                item.pop("attribute", None)
                item.pop("mac_address", None)
                grouped1.setdefault(key, []).append(item)

            dictAggregations = {
                "aggregation_level": level,
                "attributes": grouped1
            }

        else:
            dictAggregations = {

            }
        ####

        if params.attributes != None and params.attributes != [] and params.attributes != "":
            common3 = any(att in params.attributes for att in mode_list)
            
            q= MODE_QUERY_WITH_ATTR.format(table_path=table_path3, in_placeholders=in_placeholders)
            
            params3 = (
                params.mac_address,
                *params.attributes,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )

        else:

            common3 = mode_list

            q= MODE_QUERY_NO_ATTR.format(table_path=table_path3)
            
            params3 = (
                params.mac_address,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )

        if common3:
            try:
                q_results : List[Dict[str, Any]] = query(q, warehouse_id, params3)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error while reading database: {e}")

            grouped3: Dict[str, List[Dict[str, Any]]] = {}

            for row in q_results:
                key = row["mode_attr"]
                item = dict(row)
                item.pop("mac_address")
                item.pop("mode_attr")
                grouped3.setdefault(key, []).append(item)

            dictMode = {
                    "attributes": grouped3
            }
        else:
            dictMode = {
                    "attributes": {}
            }

        finalDict = {
            mac_address:{
                "agg_attributes": dictAggregations,
                "mode_attributes": dictMode
            }
        }

        model = MixedResponse.model_validate(finalDict)
        payload = model.model_dump(by_alias=True, exclude_none=True)

        for mac, data in payload.items():
            if isinstance(data.get("agg_attributes"), dict) and not data["agg_attributes"]:
                data["agg_attributes"] = {}
            elif data["agg_attributes"].get("attributes", None) == {}:
                data["agg_attributes"] = {}

            if isinstance(data.get("mode_attributes"), dict) and not data["mode_attributes"]:
                data["mode_attributes"] = {}
            elif data["mode_attributes"].get("attributes", None) == {}:
                data["mode_attributes"] = {}

        return payload

    else:

        env_table, level = calculate_aggregation_level(from_, to)
        TABLE = os.getenv(env_table)
        table_path = f"{DBPATH}.{TABLE}"

        common = []
        common2 = []

        if params.attributes != None and params.attributes != [] and params.attributes != "":

            common = any(att in params.attributes for att in agg_list)
            common2 = any(att in params.attributes for att in usage_list)

            q = AGG_QUERY_WITH_ATTR.format(table_path=table_path, in_placeholders=in_placeholders)

            params1 = (
                params.mac_address,
                *params.attributes,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )

        else:

            common = usage_list
            common2 = agg_list
            
            q = AGG_QUERY_NO_ATTR.format(table_path=table_path)

            params1 = (
                params.mac_address,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )

        if common:
            try:
                q_results : List[Dict[str, Any]] = query(q, warehouse_id, params1)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error while reading database: {e}")

            grouped1: Dict[str, List[Dict[str, Any]]] = {}

            for row in q_results:
                key = row["attribute"]
                item = dict(row)
                item.pop("attribute", None)
                item.pop("mac_address", None)
                grouped1.setdefault(key, []).append(item)

            dictAggregations = {
                "aggregation_level": level,
                "attributes": grouped1
            }

        else:
            dictAggregations = {
                "aggregation_level": level,
                "attributes": {}
            }

        table_path = f"{DBPATH}.{USAGETABLE}"

        if params.attributes != None and params.attributes != [] and params.attributes != "":

            common = any(att in params.attributes for att in agg_list)
            common2 = any(att in params.attributes for att in usage_list)

            q = USAGE_QUERY_WITH_ATTR.format(table_path=table_path, in_placeholders=in_placeholders)

            params2 = (
                params.mac_address,
                *params.attributes,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )
        else:

            common = usage_list
            common1 = agg_list
            
            q = USAGE_QUERY_NO_ATTR.format(table_path=table_path)

            params2 = (
                params.mac_address,
                params.product_type,
                params.to.astimezone(timezone.utc),
                params.from_.astimezone(timezone.utc)
            )

        if common2:
            try:
                q_results : List[Dict[str, Any]] = query(q, warehouse_id, params2)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error while reading database: {e}")

            grouped2: Dict[str, List[Dict[str, Any]]] = {}

            for row in q_results:
                key = row["attribute"]
                item = dict(row)
                item.pop("attribute", None)
                item.pop("mac_address", None)
                grouped2.setdefault(key, []).append(item)

            dictUsage = {
                "aggregation_level": "dynamic",
                "attributes": grouped2
            }

        else:
            dictUsage = {
                "aggregation_level": "dynamic",
                "attributes": {}
            }
        
        mac_address = str(mac_address)

        finalDict = {
            mac_address:{
                "agg_attributes": dictAggregations,
                "usage_attributes": dictUsage
            }
        }

        model = TableResponse.model_validate(finalDict)
        payload = model.model_dump(by_alias=True, exclude_none=True)

        for mac, data in payload.items():
            if isinstance(data.get("agg_attributes"), dict) and not data["agg_attributes"]:
                data["agg_attributes"] = {}
            elif data["agg_attributes"].get("attributes", None) == {}:
                data["agg_attributes"] = {}

            if isinstance(data.get("usage_attributes"), dict) and not data["usage_attributes"]:
                data["usage_attributes"] = {}
            elif data["usage_attributes"].get("attributes", None) == {}:
                data["usage_attributes"] = {}

        return payload
