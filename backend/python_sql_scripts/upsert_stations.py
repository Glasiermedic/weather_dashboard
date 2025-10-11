from wd_backend.Common.station_registry import upsert_station

upsert_station(
    "icao", "KSLE",
    ids_by_provider= {"awc": "KSLE", "twc": "KSLE"},
    name_by_provider= {"awc": "Salem Municipal Airport"},
    meta={"state" : "OR", "country":"US"}
)