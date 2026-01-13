SUPPORTED_VERSIONS = ["2025.R3.0"]

DEFAULT_USER_AGENT = "trendminer-sdk-python"

MAX_GET_SIZE = 10000  # Default max number of items for GET requests (multiple objects/endpoints)
MAX_CONTEXT_ITEM_POST_SIZE = 3000
MAX_CONTEXT_ITEM_GET_SIZE = 10000

MAX_INTERPOLATED_TAG_POINTS = 10000

MAX_TAG_CACHE = 50000
MAX_USER_CACHE = 50000
MAX_DATASOURCE_CACHE = 1000
MAX_FOLDER_CACHE = 10000

BUILTIN_DATASOURCES = {
    "FORMULA": "11111111-1111-1111-1111-111111111112",
    "AGGREGATION": "11111111-1111-1111-1111-111111111113",
    "DEMO": "11111111-1111-1111-1111-111111111114",
    "IMPORTED": "11111111-1111-1111-1111-111111111115",
    "MACHINE_LEARNING": "11111111-1111-1111-1111-111111111116",
}

TAG_TYPE_OPTIONS = ["ANALOG", "DISCRETE", "DIGITAL", "STRING"]

FOLDER_BROWSE_SIZE = 1000

ASSET_INCLUDE_OPTIONS = ["SELF", "ANCESTORS", "DESCENDANTS"]

CONTEXT_FIELD_OPTIONS = ["STRING", "ENUMERATION", "NUMERIC"]

CONTEXT_ICON_OPTIONS = [
    "alert--circle",
    "arrows--round",
    "bucket",
    "circle-success",
    "clipboard",
    "cracked",
    "file--check",
    "flame",
    "flask",
    "flow--line",
    "information",
    "person",
    "ruler",
    "snowflake",
    "spoon",
    "trending--down",
    "warning",
    "waterdrops",
    "waves",
    "wheelbarrow",
    "wrench",
]

CONTEXT_VIEW_OPTIONS = ["gantt", "grid"]

CONTEXT_OPERATOR_MAPPING = {
    "<": "LESS_THAN",
    ">": "GREATER_THAN",
    "=": "EQUAL",
    "!=": "NOT_EQUAL",
    "<=": "LESS_THAN_OR_EQUAL",
    ">=": "GREATER_THAN_OR_EQUAL",
}

WORK_ORGANIZER_CONTENT_OPTIONS = [
    "VIEW",
    "FINGERPRINT",
    "CONTEXT_LOGBOOK_VIEW",
    "DASHBOARD",
    "FORMULA",
    "AGGREGATION",
    "VALUE_BASED_SEARCH",
    "DIGITAL_STEP_SEARCH",
    "SIMILARITY_SEARCH",
    "AREA_SEARCH",
    "CROSS_ASSET_VALUE_BASED_SEARCH",
    "TREND_HUB_2_VIEW",
    "FILTER",
    "MACHINE_LEARNING",
    "PREDICTIVE",
    "LEGACY_FINGERPRINT",
    "MONITOR",
    "CUSTOM_CALCULATIONS",
]

LINE_STYLES = [
    "SOLID",
    "DASHED",
    "DOTTED",
    "DASHDOTDOTTED",
    "DASHDOTTED",
    "LOOSEDASHDOTTED",
]

CALCULATION_OPTIONS = {
    "mean": "mean",
    "avg": "mean",
    "average": "mean",
    "min": "min",
    "minimum": "min",
    "max": "max",
    "maximum": "max",
    "range": "range",
    "start": "startValue",
    "startValue": "startValue",
    "end": "endValue",
    "endValue": "endValue",
    "delta": "delta",
    "integral": "integral",
    "int": "integral",
    "stdev": "stdev",
    "std": "stdev",
    "standard deviation": "stdev",
}

SEARCH_CALCULATION_OPTIONS = {
    "mean": "MEAN",
    "avg": "MEAN",
    "average": "MEAN",
    "min": "MIN",
    "minimum": "MIN",
    "max": "MAX",
    "maximum": "MAX",
    "range": "RANGE",
    "start": "START",
    "startValue": "START",
    "end": "END",
    "endValue": "END",
    "delta": "DELTA",
    "integral": "INTEGRAL",
    "int": "INTEGRAL",
    "stdev": "STDEV",
    "std": "STDEV",
    "standard deviation": "STDEV",
}

AGGREGATION_OPTIONS = {
    "mean": "AVERAGE",
    "avg": "AVERAGE",
    "average": "AVERAGE",
    "min": "MINIMUM",
    "minimum": "MINIMUM",
    "max": "MAXIMUM",
    "maximum": "MAXIMUM",
    "range": "RANGE",
    "delta": "DELTA",
    "integral per day": "INTEGRAL_PER_DAY",
    "integral per hour": "INTEGRAL_PER_HOUR",
    "integral per minute": "INTEGRAL_PER_MINUTE",
    "integral per second": "INTEGRAL_PER_SECOND",
    "integral_per_day": "INTEGRAL_PER_DAY",
    "integral_per_hour": "INTEGRAL_PER_HOUR",
    "integral_per_minute": "INTEGRAL_PER_MINUTE",
    "integral_per_second": "INTEGRAL_PER_SECOND",
}

TIMESERIES_FORM_OPTIONS = ["interpolated", "index", "chart"]

VALUE_BASED_SEARCH_OPERATORS = ["<", ">", "=", "!=", "<=", ">=", "Constant", "In set"]

SEARCH_REFRESH_SLEEP = 0.2  # seconds to wait before checking if search results are done

MONITOR_TILE_OPTIONS = [
    "snowflake",
    "flame",
    "bucket",
    "ruler",
    "flask",
    "information",
    "waterdrops",
    "flow--line",
    "waves",
    "circle-success",
    "person",
    "arrows--round",
    "cracked",
    "wheelbarrow",
    "alert--circle",
    "clipboard",
    "wrench",
    "warning",
    "trending--down",
    "spoon",
    "wrench",
    "file--check"
]

VALUE_TILE_CONDITIONS = {
    "GREATER_THAN": "GREATER_THAN",
    ">": "GREATER_THAN",
    "GREATER_THAN_OR_EQUAL_TO": "GREATER_THAN_OR_EQUAL_TO",
    ">=": "GREATER_THAN_OR_EQUAL_TO",
    "LESS_THAN": "LESS_THAN",
    "<": "LESS_THAN",
    "LESS_THAN_OR_EQUAL_TO": "LESS_THAN_OR_EQUAL_TO",
    "<=": "LESS_THAN_OR_EQUAL_TO",
    "EQUAL_TO": "EQUAL_TO",
    "=": "EQUAL_TO",
    "NOT_EQUAL_TO": "NOT_EQUAL_TO",
    "!=": "NOT_EQUAL_TO",
    "<>": "NOT_EQUAL_TO",
    "BETWEEN": "BETWEEN",
    "NOT_BETWEEN": "NOT_BETWEEN",
    "not between": "NOT_BETWEEN",
    "CONTAINS": "CONTAINS",
    "DOES_NOT_CONTAIN": "DOES_NOT_CONTAIN",
    "does not contain": "DOES_NOT_CONTAIN",
}

INDEX_STATUS_OPTIONS = {
    "FAILED": "FAILED",
    "INCOMPLETE": "INCOMPLETE",
    "IN PROGRESS": "IN_PROGRESS",
    "IN_PROGRESS": "IN_PROGRESS",
    "OK": "OK",
    "OUT_OF_DATE": "OUT_OF_DATE",
    "OUT OF DATE": "OUT_OF_DATE",
    "STALE": "STALE",
    "DORMANT": "DORMANT",
}

CONTEXT_INTERVAL_OPTIONS = ["CUSTOM_CONTEXT_TIMESPAN", "PREDEFINED_CONTEXT_TIMESPAN_RANGE"]

CONTEXT_FILTER_MODES_EMPTY = {
    "EMPTY": "EMPTY",
    "NON_EMPTY": "NON_EMPTY",
    "non empty": "NON_EMPTY",
    "not empty": "NON_EMPTY",
}

CONTEXT_FILTER_MODES_STATES = {
    "OPEN_ONLY": "OPEN_ONLY",
    "open": "OPEN_ONLY",
    "open only": "OPEN_ONLY",
    "CLOSED_ONLY": "CLOSED_ONLY",
    "closed": "CLOSED_ONLY",
    "closed only": "CLOSED_ONLY",
}

ASSET_FRAMEWORK_SYNC_STATES = ["DONE", "DONE_WITH_ERRORS", "RUNNING", "FAILED", "CANCELLED"]

SIMILARITY_SEARCH_TYPES = {
    "absolute values": "ABSOLUTE_VALUES",
    "signal shape": "SIGNAL_SHAPE",
    "ABSOLUTE_VALUES": "ABSOLUTE_VALUES",
    "SIGNAL_SHAPE": "SIGNAL_SHAPE",
}

SIMILARITY_SEARCH_TYPE_MAPPING = {
    "ABSOLUTE_VALUES": "1",
    "SIGNAL_SHAPE": "2",
}

AGGREGATION_POSITIONS = {
    "center": "CENTER",
    "central": "CENTER",
    "forward": "START",
    "start": "START",
    "backward": "END",
    "end": "END",
}
