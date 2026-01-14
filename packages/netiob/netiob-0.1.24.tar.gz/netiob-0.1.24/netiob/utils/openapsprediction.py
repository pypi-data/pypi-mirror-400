"""
OpenAPS Blood Glucose Prediction Pipeline

This module implements the OpenapsPredictor class for blood glucose forecasting
using the oref0 algorithm. It processes insulin, carbohydrate, and CGM data to
generate glucose predictions via the determine_basal API. The predictor orchestrates
the complete pipeline including data preprocessing, IOB calculations, carbohydrate
absorption analysis, and glucose forecasting.

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
from netiob.utils.calculators import calculate_net_iob
from netiob.utils.coreutils import (parse_iso_utc, call_api, get_carb_history)
from netiob.utils.cgmdataprocessor import CGMDataProcessor

# Configure module logger
logger = logging.getLogger(__name__)


class OpenapsPredictor:
    """
    OpenAPS Blood Glucose Predictor using oref0 algorithm.
    
    This class orchestrates the complete prediction pipeline: preprocessing input data,
    calculating net insulin on board (IOB), analyzing carbohydrate absorption via the 
    meal API, and generating glucose predictions via the determine_basal API.
    
    The predictor implements the OpenAPS reference design algorithm (oref0) which determines
    insulin dosing recommendations based on forecasted scenarios using multiple prediction
    types including IOB-only, COB+IOB, and unannounced meal (UAM) predictions.
    
    Attributes:
        profile_df (pd.DataFrame): User profile data containing settings, targets, and sensitivities
        basal_df (pd.DataFrame): Basal insulin delivery records with timestamps and rates
        bolus_df (pd.DataFrame): Bolus insulin delivery records with timestamps and amounts
        carbs_df (pd.DataFrame): Carbohydrate intake records with timestamps and amounts
        cgm_df (pd.DataFrame): CGM glucose readings with timestamps and values
        iobs (list, optional): Pre-calculated IOB data objects; if None, will be calculated
        data_processor (CGMDataProcessor): Instance handling core data preprocessing
        proc_carbs (pd.DataFrame): Preprocessed carbohydrate data with normalized columns
        proc_insulin (pd.DataFrame): Combined preprocessed insulin data (basal and bolus)
        glucose_data (list): Structured glucose readings for oref0 API calls
        clock (str): ISO-formatted timestamp representing current operation time
        pumphistory (list): Structured pump treatment history for oref0 calculations
        pump_clock (str): ISO-formatted timestamp synchronized with pump data
        basal_profile (list): Scheduled basal rates throughout the day
        profile (dict): Complete user profile combining all settings for oref0
        autosens (dict): Autosensitivity calculation results with ratio and adjusted ISF
        iob_data (list): Net insulin on board calculations sorted by time (descending)
        iob_df (pd.DataFrame): IOB data in DataFrame format for manipulation
        
    Raises:
        ValueError: If required data columns are missing, DataFrames are empty, or malformed
        TypeError: If input arguments are not pandas DataFrames
        RuntimeError: If API calls to meal or determine_basal endpoints fail
        
    Example:
        >>> predictor = OpenapsPredictor(
        ...     basal_df=basal_data,
        ...     bolus_df=bolus_data,
        ...     carbs_df=carb_data,
        ...     cgm_df=glucose_data,
        ...     profile_df=user_profile
        ... )
        >>> prediction = predictor.predict_bg(
        ...     currenttemp={'rate': 0.8, 'duration': 25, 'timestamp': '2025-11-03T11:15:00Z'},
        ...     clock='2025-11-03T11:40:00Z'
        ... )
        >>> print(f"Eventual BG: {prediction['eventualBG']}")
    """
    
    def __init__(self, basal_df: pd.DataFrame, bolus_df: pd.DataFrame, carbs_df: pd.DataFrame, cgm_df: pd.DataFrame, profile_df: pd.DataFrame, iobs: list = None):
        """
        Initialize the OpenAPS predictor with user diabetes data.
        
        Args:
            basal_df (pd.DataFrame): Basal insulin delivery records with columns for timestamps and basal rates (units/hour). Must not be empty.
            bolus_df (pd.DataFrame): Bolus insulin delivery records with columns for timestamps and insulin amounts (units). Must not be empty.
            carbs_df (pd.DataFrame): Carbohydrate intake records with columns for timestamps and carbohydrate amounts (grams). Must not be empty.
            cgm_df (pd.DataFrame): Continuous glucose monitoring readings with columns for timestamps and glucose values (mg/dL or mmol/L). Must not be empty.
            profile_df (pd.DataFrame): User profile containing insulin sensitivity factor (ISF), carb ratios, duration of insulin action (DIA), and target glucose 
                ranges. Must not be empty or None.
            iobs (list, optional): Pre-calculated IOB objects as list of dicts with keys time, iob, activity, basaliob, bolusiob. If None, will be calculated from input data. Default is None.
                
        Raises:
            TypeError: If any required DataFrame argument is not a pandas DataFrame, or if iobs is provided but is not a list
            ValueError: If any required DataFrame is None or empty, or if preprocessing or IOB calculation fails
            Exception: If CGMDataProcessor initialization fails or IOB processing encounters  unexpected errors
        """
        # Validate input types
        if not all(isinstance(df, pd.DataFrame) for df in [basal_df, bolus_df, carbs_df, cgm_df, profile_df]):
            raise TypeError( "All input data (basal_df, bolus_df, carbs_df, cgm_df, profile_df) must be pandas DataFrames")
        
        if iobs is not None and not isinstance(iobs, list):
            raise TypeError("iobs must be a list of IOB objects or None")
        
        optional_dfs = {
            'basal_df': basal_df,
            'bolus_df': bolus_df,
            'carbs_df': carbs_df,
            'cgm_df': cgm_df,
            'profile_df': profile_df
        }

        # Validate input types
        for df_name, df in optional_dfs.items():
            if df is not None and not isinstance(df, pd.DataFrame):
                raise TypeError(f"{df_name} must be a pandas DataFrame or None, got {type(df).__name__}")
        
        # Store raw input dataframes
        self.profile_df = profile_df
        self.iobs = iobs
        self.basal_df = basal_df if basal_df is not None else pd.DataFrame()
        self.bolus_df = bolus_df if bolus_df is not None else pd.DataFrame()
        self.carbs_df = carbs_df if carbs_df is not None else pd.DataFrame()
        self.cgm_df = cgm_df
            
        # Initialize attributes that will be set during processing
        self.data_processor = None
        self.proc_carbs = None
        self.proc_insulin = None
        self.glucose_data = None
        self.clock = None
        self.pumphistory = None
        self.pump_clock = None
        self.basal_profile = None
        self.profile = None
        self.autosens = None
        self.iob_data = None
        self.iob_df = None
        
        # Build core prediction structures by instantiating CGMDataProcessor
        try:
            # Create an instance of the CGMDataProcessor class to get all core prediction objects
            # This handles preprocessing and extraction of glucose data, pump history, profile, and autosens
            self.data_processor = CGMDataProcessor(basal_df=self.basal_df, bolus_df=self.bolus_df, carbs_df=self.carbs_df, cgm_df=self.cgm_df, profile_df=self.profile_df)
            
            # Validate that data_processor was created successfully
            if self.data_processor is None:
                raise ValueError("CGMDataProcessor initialization returned None")
            
            # Extract processed data from the data processor instance
            self.proc_carbs = self.data_processor.proc_carbs
            self.proc_insulin = self.data_processor.proc_insulin
            self.glucose_data = self.data_processor.glucose_data
            self.clock = self.data_processor.clock
            self.pumphistory = self.data_processor.pumphistory
            self.pump_clock = self.data_processor.pump_clock
            
            # Use computed basal profile if no user profile provided, otherwise use extracted profile
            self.basal_profile = (self.data_processor.profile if self.profile_df is None else self.data_processor.basal_profile)
            self.profile = self.data_processor.profile
            self.autosens = self.data_processor.autosens
            
            # Validate critical extracted data
            if not self.glucose_data:
                raise ValueError("No glucose data available from data processor")
            if not self.profile:
                raise ValueError("Profile data missing from data processor")
            if not self.autosens:
                raise ValueError("Autosens data missing from data processor")
            
        except (ValueError, TypeError) as e:
            logger.error(f"Data processor initialization failed: {type(e).__name__}: {e}")
            raise ValueError(f"Failed to initialize CGMDataProcessor: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error during data processor initialization")
            raise Exception(f"CGMDataProcessor initialization failed: {e}") from e
        
        # Calculate or use provided net insulin on board (IOB)
        try:
            # Net IOB includes both bolus insulin and impact of temp basals vs. scheduled basals
            # This is more accurate than pump-native IOB which only considers boluses
            # NOTE: calculate_net_iob can still be calculated without passing profile and autosens objects.
            # In that case, a self-defined baseline basal profile and autosensitivity ratio would be used.
            if self.iobs is None:
                logger.info("Calculating net IOB from insulin and carb data")
                iob_data = calculate_net_iob(basal_df=self.basal_df, bolus_df=self.bolus_df, cgm_df=self.cgm_df, profile=self.profile_df, autosens=self.autosens)
                
                # Validate IOB calculation result
                if not iob_data:
                    raise ValueError("IOB calculation returned empty result")
            else:
                logger.info("Using pre-calculated IOB data")
                iob_data = self.iobs
                
                # Validate provided IOB data structure
                if not all(isinstance(iob, dict) and 'time' in iob for iob in iob_data):
                    raise ValueError("Invalid IOB data structure: each IOB must be a dict with 'time' key")
            
            # Sort the IOB objects by timestamp, most recent first (descending order)
            # Each IOB object contains: time, iob, activity, basaliob, bolusiob, etc.
            try:
                self.iob_data = sorted(iob_data, key=lambda x: parse_iso_utc(x['time']), reverse=True)
            except (KeyError, TypeError, ValueError) as sort_error:
                logger.error(f"Failed to sort IOB data: {sort_error}")
                raise ValueError(f"IOB data sorting failed - invalid time format: {sort_error}") from sort_error
            
            # Convert IOB objects to DataFrame for easier manipulation
            # sep="-" flattens nested dicts with hyphenated column names (e.g., 'iob-data')
            try:
                iob_df = pd.json_normalize(self.iob_data, sep="-")
                
                if iob_df.empty:
                    raise ValueError("IOB DataFrame is empty after normalization")
                
            except (ValueError, TypeError) as norm_error:
                logger.error(f"Failed to normalize IOB data to DataFrame: {norm_error}")
                raise ValueError(f"IOB DataFrame creation failed: {norm_error}") from norm_error
            
            # Create working copy of IOB dataframe
            self.iob_df = iob_df.copy()
            
            # Validate that time column exists in IOB data
            if 'time' not in self.iob_df.columns:
                raise ValueError("IOB DataFrame missing required 'time' column")
            
            # Convert time column to datetime objects if in string format
            # Ensures proper sorting and time-based operations
            try:
                self.iob_df['time'] = pd.to_datetime(self.iob_df['time'])
            except (ValueError, TypeError) as dt_error:
                logger.error(f"Failed to convert IOB time column to datetime: {dt_error}")
                raise ValueError(f"IOB time conversion failed: {dt_error}") from dt_error
            
            # Sort by time with most recent entries first (descending order)
            # This order matches oref0 expectations for API calls
            self.iob_df = self.iob_df.sort_values(by='time', ascending=False)
            
            logger.info(f"Successfully processed {len(self.iob_data)} IOB entries")
            
        except ValueError as e:
            logger.error(f"IOB processing validation error: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during IOB data processing")
            raise Exception(f"IOB processing failed: {e}") from e
        
        logger.info("OpenapsPredictor initialized successfully")

    def predict_bg(self, currenttemp: dict, clock: str, sim_carb: int = None) -> dict:
        """
        Generate blood glucose predictions using the oref0 determine_basal algorithm.
        
        This method orchestrates the two-stage prediction process:
        1. Calls the meal API to analyze carbohydrate absorption and calculate carbs on board (COB)
        2. Calls the determine_basal API to forecast glucose and recommend insulin adjustments
        
        The determine_basal logic forecasts glucose using different prediction scenarios
        (IOB-only, COB+IOB, UAM for unannounced meals) and selects appropriate insulin
        adjustments based on the safest prediction curve.
        
        Args:
            currenttemp (dict): Current temporary basal rate information. Should contain:
                - rate (float): Current temp basal rate in U/hr
                - duration (int): Remaining duration in minutes
                - timestamp (str): ISO timestamp when temp basal was set
                Pass empty dict {} if no temp basal is currently active.
            clock (str): ISO-formatted timestamp for prediction time point. Must be valid
                ISO 8601 format (e.g., "2025-11-03T11:40:00Z"). This represents the "now"
                time for the prediction.
            sim_carb (int, optional): Simulated carbohydrate entry for "what-if" scenario
                analysis. Should contain:
                - carbs (float): Grams of carbohydrates
                - absorptionTime (int): Expected absorption time in minutes
                - created_at (str): ISO timestamp when carbs were/will be consumed
                Default None uses only actual carb history from input data.
                
        Returns:
            dict: Prediction result from determine_basal API containing:
                - bg (int): Current blood glucose value in mg/dL
                - tick (str): Blood glucose trend direction indicator
                - eventualBG (int): Predicted eventual BG without intervention
                - insulinReq (float): Recommended insulin adjustment amount
                - reason (str): Human-readable explanation of the recommendation
                - predBGs (dict): Multiple prediction curves including IOB, COB, UAM, ZT
                - IOB (float): Current insulin on board in units
                - COB (float): Current carbs on board from meal_data analysis
                - rate (float): Recommended temporary basal rate in U/hr
                - duration (int): Recommended temporary basal duration in minutes
                Additional fields may be present depending on the scenario.
                
        Raises:
            TypeError: If currenttemp is not a dict or clock is not a string
            ValueError: If clock string is not valid ISO format, or if carb history
                extraction fails
            RuntimeError: If meal API or determine_basal API calls fail or return None
            
        Example:
            >>> result = predictor.predict_bg(
            ...     currenttemp={'rate': 0.8, 'duration': 25, 'timestamp': '2025-11-03T11:15:00Z'},
            ...     clock='2025-11-03T11:40:00Z'
            ... )
            >>> print(f"Eventual BG: {result['eventualBG']} mg/dL")
            >>> print(f"Recommendation: {result['reason']}")
        """
        # Validate input types
        if not isinstance(currenttemp, dict):
            raise TypeError("currenttemp must be a dictionary")
        if not isinstance(clock, str):
            raise TypeError("clock must be an ISO-formatted string")
        if sim_carb is not None and not isinstance(sim_carb, int):
            raise TypeError("sim_carb must be a dictionary or None")
        
        # Validate clock format
        try:
            parse_iso_utc(clock)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid clock format - must be ISO 8601: {e}") from e
        
        # Extract carbohydrate history and prepare for meal analysis
        # If sim_carb is provided, it simulates a future carb entry for scenario planning
        # carb_clock may differ from main clock to align with carb entry timing
        try:
            carb_clock, carb_history = get_carb_history(self.proc_carbs, self.iob_df, clock=clock, sim_carb=sim_carb)
            
            # Validate carb history extraction results
            if not carb_clock:
                raise ValueError("Carb clock extraction failed - returned empty value")
            if carb_history is None:
                logger.warning("No carb history available - predictions will be IOB-based only")
                carb_history = []
                
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to extract carb history: {type(e).__name__}: {e}")
            raise ValueError(f"Carb history extraction failed: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error during carb history extraction")
            raise Exception(f"Failed to get carb history: {e}") from e
        
        # Call meal API to analyze carbohydrate absorption
        # This calculates carbs on board (COB), absorption rate, and carb decay curves
        # Meal analysis is critical for predicting post-meal glucose rise and determining
        # how much insulin has already been delivered vs. how much is still needed
        try:
            meal_inputs = {
                "history": self.pumphistory,  # Insulin treatment history for carb impact calculation
                "profile": self.profile,  # User profile with carb ratios, ISF, and DIA
                "basalprofile": self.basal_profile,  # Scheduled basal rates for baseline calculation
                "clock": carb_clock,  # Use carb-aligned timestamp for meal timing accuracy
                "carbs": carb_history,  # Carb entries with timestamps, amounts, and absorption times
                "glucose": self.glucose_data  # Recent BG readings to estimate actual carb absorption
            }
            
            logger.debug(f"Calling meal API with {len(carb_history)} carb entries")
            meal_result = call_api("/meal", meal_inputs)
            
            # Validate meal API response before proceeding to determine_basal
            if meal_result is None:
                raise RuntimeError("Meal API returned None - carb analysis failed")
            
            # Log COB if available for debugging
            if isinstance(meal_result, dict) and 'mealCOB' in meal_result:
                logger.info(f"Meal API calculated COB: {meal_result.get('mealCOB', 0)}g")
                
        except RuntimeError as e:
            logger.error(f"Meal API call failed: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during meal API call")
            raise RuntimeError(f"Meal API failed: {e}") from e
        
        # Call determine_basal API to generate glucose prediction and insulin recommendation
        # This is the core oref0 algorithm that forecasts blood glucose and determines dosing
        # It creates multiple prediction curves (IOB-only, COB+IOB, UAM) and selects the
        # safest approach to keep BG in target range while avoiding hypoglycemia
        try:
            final_inputs = {
                "glucose_status": self.glucose_data[0],  # Most recent glucose reading with delta and trend
                "currenttemp": currenttemp,  # Active temporary basal (rate, duration) or empty dict
                "iob_data": self.iob_data,  # Net IOB including temp basals (not just boluses)
                "profile": self.profile,  # Complete user profile with all parameters
                "autosens_data": self.autosens,  # Autosensitivity ratio to adjust insulin needs
                "meal_data": meal_result,  # COB and carb absorption analysis from meal API
                "microBolusAllowed": False,  # Whether to enable super micro boluses (SMB feature)
                "reservoir_data": None,  # Insulin reservoir level (optional safety check)
                "currentTime": clock,  # Timestamp for this prediction cycle
                "debug": True  # Include detailed reasoning in response for transparency
            }
            
            logger.debug(f"Calling determine_basal API at {clock}")
            prediction_result = call_api("/determine_basal", final_inputs)
            
            # Validate determine_basal API response
            if prediction_result is None:
                raise RuntimeError("determine_basal API returned None - prediction failed")
            
            # Log key prediction results
            if isinstance(prediction_result, dict):
                eventual_bg = prediction_result.get('eventualBG', 'N/A')
                reason = prediction_result.get('reason', 'No reason provided')
                logger.info(f"Prediction: eventual BG = {eventual_bg}, reason = {reason}")
            
            # Return the complete prediction with recommended actions and detailed reasoning
            return prediction_result
            
        except RuntimeError as e:
            logger.error(f"determine_basal API call failed: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during determine_basal API call")
            raise RuntimeError(f"determine_basal API failed: {e}") from e
