"""
OpenAPS Core Utilities Module for BG Prediction and NetIOB Calculations.

This module provides essential utility functions for the OpenAPS blood glucose 
prediction pipeline and netIOB calculation. It handles data conversion, API communication, profile 
construction, and time-series processing required by the oref0 algorithm.

Key functionality includes:
    - Datetime formatting and parsing for OpenAPS compatibility
    - HTTP API communication with oref0 server endpoints
    - Profile construction (basal schedules, targets, ISF, carb ratios)
    - Insulin history processing (pump events, temp basals, boluses)
    - Glucose data processing with rate-of-change calculations
    - Carbohydrate history with IOB alignment
    - JSON serialization for complex Python objects

The module serves as the bridge between Django ORM data models and the 
OpenAPS oref0 prediction and netiob calculation algorithms, transforming raw pump/CGM data into 
standardized formats expected by the oref0 APIs.

Dependencies:
    - Django settings for OREF0_API_SERVER_URL configuration
    - Pandas for time-series data manipulation
    - NumPy for numerical operations
    - Requests for HTTP API communication

Author:
    Abiodun Solanke, Ph.D.
"""
import json
import logging
import uuid
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

import numpy as np
import pandas as pd
import requests

from django.conf import settings
from django_pandas.io import read_frame
from django.utils import timezone

# Global configuration constants
TIMEZONE = 'Z'  # UTC timezone indicator for ISO timestamps

# Load OpenAPS API server URL from Django settings
api_base = getattr(settings, "OREF0_API_SERVER_URL", None)
if not api_base:
    raise ValueError("OREF0_API_SERVER_URL is not set in Django settings.")


def to_iso_z(dt):
    """
    Format timezone-aware datetime as ISO 8601 string with 'Z' suffix.
    
    Converts any timezone-aware datetime to UTC and formats it with the
    'Z' suffix notation (Zulu time) commonly used in OpenAPS APIs for
    consistent timestamp representation across timezones.
    
    Args:
        dt (datetime): Timezone-aware datetime object to format.
            Must be a valid datetime instance with tzinfo set.
        
    Returns:
        str: ISO 8601 formatted string with 'Z' suffix indicating UTC.
            Format: 'YYYY-MM-DDTHH:MM:SSZ' (e.g., '2025-11-03T12:23:00Z').
    
    Raises:
        TypeError: If dt is not a datetime object.
        
    Note:
        - Naive datetimes (no tzinfo) are assumed to be UTC
        - All datetimes are converted to UTC before formatting
        - The 'Z' suffix is OpenAPS convention for UTC timestamps
        
    Example:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2025, 11, 3, 12, 23, 45, tzinfo=timezone.utc)
        >>> to_iso_z(dt)
        '2025-11-03T12:23:45Z'
    """
    # Validate input type
    if not isinstance(dt, datetime):
        raise TypeError(f"to_iso_z expects a datetime object, got {type(dt).__name__}.")
    
    # Ensure datetime is timezone-aware (default to UTC if naive)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_timezone.utc)
    
    # Convert to UTC and format with 'Z' suffix
    return dt.astimezone(dt_timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_iso_utc(s):
    """
    Parse ISO 8601 string to timezone-aware UTC datetime.
    
    Handles multiple input formats for flexible timestamp parsing:
        - ISO strings with 'Z' suffix (e.g., '2025-11-03T12:23:00Z')
        - ISO strings with timezone offset (e.g., '2025-11-03T12:23:00+00:00')
        - Datetime objects (ensures timezone-aware)
    
    Args:
        s (str or datetime): ISO formatted string or datetime object to parse.
            Strings should follow ISO 8601 format with timezone information.
        
    Returns:
        datetime: Timezone-aware datetime object in UTC.
            All inputs are normalized to UTC timezone.
    
    Raises:
        TypeError: If input is neither string nor datetime.
        
    Note:
        - Naive datetime objects are assumed to be UTC
        - The 'Z' suffix is replaced with '+00:00' for proper ISO parsing
        - All returned datetimes have tzinfo set to UTC
        
    Example:
        >>> parse_iso_utc('2025-11-03T12:23:00Z')
        datetime.datetime(2025, 11, 3, 12, 23, tzinfo=datetime.timezone.utc)
        
        >>> parse_iso_utc('2025-11-03T12:23:00+05:00')
        datetime.datetime(2025, 11, 3, 7, 23, tzinfo=datetime.timezone.utc)
    """
    # If already a datetime object, ensure it's timezone-aware
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    
    # Validate input type
    if not isinstance(s, str):
        raise TypeError(f"parse_iso_utc expects an ISO string or datetime, got {type(s).__name__}.")    
    
    # Replace 'Z' suffix with explicit '+00:00' offset for proper parsing
    # Python's fromisoformat() requires explicit offset, not 'Z' shorthand
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def call_api(endpoint: str, payload: str) -> dict:
    """
    Make HTTP POST request to OpenAPS API endpoint.
    
    Handles complete API communication workflow including JSON serialization,
    request logging, error handling, and response parsing. All oref0 API calls
    (e.g., /iob, /meal, /determine_basal, /profile) use this unified interface.
    
    Args:
        endpoint (str): API endpoint path starting with '/' (e.g., '/iob', 
            '/determine_basal', '/meal', '/profile', '/detect_sensitivity').
        payload (dict): Request payload containing inputs for the API.
            Must be a dictionary that will be JSON-serialized. Complex objects
            (UUID, datetime, numpy types) are automatically converted.
        
    Returns:
        dict or None: JSON response from API on success (HTTP 200).
            Returns None if request fails or server returns non-200 status.
    
    Raises:
        TypeError: If payload is not a dictionary.
        
    Note:
        - Automatically converts non-JSON-serializable types via make_json_serializable()
        - Logs truncated payload (first 2000 chars) for debugging
        - Full response is logged on success
        - Errors are logged with status code and response text
        - Network errors (connection, timeout) are caught and logged
        
    Example:
        >>> payload = {
        ...     "glucose_status": {"glucose": 120, "delta": -2},
        ...     "iob_data": [{"iob": 1.5, "time": "2025-11-03T12:00:00Z"}],
        ...     "profile": {"dia": 5, "sens": 50}
        ... }
        >>> result = call_api("/determine_basal", payload)
        >>> if result:
        ...     print(f"Predicted BG: {result['eventualBG']}")
    """
    # Validate payload type
    if not isinstance(payload, dict):
        raise TypeError(f"API payload must be a dict, got {type(payload).__name__}.")
    
    # Construct full API URL
    url = f"{api_base}{endpoint}"
    
    # Convert Python objects (UUID, datetime, numpy) to JSON-serializable types
    payload_json = make_json_serializable(payload)

    try:
        logging.debug(f"Calling API {endpoint}")
        # Log truncated payload for debugging (first 2000 chars to avoid log bloat)
        logging.debug(f"Payload to {endpoint}: {json.dumps(payload_json, indent=2)[:2000]}...")
        
        # Make POST request with JSON payload
        response = requests.post(url, json=payload_json)

        # Check for successful response
        if response.status_code == 200:
            logging.debug(f"Response from {endpoint}: {response.json()}")
            return response.json()
        else:
            # Log error details for debugging
            logging.error(
                f"API {endpoint} failed: HTTP {response.status_code} - {response.text}"
            )
            return None
            
    except requests.RequestException as e:
        # Catch network errors (connection, timeout, etc.)
        logging.error(f"API {endpoint} request error: {type(e).__name__}: {e}")
        return None


def datetime_to_zoned_iso(time):
    """
    Convert datetime or ISO string to OpenAPS-compatible ISO format with 'Z'.
    
    Convenience function that combines parsing and formatting in a single call.
    Accepts either datetime objects or ISO strings and returns standardized
    UTC ISO format with 'Z' suffix.
    
    Args:
        time (datetime or str): Input timestamp to convert.
            Can be datetime object or ISO-formatted string.
        
    Returns:
        str: ISO 8601 formatted string with 'Z' suffix (UTC).
            Format: 'YYYY-MM-DDTHH:MM:SSZ'.
    
    Note:
        This is a convenience wrapper around parse_iso_utc() and to_iso_z().
        Useful for normalizing timestamps from mixed sources.
        
    Example:
        >>> datetime_to_zoned_iso('2025-11-03T12:23:00+05:00')
        '2025-11-03T07:23:00Z'
        
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2025, 11, 3, 12, 23, tzinfo=timezone.utc)
        >>> datetime_to_zoned_iso(dt)
        '2025-11-03T12:23:00Z'
    """
    # Parse input to datetime, then format as ISO with 'Z'
    dt = parse_iso_utc(time)
    return to_iso_z(dt)


def minutes_to_time_str(minutes) -> str:
    """
    Convert minute offset to HH:MM:SS time string.
    
    Used for converting profile segment start times from minute-based offsets
    (e.g., 720 minutes since midnight) to human-readable time strings (e.g., "12:00:00").
    This is the format expected by OpenAPS profile segments.
    
    Args:
        minutes (int or float): Minutes since midnight (0-1439).
            Negative values and values >= 1440 are handled but may produce
            unexpected time strings.
        
    Returns:
        str: Formatted time string in HH:MM:SS format (e.g., "12:00:00").
            Uses 24-hour time notation.
    
    Note:
        - Uses timedelta for automatic hour/minute/second calculation
        - Values >= 1440 will show days (e.g., "1 day, 2:00:00")
        - Fractional minutes are truncated to integers
        
    Example:
        >>> minutes_to_time_str(0)
        '0:00:00'
        
        >>> minutes_to_time_str(720)
        '12:00:00'
        
        >>> minutes_to_time_str(1439)
        '23:59:00'
    """
    # Use timedelta for automatic time component calculation
    return str(timedelta(minutes=int(minutes)))


def make_json_serializable(obj):
    """
    Recursively convert Python objects to JSON-serializable types.
    
    Handles conversion of complex Python objects that are not natively JSON-serializable.
    This is essential for API payloads containing datetime objects, UUIDs, and numpy types.
    
    Supported conversions:
        - dict: Recursively converts all values
        - list: Recursively converts all items
        - uuid.UUID: Converts to string representation
        - datetime: Converts to ISO format string
        - numpy integer/float: Converts to Python native int/float
        - numpy array: Converts to Python list
        - All other types: Returns unchanged (primitives pass through)
    
    Args:
        obj: Any Python object (dict, list, UUID, datetime, numpy type, primitive).
            Can be arbitrarily nested (dicts of lists of dicts, etc.).
        
    Returns:
        JSON-serializable version of input object with same structure.
        Primitives (str, int, float, bool, None) are returned unchanged.
    
    Note:
        - Operates recursively on nested structures
        - Preserves dict keys and list order
        - numpy arrays are fully converted to nested Python lists
        - Does not validate JSON schema or structure
        
    Example:
        >>> import uuid
        >>> import numpy as np
        >>> from datetime import datetime, timezone
        >>> 
        >>> obj = {
        ...     'id': uuid.uuid4(),
        ...     'timestamp': datetime(2025, 11, 3, 12, 23, tzinfo=timezone.utc),
        ...     'values': np.array([1.0, 2.5, 3.7]),
        ...     'nested': {'count': np.int64(42)}
        ... }
        >>> serializable = make_json_serializable(obj)
        >>> # All values are now JSON-serializable strings/lists/numbers
    """
    if isinstance(obj, dict):
        # Recursively convert all dict values
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Recursively convert all list items
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, uuid.UUID):
        # Convert UUID to string representation
        return str(obj)
    elif isinstance(obj, datetime):
        # Convert datetime to ISO format string
        return obj.isoformat()
    elif isinstance(obj, (np.integer, np.floating)):
        # Convert numpy numeric types to native Python types
        # .item() extracts the scalar value
        return obj.item()
    elif isinstance(obj, np.ndarray):
        # Convert numpy array to Python list (recursively handles nested arrays)
        return obj.tolist()
    # Return primitives and other types unchanged
    return obj


def build_basal_profile(df: pd.DataFrame) -> list:
    """
    Construct 24-hour basal rate profile from profile segments.
    
    Builds a minute-by-minute basal rate array (1440 minutes = 24 hours) from
    segmented profile data, then samples hourly to create an OpenAPS-compatible
    basal profile. Fills any gaps with a minimum rate of 0.01 U/hr to avoid
    division-by-zero errors in oref0 calculations.
    
    The algorithm:
        1. Creates 1440-minute array initialized to 0.01 U/hr
        2. Sorts segments by start time
        3. Fills each segment's minutes with its basal rate
        4. Samples every 60th minute to create 24 hourly entries
    
    Args:
        df (pd.DataFrame): Profile segments with required columns:
            - start_time (int): Minutes since midnight (0-1439)
            - basal_rate (float): Basal rate in mU/hr (will be converted to U/hr)
        
    Returns:
        list: 24 hourly basal rate entries in OpenAPS format. Each entry contains:
            - i (int): Hour index (0-23)
            - start (str): Time string (e.g., "12:00:00")
            - minutes (int): Minutes since midnight (hour * 60)
            - rate (float): Basal rate in U/hr (rounded to 3 decimals)
    
    Raises:
        ValueError: If DataFrame is empty or missing required columns.
        
    Example:
        >>> df = pd.DataFrame({
        ...     'start_time': [0, 360, 1080],  # Midnight, 6am, 6pm
        ...     'basal_rate': [800, 1200, 900]  # mU/hr
        ... })
        >>> profile = build_basal_profile(df)
        >>> profile[0]  # Midnight rate
        {'i': 0, 'start': '00:00:00', 'minutes': 0, 'rate': 0.8}
        >>> profile[6]  # 6am rate
        {'i': 6, 'start': '06:00:00', 'minutes': 360, 'rate': 1.2}
    """
    # Validate input DataFrame
    if df.empty or 'start_time' not in df or 'basal_rate' not in df:
        logging.error("Basal profile DataFrame missing required columns.")
        raise ValueError(
            "Input DataFrame for basal profile construction must contain "
            "'start_time' and 'basal_rate' columns."
        )
    
    # Sort segments by start time to ensure proper sequential processing
    df = df.sort_values('start_time')
    
    # Initialize minute-by-minute rate array (1440 minutes in 24 hours)
    # Default to 0.01 U/hr for any undefined periods to avoid division by zero
    rates = [0.01] * 1440
    
    # Create boundary list: segment starts + end of day (1440)
    # This allows us to calculate duration of each segment
    starts = list(df['start_time']) + [1440]
   
    # Fill in rates for each segment
    for idx, start in enumerate(starts[:-1]):
        # Convert basal rate from mU/hr to U/hr (divide by 1000)
        rate = df.iloc[idx]['basal_rate'] / 1000.0
        
        # Apply this rate to all minutes from segment start to next segment start
        for m in range(start, starts[idx + 1]):
            rates[m] = rate

    # Sample hourly (every 60th minute) to create 24-hour profile
    # OpenAPS uses hourly segments rather than minute-by-minute
    basal_profile = [
        {
            "i": hr,  # Hour index (0-23)
            "start": f"{hr:02d}:00:00",  # Formatted time string
            "minutes": hr * 60,  # Minutes since midnight
            "rate": round(rates[hr * 60], 3)  # Rate at this hour (3 decimal places)
        }
        for hr in range(24)
    ]
    
    return basal_profile


def get_profile_settings(settings: dict, bg_targets: dict, sensitivities: dict, basal_profile: list, profile_carbs: dict) -> dict:
    """
    Construct complete user profile via OpenAPS /profile API.
    
    Assembles all profile components (settings, targets, ISF, basals) and
    calls the OpenAPS /profile API to generate a validated, complete profile
    object. The API performs consistency checks and fills in derived values.
    Carb ratio details are merged after API call since they're not processed
    by the /profile endpoint.
    
    Args:
        settings (dict): Core profile settings including:
            - maxBasal (float): Maximum allowed basal rate (U/hr)
            - insulin_action_curve (int): Duration of insulin action (hours)
            - temp_basal (dict): Temp basal configuration
        bg_targets (dict): Blood glucose targets with schedule
        sensitivities (dict): Insulin sensitivity factors (ISF) by time
        basal_profile (list): 24-hour basal rate schedule
        profile_carbs (dict): Carb ratio schedule
    
    Returns:
        dict: Complete OpenAPS profile with all components merged.
            Includes DIA, ISF, carb ratios, basal schedule, targets, etc.
            Ready for use in /determine_basal and other oref0 APIs.
        
    Raises:
        ValueError: If /profile API call fails or returns None.
        
    Example:
        >>> profile = get_profile_settings(
        ...     settings={'maxBasal': 3.0, 'insulin_action_curve': 5},
        ...     bg_targets={'targets': [{'low': 100, 'high': 100}]},
        ...     sensitivities={'sensitivities': [{'sensitivity': 50}]},
        ...     basal_profile=[{'rate': 0.8, 'start': '00:00:00'}],
        ...     profile_carbs={'schedule': [{'ratio': 10}]}
        ... )
        >>> profile['dia']  # Duration of insulin action
        5
        >>> profile['carb_ratio']  # Default carb ratio
        10
    """
    # Assemble profile input components
    profile_inputs = {
        "settings": settings,  # Core settings (max basal, DIA, etc.)
        "targets": bg_targets,  # BG target ranges by time
        "isf": sensitivities,  # Insulin sensitivity factors
        "basals": basal_profile,  # 24-hour basal schedule
        "temptargets": []  # Temporary target overrides (empty for now)
    }
    
    # Construct API payload with required structure
    profile_payload = {
        "final_result": {"stdout": "", "err": "", "return_val": 0},
        "inputs": profile_inputs,
        "opts": {}  # Additional options (empty for default behavior)
    }

    # Call OpenAPS /profile API to process and validate profile
    profile = call_api("/profile", profile_payload)
    if not profile:
        logging.error("Failed to generate profile from API.")
        raise ValueError("Profile API call failed - check API server and inputs.")

    # Merge carb ratio details into profile (not handled by /profile API)
    # The /profile API doesn't process carb ratios, so we add them manually
    profile["carb_ratios"] = profile_carbs
    # Set default carb ratio from first schedule entry
    profile["carb_ratio"] = profile_carbs["schedule"][0]["ratio"]

    return profile


def get_autosens(pumphistory: list, profile: dict, basal_profile: list, glucose_data: list):
    """
    Calculate autosensitivity ratio via OpenAPS /detect_sensitivity API.
    
    Autosensitivity (autosens) adjusts insulin sensitivity factor and carb ratio
    based on recent blood glucose patterns. It detects when the body is more or
    less sensitive to insulin than the profile settings indicate, allowing the
    algorithm to adapt to physiological changes (illness, stress, exercise, etc.).
    
    The autosens calculation analyzes BG deviations from predictions over the
    past 24 hours to determine if insulin needs should be adjusted up or down.
    
    Args:
        pumphistory (list): Pump history events (basals, boluses) for the
            sensitivity calculation period (typically 24+ hours).
        profile (dict): Complete user profile with DIA, ISF, carb ratios.
        basal_profile (list): 24-hour basal rate schedule.
        glucose_data (list): Recent glucose readings with deltas (typically 24+ hours).
        
    Returns:
        dict or None: Autosensitivity data including:
            - ratio (float): Sensitivity ratio (1.0 = normal, >1.0 = more sensitive,
              <1.0 = less sensitive)
            - Adjustments to apply to ISF and carb ratios
            Returns None if API call fails.
    
    Note:
        - Autosens requires at least 24 hours of BG data for accuracy
        - Ratio typically ranges from 0.7 to 1.3 (70% to 130% of profile sensitivity)
        - OpenAPS applies limits to prevent extreme adjustments
        - Retrospective mode is disabled (False) for real-time predictions
        - Empty carbs and temptargets arrays indicate no special events
        
    Example:
        >>> autosens = get_autosens(pumphistory, profile, basal_profile, glucose_data)
        >>> if autosens:
        ...     print(f"Sensitivity ratio: {autosens['ratio']}")
        ...     # ratio = 1.2 means 20% more insulin sensitive than profile
    """
    # Assemble autosensitivity API inputs

    # Basic validation
    if not glucose_data or len(glucose_data) < 9:
        print(f"WARNING: Insufficient glucose data ({len(glucose_data)} points)")
        return {"ratio": 1.0, "newisf": profile.get("sens", 50)}
    
    autosens_inputs = {
        "iob_inputs": {
            "history": pumphistory,
            "profile": profile
        },
        "glucose_data": glucose_data,
        "basalprofile": basal_profile,
        "temptargets": [],
        "carbs": [],
        "retrospective": False
    }

    try:
        detect_sens = call_api("/detect_sensitivity", autosens_inputs)
        
        if detect_sens is not None and isinstance(detect_sens, dict):
            # Validate the response has valid ratio
            ratio = detect_sens.get('ratio')
            if ratio is not None and isinstance(ratio, (int, float)):
                return detect_sens
            else:
                print(f"WARNING: Invalid ratio in response: {ratio}")
        else:
            print(f"WARNING: Invalid API response: {detect_sens}")
            
    except Exception as e:
        print(f"ERROR calling detect_sensitivity: {e}")
    
    # Fallback to safe defaults
    newisf = profile.get("sens", 50)
    return {"ratio": 1.0, "newisf": newisf}


def get_profile_inputs(profile_df: pd.DataFrame, basal_df: pd.DataFrame) -> tuple:
    """
    Extract and format user profile settings from pump configuration.
    
    Builds all components of the OpenAPS profile from pump profile segments:
        - Settings: max basal rate, insulin action curve, temp basal config
        - BG targets: target glucose ranges by time of day
        - Basal profile: 24-hour basal rate schedule
        - Sensitivities: insulin sensitivity factors (ISF) by time
        - Carb ratios: carb-to-insulin ratios by time
    
    This function parses segmented profile data (where settings vary by time of day)
    and converts it into the structured formats required by OpenAPS APIs.
    
    Args:
        profile_df (pd.DataFrame): Profile segments with required columns:
            - start_time (int): Minutes since midnight for segment start
            - carb_ratio (int): Carb-to-insulin ratio in mg (converted to g)
            - isf (float): Insulin sensitivity factor (mg/dL per unit)
            - target_bg (int): Target blood glucose (mg/dL)
        basal_df (pd.DataFrame): Basal configuration with column:
            - max_basal_rate (float): Maximum allowed basal rate (U/hr)
        
    Returns:
        tuple: (settings, bg_targets, basal_profile, sensitivities, profile_carbs)
            All components ready for profile construction via get_profile_settings().
    
    Raises:
        ValueError: If required columns are missing or DataFrames are empty.
        
    Note:
        - Uses first 3 profile segments as representative sample (typically covers
          main time blocks: overnight, morning, afternoon)
        - Carb ratios are converted from mg to grams (divide by 1000)
        - BG targets use same value for high/low (single target, not range)
        - All time offsets are in minutes since midnight (0-1439)
        - Profile column name varies by model version ('profile_id' or 'profile')
        
    Example:
        >>> settings, targets, basal, isf, carbs = get_profile_inputs(profile_df, basal_df)
        >>> settings['maxBasal']  # Maximum basal rate
        3.0
        >>> targets['targets'][0]  # First BG target
        {'high': 100, 'low': 100, 'offset': 0, 'start': '00:00:00'}
    """
    # Validate DataFrames are not empty
    if profile_df.empty or basal_df.empty:
        raise ValueError("Profile or basal DataFrame is empty.")
    
    # Determine column name for profile ID (varies by model version)
    profile_col = 'profile_id' if 'profile_id' in profile_df.columns else 'profile'

    # Validate required columns exist
    required_cols = ['start_time', 'carb_ratio', 'isf', 'target_bg']
    for col in required_cols:
        if col not in profile_df.columns:
            raise ValueError(f"Profile DataFrame missing required column: {col}")
    
    # Take first 3 profile segments as representative sample
    # This typically covers main time blocks: overnight, morning, afternoon/evening
    df = profile_df.iloc[:3] if profile_col in profile_df.columns else pd.DataFrame()

    # Extract max basal rate from basal configuration
    max_basal_rate = basal_df['max_basal_rate'].iloc[0] if 'max_basal_rate' in basal_df.columns else None
    
    # Build settings dict with core profile parameters
    settings = {
        "maxBasal": max_basal_rate,  # Maximum allowed basal rate (U/hr)
        "temp_basal": {
            "percent": 100,  # Base percentage for temp basal calculations
            "type": "Units/hour"  # Temp basal type (absolute vs. percentage)
        },
        "insulin_action_curve": 5  # Duration of insulin action (hours) - DIA
    }

    # Build BG targets: convert profile segments to OpenAPS target format
    # Using same value for high and low creates single target (not a range)
    targets = [{
        "high": row['target_bg'],  # Upper target (mg/dL)
        "low": row['target_bg'],  # Lower target (mg/dL) - same as high for single target
        "offset": row['start_time'],  # Minutes since midnight when this target starts
        "start": minutes_to_time_str(row['start_time'])  # Human-readable time string
    } for _, row in df.iterrows()]
    
    # Format BG targets dict
    bg_targets = {
        "units": "mg/dL",  # Glucose units
        "targets": targets,  # List of target ranges by time
        "first": 1  # Index of first target (1-based for OpenAPS compatibility)
    }

    # Build carb ratio and sensitivity (ISF) schedules
    carb_schedule = []
    sensitivities = []
    
    for i, row in df.iterrows():
        # Convert start time to HH:MM:SS format
        time_str = minutes_to_time_str(row['start_time'])
        
        # Convert carb ratio from mg to grams (divide by 1000)
        # Original value is in mg of carbs per unit of insulin
        carb_ratio = int(row['carb_ratio']) // 1000  
        
        # Add carb ratio entry for this time segment
        carb_schedule.append({
            "x": i,  # Index in schedule
            "i": i,  # Duplicate index for OpenAPS compatibility
            "offset": row['start_time'],  # Minutes since midnight
            "ratio": carb_ratio,  # Grams of carbs per unit insulin
            "r": carb_ratio,  # Duplicate ratio for OpenAPS compatibility
            "start": time_str  # Time string (e.g., "06:00:00")
        })
        
        # Add insulin sensitivity factor (ISF) entry for this time segment
        sensitivities.append({
            "start": time_str,  # Time string
            "offset": row['start_time'],  # Minutes since midnight
            "sensitivity": row['isf']  # mg/dL drop per unit insulin
        })
    
    # Format sensitivities dict
    sensitivities = {
        "sensitivities": sensitivities,  # List of ISF values by time
        "units": "mg/dL",  # Units for sensitivity values
        "user_preferred_units": "mg/dL"  # Display units for user
    }
    
    # Format carb ratios dict
    profile_carbs = {
        "schedule": carb_schedule,  # List of carb ratios by time
        "units": "grams"  # Units for carb amounts
    }

    # Build 24-hour basal profile from segments
    basal_profile = build_basal_profile(df)

    return settings, bg_targets, basal_profile, sensitivities, profile_carbs


def get_last_x_hr(df: pd.DataFrame, time: str, pull_hr: int) -> pd.DataFrame:
    """
    Extract insulin data for specified time window before given timestamp.
    
    Used for IOB (insulin on board) calculation at multiple time points by
    pulling the relevant historical insulin data. The time window must be
    sufficient to cover the full duration of insulin action (typically 5-6 hours).
    
    Args:
        df (pd.DataFrame): Insulin dataframe with required column:
            - FADTC (str or datetime): Insulin delivery timestamps
        time (str or datetime): End timestamp for time window (most recent point).
        pull_min (int): Number of minutes to look back from end timestamp.
            Should be >= DIA * 60 to capture all active insulin.
        
    Returns:
        pd.DataFrame: Filtered insulin data within time window.
            Sorted by timestamp descending (most recent first).
            Includes all insulin events (basal and bolus) in the window.
    
    Note:
        - Window is exclusive of start time, inclusive of end time: (start, end]
        - Timestamps are parsed to UTC for consistent comparison
        - Result is sorted descending for OpenAPS compatibility
        - Typical pull_min values: 360 (6 hours), 480 (8 hours)
        
    Example:
        >>> insulin_data = get_last_x_hr(
        ...     df=insulin_df,
        ...     time='2025-11-03T12:00:00Z',
        ...     pull_min=360  # 6 hours
        ... )
        >>> # Returns insulin from 06:00:00 to 12:00:00
    """
    # Parse target timestamp to datetime
    
    # Calculate window start time (e.g., 6 hours before end)
    start = time - timedelta(hours=pull_hr)
    
    # Parse timestamp column to datetime for comparison
    # Ensures all timestamps are timezone-aware UTC
    fadts = pd.to_datetime(df['FADTC'], utc=True)

    # Filter to time window: start < timestamp <= end
    # Sort descending (most recent first) for OpenAPS compatibility
    return df.loc[(fadts > start) & (fadts <= time)].sort_values('FADTC', ascending=False)


def compute_basal_duration(basal_records: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate duration of each basal rate segment.
    
    Computes the duration each basal rate was active by calculating the time
    difference to the next basal event. This is essential for IOB calculations,
    as the amount of insulin delivered depends on both rate and duration.
    
    Args:
        basal_records (pd.DataFrame): Basal insulin records with required column:
            - FADTC (str or datetime): Basal event timestamps
        
    Returns:
        pd.DataFrame: Input dataframe with added column:
            - DURATION (float): Duration in minutes until next basal event
                Last row will have NaN duration (no subsequent event)
    
    Raises:
        ValueError: If 'FADTC' column is missing.
        
    Note:
        - Uses shift(-1) to get next event timestamp for each row
        - Duration is in minutes (converted from seconds)
        - Last basal event has NaN duration (no end time available)
        - Handles timezone-aware and naive datetimes
        
    Example:
        >>> basal_df = pd.DataFrame({
        ...     'FADTC': ['2025-11-03T06:00:00Z', '2025-11-03T08:30:00Z'],
        ...     'rate': [0.8, 1.2]
        ... })
        >>> result = compute_basal_duration(basal_df)
        >>> result.iloc[0]['DURATION']
        150.0  # 2.5 hours = 150 minutes
    """
    # Validate required column exists
    if 'FADTC' not in basal_records.columns:
        raise ValueError("Basal records must contain 'FADTC' column.")

    # Calculate duration as time difference to next event
    # shift(-1) moves timestamps up by one row (gets next event time)
    # Subtract current time from next time to get duration
    basal_records['DURATION'] = (
        pd.to_datetime(basal_records['FADTC'].shift(-1)) - 
        pd.to_datetime(basal_records['FADTC'])
    ).dt.total_seconds() / 60  # Convert seconds to minutes
    
    return basal_records


def avg_basal_rate(insulin_data: pd.DataFrame) -> tuple:
    """
    Calculate average hourly basal rates from insulin delivery data.
    
    Constructs a 24-hour basal profile by averaging observed basal rates for each
    hour of the day. Fills gaps with interpolated values and ensures all hours
    have valid rates (minimum 0.01 U/hr).
    
    This is used as a fallback when detailed basal schedules are not available
    from pump settings.
    
    Args:
        insulin_data (pd.DataFrame): Insulin delivery records with columns:
            - FADTC (datetime): Delivery timestamps
            - FACAT (str): Category ('BASAL' or 'BOLUS')
            - FATEST (str): Test type (e.g., 'BASAL INSULIN')
            - INSSTYPE (str): Subtype (e.g., 'basal', 'basal_chunk')
            - FASTRESN (float): Insulin rate (U/hr)
            - commanded_basal_rate (float): Insulin amount delivered (U)
    
    Returns:
        tuple: (basal_rate_structure_list, profile)
            - basal_rate_structure_list (list): 24 hourly basal entries in OpenAPS format
            - profile (dict): Profile dict with DIA and basal schedule
    
    Note:
        - Groups insulin records by hour of day
        - Interpolates missing hours using adjacent hour values
        - Forward/backward fills remaining gaps
        - Replaces zero rates with 0.01 U/hr minimum
        - Returns both list format and dict format for flexibility
        
    Example:
        >>> basal_list, profile = avg_basal_rate(insulin_df)
        >>> profile['dia']
        5
        >>> basal_list[12]  # Noon basal rate
        {'i': 12, 'start': '12:00:00', 'minutes': 720, 'rate': 0.95}
    """
    # Filter DataFrame to extract only basal-related data
    basal_insulin_data = insulin_data[insulin_data['FACAT'] == 'BASAL'].copy()
    
    # Extract hour of day from timestamps for grouping
    basal_insulin_data['HOUR'] = pd.to_datetime(basal_insulin_data['FADTC']).dt.hour

    # Filter to main basal insulin records (exclude temporary basals)
    basal_insulin_df = basal_insulin_data[
        (basal_insulin_data['FACAT'] == 'BASAL') & 
        (basal_insulin_data['FATEST'] == 'BASAL INSULIN') & 
        (basal_insulin_data['INSSTYPE'].isin(['basal', 'basal_chunk']))
    ]

    # Create template with all 24 hours
    hours_template = pd.DataFrame({'HOUR': range(24)})

    # Fill in rates for hours that have data
    for _, row in basal_insulin_df.iterrows():
        hour = row['HOUR']
        hours_template.loc[hours_template['HOUR'] == hour, 'commanded_basal_rate'] = row['commanded_basal_rate']

    # Interpolate missing hours using adjacent values
    # Only interpolate if previous and next values are different (avoid flat lines)
    for i in range(1, 23):  # Skip first and last hour to ensure prev/next exist
        if pd.isna(hours_template.at[i, 'commanded_basal_rate']):
            prev_val = hours_template.at[i - 1, 'commanded_basal_rate']
            next_val = hours_template.at[i + 1, 'commanded_basal_rate']
            # Only interpolate if both neighbors exist and are different
            if not pd.isna(prev_val) and not pd.isna(next_val) and prev_val != next_val:
                hours_template.at[i, 'commanded_basal_rate'] = float(prev_val + next_val) / 2

    # Fill remaining gaps with forward fill, then backward fill
    # This ensures all hours have valid rates
    hours_template['FASTRESN'] = hours_template['commanded_basal_rate'].fillna(method='ffill').fillna(method='bfill')
    
    # Replace zero rates with minimum 0.01 U/hr to avoid division by zero
    hours_template.loc[hours_template['commanded_basal_rate'] == 0.0, 'commanded_basal_rate'] = 0.01
    
    # Convert to dictionary: hour -> rate
    avg_basal_rate_dict = hours_template.set_index('HOUR')['commanded_basal_rate'].to_dict()
    
    # Build OpenAPS basal structure list
    basal_rate_structure_list = [
        {
            'i': i,  # Hour index
            'start': f'{hour:02d}:00:00',  # Time string
            'minutes': hour * 60,  # Minutes since midnight
            'rate': rate  # Basal rate (U/hr)
        } 
        for i, (hour, rate) in enumerate(avg_basal_rate_dict.items())
    ]

    # Build profile dict with DIA and basal schedule
    profile = {
        'dia': 5,  # Duration of insulin action (5 hours default)
        'basalprofile': basal_rate_structure_list
    }

    return basal_rate_structure_list, profile


def get_pump_history(insulin_df: pd.DataFrame, filtered_df: pd.DataFrame=None) -> tuple:
    """
    Build OpenAPS-compatible pump history from insulin dataframe.
    
    Converts insulin delivery records into OpenAPS pump event format required
    by IOB calculation and prediction algorithms. Processes two types of events:
        - TempBasal + TempBasalDuration: Temporary basal rate changes
        - Bolus: Bolus insulin deliveries (normal and extended)
    
    The pump history format follows OpenAPS conventions where each basal rate
    change is represented by paired TempBasal and TempBasalDuration events.
    
    Args:
        insulin_df (pd.DataFrame): processed insulin data with columns:
            - FADTC (datetime): Delivery timestamps
            - FACAT (str): Category ('BASAL' or 'BOLUS')
            - FATEST (str): Test type ('BASAL INSULIN' or 'BOLUS INSULIN')
            - INSSTYPE (str): Subtype ('basal', 'basal_chunk', 'normal', 'extended')
            - FASTRESN (float): Basal rate (U/hr) for basals
            - INSNMBOL (float): Normal bolus amount (U)
            - INSEXBOL (float): Extended bolus amount (U)
            - commanded_basal_rate (float): Insulin amount delivered (U)
        filtered_df (Optional: pd.DataFrame): Filtered insulin data. 
            Specifically needed for netiob 24 hours data pull for every reference timestamps
        
    Returns:
        tuple: (pumphistory, pump_clock)
            - pumphistory (list): Pump events in OpenAPS format. Each event is a dict
              with keys: timestamp, _type, and type-specific fields
            - pump_clock (str): ISO timestamp of most recent pump event, or current
              time if no events exist
    
    Note:
        - Basal events include both rate and duration for IOB calculations
        - Boluses are represented as instantaneous deliveries (duration=0)
        - Extended boluses create separate events from normal boluses
        - Events are sorted chronologically (ascending by timestamp)
        - Empty DataFrame returns empty history with current timestamp
        - Handles None/'None' string values in bolus amount columns
        
    Example:
        >>> pumphistory, pump_clock = get_pump_history(insulin_df)
        >>> pumphistory[0]
        {
            'timestamp': '2025-11-03T06:00:00Z',
            '_type': 'TempBasal',
            'temp': 'absolute',
            'rate': 0.8
        }
        >>> pumphistory[1]
        {
            'timestamp': '2025-11-03T06:00:00Z',
            '_type': 'TempBasalDuration',
            'duration (min)': 150.0
        }
    """
    # Work on copy to avoid modifying original DataFrame
    df = insulin_df.copy()
    
    # Handle empty DataFrame - return empty history with current time
    if df.empty:
        return [], to_iso_z(datetime.now(dt_timezone.utc))

    # Ensure timestamps are properly formatted as UTC datetime
    df['FADTC'] = pd.to_datetime(df['FADTC'], utc=True)
    
    # Sort by timestamp ascending (oldest to newest)
    df = df.sort_values(by='FADTC')
    
    # Filter to extract only basal insulin-related records
    basal_records = df[df['FACAT'] == 'BASAL'].copy()
    main_basal_insulin_records = basal_records[basal_records['FATEST'] == 'BASAL INSULIN']

    # Create basal dataframe with computed duration column
    # Duration is time until next basal event
    basal_with_duration = compute_basal_duration(main_basal_insulin_records)[['FADTC', 'FASTRESN', 'commanded_basal_rate', 'DURATION']]

    # Define insulin delivery type categories
    basal_types = ['basal', 'basal_chunk']  # Types that represent basal delivery
    bolus_types = ['normal', 'extended']  # Types that represent bolus delivery
    
    # determine which of the DFs to iterate. Pumphistory for prediction will be df
    # while for netiob prediction will be filtered_df
    df_iter = filtered_df if filtered_df is not None else df

    pumphistory = []    
    # Process each insulin delivery record
    for _, row in df_iter.iterrows():
        # Convert timestamp to OpenAPS ISO format with 'Z'
        ts = datetime_to_zoned_iso(pd.to_datetime(row['FADTC']))

        # Process basal insulin events
        if row['FATEST'] == 'BASAL INSULIN' and row['INSSTYPE'] in basal_types:
            # Look up duration for this basal event
            duration_row = basal_with_duration.loc[ basal_with_duration['FADTC'] == row['FADTC'], 'DURATION']
            duration = duration_row.iloc[0] if not duration_row.empty else 0
            # Convert NaN to 0 (last basal event has no duration)
            duration = 0 if np.isnan(duration) else duration
            
            # Create TempBasalDuration event (must come before TempBasal for OpenAPS)
            pumphistory.append({
                "timestamp": ts,
                "_type": "TempBasalDuration",
                "duration (min)": duration  # Minutes until next basal change
            })
            
            # Create TempBasal event with rate
            pumphistory.append({
                "timestamp": ts,
                "_type": "TempBasal",
                "temp": "absolute",  # Absolute rate (not percentage adjustment)
                "rate": row['commanded_basal_rate']  # Insulin amount delivered (U)
            })

        # Process bolus insulin events
        elif row['FATEST'] == 'BOLUS INSULIN' and row['INSSTYPE'] in bolus_types:
           
            # FIX: Extract and validate bolus amounts
            normal_amount = row.get('INSNMBOL', 0)
            extended_amount = row.get('INSEXBOL', 0)
            
            # Convert NaN to 0 using pd.isna
            normal_amount = 0 if pd.isna(normal_amount) else float(normal_amount)
            extended_amount = 0 if pd.isna(extended_amount) else float(extended_amount)
            
            # FIX: Only create bolus events for non-zero amounts
            if row['INSSTYPE'] == 'normal':
                # Only create event if normal bolus amount > 0
                if normal_amount > 0:
                    pumphistory.append({
                        "timestamp": ts,
                        "_type": "Bolus",
                        "amount": normal_amount,
                        "programmed": normal_amount,
                        "unabsorbed": 0,
                        "duration": 0
                    })
                    
            # Create separate event for extended bolus if present
            elif row['INSSTYPE'] == 'extended':
                # Create normal component if > 0
                if normal_amount > 0:
                    pumphistory.append({
                        "timestamp": ts,
                        "_type": "Bolus",
                        "amount": normal_amount,
                        "programmed": normal_amount,
                        "unabsorbed": 0,
                        "duration": 0
                    })
                
                # Create extended component if > 0
                if extended_amount > 0:
                    pumphistory.append({
                        "timestamp": ts,
                        "_type": "Bolus",
                        "amount": extended_amount,
                        "programmed": extended_amount,
                        "unabsorbed": 0,
                        "duration": 0  # Consider adding actual duration for extended
                    })

    
    # Pump clock is timestamp of most recent event, or current time if no events
    if pumphistory:
        last_timestamp = pumphistory[-1]['timestamp']
        pump_clock = to_iso_z(parse_iso_utc(last_timestamp))
    else:
        pump_clock = to_iso_z(datetime.now(dt_timezone.utc))
    
    return pumphistory, pump_clock

def get_glucose_and_clock(glucose_df: pd.DataFrame) -> tuple:
    """
    Build glucose status array with rate-of-change metrics.
    
    Constructs the glucose_status structure used by OpenAPS prediction algorithms.
    For each glucose reading, calculates multiple delta metrics:
        - delta: Immediate change from previous reading (5 min)
        - short_avgdelta: Average change over 15 min (3 readings)
        - long_avgdelta: Average change over 30 min (6 readings)
    
    These delta calculations help the algorithm understand both current BG trend
    and acceleration/deceleration of BG changes, which are critical for safe
    insulin dosing decisions.
    
    Follows OpenAPS glucose-get-last.js logic:
    https://github.com/openaps/oref0/blob/master/lib/glucose-get-last.js
    
    Args:
        glucose_df (pd.DataFrame): Glucose readings with required columns:
            - LBDTC (datetime or str): Reading timestamps (assumed 5-min intervals)
            - LBORRES (float): Blood glucose values (mg/dL)
    
    Returns:
        tuple: (glucose_data, clock)
            - glucose_data (list): Glucose status entries sorted by date descending
              (most recent first). Each entry contains:
                * date (int): Unix epoch milliseconds
                * dateString (str): ISO formatted timestamp
                * sgv (int): Sensor glucose value (mg/dL)
                * glucose (int): Same as sgv (for compatibility)
                * delta (float): Change from previous reading (mg/dL)
                * short_avgdelta (float): Average delta over 15 min
                * long_avgdelta (float): Average delta over 30 min
            - clock (str): ISO timestamp of most recent glucose reading
    
    Raises:
        ValueError: If glucose DataFrame is empty or missing required columns.
        
    Note:
        - Requires at least 10 readings (9 prior + current) for full delta calculations
        - Entries with invalid (non-finite) deltas are excluded
        - Assumes CGM readings are at 5-minute intervals
        - Delta calculations use mean of prior readings, not linear regression
        - Result is sorted descending (most recent first) for OpenAPS compatibility
        
    Example:
        >>> glucose_data, clock = get_glucose_and_clock(cgm_df)
        >>> glucose_data[0]  # Most recent reading
        {
            'date': 1730641380000,
            'dateString': '2025-11-03T12:23:00Z',
            'sgv': 120,
            'glucose': 120,
            'delta': -2.0,
            'short_avgdelta': -1.667,
            'long_avgdelta': -1.333
        }
        >>> clock
        '2025-11-03T12:23:00Z'
    """
    # Work on copy to avoid modifying original DataFrame
    df = glucose_df.copy()

    # Validate DataFrame is not empty
    if df.empty:
        raise ValueError("Glucose data is empty. Cannot proceed with BG prediction.")
    
    # Validate required columns exist
    if 'LBDTC' not in df or 'LBORRES' not in df:
        raise ValueError("Glucose DataFrame missing required columns 'LBDTC' or 'LBORRES'.")

    # Parse timestamp column as UTC datetime
    df['LBDTC'] = pd.to_datetime(df['LBDTC'], utc=True)

    # Sort by time ascending (oldest first) and reset index
    # This is necessary for proper delta calculations
    df = df.sort_values('LBDTC').reset_index(drop=True)

    glucose_data = []

    # Start at index 9 (need at least 9 prior readings for 30-min average)
    # This provides: 1 for immediate delta, 3 for short avg, 6 for long avg
    for i in range(9, len(df)):
        current = df.loc[i]

        # Current and previous BG values (mg/dL)
        glucose_now = current['LBORRES']  # Current reading
        glucose_prev = df.loc[i - 1]['LBORRES']  # Previous reading (5 min ago)

        # Delta: immediate change from previous reading
        # Positive = rising, negative = falling
        delta = glucose_now - glucose_prev

        # Short-term avg delta: average change over last 15 min
        # Uses 3 readings at 5-min intervals (15 min total)
        # Dividing by 3 gives average per-reading change
        short_avgdelta = (glucose_now - df.loc[i - 3:i - 1]['LBORRES'].mean()) / 3

        # Long-term avg delta: average change over last 30 min
        # Uses 6 readings at 5-min intervals (30 min total)
        # Dividing by 6 gives average per-reading change
        long_avgdelta = (glucose_now - df.loc[i - 6:i - 1]['LBORRES'].mean()) / 6

        # Construct glucose_status entry for this reading
        entry = {
            "date": int(current['LBDTC'].timestamp() * 1000),  # Unix epoch milliseconds
            "dateString": current['LBDTC'].strftime(f'%Y-%m-%dT%H:%M:%S{TIMEZONE}'),  # ISO format
            "sgv": glucose_now,  # Sensor glucose value (mg/dL)
            "glucose": glucose_now,  # Duplicate for compatibility
            "delta": round(delta, 1),  # Round to 1 decimal
            "short_avgdelta": round(short_avgdelta, 3),  # Round to 3 decimals
            "long_avgdelta": round(long_avgdelta, 3)  # Round to 3 decimals
        }

        # Only include entries with valid (finite) delta values
        # This excludes NaN, inf, -inf values that would break predictions
        if all(np.isfinite(entry[k]) for k in ['delta', 'short_avgdelta', 'long_avgdelta']):
            glucose_data.append(entry)

    # Sort by date descending (most recent first) for OpenAPS compatibility
    # OpenAPS expects glucose_data[0] to be the most recent reading
    glucose_data.sort(key=lambda x: x['date'], reverse=True)

    # Clock is timestamp of most recent glucose reading
    last_time = pd.to_datetime(glucose_data[0]['dateString'], utc=True)
    clock = last_time.strftime(f'%Y-%m-%dT%H:%M:%S{TIMEZONE}')

    return glucose_data, clock


def get_carb_history(carbs: pd.DataFrame, iobs: pd.DataFrame, clock: str, sim_carb: int=None) -> tuple:
    """
    Build carbohydrate history with aligned IOB data.
    
    Constructs OpenAPS-compatible carb history by merging carb intake events
    with corresponding insulin-on-board values. The IOB at time of carb ingestion
    helps the meal absorption algorithm determine how much insulin is available
    to cover the carbs.
    
    The merge process:
        1. Aligns carb events with nearest IOB values (within 2-minute tolerance)
        2. Adds simulated carbs if scenario specifies (for what-if predictions)
        3. Sorts from most recent to oldest (OpenAPS convention)
    
    Args:
        carbs (pd.DataFrame): Carbohydrate intake records with columns:
            - MLDTC (datetime or str): Carb entry timestamps
            - MLDOSE (float): Carb amount in grams
        iobs (pd.DataFrame): Net IOB calculations with columns:
            - time (datetime or str): IOB calculation timestamps
            - iob (float): Net insulin on board (units)
        clock (str): Current timestamp for simulation reference.
        sim_carb (int, optional): Simulated carb grams to add at current time.
            Used for what-if scenarios (e.g., "what if I eat 15g now?").
    
    Returns:
        tuple: (carb_clock, carb_history)
            - carb_clock (datetime or None): Timestamp of most recent carb entry.
              None if no carb history exists.
            - carb_history (list): Carb events in OpenAPS format. Each entry contains:
                * entered_by (str): Data source identifier ("Tandem")
                * carbs (int): Carbohydrate amount in grams
                * created_at (str): ISO timestamp of carb entry
                * insulin (float or None): IOB at time of carb ingestion
    
    Note:
        - Uses merge_asof with 2-minute tolerance for temporal alignment
        - IOB values are matched to nearest carb time within tolerance window
        - Simulated carbs have insulin=None (no IOB alignment)
        - Result is sorted descending (most recent first)
        - Empty carb history returns None for carb_clock
        - Missing IOB columns are handled gracefully with error logging
        
    Example:
        >>> carb_clock, carb_history = get_carb_history(
        ...     carbs=carbs_df,
        ...     iobs=iob_df,
        ...     clock='2025-11-03T12:00:00Z',
        ...     sim_carb=15
        ... )
        >>> carb_history[0]  # Most recent (simulated)
        {
            'entered_by': 'Tandem',
            'carbs': 15,
            'created_at': '2025-11-03T12:00:00Z',
            'insulin': None
        }
        >>> carb_history[1]  # Actual carb intake
        {
            'entered_by': 'Tandem',
            'carbs': 30,
            'created_at': '2025-11-03T08:00:00Z',
            'insulin': 2.5
        }
    """
    # Validate required columns in IOB DataFrame
    required_columns = ['iob', 'time']
    missing = [col for col in required_columns if col not in iobs.columns]
    if missing:
        logging.error(f"Missing columns in IOB DataFrame: {missing}. Available: {iobs.columns.tolist()}")
        # Fallback: proceed without IOB alignment (all insulin values will be None)
    
    # Work on copies to avoid modifying original DataFrames
    carbs_df = carbs.copy()
    netiob_df = iobs[['iob', 'time']].copy() if not missing else pd.DataFrame(columns=['iob', 'time'])

    # Parse timestamps for temporal alignment
    carbs_df['time'] = pd.to_datetime(carbs_df['MLDTC'], utc=True)
    if not netiob_df.empty:
        netiob_df['time'] = pd.to_datetime(netiob_df['time'], utc=True)

    # Merge carb events with nearest IOB value (within 2-minute tolerance)
    # This aligns insulin-on-board at the time of carb ingestion
    # merge_asof requires both DataFrames sorted by 'on' column
    if not netiob_df.empty:
        merged = pd.merge_asof(
            carbs_df.sort_values('time'),
            netiob_df.sort_values('time'),
            on='time',
            tolerance=pd.Timedelta('2min'),  # Match within 2 minutes
            direction='nearest'  # Find closest IOB reading (before or after)
        )
    else:
        # No IOB data available - proceed with carbs only
        merged = carbs_df
        merged['iob'] = None
    
    # Build carb history list from merged data
    carb_history = []
    for _, r in merged.iterrows():
        carb_history.append({
            "entered_by": "Tandem",  # Data source identifier
            "carbs": min(int(r['MLDOSE']), 120),  # Carb amount in grams. Defaults to 120 if MLDOSE > 120
            "created_at": r['MLDTC'].strftime(f'%Y-%m-%dT%H:%M:%S{TIMEZONE}'),  # ISO timestamp
            "insulin": None if pd.isna(r['iob']) else r['iob']  # IOB at ingestion time
        })

    # Add simulated carb entry if scenario specifies
    if sim_carb is not None:
        carb_history.append({
            "entered_by": "Tandem",
            "carbs": sim_carb,  # Simulated carb amount
            "created_at": clock,  # Use current clock time
            "insulin": None  # No IOB alignment for simulated carbs
        })
    
    # Sort from most recent to oldest (OpenAPS convention)
    # OpenAPS expects carb_history[0] to be the most recent entry
    carb_history.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Extract timestamp of most recent carb entry
    carb_clock = pd.to_datetime(carb_history[0]['created_at']) if carb_history else None

    return carb_clock, carb_history
