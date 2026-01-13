import logging
import uuid
from datetime import datetime
from typing import List, TypedDict, Union, Literal, Optional, Dict

import pandas as pd
from dotenv import load_dotenv
from fastmcp import FastMCP

from mcp_trendminer_server.settings import settings
from mcp_trendminer_server.auth import create_auth_provider
from mcp_trendminer_server.client import get_tm_client
from mcp_trendminer_server.client.cache import _get_tm_server_url
from mcp_trendminer_server.utils import check_server_connectivity, configure_logging, get_rich_handler

# ------------------------------------------------------------------------------
# MCP setup
# ------------------------------------------------------------------------------

load_dotenv()

# Configure logging with Rich for consistent formatting
configure_logging()

# Get logger after logging is configured
logger = logging.getLogger("mcp_trendminer_server")

# Create auth provider (None for credentials mode, OAuth provider for OAuth mode)
auth_provider = create_auth_provider()

# Create FastMCP instance
mcp = FastMCP(
    name="TrendMiner MCP",
    auth=auth_provider  # Can be None for credentials mode
)

# Log authentication mode
if settings.auth_mode == "credentials":
    logger.info("[Auth] Server configured with credentials mode (no OAuth)")
    logger.info("[Cache] Single-client caching enabled for credentials mode")
else:
    logger.info("[Auth] Server configured with OAuth mode")
    logger.info("[Cache] Token-based client caching enabled for performance optimization")

# ------------------------------------------------------------------------------
# In-memory dataset registry (for pandas DataFrames)
# ------------------------------------------------------------------------------

_DATASETS: Dict[str, pd.DataFrame] = {}


def _store_df(df: pd.DataFrame) -> str:
    """Store a DataFrame in memory and return an opaque handle."""
    handle = str(uuid.uuid4())
    _DATASETS[handle] = df
    logger.info(f"Stored DataFrame with handle={handle}, rows={len(df)}, cols={list(df.columns)}")
    return handle


def _get_df(handle: str) -> pd.DataFrame:
    """Retrieve a stored DataFrame by its handle."""
    if handle not in _DATASETS:
        raise ValueError(f"Unknown dataset handle: {handle}")
    return _DATASETS[handle]


def _build_trendhub_external_view_link(
        start_iso_utc: str,
        end_iso_utc: str,
        timeseries_names: List[str],
        server_url: str,
) -> Optional[str]:
    """
    Build a TrendHub externalView URL for the given time range and timeseries names.

    Parameters
    ----------
    start_iso_utc : str
        Start time in ISO 8601 format with UTC designator (e.g. '2025-12-01T00:00:00Z').
    end_iso_utc : str
        End time in ISO 8601 format with UTC designator.
    timeseries_names : List[str]
        List of tag names to include in the URL as `tag=` parameters.
    server_url : str
        TrendMiner server URL.

    Returns
    -------
    Optional[str]
        The constructed URL, or None if the server_url is not configured.
    """
    host = server_url
    if not host:
        return None

    # Convert ISO 8601 dates to epoch milliseconds
    start_epoch = int(datetime.fromisoformat(start_iso_utc.replace("Z", "+00:00")).timestamp() * 1000)
    end_epoch = int(datetime.fromisoformat(end_iso_utc.replace("Z", "+00:00")).timestamp() * 1000)

    # Build URL with timeseries tags
    tags_params = "&".join([f"tag={name}" for name in timeseries_names])
    url = (
        f"{host}/trendhub2/#/chart/externalView?"
        f"start={start_epoch}&end={end_epoch}&{tags_params}"
    )
    return url


# ------------------------------------------------------------------------------
# Typed definitions
# ------------------------------------------------------------------------------

class TagRef(TypedDict):
    tag_identifier: str
    tag_name: str
    tag_type: str
    tag_states: Optional[List[str]]
    tag_unit: str | None
    tag_description: str | None
    # Data availability fields (auto-populated)
    index_status: str
    data_start: Optional[str]
    data_end: Optional[str]


class QueryRef(TypedDict):
    """Defines a single condition in the value-based search."""
    tag_identifier: str
    operator: Literal[">", "<", "=", ">=", "<=", "!=", "Constant", "In set"]
    value: Optional[Union[float, str, List[str]]]


class SearchCalculationRef(TypedDict):
    """Defines a calculation to perform on the resulting events."""
    tag_identifier: str
    operation: Literal[
        "MEAN", "MIN", "MAX", "RANGE",
        "START", "END", "DELTA", "INTEGRAL", "STDEV"
    ]
    key: str  # The key/name for the resulting column.


class AssetTagInfo(TypedDict):
    """Information about a tag found through an attribute."""
    attribute_name: str
    tag_identifier: str
    tag_name: str
    tag_type: str
    tag_states: Optional[List[str]]
    tag_unit: str | None
    tag_description: str | None
    # Data availability fields (auto-populated)
    index_status: str
    data_start: Optional[str]
    data_end: Optional[str]


class AssetNode(TypedDict):
    """Represents an asset node in the hierarchy."""
    asset_name: str
    asset_identifier: str
    asset_path: str
    asset_description: Optional[str]
    tags: List[AssetTagInfo]
    child_assets: List['AssetNode']


# ------------------------------------------------------------------------------
# New TypedDict schemas for enhanced tag context
# ------------------------------------------------------------------------------

class SuggestedThresholds(TypedDict):
    """Pre-computed thresholds for value-based search queries."""
    low_threshold: float  # ~10th percentile
    high_threshold: float  # ~90th percentile
    very_low: float  # ~5th percentile
    very_high: float  # ~95th percentile


class ValueStats(TypedDict):
    """Statistical summary of numeric tag values."""
    min: float
    max: float
    mean: float
    recent_value: Optional[float]
    sample_period_start: str
    sample_period_end: str
    sample_points: int
    suggested_thresholds: SuggestedThresholds


class TagProfile(TypedDict):
    """Complete profile of a tag for LLM context."""
    tag_identifier: str
    tag_name: str
    tag_type: Literal["ANALOG", "DISCRETE", "DIGITAL", "STRING"]
    tag_unit: Optional[str]
    tag_description: Optional[str]
    tag_states: Optional[List[str]]
    index_status: str
    data_start: Optional[str]
    data_end: Optional[str]
    current_value: Optional[Union[float, str]]
    current_timestamp: Optional[str]
    value_stats: Optional[ValueStats]
    distinct_values: Optional[List[str]]
    recommended_approach: str
    error: Optional[str]


class TagAvailability(TypedDict):
    """Data availability info for a single tag."""
    tag_identifier: str
    tag_name: str
    index_status: str
    has_data_in_range: bool
    data_coverage_percent: Optional[float]
    data_start: Optional[str]
    data_end: Optional[str]
    issue: Optional[str]


class DataAvailabilityReport(TypedDict):
    """Report on data availability for multiple tags."""
    requested_start: str
    requested_end: str
    tags: List[TagAvailability]
    all_tags_available: bool
    summary: str
    error: Optional[str]


class DistinctValuesResult(TypedDict):
    """Result of getting distinct values for a STRING/DIGITAL tag."""
    tag_identifier: str
    tag_name: str
    tag_type: str
    all_known_values: List[str]
    value_count: int
    example_query: Optional[str]
    error: Optional[str]


# ------------------------------------------------------------------------------
# Monitor TypedDicts
# ------------------------------------------------------------------------------

class MonitorRef(TypedDict):
    """Information about a monitor."""
    identifier: str
    name: str
    enabled: bool
    description: Optional[str]
    trigger_count: Optional[int]
    last_triggered: Optional[str]
    created_at: Optional[str]
    search_type: str  # "VALUE", "SIMILARITY", "FINGERPRINT"


class MonitorNotificationConfig(TypedDict):
    """Notification configuration for a monitor."""
    type: Literal["email", "webhook"]
    # For email:
    to: Optional[List[str]]
    subject: Optional[str]
    message: Optional[str]
    # For webhook:
    url: Optional[str]


class MonitorCreationResult(TypedDict):
    """Result of creating a monitor."""
    identifier: Optional[str]
    name: Optional[str]
    enabled: bool
    url: Optional[str]
    error: Optional[str]


class MonitorManageResult(TypedDict):
    """Result of managing a monitor."""
    identifier: str
    action: str
    success: bool
    message: str
    error: Optional[str]


# ------------------------------------------------------------------------------
# Formula Tag TypedDicts
# ------------------------------------------------------------------------------

class FormulaTagMapping(TypedDict):
    """Maps a variable in the formula to a tag."""
    variable: str  # e.g., "A", "B", "X"
    tag_identifier: str


class FormulaTagResult(TypedDict):
    """Result of creating a formula tag."""
    tag_identifier: Optional[str]
    tag_name: Optional[str]
    formula: str
    mapping: Dict[str, str]  # variable -> tag_name
    error: Optional[str]


# ------------------------------------------------------------------------------
# Session URL TypedDict
# ------------------------------------------------------------------------------

class SessionUrlResult(TypedDict):
    """Result of generating a session URL."""
    session_url: Optional[str]
    tag_count: int
    start: str
    end: str
    error: Optional[str]


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

def _get_tag_index_info(tag) -> dict:
    """
    Get basic index information for a tag (efficient metadata call).

    Returns dict with:
        - index_status: str
        - data_start: Optional[str] (ISO format)
        - data_end: Optional[str] (ISO format)
        - tag_states: Optional[List[str]] (for STRING/DIGITAL tags)
    """
    result = {
        "index_status": "UNKNOWN",
        "data_start": None,
        "data_end": None,
        "tag_states": None,
    }

    try:
        index = tag.index
        result["index_status"] = getattr(index, "status", "UNKNOWN")

        # Get data boundaries if available
        data_start = getattr(index, "data_start", None)
        data_end = getattr(index, "data_end", None)

        if data_start is not None:
            result["data_start"] = data_start.isoformat() if hasattr(data_start, 'isoformat') else str(data_start)
        if data_end is not None:
            result["data_end"] = data_end.isoformat() if hasattr(data_end, 'isoformat') else str(data_end)
    except Exception as e:
        logger.warning(f"Failed to get index info for tag {getattr(tag, 'name', 'unknown')}: {e}")

    # Get states for STRING/DIGITAL tags
    try:
        tag_type = getattr(tag, "tag_type", "")
        if tag_type in ("STRING", "DIGITAL"):
            states = getattr(tag, "states", None)
            if states:
                result["tag_states"] = list(states.values())
    except Exception as e:
        logger.warning(f"Failed to get states for tag {getattr(tag, 'name', 'unknown')}: {e}")

    return result


def _collect_tags_from_asset(asset, flatten: bool = False) -> Union[AssetNode, List[AssetTagInfo]]:
    """
    Recursively collect all tags from an asset and its children.

    Parameters
    ----------
    asset : Asset
        The asset to traverse
    flatten : bool
        If True, return a flat list of all tags. If False, return hierarchical structure.

    Returns
    -------
    Union[AssetNode, List[AssetTagInfo]]
        Either a hierarchical AssetNode or a flat list of tags
    """
    tags = []
    child_assets = []

    try:
        children = asset.get_children()
    except Exception as e:
        logger.warning(f"Failed to get children for asset {getattr(asset, 'name', 'unknown')}: {e}")
        children = []

    for child in children:
        # Check if it's an Attribute (has a tag) or an Asset
        if hasattr(child, 'tag') and child.tag is not None:
            # This is an Attribute with a tag
            try:
                tag = child.tag
                # Get index info for data availability
                index_info = _get_tag_index_info(tag)
                tag_states = list(getattr(tag, "states", {}).values()) if getattr(tag, "states", None) else None
                if index_info["tag_states"] and not tag_states:
                    tag_states = index_info["tag_states"]

                tag_info: AssetTagInfo = {
                    "attribute_name": getattr(child, "name", "unknown"),
                    "attribute_path": getattr(child, "path", "unknown"),
                    "tag_identifier": getattr(tag, "identifier", "unknown"),
                    "tag_name": getattr(tag, "name", "unknown"),
                    "tag_type": getattr(tag, "tag_type", "unknown"),
                    "tag_states": tag_states,
                    "tag_unit": getattr(tag, "unit", None),
                    "tag_description": getattr(tag, "description", None),
                    "index_status": index_info["index_status"],
                    "data_start": index_info["data_start"],
                    "data_end": index_info["data_end"],
                }
                tags.append(tag_info)
            except Exception as e:
                logger.warning(f"Failed to extract tag from attribute {getattr(child, 'name', 'unknown')}: {e}")
        elif hasattr(child, 'get_children'):
            # This is a child Asset - recurse into it
            child_result = _collect_tags_from_asset(child, flatten=flatten)
            if flatten:
                tags.extend(child_result)
            else:
                child_assets.append(child_result)

    if flatten:
        return tags
    else:
        node: AssetNode = {
            "asset_name": getattr(asset, "name", "unknown"),
            "asset_identifier": getattr(asset, "identifier", "unknown"),
            "asset_path": getattr(asset, "path", "unknown"),
            "asset_description": getattr(asset, "description", None),
            "tags": tags,
            "child_assets": child_assets,
        }
        return node


# ------------------------------------------------------------------------------
# Tools
# ------------------------------------------------------------------------------

@mcp.tool()
def search_tags(name: str) -> List[TagRef]:
    """
    Search TrendMiner tags by name. Use wildcards (*) for broad searches.

    IMPORTANT: Results include data availability info (index_status, data_start, data_end)
    to help you select valid time ranges for queries.

    For STRING/DIGITAL tags, tag_states shows all possible values you can use in
    value_based_search queries with "=" or "In set" operators.

    After finding tags, you can:
    - Use get_tag_profile(tag_identifier) to get value statistics and thresholds
    - Use get_distinct_values(tag_identifier) to explore STRING/DIGITAL tag values
    - Use check_data_availability(tag_identifiers, start, end) to verify a time range

    Examples
    --------
    - search_tags("*TEMP*") - Find all temperature tags
    - search_tags("TM5-BP2-*") - Find tags with specific prefix
    """
    tm_client = get_tm_client()
    tags = tm_client.tag.search(name)
    results = []
    for t in tags:
        # Get basic info
        tag_ref = {
            "tag_identifier": t.identifier,
            "tag_name": t.name,
            "tag_type": t.tag_type,
            "tag_states": list(getattr(t, "states", {}).values()) if getattr(t, "states", None) else None,
            "tag_unit": getattr(t, "unit", None),
            "tag_description": getattr(t, "description", None),
        }
        # Add index/data availability info
        index_info = _get_tag_index_info(t)
        tag_ref["index_status"] = index_info["index_status"]
        tag_ref["data_start"] = index_info["data_start"]
        tag_ref["data_end"] = index_info["data_end"]
        # Override tag_states if we got more info from index
        if index_info["tag_states"] and not tag_ref["tag_states"]:
            tag_ref["tag_states"] = index_info["tag_states"]
        results.append(tag_ref)
    return results


@mcp.tool()
def navigate_asset_hierarchy(
        asset_path: str,
        flatten: bool = False,
) -> Union[dict, List[AssetTagInfo]]:
    """
    Navigate the asset hierarchy to discover all tags under a given asset.

    This tool allows you to find tags without knowing their exact names by
    browsing through the asset structure. It recursively traverses all child
    assets and attributes, collecting tag information.

    IMPORTANT: Results include data availability info (index_status, data_start, data_end)
    to help you select valid time ranges for queries.

    For STRING/DIGITAL tags, tag_states shows all possible values you can use in
    value_based_search queries with "=" or "In set" operators.

    Parameters
    ----------
    asset_path : str
        Path to the asset (e.g., "Batch Line" or "Plant/Reactor1").
        This is a human-readable path using asset names separated by '/'.
    flatten : bool, default False
        If True, returns a flat list of all tags found in the hierarchy.
        If False, returns a hierarchical structure showing the asset tree.

    Returns
    -------
    Union[dict, List[AssetTagInfo]]
        If flatten=True: List of all tags found with data availability info.
        If flatten=False: Hierarchical structure with assets and their tags.

    Examples
    --------
    - Navigate to a specific asset: navigate_asset_hierarchy("Batch Line")
    - Get flat list of all tags: navigate_asset_hierarchy("Batch Line", flatten=True)
    """
    tm_client = get_tm_client()
    try:
        # Get the asset from the path
        asset = tm_client.asset.from_path(asset_path)
    except Exception as e:
        return {"error": f"Failed to find asset at path '{asset_path}': {str(e)}"}

    try:
        result = _collect_tags_from_asset(asset, flatten=flatten)

        if flatten:
            return result
        else:
            return {
                "error": None,
                "asset_hierarchy": result,
                "total_tags_found": len(_collect_tags_from_asset(asset, flatten=True)),
            }
    except Exception as e:
        return {"error": f"Failed to navigate asset hierarchy: {str(e)}"}


@mcp.tool()
def get_tag_data(
        tag_identifiers: Union[str, List[str]],
        start: str,
        end: str,
        freq: str = "1m",
        max_tags: int = 20,
) -> dict:
    """
    Fetch continuous time-series data for analysis, plotting, or export.

    WHEN TO USE THIS TOOL:
    - Visualizing trends over time
    - Correlation analysis between multiple tags
    - Custom Python analysis with run_python_on_dataset
    - Exporting data for external tools

    WHEN TO USE value_based_search INSTEAD:
    - Finding specific events/conditions (e.g., "when was temp > 100?")
    - Need event-based statistics (mean/max during each event)
    - Working with process states or batch identifiers

    BEFORE USING:
    1. Check data_start/data_end from search_tags to verify time range has data
    2. Use check_data_availability for multiple tags
    3. Consider data volume: 1 month at 1m = ~43,000 points per tag

    FREQUENCY GUIDELINES:
    - "1m": Good for < 1 day, detailed analysis
    - "5m": Good for 1-7 days
    - "15m": Good for 1-4 weeks
    - "1h": Good for 1-6 months
    - "1d": Good for > 6 months

    Parameters
    ----------
    tag_identifiers : Union[str, List[str]]
        Single tag identifier or list of identifiers
    start : str
        Start time (use data_start from search results)
    end : str
        End time (use data_end from search results)
    freq : str, default "1m"
        Data frequency. Use coarser frequency for larger time ranges.
    max_tags : int, default 20
        Maximum number of tags allowed in a single request

    Returns
    -------
    dict
        Dataset handle for use with run_python_on_dataset, row count, columns, preview

    Examples
    --------
    Single tag for one day:
        get_tag_data("abc123", "2024-01-01", "2024-01-02", freq="1m")

    Multiple tags for correlation over a month:
        get_tag_data(["tag1", "tag2", "tag3"], "2024-01-01", "2024-02-01", freq="15m")
    """
    # Normalize to list
    if isinstance(tag_identifiers, str):
        tag_identifiers = [tag_identifiers]

    # Validate tag count
    if len(tag_identifiers) > max_tags:
        return {
            "error": f"Too many tags requested ({len(tag_identifiers)}). Maximum is {max_tags}."
        }

    if len(tag_identifiers) == 0:
        return {"error": "No tag identifiers provided."}

    tm_client = get_tm_client()

    # Parse time interval
    try:
        interval = pd.Interval(
            pd.Timestamp(start, tz=tm_client.tz),
            pd.Timestamp(end, tz=tm_client.tz),
            closed="both"
        )
    except Exception as e:
        return {"error": f"Failed to parse time range: {str(e)}"}

    # Calculate expected data points for warning
    duration_seconds = (interval.right - interval.left).total_seconds()
    freq_seconds = pd.Timedelta(freq).total_seconds()
    expected_points = int(duration_seconds / freq_seconds)

    # Warn if dataset will be very large
    warning = None
    if expected_points > 10000:
        suggested_freq = None
        if expected_points > 50000:
            suggested_freq = "1h"
        elif expected_points > 20000:
            suggested_freq = "15m"

        warning = (f"Large dataset warning: ~{expected_points} points expected per tag. "
                   f"Consider using coarser frequency" +
                   (f" like '{suggested_freq}'" if suggested_freq else "") +
                   " to reduce memory usage.")
        logger.warning(warning)

    # Fetch tags and data
    tags = []
    tag_names = []
    series_list = []

    for tag_id in tag_identifiers:
        try:
            tag = tm_client.tag.from_identifier(tag_id)
            tags.append(tag)
            tag_names.append(getattr(tag, "name", tag_id))
        except Exception as e:
            return {"error": f"Failed to resolve tag '{tag_id}': {str(e)}"}

        try:
            series = tag.get_data(interval=interval, freq=freq)
            series_list.append(series)
        except Exception as e:
            return {"error": f"Failed to fetch data for tag '{tag_id}': {str(e)}"}

    # Build DataFrame
    if len(tags) == 1:
        # Single tag: simple timestamp + value DataFrame
        if series_list[0].empty:
            return {"error": "No data found for this range"}

        df = series_list[0].to_frame(name=tag_names[0]).reset_index()
        df.columns = ["timestamp", "value"]
    else:
        # Multiple tags: timestamp + one column per tag
        # Use outer join to keep all timestamps, forward-fill missing values
        df_dict = {"timestamp": []}
        all_timestamps = set()

        # Collect all unique timestamps
        for series in series_list:
            all_timestamps.update(series.index)

        if not all_timestamps:
            return {"error": "No data found for any tags in this range"}

        # Sort timestamps
        all_timestamps = sorted(all_timestamps)
        df = pd.DataFrame({"timestamp": all_timestamps})

        # Add each tag as a column
        for tag_name, series in zip(tag_names, series_list):
            tag_df = series.to_frame(name=tag_name).reset_index()
            tag_df.columns = ["timestamp", tag_name]
            df = df.merge(tag_df, on="timestamp", how="left")

        # Forward-fill missing values for better continuity
        for tag_name in tag_names:
            df[tag_name] = df[tag_name].ffill()

    # Store dataset
    handle = _store_df(df)

    # Build response
    return {
        "error": None,
        "warning": warning,
        "dataset_handle": handle,
        "row_count": len(df),
        "columns": list(df.columns),
        "tag_count": len(tags),
        "tag_names": tag_names,
        "frequency": freq,
        "time_range": f"{start} to {end}",
        "preview": df.head(10).to_dict(orient="records"),
        "summary": (f"Fetched {len(df)} data points for {len(tags)} tag(s) "
                    f"from {start} to {end} at {freq} frequency.")
    }


@mcp.tool()
def value_based_search(
        queries: List[QueryRef],
        start_time: str,
        end_time: str,
        calculations: Optional[List[SearchCalculationRef]] = None,
        duration: str = "2m",
        combine_operator: Literal["AND", "OR"] = "AND",
) -> dict:
    """
    Find time periods (events) where tag conditions are met, with optional calculations.

    WHEN TO USE THIS TOOL:
    - Finding when values exceeded/dropped below thresholds
    - Identifying process states or product batches (e.g., Product = "ALPHA")
    - Correlating multiple conditions across tags
    - Generating event datasets for statistical analysis

    WHEN TO USE get_tag_data INSTEAD:
    - Need continuous time-series data for plotting
    - Want to see actual values over time (not just when conditions met)
    - Performing time-series calculations that need all data points

    BEFORE USING THIS TOOL:
    1. Check data_start/data_end from search_tags results to pick valid time range
    2. Use get_tag_profile to understand value ranges and pick appropriate thresholds
    3. For STRING/DIGITAL tags, check tag_states in search results or use get_distinct_values

    OPERATORS:
    - Numeric tags (ANALOG/DISCRETE): ">", "<", ">=", "<=", "=", "!=", "Constant"
    - STRING/DIGITAL tags: "=" (single value), "In set" (list of values)

    CALCULATIONS (optional):
    Compute statistics for each found event: MEAN, MIN, MAX, RANGE, START, END, DELTA, INTEGRAL, STDEV

    Parameters
    ----------
    queries : List[QueryRef]
        List of conditions. Each has: tag_identifier, operator, value
    start_time : str
        Start time (parseable by pandas.Timestamp). Use data_start from search results.
    end_time : str
        End time (parseable by pandas.Timestamp). Use data_end from search results.
    calculations : List[SearchCalculationRef], optional
        Statistics to compute for each event.
    duration : str, default "2m"
        Minimum duration for events to be included.
    combine_operator : "AND" | "OR", default "AND"
        How to combine multiple query conditions.

    Examples
    --------
    Find high temperature events:
        value_based_search(
            queries=[{"tag_identifier": "abc123", "operator": ">", "value": 95}],
            start_time="2024-01-01", end_time="2024-03-31"
        )

    Find ALPHA product batches with calculations:
        value_based_search(
            queries=[{"tag_identifier": "product-tag-id", "operator": "=", "value": "ALPHA"}],
            start_time="2024-01-01", end_time="2024-12-31",
            calculations=[
                {"tag_identifier": "conc-tag-id", "operation": "MAX", "key": "max_concentration"},
                {"tag_identifier": "temp-tag-id", "operation": "MEAN", "key": "avg_temperature"}
            ]
        )
    """
    tm_client = get_tm_client()

    # 1. Build SDK query list
    sdk_queries = []
    for q_ref in queries:
        tag_id = q_ref.get("tag_identifier")
        operator = q_ref.get("operator")
        value = q_ref.get("value")

        if not all([tag_id, operator]):
            return {"error": "Each query must contain 'tag_identifier' and 'operator'."}

        # Check if value is required but missing
        if operator != "Constant" and value is None:
            return {"error": f"Operator '{operator}' requires a 'value' for tag '{tag_id}'."}

        # Resolve tag identifier to TrendMiner tag object
        try:
            tag = tm_client.tag.from_identifier(tag_id)
        except Exception as e:
            return {"error": f"Tag '{tag_id}' could not be resolved: {str(e)}"}

        # Build query tuple based on operator
        if operator == "Constant":
            sdk_queries.append((tag, operator))
        else:
            sdk_queries.append((tag, operator, value))

    if not sdk_queries:
        return {"error": "No valid search queries were constructed."}

    # 2. Build calculation dictionary if provided
    sdk_calculations = {}
    if calculations:
        for calc_ref in calculations:
            try:
                tag = tm_client.tag.from_identifier(calc_ref["tag_identifier"])
                sdk_calculations[calc_ref["key"]] = (tag, calc_ref["operation"])
            except Exception as e:
                return {
                    "error": f"Tag '{calc_ref['tag_identifier']}' for calculation could not be resolved: {str(e)}"
                }

    logger.info(f"queries: {sdk_queries}")
    logger.info(f"calculations: {sdk_calculations}")

    # 3. Create search object
    try:
        search = tm_client.search.value(
            queries=sdk_queries,
            duration=duration,
            operator=combine_operator,
            calculations=sdk_calculations if sdk_calculations else None,
        )
    except Exception as e:
        return {"error": f"Failed to create search: {str(e)}"}

    # 4. Execute search
    time_interval = pd.Interval(
        left=pd.Timestamp(start_time, tz=tm_client.tz),
        right=pd.Timestamp(end_time, tz=tm_client.tz),
        closed="both",
    )
    logger.info(f"time_interval: {time_interval}")

    try:
        results = search.get_results(intervals=time_interval)
    except Exception as e:
        return {"error": f"Search execution failed: {str(e)}"}

    logger.info(f"results type: {type(results)}")

    # Add start/end columns for convenience
    results.insert(0, "start", [iv.left for iv in results.index])
    results.insert(1, "end", [iv.right for iv in results.index])

    if results.empty:
        return {
            "dataset_handle": None,
            "row_count": 0,
            "columns": [],
            "index_type": type(results.index).__name__,
            "preview": [],
            "summary": "No events found matching the criteria in this time range.",
            "error": None,
        }

    # 6. Store DataFrame and build response
    handle = _store_df(results)

    preview_rows = results.head(10).to_dict(orient="records")

    summary_lines = [f"Found {len(results)} events."]
    for i, row in enumerate(preview_rows, 1):
        extra_cols = {k: v for k, v in row.items() if k not in ("start", "end")}
        extra_str = ", ".join(f"{k}={v}" for k, v in extra_cols.items())
        summary_lines.append(
            f"{i}. {row['start']} → {row['end']}"
            + (f" | {extra_str}" if extra_str else "")
        )
    if len(results) > 10:
        summary_lines.append(f"... and {len(results) - 10} more events.")

    return {
        "dataset_handle": handle,
        "row_count": int(len(results)),
        "columns": list(results.columns),
        "index_type": type(results.index).__name__,
        "preview": preview_rows,
        "summary": "\n".join(summary_lines),
        "error": None,
    }


@mcp.tool()
def add_calculations(
        dataset_handle: str,
        calculations: List[SearchCalculationRef],
) -> dict:
    """
    Add calculations to an existing pandas DataFrame with an IntervalIndex.

    This tool does NOT re-run a value-based search.
    It applies calculations directly on the existing intervals using
    `df.interval.calculate(...)`.

    Parameters
    ----------
    dataset_handle : str
        Handle of a stored DataFrame with a pandas IntervalIndex.
    calculations : List[SearchCalculationRef]
        List of calculations to add (tag_identifier, operation, key).
    """
    # Retrieve dataset
    try:
        df = _get_df(dataset_handle)
    except Exception as e:
        return {"error": str(e)}

    # Validate IntervalIndex
    if not isinstance(df.index, pd.IntervalIndex):
        return {
            "error": "Dataset index is not a pandas IntervalIndex; cannot add calculations."
        }

    if not calculations:
        return {"error": "No calculations provided."}

    tm_client = get_tm_client()

    # Apply calculations
    try:
        for calc in calculations:
            tag_identifier = calc["tag_identifier"]
            operation = calc["operation"]
            key = calc["key"]

            try:
                tag = tm_client.tag.from_identifier(tag_identifier)
            except Exception as e:
                return {
                    "error": f"Failed to resolve tag '{tag_identifier}': {e}"
                }

            # TrendMiner IntervalIndex calculation helper
            df = df.interval.calculate(
                tag=tag,
                operation=operation,
                name=key,
            )

    except Exception as e:
        return {"error": f"Failed to add calculations: {e}"}

    # Store updated DataFrame as new dataset
    new_handle = _store_df(df)

    return {
        "dataset_handle": new_handle,
        "row_count": int(len(df)),
        "columns": list(df.columns),
        "index_type": type(df.index).__name__,
        "preview": df.head(10).to_dict(orient="records"),
        "summary": f"Added {len(calculations)} calculation(s).",
        "error": None,
    }


@mcp.tool()
def run_python_on_dataset(dataset_handle: str, code: str) -> dict:
    """
    Execute Python code with `df` (pandas DataFrame) and `pd` available.

    Convention:
      - The code should assign a variable `result`.
      - If `result` is a DataFrame, we store it and return a new handle + preview.
      - Otherwise we return a string representation of `result`.

    NOTE: This uses `exec` and is intended for local use with trusted input.
    """
    try:
        df = _get_df(dataset_handle)
    except Exception as e:
        return {"error": str(e)}

    local_env = {"df": df, "pd": pd}

    try:
        exec(code, {}, local_env)
    except Exception as e:
        return {"error": f"Execution error: {e}"}

    result = local_env.get("result", None)

    out: dict = {
        "error": None,
        "result_type": type(result).__name__,
        "text": repr(result),
        "new_dataset_handle": None,
        "preview": None,
    }

    if isinstance(result, pd.DataFrame):
        new_handle = _store_df(result)
        out["new_dataset_handle"] = new_handle
        out["preview"] = result.head(10).to_dict(orient="records")

    return out


@mcp.tool()
def create_trend_view(
        tag_identifiers: List[str],
        start_times: List[str],
        end_times: List[str],
        view_name: str = "New View",
) -> dict:
    """
    Create and save a TrendHub view with multiple tags and/or time layers.

    Parameters
    ----------
    tag_identifiers : List[str]
        List of tag identifiers to include in the view.
    start_times : List[str]
        Start times for each layer, parseable by pandas.Timestamp.
    end_times : List[str]
        End times for each layer, parseable by pandas.Timestamp.
    view_name : str, default "New View"
        Name of the TrendHub view that will be saved.

    Returns
    -------
    dict
        A dictionary with basic information about the saved view or an error message:
          - error: str | None
          - name: str | None
          - layers_count: int
          - tags_count: int
          - view_id: Any | None
          - url: str | None
    """
    tm_client = get_tm_client()

    try:
        # Resolve all tags
        tags = []
        for tag_id in tag_identifiers:
            try:
                tag = tm_client.tag.from_identifier(tag_id)
                tags.append(tag)
            except Exception as e:
                return {"error": f"Failed to resolve tag '{tag_id}': {e}"}

        if not tags:
            return {"error": "No valid tags provided."}

        # Build layers from start/end time pairs
        if len(start_times) != len(end_times):
            return {"error": f"Mismatched start_times ({len(start_times)}) and end_times ({len(end_times)})."}

        layers = []
        for start_str, end_str in zip(start_times, end_times):
            layer = pd.Interval(
                left=pd.Timestamp(start_str, tz=tm_client.tz),
                right=pd.Timestamp(end_str, tz=tm_client.tz),
                closed="both",
            )
            layers.append(layer)

        if not layers:
            return {"error": "No layers provided."}

        # Use the first layer as context interval
        context_interval = layers[0]

        # Create and save TrendHub view
        view = tm_client.trend.view(
            entries=tags,
            layers=layers,
            context_interval=context_interval,
            name=view_name,
        )
        view.save()

        # Get shareable session URL
        session_url = None
        try:
            session_url = view.get_session_url()
        except Exception as e:
            logger.warning(f"Failed to get session URL: {e}")

        # Build external view link using first layer and all tag names
        first_layer = layers[0]
        start_iso_utc = first_layer.left.tz_convert("UTC").isoformat().replace("+00:00", "Z")
        end_iso_utc = first_layer.right.tz_convert("UTC").isoformat().replace("+00:00", "Z")
        tag_names = [getattr(tag, "name", tag_identifiers[i]) for i, tag in enumerate(tags)]
        external_url = _build_trendhub_external_view_link(
            start_iso_utc=start_iso_utc,
            end_iso_utc=end_iso_utc,
            timeseries_names=tag_names,
            server_url=_get_tm_server_url(),
        )

        return {
            "error": None,
            "name": getattr(view, "name", view_name),
            "layers_count": len(layers),
            "tags_count": len(tags),
            "view_id": getattr(view, "id", None),
            "url": external_url,
            "session_url": session_url,
        }
    except Exception as e:
        return {
            "error": str(e),
            "name": None,
            "layers_count": 0,
            "tags_count": 0,
            "view_id": None,
            "url": None,
            "session_url": None,
        }


@mcp.tool()
def get_tag_profile(
        tag_identifier: str,
        sample_window_hours: int = 24,
) -> TagProfile:
    """
    Get comprehensive profile of a tag including value statistics and suggested thresholds.

    Use this tool after finding tags via search_tags or navigate_asset_hierarchy
    to understand the data before constructing queries.

    For ANALOG/DISCRETE tags, returns value statistics (min, max, mean) and
    suggested thresholds for use in value_based_search queries.

    For STRING/DIGITAL tags, returns all distinct values that can be used
    in value_based_search queries with "=" or "In set" operators.

    Parameters
    ----------
    tag_identifier : str
        The tag identifier (UUID) from search_tags or navigate_asset_hierarchy.
    sample_window_hours : int, default 24
        Number of hours of recent data to sample for statistics.
        Larger windows give more representative statistics but take longer.

    Returns
    -------
    TagProfile
        Complete tag profile including:
        - Basic info (name, type, unit, description)
        - Data availability (index_status, data_start, data_end)
        - Current value and timestamp
        - For numeric tags: value_stats with min/max/mean and suggested_thresholds
        - For STRING/DIGITAL tags: distinct_values list
        - recommended_approach: guidance on how to query this tag
    """
    tm_client = get_tm_client()

    try:
        tag = tm_client.tag.from_identifier(tag_identifier)
    except Exception as e:
        return {
            "tag_identifier": tag_identifier,
            "tag_name": None,
            "tag_type": None,
            "tag_unit": None,
            "tag_description": None,
            "tag_states": None,
            "index_status": "UNKNOWN",
            "data_start": None,
            "data_end": None,
            "current_value": None,
            "current_timestamp": None,
            "value_stats": None,
            "distinct_values": None,
            "recommended_approach": None,
            "error": f"Failed to resolve tag: {str(e)}",
        }

    # Get basic info
    tag_name = getattr(tag, "name", "unknown")
    tag_type = getattr(tag, "tag_type", "unknown")
    tag_unit = getattr(tag, "unit", None)
    tag_description = getattr(tag, "description", None)

    # Get index info
    index_info = _get_tag_index_info(tag)
    tag_states = list(getattr(tag, "states", {}).values()) if getattr(tag, "states", None) else None
    if index_info["tag_states"] and not tag_states:
        tag_states = index_info["tag_states"]

    # Get current value
    current_value = None
    current_timestamp = None
    try:
        last_point = tag.get_last_point()
        if last_point:
            current_value = last_point.value if hasattr(last_point, 'value') else None
            current_ts = last_point.ts if hasattr(last_point, 'ts') else None
            if current_ts:
                current_timestamp = current_ts.isoformat() if hasattr(current_ts, 'isoformat') else str(current_ts)
    except Exception as e:
        logger.warning(f"Failed to get last point for tag {tag_name}: {e}")

    # Get value statistics for numeric tags
    value_stats = None
    distinct_values = None
    recommended_approach = ""

    is_numeric = tag_type in ("ANALOG", "DISCRETE")

    if is_numeric and index_info["index_status"] == "OK":
        try:
            end = pd.Timestamp.now(tz=tm_client.tz)
            start = end - pd.Timedelta(hours=sample_window_hours)
            interval = pd.Interval(start, end, closed="both")

            # Use get_chart_data for efficiency (designed for charting, returns ~4 points per period)
            try:
                chart_data = tag.get_chart_data(interval, periods=100)
            except Exception:
                # Fallback to get_data if get_chart_data not available
                chart_data = tag.get_data(interval=interval, freq="15min")

            if not chart_data.empty:
                # Calculate statistics
                min_val = float(chart_data.min())
                max_val = float(chart_data.max())
                mean_val = float(chart_data.mean())

                # Calculate percentiles for thresholds
                try:
                    p5 = float(chart_data.quantile(0.05))
                    p10 = float(chart_data.quantile(0.10))
                    p90 = float(chart_data.quantile(0.90))
                    p95 = float(chart_data.quantile(0.95))
                except Exception:
                    # If quantile fails, use min/max based estimates
                    range_val = max_val - min_val
                    p5 = min_val + 0.05 * range_val
                    p10 = min_val + 0.10 * range_val
                    p90 = min_val + 0.90 * range_val
                    p95 = min_val + 0.95 * range_val

                value_stats = {
                    "min": round(min_val, 4),
                    "max": round(max_val, 4),
                    "mean": round(mean_val, 4),
                    "recent_value": round(float(chart_data.iloc[-1]), 4) if len(chart_data) > 0 else None,
                    "sample_period_start": start.isoformat(),
                    "sample_period_end": end.isoformat(),
                    "sample_points": len(chart_data),
                    "suggested_thresholds": {
                        "very_low": round(p5, 4),
                        "low_threshold": round(p10, 4),
                        "high_threshold": round(p90, 4),
                        "very_high": round(p95, 4),
                    },
                }

                recommended_approach = (
                    f"This is a numeric ({tag_type}) tag. Use value_based_search with operators "
                    f"like '>', '<', '>=', '<='. Based on recent data, typical values range from "
                    f"{round(min_val, 2)} to {round(max_val, 2)}. "
                    f"Suggested thresholds: low={round(p10, 2)}, high={round(p90, 2)}."
                )
        except Exception as e:
            logger.warning(f"Failed to get statistics for tag {tag_name}: {e}")
            recommended_approach = f"This is a numeric ({tag_type}) tag. Use value_based_search with numeric operators."

    elif tag_type in ("STRING", "DIGITAL"):
        distinct_values = tag_states
        if distinct_values:
            recommended_approach = (
                f"This is a {tag_type} tag with {len(distinct_values)} distinct values: {distinct_values}. "
                f"Use value_based_search with operator '=' for a single value or 'In set' for multiple values."
            )
        else:
            recommended_approach = (
                f"This is a {tag_type} tag. Use get_distinct_values to discover possible values, "
                f"then use value_based_search with '=' or 'In set' operator."
            )
    else:
        recommended_approach = f"Tag type is {tag_type}. Check index_status and data availability before querying."

    return {
        "tag_identifier": tag_identifier,
        "tag_name": tag_name,
        "tag_type": tag_type,
        "tag_unit": tag_unit,
        "tag_description": tag_description,
        "tag_states": tag_states,
        "index_status": index_info["index_status"],
        "data_start": index_info["data_start"],
        "data_end": index_info["data_end"],
        "current_value": current_value,
        "current_timestamp": current_timestamp,
        "value_stats": value_stats,
        "distinct_values": distinct_values,
        "recommended_approach": recommended_approach,
        "error": None,
    }


@mcp.tool()
def check_data_availability(
        tag_identifiers: List[str],
        start: str,
        end: str,
) -> DataAvailabilityReport:
    """
    Check if data exists for multiple tags in a given time range.

    Use this tool BEFORE running value_based_search or get_tag_data to verify
    that your requested time range has data. This prevents failed queries.

    Parameters
    ----------
    tag_identifiers : List[str]
        List of tag identifiers to check.
    start : str
        Start time (parseable by pandas.Timestamp).
    end : str
        End time (parseable by pandas.Timestamp).

    Returns
    -------
    DataAvailabilityReport
        Report containing:
        - Per tag: has_data_in_range, data_coverage_percent, any issues
        - Overall: all_tags_available, summary
    """
    tm_client = get_tm_client()

    try:
        start_ts = pd.Timestamp(start, tz=tm_client.tz)
        end_ts = pd.Timestamp(end, tz=tm_client.tz)
    except Exception as e:
        return {
            "requested_start": start,
            "requested_end": end,
            "tags": [],
            "all_tags_available": False,
            "summary": f"Failed to parse time range: {str(e)}",
            "error": str(e),
        }

    results = []
    all_available = True
    issues_count = 0

    for tag_id in tag_identifiers:
        tag_result = {
            "tag_identifier": tag_id,
            "tag_name": None,
            "index_status": "UNKNOWN",
            "has_data_in_range": False,
            "data_coverage_percent": None,
            "data_start": None,
            "data_end": None,
            "issue": None,
        }

        try:
            tag = tm_client.tag.from_identifier(tag_id)
            tag_result["tag_name"] = getattr(tag, "name", "unknown")

            index_info = _get_tag_index_info(tag)
            tag_result["index_status"] = index_info["index_status"]
            tag_result["data_start"] = index_info["data_start"]
            tag_result["data_end"] = index_info["data_end"]

            if index_info["index_status"] == "NOT_INDEXED":
                tag_result["issue"] = "Tag is not indexed. Request indexing first."
                all_available = False
                issues_count += 1
            elif index_info["index_status"] in ("FAILED", "IN_PROGRESS"):
                tag_result["issue"] = f"Index status is {index_info['index_status']}"
                all_available = False
                issues_count += 1
            elif index_info["data_start"] and index_info["data_end"]:
                # Parse the data boundaries
                data_start = pd.Timestamp(index_info["data_start"])
                data_end = pd.Timestamp(index_info["data_end"])

                # Ensure timezone awareness
                if data_start.tz is None:
                    data_start = data_start.tz_localize(tm_client.tz)
                if data_end.tz is None:
                    data_end = data_end.tz_localize(tm_client.tz)

                # Calculate overlap
                overlap_start = max(start_ts, data_start)
                overlap_end = min(end_ts, data_end)

                if overlap_start < overlap_end:
                    tag_result["has_data_in_range"] = True
                    requested_duration = (end_ts - start_ts).total_seconds()
                    overlap_duration = (overlap_end - overlap_start).total_seconds()
                    tag_result["data_coverage_percent"] = round(100 * overlap_duration / requested_duration, 1)

                    if tag_result["data_coverage_percent"] < 100:
                        tag_result["issue"] = f"Partial coverage ({tag_result['data_coverage_percent']}%)"
                else:
                    tag_result[
                        "issue"] = f"No data overlap. Data available: {index_info['data_start']} to {index_info['data_end']}"
                    all_available = False
                    issues_count += 1
            else:
                tag_result["issue"] = "Data boundaries not available"
                all_available = False
                issues_count += 1

        except Exception as e:
            tag_result["issue"] = f"Failed to check tag: {str(e)}"
            all_available = False
            issues_count += 1

        results.append(tag_result)

    # Build summary
    if all_available and issues_count == 0:
        summary = f"All {len(tag_identifiers)} tags have data available in the requested time range."
    elif issues_count > 0:
        summary = f"{issues_count} of {len(tag_identifiers)} tags have issues. Check 'issue' field for details."
    else:
        summary = "Some tags may have partial data coverage. Check individual tag results."

    return {
        "requested_start": start,
        "requested_end": end,
        "tags": results,
        "all_tags_available": all_available,
        "summary": summary,
        "error": None,
    }


@mcp.tool()
def get_distinct_values(
        tag_identifier: str,
) -> DistinctValuesResult:
    """
    Get all distinct values for a STRING or DIGITAL tag.

    Use this tool to discover what values you can use in value_based_search
    queries with the "=" or "In set" operators.

    For example, a Product tag might have values like ["ALPHA", "BETA", "GAMMA"].
    A Status tag might have values like ["RUNNING", "STOPPED", "MAINTENANCE"].

    Parameters
    ----------
    tag_identifier : str
        The tag identifier (UUID).

    Returns
    -------
    DistinctValuesResult
        Contains:
        - all_known_values: List of all possible values
        - value_count: Number of distinct values
        - example_query: A ready-to-use value_based_search example
    """
    tm_client = get_tm_client()

    try:
        tag = tm_client.tag.from_identifier(tag_identifier)
    except Exception as e:
        return {
            "tag_identifier": tag_identifier,
            "tag_name": None,
            "tag_type": None,
            "all_known_values": [],
            "value_count": 0,
            "example_query": None,
            "error": f"Failed to resolve tag: {str(e)}",
        }

    tag_name = getattr(tag, "name", "unknown")
    tag_type = getattr(tag, "tag_type", "unknown")

    # Check if tag is STRING or DIGITAL
    if tag_type not in ("STRING", "DIGITAL"):
        return {
            "tag_identifier": tag_identifier,
            "tag_name": tag_name,
            "tag_type": tag_type,
            "all_known_values": [],
            "value_count": 0,
            "example_query": None,
            "error": f"Tag is {tag_type}, not STRING or DIGITAL. Use get_tag_profile for numeric tags to see value ranges.",
        }

    # Get all known states
    states = getattr(tag, "states", None)
    all_values = list(states.values()) if states else []

    # Generate example query
    example_query = None
    if all_values:
        example_value = all_values[0]
        example_query = (
            f'value_based_search(\n'
            f'    queries=[{{"tag_identifier": "{tag_identifier}", "operator": "=", "value": "{example_value}"}}],\n'
            f'    start_time="2024-01-01",\n'
            f'    end_time="2024-12-31"\n'
            f')'
        )

    return {
        "tag_identifier": tag_identifier,
        "tag_name": tag_name,
        "tag_type": tag_type,
        "all_known_values": all_values,
        "value_count": len(all_values),
        "example_query": example_query,
        "error": None,
    }


@mcp.tool()
def get_trendhub_session_url(
        tag_identifiers: List[str],
        start: str,
        end: str,
) -> SessionUrlResult:
    """
    Generate a shareable TrendHub session URL for specific tags and time range.

    This creates a temporary session that anyone with the link can access
    to view the specified data in TrendMiner's full UI.

    Use this when you want to:
    - Share analysis results with colleagues
    - Continue detailed analysis in TrendMiner's full interface
    - Create a link for a report or documentation

    Unlike create_trend_view, this does NOT save a persistent view - it only
    generates a shareable session link.

    Parameters
    ----------
    tag_identifiers : List[str]
        List of tag identifiers to include.
    start : str
        Start time for the view (parseable by pandas.Timestamp).
    end : str
        End time for the view (parseable by pandas.Timestamp).

    Returns
    -------
    SessionUrlResult
        Contains:
        - session_url: The shareable URL to open in TrendMiner
        - tag_count: Number of tags included
        - start/end: The time range
    """
    tm_client = get_tm_client()

    try:
        # Parse time interval
        start_ts = pd.Timestamp(start, tz=tm_client.tz)
        end_ts = pd.Timestamp(end, tz=tm_client.tz)
        interval = pd.Interval(start_ts, end_ts, closed="both")

        # Resolve tags
        tags = []
        for tag_id in tag_identifiers:
            try:
                tag = tm_client.tag.from_identifier(tag_id)
                tags.append(tag)
            except Exception as e:
                return {
                    "session_url": None,
                    "tag_count": 0,
                    "start": start,
                    "end": end,
                    "error": f"Failed to resolve tag '{tag_id}': {e}",
                }

        if not tags:
            return {
                "session_url": None,
                "tag_count": 0,
                "start": start,
                "end": end,
                "error": "No valid tags provided.",
            }

        # Create TrendHub view (without saving)
        view = tm_client.trend.view(
            entries=tags,
            layers=[interval],
            context_interval=interval,
            name="Session View",
        )

        # Get session URL
        session_url = view.get_session_url()

        return {
            "session_url": session_url,
            "tag_count": len(tags),
            "start": start,
            "end": end,
            "error": None,
        }
    except Exception as e:
        return {
            "session_url": None,
            "tag_count": 0,
            "start": start,
            "end": end,
            "error": str(e),
        }


@mcp.tool()
def list_monitors(
        name_filter: Optional[str] = None,
        enabled_only: bool = False,
) -> List[MonitorRef]:
    """
    List all monitors in TrendMiner.

    Use this to see existing monitors before creating duplicates,
    or to find a monitor to enable/disable/delete.

    Parameters
    ----------
    name_filter : str, optional
        Filter monitors by name (case-insensitive contains).
    enabled_only : bool, default False
        If True, only return enabled monitors.

    Returns
    -------
    List[MonitorRef]
        List of monitors with their status and configuration.
    """
    tm_client = get_tm_client()

    try:
        monitors = tm_client.monitor.all()
    except Exception as e:
        logger.error(f"Failed to list monitors: {e}")
        return []

    results = []
    for monitor in monitors:
        name = getattr(monitor, "name", "")

        # Apply name filter
        if name_filter and name_filter.lower() not in name.lower():
            continue

        enabled = getattr(monitor, "enabled", False)

        # Apply enabled filter
        if enabled_only and not enabled:
            continue

        # Get search type
        search = getattr(monitor, "search", None)
        search_type = "UNKNOWN"
        if search:
            search_type = getattr(search, "type", "UNKNOWN")

        # Get trigger info
        trigger_count = getattr(monitor, "trigger_count", None)
        last_triggered = None
        last_triggered_dt = getattr(monitor, "last_triggered", None)
        if last_triggered_dt:
            last_triggered = last_triggered_dt.isoformat() if hasattr(last_triggered_dt, 'isoformat') else str(
                last_triggered_dt)

        created_at = None
        created_at_dt = getattr(monitor, "created_at", None)
        if created_at_dt:
            created_at = created_at_dt.isoformat() if hasattr(created_at_dt, 'isoformat') else str(created_at_dt)

        results.append({
            "identifier": getattr(monitor, "identifier", ""),
            "name": name,
            "enabled": enabled,
            "description": getattr(monitor, "description", None),
            "trigger_count": trigger_count,
            "last_triggered": last_triggered,
            "created_at": created_at,
            "search_type": search_type,
        })

    return results


@mcp.tool()
def create_value_monitor(
        name: str,
        queries: List[QueryRef],
        duration: str = "2m",
        combine_operator: Literal["AND", "OR"] = "AND",
        notifications: Optional[List[MonitorNotificationConfig]] = None,
        enabled: bool = True,
        description: Optional[str] = None,
) -> MonitorCreationResult:
    """
    Create a monitor that triggers when value conditions are met.

    This creates a persistent monitor in TrendMiner that will:
    - Continuously check for the specified conditions
    - Send notifications (email/webhook) when conditions are met
    - Track trigger history

    The query syntax is identical to value_based_search.

    BEFORE USING:
    1. Test your query with value_based_search to verify it finds expected events
    2. Use list_monitors to check if a similar monitor already exists

    Parameters
    ----------
    name : str
        Name for the monitor (must be unique).
    queries : List[QueryRef]
        Same query format as value_based_search.
        Each query has: tag_identifier, operator, value
        Operators: ">", "<", ">=", "<=", "=", "!=", "Constant", "In set"
    duration : str, default "2m"
        Minimum duration for events to trigger the monitor.
    combine_operator : "AND" | "OR", default "AND"
        How to combine multiple query conditions.
    notifications : List[MonitorNotificationConfig], optional
        List of notifications to send when triggered.
        Email: {"type": "email", "to": ["user@example.com"], "subject": "Alert", "message": "..."}
        Webhook: {"type": "webhook", "url": "https://..."}
    enabled : bool, default True
        Whether to enable the monitor immediately.
    description : str, optional
        Description of what this monitor is tracking.

    Returns
    -------
    MonitorCreationResult
        Contains the monitor identifier and URL to view in TrendMiner.

    Examples
    --------
    Create a high temperature alert:
        create_value_monitor(
            name="High Temperature Alert",
            queries=[{"tag_identifier": "temp-tag-id", "operator": ">", "value": 95}],
            notifications=[{"type": "email", "to": ["operator@example.com"], "subject": "High Temp!"}]
        )

    Create a product batch monitor:
        create_value_monitor(
            name="ALPHA Batch Monitor",
            queries=[{"tag_identifier": "product-tag-id", "operator": "=", "value": "ALPHA"}],
            description="Triggers when ALPHA product batches start"
        )
    """
    tm_client = get_tm_client()

    # 1. Build SDK query list (same logic as value_based_search)
    sdk_queries = []
    for q_ref in queries:
        tag_id = q_ref.get("tag_identifier")
        operator = q_ref.get("operator")
        value = q_ref.get("value")

        if not all([tag_id, operator]):
            return {
                "identifier": None,
                "name": name,
                "enabled": False,
                "url": None,
                "error": "Each query must contain 'tag_identifier' and 'operator'.",
            }

        if operator != "Constant" and value is None:
            return {
                "identifier": None,
                "name": name,
                "enabled": False,
                "url": None,
                "error": f"Operator '{operator}' requires a 'value' for tag '{tag_id}'.",
            }

        try:
            tag = tm_client.tag.from_identifier(tag_id)
        except Exception as e:
            return {
                "identifier": None,
                "name": name,
                "enabled": False,
                "url": None,
                "error": f"Tag '{tag_id}' could not be resolved: {str(e)}",
            }

        if operator == "Constant":
            sdk_queries.append((tag, operator))
        else:
            sdk_queries.append((tag, operator, value))

    if not sdk_queries:
        return {
            "identifier": None,
            "name": name,
            "enabled": False,
            "url": None,
            "error": "No valid search queries were constructed.",
        }

    # 2. Create search with name and save it
    try:
        search = tm_client.search.value(
            queries=sdk_queries,
            name=name,
            description=description or "",
            duration=duration,
            operator=combine_operator,
        )
        # Save the search to TrendMiner (this sets identifier_complex)
        search.save()
    except Exception as e:
        return {
            "identifier": None,
            "name": name,
            "enabled": False,
            "url": None,
            "error": f"Failed to create/save search: {str(e)}",
        }

    # 3. Retrieve the monitor for this saved search
    try:
        monitor = tm_client.monitor.from_search(search)

        # Set enabled state
        monitor.enabled = enabled

        # Configure email notification
        if notifications:
            for notif_config in notifications:
                notif_type = notif_config.get("type")
                if notif_type == "email":
                    from trendminer_interface.monitor.notification.email import EmailMonitorNotification
                    monitor.email = EmailMonitorNotification(
                        monitor=monitor,
                        enabled=True,
                        enabled_at=None,
                        to=notif_config.get("to", []),
                        subject=notif_config.get("subject", f"Monitor Alert: {name}"),
                        message=notif_config.get("message", f"Monitor '{name}' has triggered."),
                    )
                elif notif_type == "webhook":
                    from trendminer_interface.monitor.notification.webhook import WebhookMonitorNotification
                    monitor.webhook = WebhookMonitorNotification(
                        monitor=monitor,
                        enabled=True,
                        enabled_at=None,
                        url=notif_config.get("url", ""),
                    )

        # Update the monitor configuration
        monitor.update()

        # Build URL to view monitor in TrendMiner
        monitor_url = None
        try:
            tm_server_url = _get_tm_server_url()
            monitor_url = f"{tm_server_url}/monitor/#/monitor/{monitor.identifier}"
        except ValueError:
            # TM_SERVER_URL not configured
            pass

        return {
            "identifier": monitor.identifier,
            "name": monitor.name,
            "enabled": monitor.enabled,
            "url": monitor_url,
            "error": None,
        }
    except Exception as e:
        return {
            "identifier": None,
            "name": name,
            "enabled": False,
            "url": None,
            "error": f"Failed to create monitor: {str(e)}",
        }


@mcp.tool()
def manage_monitor(
        identifier: str,
        action: Literal["enable", "disable", "delete"],
) -> MonitorManageResult:
    """
    Enable, disable, or delete an existing monitor.

    Use list_monitors to find monitor identifiers.

    Parameters
    ----------
    identifier : str
        The monitor identifier (UUID).
    action : str
        Action to perform: "enable", "disable", or "delete".

    Returns
    -------
    MonitorManageResult
        Contains success status and message.
    """
    tm_client = get_tm_client()

    try:
        monitor = tm_client.monitor.from_identifier(identifier)
    except Exception as e:
        return {
            "identifier": identifier,
            "action": action,
            "success": False,
            "message": f"Failed to find monitor: {str(e)}",
            "error": str(e),
        }

    try:
        if action == "enable":
            monitor.enabled = True
            monitor.update()
            return {
                "identifier": identifier,
                "action": action,
                "success": True,
                "message": f"Monitor '{monitor.name}' has been enabled.",
                "error": None,
            }
        elif action == "disable":
            monitor.enabled = False
            monitor.update()
            return {
                "identifier": identifier,
                "action": action,
                "success": True,
                "message": f"Monitor '{monitor.name}' has been disabled.",
                "error": None,
            }
        elif action == "delete":
            monitor_name = monitor.name
            monitor.delete()
            return {
                "identifier": identifier,
                "action": action,
                "success": True,
                "message": f"Monitor '{monitor_name}' has been deleted.",
                "error": None,
            }
        else:
            return {
                "identifier": identifier,
                "action": action,
                "success": False,
                "message": f"Unknown action: {action}",
                "error": f"Unknown action: {action}. Use 'enable', 'disable', or 'delete'.",
            }
    except Exception as e:
        return {
            "identifier": identifier,
            "action": action,
            "success": False,
            "message": f"Failed to {action} monitor: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def create_formula_tag(
        name: str,
        formula: str,
        mapping: List[FormulaTagMapping],
        description: Optional[str] = None,
) -> FormulaTagResult:
    """
    Create a formula tag that computes values based on other tags.

    Formula tags are computed on-the-fly and can be used like any other tag
    in searches, charts, and analysis.

    SYNTAX:
    - Use single letters (A, B, C, etc.) as placeholders for tags
    - Standard math operators: +, -, *, /, ^
    - Functions: sqrt, abs, log, sin, cos, min, max, avg
    - Example: "(A - B) / C * 100" for percentage calculation

    WORKFLOW:
    1. Find tags using search_tags or navigate_asset_hierarchy
    2. Create formula with meaningful calculation
    3. The formula tag can then be used in value_based_search, get_tag_data, etc.

    Parameters
    ----------
    name : str
        Name for the new formula tag.
    formula : str
        Mathematical expression using variable placeholders.
        Example: "A + B", "(A - B) / A * 100", "sqrt(A^2 + B^2)"
    mapping : List[FormulaTagMapping]
        Maps variables to tags.
        Example: [{"variable": "A", "tag_identifier": "abc123"}, ...]
    description : str, optional
        Description of what this formula calculates.

    Returns
    -------
    FormulaTagResult
        Contains the new tag's identifier, which can be used in other tools.

    Examples
    --------
    Calculate temperature delta:
        create_formula_tag(
            name="Reactor_TempDelta",
            formula="A - B",
            mapping=[
                {"variable": "A", "tag_identifier": "inlet-temp-id"},
                {"variable": "B", "tag_identifier": "outlet-temp-id"}
            ]
        )

    Calculate efficiency percentage:
        create_formula_tag(
            name="Efficiency_Pct",
            formula="(A / B) * 100",
            mapping=[
                {"variable": "A", "tag_identifier": "output-flow-id"},
                {"variable": "B", "tag_identifier": "input-flow-id"}
            ]
        )
    """
    tm_client = get_tm_client()

    # Build mapping dict: variable -> Tag object
    sdk_mapping = {}
    mapping_names = {}  # For return value

    for m in mapping:
        variable = m.get("variable")
        tag_id = m.get("tag_identifier")

        if not variable or not tag_id:
            return {
                "tag_identifier": None,
                "tag_name": None,
                "formula": formula,
                "mapping": {},
                "error": "Each mapping must have 'variable' and 'tag_identifier'.",
            }

        try:
            tag = tm_client.tag.from_identifier(tag_id)
            sdk_mapping[variable] = tag
            mapping_names[variable] = getattr(tag, "name", tag_id)
        except Exception as e:
            return {
                "tag_identifier": None,
                "tag_name": None,
                "formula": formula,
                "mapping": {},
                "error": f"Failed to resolve tag '{tag_id}' for variable '{variable}': {str(e)}",
            }

    if not sdk_mapping:
        return {
            "tag_identifier": None,
            "tag_name": None,
            "formula": formula,
            "mapping": {},
            "error": "No valid mappings provided.",
        }

    # Create formula tag
    try:
        formula_tag = tm_client.formula(
            formula=formula,
            mapping=sdk_mapping,
            name=name,
        )

        # Set description if provided
        if description:
            formula_tag.description = description

        # Save the formula tag
        formula_tag.save()

        return {
            "tag_identifier": formula_tag.identifier,
            "tag_name": formula_tag.name,
            "formula": formula,
            "mapping": mapping_names,
            "error": None,
        }
    except Exception as e:
        return {
            "tag_identifier": None,
            "tag_name": None,
            "formula": formula,
            "mapping": mapping_names,
            "error": f"Failed to create formula tag: {str(e)}",
        }


# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------

def main():
    # Check server connectivity before starting
    check_server_connectivity()

    # Log startup information based on auth mode
    if settings.auth_mode == "credentials":
        logger.info(f"[Server] Starting MCP server in credentials mode")
        logger.info(f"[Server] Using TrendMiner credentials: {settings.tm_username}@{settings.tm_client_id}")
    else:
        logger.info(f"[Server] Starting MCP server with OAuth authentication")
        logger.info(f"[OAuth] Resource Server: {settings.resource_server}")
        logger.info(f"[OAuth] Authorization Server: {settings.authorization_server}")
        logger.info(f"[OAuth] Note: Token logging will happen when authenticated requests are received")

    logger.info(f"[Server] Server will bind to: {settings.bind_host}:{settings.bind_port}")

    # Reconfigure logging right before starting to ensure it's not overridden
    # by any imports or library initialization
    rich_handler = get_rich_handler()
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastmcp"]:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.handlers.clear()  # Remove any handlers that were added
        lib_logger.addHandler(rich_handler)
        lib_logger.propagate = False
        lib_logger.setLevel(logging.INFO)

    # Configure session management mode based on auth mode
    # OAuth mode: Use stateless (recommended - avoids session issues after restarts)
    # Credentials mode: Use stateful (sessions work fine with single local client)
    use_stateless = settings.auth_mode == "oauth"

    # Apply session manager patch only for stateful mode
    if not use_stateless:
        from mcp_trendminer_server.patches import patch_session_manager_auto_recovery

        # Option 1: Auto-recovery (strips invalid session IDs, lets client reinitialize)
        # This is more forgiving - allows clients to recover after server restarts
        patch_session_manager_auto_recovery()
        logger.info(f"[Session] Running in stateful mode with auto-recovery enabled")
        logger.info(f"[Session] Invalid session IDs will be automatically stripped")

        # Option 2: Spec-compliant 404 responses (uncomment to use instead)
        # WARNING: Most MCP clients have bugs and don't handle 404 correctly
        # from mcp_trendminer_server.patches import patch_session_manager
        # patch_session_manager()
        # logger.info(f"[Session] Running in stateful mode with 404 responses for invalid sessions")
    else:
        logger.info(f"[Session] Running in stateless mode (no session management)")
        logger.info(f"[Session] OAuth mode uses stateless for reliability across restarts")

    mcp.run(
        transport="streamable-http",
        stateless_http=use_stateless,
        host=settings.bind_host,
        port=settings.bind_port,
    )


if __name__ == "__main__":
    main()
