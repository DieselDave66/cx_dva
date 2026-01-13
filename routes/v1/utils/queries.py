AGG_QUERY_WITH_ATTR = """
SELECT
  mac_address,
  attribute,
  start_timestamp,
  end_timestamp,
  min_val,
  max_val,
  median_val
FROM {table_path}
WHERE
  mac_address = ?
  AND attribute IN ({in_placeholders})
  AND product_type = ?
  AND start_timestamp < ?
  AND end_timestamp > ?
  ORDER BY start_timestamp
"""
AGG_QUERY_NO_ATTR = """
SELECT
  mac_address,
  attribute,
  start_timestamp,
  end_timestamp,
  min_val,
  max_val,
  median_val
FROM {table_path}
WHERE
  mac_address = ?
  AND product_type = ?
  AND start_timestamp < ?
  AND end_timestamp > ?
  ORDER BY start_timestamp
"""
USAGE_QUERY_WITH_ATTR="""
SELECT
  mac_address,
  attribute,
  start_timestamp,
  end_timestamp,
  min_val,
  max_val,
  consumption
FROM {table_path}
WHERE
  mac_address = ?
  AND attribute IN ({in_placeholders})
  AND product_type = ?
  AND start_timestamp < ?
  AND end_timestamp > ?
  ORDER BY start_timestamp
"""
USAGE_QUERY_NO_ATTR="""
SELECT
  mac_address,
  attribute,
  start_timestamp,
  end_timestamp,
  min_val,
  max_val,
  consumption
FROM {table_path}
WHERE
  mac_address = ?
  AND product_type = ?
  AND start_timestamp < ?
  AND end_timestamp > ?
  ORDER BY start_timestamp
"""
MODE_QUERY_WITH_ATTR="""
SELECT
  mac_address,
  mode_attr,
  mode_value,
  start_timestamp,
  end_timestamp,
  window_duration_S,
  HEATSETP_min,
  HEATSETP_max,
  HEATSETP_median,
  COOLSETP_min,
  COOLSETP_max,
  COOLSETP_median,
  SPT_min,
  SPT_max,
  SPT_median
FROM {table_path}
WHERE
  mac_address = ?
  AND mode_attr IN ({in_placeholders})
  AND product_type = ?
  AND start_timestamp < ?
  AND end_timestamp > ?
  ORDER BY start_timestamp
"""
MODE_QUERY_NO_ATTR="""
SELECT
  mac_address,
  mode_attr,
  mode_value,
  start_timestamp,
  end_timestamp,
  window_duration_S,
  HEATSETP_min,
  HEATSETP_max,
  HEATSETP_median,
  COOLSETP_min,
  COOLSETP_max,
  COOLSETP_median,
  SPT_min,
  SPT_max,
  SPT_median
FROM {table_path}
WHERE
  mac_address = ?
  AND product_type = ?
  AND start_timestamp < ?
  AND end_timestamp > ?
  ORDER BY start_timestamp
"""