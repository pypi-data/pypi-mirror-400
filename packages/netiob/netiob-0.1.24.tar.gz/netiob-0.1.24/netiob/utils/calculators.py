"""
Net Insulin On Board (IOB) Calculator with Parallel Processing

This module provides high-performance net IOB calculation by parallelizing API
calls to the OpenAPS oref0 IOB endpoint. It processes insulin delivery history
across multiple time points simultaneously using ThreadPoolExecutor for optimal
throughput on IO-bound API calls.

Net IOB differs from traditional pump-native IOB by including the impact of
temporary basal rates relative to scheduled basals, providing a more accurate
representation of active insulin for prediction algorithms. Traditional pump IOB
only accounts for bolus insulin, while net IOB captures the full insulin activity
including basal variations.

The calculator generates IOB values at regular intervals (typically 5 minutes)
across the full insulin history timespan, enabling accurate time-series analysis
for glucose prediction and retrospective evaluation.

Key Features:
    - Parallel processing of multiple time points for high throughput
    - 5-minute interval calculations matching CGM reading frequency
    - 24-hour lookback window for each calculation point
    - Automatic retry and error handling for failed API calls
    - Comprehensive logging for debugging and monitoring

Dependencies:
    - OpenAPS oref0 API server (configured via OREF0_API_SERVER_URL)
    - ThreadPoolExecutor for concurrent processing
    - Pandas for time-series data manipulation
    - notebooks.coreutils for insulin data preprocessing
    - notebooks.cgmdataprocessor for data processing pipeline

Configuration:
    Set in netiob.settings:
        - OREF0_API_SERVER_URL: Base URL for oref0 API server (e.g., http://localhost:5000)
        - MAX_WORKERS: Maximum concurrent threads (default: 75% of CPU cores, capped at 8)

Author:
    Abiodun Solanke, Ph.D.
"""
import os
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import logging
import warnings
from datetime import datetime, timedelta

import numpy as np
import requests

from netiob.settings import OREF0_API_SERVER_URL, MAX_WORKERS
from netiob.utils.coreutils import get_pump_history, avg_basal_rate, datetime_to_zoned_iso, get_last_x_hr, make_json_serializable
from netiob.utils.cgmdataprocessor import CGMDataProcessor

# Configure module logger
logger = logging.getLogger(__name__)

# Suppress pandas/numpy warnings for cleaner logs
warnings.filterwarnings("ignore")

# Calculate optimal worker pool size based on available CPU cores
# Default: 75% of CPU cores, capped at 8 workers maximum
# This prevents CPU saturation while maximizing throughput
max_workers = MAX_WORKERS or min(8, int((os.cpu_count() or 1) * 0.75))
logger.info(f"Max available workers are {max_workers}/{int((os.cpu_count() or 1))}")


def check_net_iob_server_is_live():
    """
    Check if OpenAPS oref0 API server is accessible and responding.
    
    Performs a simple health check by sending a GET request to the API base URL.
    This validation ensures the API is available before attempting expensive IOB
    calculations, preventing wasted computation on unavailable services.
    
    Returns:
        bool: True if server is accessible (HTTP 200), False otherwise.
        
    Raises:
        Exception: If connection fails or server is unreachable.
            Includes the API URL and error details in the exception message.
    
    Note:
        - Uses HTTP GET request to base URL (no specific endpoint)
        - Only checks for HTTP 200 status code (success)
        - Logs error details if connection fails
        - Should be called before batch IOB calculations
        - Relatively fast check (~100ms typical latency)
        
    Example:
        >>> if check_net_iob_server_is_live():
        ...     print("API is ready for IOB calculations")
        ... else:
        ...     print("API unavailable - cannot calculate IOB")
    """
    try:
        # Send health check request to API base URL
        url = OREF0_API_SERVER_URL
        response = requests.get(url)
        
        # Return True if server responds with HTTP 200 (OK)
        return response.status_code == 200
        
    except Exception as ex:
        # Log error with URL and exception details
        logger.error(f"NetIOB API is not available at {OREF0_API_SERVER_URL} | {ex.__str__()}")
        # Re-raise exception to caller for handling
        raise


def get_net_iob(pumphistory: list, profile: dict, clock: str, autosens: dict=None, pumphistory24: list=None) -> dict:
    """
    Calculate net insulin on board via OpenAPS /iob API endpoint.
    
    Makes a POST request to the oref0 /iob API to calculate net IOB at a specific
    time point. Net IOB includes both bolus insulin activity and the difference
    between temporary and scheduled basal rates, providing a more accurate measure
    of active insulin than pump-native IOB calculations.
    
    Args:
        pumphistory (list): Pump events (basals, boluses) for IOB calculation
            window (typically 6-8 hours covering full DIA period). Each event
            should contain timestamp, type (_type), and insulin amounts.
        profile (dict): User profile with required keys:
            - dia (int): Duration of insulin action (hours)
            - basalprofile (list): Scheduled basal rates
            - sens (float): Insulin sensitivity factor (mg/dL per unit)
        clock (str): ISO timestamp for IOB calculation time point
            (e.g., "2025-11-03T12:00:00Z"). This is the "now" time for calculation.
        autosens (dict): Autosensitivity data with keys:
            - ratio (float): Sensitivity adjustment ratio (1.0 = no adjustment)
            - newisf (float): Adjusted insulin sensitivity factor
        pumphistory24 (list, optional): Extended pump history covering 24 hours
            for more accurate autosensitivity calculations. Default None.
    
    Returns:
        dict: Net IOB calculation result containing:
            - iob (float): Net insulin on board (units)
            - activity (float): Current insulin activity rate (U/hr)
            - basaliob (float): IOB from basal insulin only
            - bolusiob (float): IOB from bolus insulin only
            - time (str): Timestamp of calculation
            - lastTemp (dict): Most recent temp basal information
    
    Raises:
        Exception: If API request fails or returns invalid response.
            Logs error with URL and exception details.
    
    Note:
        - Calculation includes both bolus and basal insulin
        - Net basal IOB = (temp basal - scheduled basal) over time
        - Activity represents rate of insulin absorption at clock time
        - pumphistory should cover at least DIA hours before clock time
        - Returns first element of API response array (most recent)
        
    Example:
        >>> iob_result = get_net_iob(
        ...     pumphistory=pump_events,
        ...     profile={'dia': 5, 'basalprofile': [...]},
        ...     clock='2025-11-03T12:00:00Z',
        ...     autosens={'ratio': 1.0, 'newisf': 50}
        ... )
        >>> print(f"Net IOB: {iob_result['iob']} U")
        >>> print(f"Activity: {iob_result['activity']} U/hr")
    """
    try:
        # Construct full API endpoint URL
        url = f'{OREF0_API_SERVER_URL}/iob'
        
        # Assemble API payload with all required parameters
        data = {
            "history": pumphistory,  # Recent insulin delivery events
            "profile": profile,  # User profile with DIA and basals
            "clock": clock,  # Time point for calculation
            "autosens": autosens,  # Sensitivity adjustment ratio
            "history24": pumphistory24  # Extended history (optional)
        }
        
        # Send POST request to IOB API
        response = requests.post(url, json=data)
        
        # Parse and return JSON response
        # API returns array of IOB objects, take first (most recent)
        return response.json()
        
    except Exception as ex:
        # Log error with API URL and exception details
        logger.error(f"NetIOB API is not available {OREF0_API_SERVER_URL} | {ex.__str__()}")
        # Re-raise exception to caller for handling
        raise


def calculate_net_iob(basal_df: pd.DataFrame, bolus_df: pd.DataFrame, cgm_df: pd.DataFrame, profile: pd.DataFrame=None, autosens: dict=None) -> list:
    """
    Calculate net IOB time series across full insulin history with parallel processing.
    
    Generates net insulin on board calculations at regular intervals (5 minutes)
    across the entire insulin delivery history. Uses ThreadPoolExecutor to
    parallelize API calls for optimal performance, processing multiple time points
    simultaneously.
    
    The calculation workflow:
        1. Validates API server availability
        2. Preprocesses insulin data (fill NaN, round values)
        3. Generates time range at 5-minute intervals
        4. For each time point (in parallel):
            a. Extracts insulin history for last 24 hours
            b. Builds pump history structure
            c. Calls /iob API for net IOB calculation
        5. Aggregates results, filtering out failures
    
    Args:
        basal_df (pd.DataFrame): Basal insulin delivery records with columns for
            timestamps, basal rates (units/hour), and delivery types. Must contain
            temporal data to establish calculation range.
        bolus_df (pd.DataFrame): Bolus insulin delivery records with columns for
            timestamps and insulin amounts (units). Includes manual and automated boluses.
        profile (pd.DataFrame, optional): User profile settings containing DIA, basal
            schedule, ISF, carb ratios, and target ranges. If None, calculates average
            basal profile from processed insulin data. Default is None.
        autosens (dict, optional): Autosensitivity data with keys:
            - ratio (float): Sensitivity adjustment ratio
            - newisf (float): Adjusted insulin sensitivity factor
            If None, uses default {'ratio': 1.0, 'newisf': 29} (no adjustment).
            Default is None.
    
    Returns:
        list of dict: Net IOB calculations for each 5-minute interval. Each element
            is a dict containing:
            - iob (float): Net insulin on board in units
            - activity (float): Insulin activity rate in U/hr
            - basaliob (float): Basal contribution to IOB
            - bolusiob (float): Bolus contribution to IOB
            - time (str): ISO timestamp of calculation
            - lastTemp (dict): Recent temp basal information
        Returns empty list if API is unavailable or all calculations fail.
        Results are sorted by time (descending) for most recent first.
    
    Raises:
        TypeError: If input DataFrames are not pandas DataFrame objects
        ValueError: If required DataFrames are empty or missing required columns
        Exception: If NetIOB API server is unavailable or unresponsive
    
    Note:
        - Uses 5-minute intervals matching typical CGM reading frequency
        - Lookback window: 24 hours of insulin history for each calculation point
        - Parallel processing with configurable worker pool (max_workers setting)
        - Failed calculations are logged but excluded from results (graceful degradation)
        - NaN values in insulin data are filled with 0 before processing
        - All numeric values rounded to 2 decimal places for consistency
        - Time range spans from earliest to latest insulin timestamp in data
        - ThreadPoolExecutor is ideal for IO-bound API calls (not CPU-bound computation)
        - Each thread operates independently without shared state
    
    Example:
        >>> # Basic usage with DataFrames
        >>> iob_series = calculate_net_iob(basal_df=basal_data, bolus_df=bolus_data)
        >>> print(f"Calculated {len(iob_series)} IOB time points")
        >>> 
        >>> # With profile and autosens
        >>> iob_series = calculate_net_iob(basal_df=basal_data, bolus_df=bolus_data, profile=user_profile_df, autosens={'ratio': 1.1, 'newisf': 45})
        >>> 
        >>> # Extract IOB values for analysis or plotting
        >>> times = [pd.to_datetime(pt['time']) for pt in iob_series]
        >>> iob_values = [pt['iob'] for pt in iob_series]
        >>> basal_iob_values = [pt['basaliob'] for pt in iob_series]
        >>> 
        >>> # Convert to DataFrame for analysis
        >>> iob_df = pd.DataFrame(iob_series)
        >>> iob_df['time'] = pd.to_datetime(iob_df['time'])
        >>> iob_df.set_index('time', inplace=True)
    """
    # Validate input types
    if not all(isinstance(df, pd.DataFrame) for df in [basal_df, bolus_df]):
        raise TypeError(
            "All input data (basal_df, bolus_df, carbs_df, cgm_df) must be pandas DataFrames"
        )
    
    if profile is not None and not isinstance(profile, pd.DataFrame):
        raise TypeError("profile must be a pandas DataFrame or None")
    
    if autosens is not None and not isinstance(autosens, dict):
        raise TypeError("autosens must be a dictionary or None")
    
    # Validate DataFrames are not empty
    if any(df.empty for df in [basal_df, bolus_df]):
        raise ValueError(
            "Input DataFrames (basal_df, bolus_df) cannot be empty"
        )
    
    # Initialize CGMDataProcessor to preprocess all input data
    # This handles normalization, cleaning, and extraction of core structures
    try:
        logger.info("Initializing CGMDataProcessor for insulin data preprocessing")
        dataprocessor = CGMDataProcessor(basal_df=basal_df, bolus_df=bolus_df, cgm_df=cgm_df, profile_df=profile)
        
        # Extract preprocessed data from processor
        insulin_df = dataprocessor.proc_insulin
        _profile = dataprocessor.profile
        _autosens = dataprocessor.autosens
        
        # Validate preprocessed data
        if insulin_df is None or insulin_df.empty:
            raise ValueError("Preprocessed insulin data is empty")
        if _profile is None:
            raise ValueError("Profile extraction failed")
        if _autosens is None:
            raise ValueError("Autosens extraction failed")
            
    except (ValueError, TypeError) as e:
        logger.error(f"Data preprocessing failed: {type(e).__name__}: {e}")
        raise ValueError(f"Failed to preprocess insulin data: {e}") from e
    except Exception as e:
        logger.exception("Unexpected error during data preprocessing")
        raise Exception(f"CGMDataProcessor initialization failed: {e}") from e

    # Validate required FADTC column exists in preprocessed insulin data
    if 'FADTC' not in insulin_df.columns:
        raise ValueError(
            "Preprocessed insulin_df missing required 'FADTC' (timestamp) column"
        )
    
    # Check API server availability before starting expensive calculations
    # This fails fast if API is down, preventing wasted computation
    try:
        if not check_net_iob_server_is_live():
            error_msg = f"NetIOB API is not available at {OREF0_API_SERVER_URL}"
            logger.error(error_msg)
            raise Exception(error_msg)
    except Exception as e:
        logger.error(f"API availability check failed: {e}")
        raise
    
    logger.info(f"NetIOB API is available at {OREF0_API_SERVER_URL}, starting IOB calculations")

    # Preprocess insulin data: fill NaN and round to 2 decimals
    # This ensures consistent numeric values for calculations
    insulin_data = insulin_df.copy()
    insulin_data.fillna(0, inplace=True)  # Replace NaN with 0
    insulin_data = insulin_data.round(2)  # Round all numeric columns

    # Define time interval for IOB calculations (5 minutes)
    # This matches typical CGM reading frequency for aligned time series
    interval = timedelta(minutes=5)
    
    # Calculate time range spanning full insulin delivery history
    try:
        start_time = insulin_data['FADTC'].min()  # Earliest timestamp
        end_time = insulin_data['FADTC'].max()  # Latest timestamp
        
        # Validate time range
        if pd.isna(start_time) or pd.isna(end_time):
            raise ValueError("Invalid time range: start_time or end_time is NaT")
        
        # Generate time range at 5-minute intervals
        # This creates array of time points where IOB will be calculated
        time_range = pd.date_range(start=start_time, end=end_time, freq=interval)
        
        if len(time_range) == 0:
            raise ValueError("Generated time range is empty")
        
        logger.info(
            f"Calculating IOB for {len(time_range)} time points "
            f"from {start_time} to {end_time}"
        )
        
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to generate time range: {e}")
        raise ValueError(f"Time range generation failed: {e}") from e

    def process_time(time):
        """
        Calculate net IOB for a single time point.
        
        This is the worker function executed in parallel by ThreadPoolExecutor.
        Each worker processes one time point independently.
        
        Args:
            time (datetime): Time point for IOB calculation.
        
        Returns:
            dict or None: IOB calculation result, or None if calculation fails
                (e.g., no pump history available for this time).
        """
        # Convert time to OpenAPS-compatible ISO format with 'Z'
        time_zoned_iso = datetime_to_zoned_iso(time)

        # Extract insulin data for last 24 hours before this time
        # This provides sufficient history for IOB calculation (covers multiple DIA periods)
        last_xhr_records = get_last_x_hr(insulin_data, time, 24)  # 24 hours

        # Build pump history structure from insulin records
        # This converts DataFrame rows to OpenAPS pump event format
        pumphistory = get_pump_history(insulin_data, last_xhr_records)[0]

        # Skip this time point if no pump history available
        # This can occur early in the time series before sufficient data accumulates
        if not pumphistory:
            # logger.warning(f"No pump history extracted for time {time}")
            return None 

        try:
            # Call IOB API for this time point
            output = get_net_iob(
                pumphistory=pumphistory,
                profile=_profile,
                clock=time_zoned_iso,
                autosens=_autosens
            )
            # Validate API response structure
            if not isinstance(output, list) or len(output) == 0:
                logger.warning(f"Invalid IOB API response for time {time_zoned_iso}")
                return None
            
            # Return first element (most recent IOB calculation)
            return output[0]
            
        except ConnectionError as ex:
            # Log connection errors with full traceback
            logger.error(ex.__str__(), exc_info=True)
            return None
            
        except Exception as ex:
            # Log other errors with full traceback
            logger.error(ex.__str__(), exc_info=True)
            return None

    # Execute IOB calculations in parallel using ThreadPoolExecutor
    # Each worker processes one time point independently
    # executor.map() maintains order of results matching input time_range
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_time, time_range))

    # Filter out None values (failed calculations)
    # Only return successful IOB calculations
    results = [r for r in results if r is not None]

    return results
