import re

def calculate_aggregation_level(start_date, end_date):

    minutes = (end_date-start_date).total_seconds() / 60

    ranges = (
        (60,  "DATABRICKS_TABLE_1MIN", "1 Minute"), #less than an hour
        (360, "DATABRICKS_TABLE_5MIN", "5 Minutes"), #less than 6 hours
        (1440,"DATABRICKS_TABLE_15MIN", "15 Minutes"), #less than a day
        (10080, "DATABRICKS_TABLE_1HOUR", "1 Hour"), #less than 7 days
        (40320, "DATABRICKS_TABLE_6HOUR", "6 Hours"), #1-4 weeks that a month, updated to 28 days
        (1051200, "DATABRICKS_TABLE_1WEEK", "1 Week") #less than 2 years
    )

    for limit, table, level in ranges: 
        if minutes <= limit:
            return table, level

def is_valid_mac_address(mac_address: str) -> bool:
    mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
    return bool(mac_pattern.match(mac_address))