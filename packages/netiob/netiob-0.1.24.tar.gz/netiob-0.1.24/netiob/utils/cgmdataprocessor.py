"""
CGM Data Processor Pipeline

This module provides the CGMDataProcessor class for processing continuous glucose 
monitoring (CGM) data and preparing it for OpenAPS blood glucose prediction using 
the oref0 library. It handles preprocessing of basal insulin, bolus, carbohydrate, 
and CGM data, and constructs the necessary data structures for oref0 API calls.

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
from netiob.utils.preprocessors import (preprocess_user_data, preprocess_basal_data, preprocess_bolus_data, 
                                        preprocess_carbs_data, preprocess_cgm_data, preprocess_insulin_data)
from netiob.utils.coreutils import (parse_iso_utc, call_api, get_glucose_and_clock, get_pump_history, avg_basal_rate,     
                                    get_profile_inputs, get_profile_settings, get_autosens, get_carb_history)

# Configure module logger
logger = logging.getLogger(__name__)


class CGMDataProcessor:
    """
    Processes CGM and insulin pump data for OpenAPS blood glucose prediction.
    
    This class handles the initialization and preprocessing of user diabetes data 
    including basal and bolus insulin delivery, carbohydrate intake, continuous 
    glucose monitoring readings, and user profile settings. It prepares data 
    structures compatible with the oref0 library for blood glucose forecasting.
    
    Attributes:
        profile_df (pd.DataFrame): User profile settings dataframe
        basal_df (pd.DataFrame): Basal insulin delivery records
        bolus_df (pd.DataFrame): Bolus insulin delivery records
        carbs_df (pd.DataFrame): Carbohydrate intake records
        cgm_df (pd.DataFrame): CGM glucose readings
        proc_basal (pd.DataFrame): Preprocessed basal data
        proc_bolus (pd.DataFrame): Preprocessed bolus data
        proc_carbs (pd.DataFrame): Preprocessed carbohydrate data
        proc_glucose (pd.DataFrame): Preprocessed glucose data
        proc_insulin (pd.DataFrame): Combined preprocessed insulin data
        glucose_data (list): Formatted glucose readings for oref0
        clock (str): ISO timestamp of most recent glucose reading
        pumphistory (list): Formatted pump history for oref0
        pump_clock (str): ISO timestamp for pump synchronization
        profile (dict): Complete user profile for oref0 API
        autosens (dict): Autosensitivity calculation results
    """
    
    def __init__(self, basal_df: pd.DataFrame, bolus_df: pd.DataFrame, carbs_df: pd.DataFrame=None, cgm_df: pd.DataFrame=None, profile_df: pd.DataFrame = None):
        """
        Initialize the CGM data processor with user diabetes data.
        
        Args:
            basal_df (pd.DataFrame): Basal insulin delivery records with columns for timestamps and basal rates (units/hour)
            bolus_df (pd.DataFrame): Bolus insulin delivery records with columns for timestamps and insulin amounts (units)
            carbs_df (pd.DataFrame, optional): Carbohydrate intake records with columns for timestamps and carbohydrate amounts (grams)
            cgm_df (pd.DataFrame, optional): Continuous glucose monitoring readings with columns for timestamps and glucose values (mg/dL or mmol/L)
            profile_df (pd.DataFrame, optional): User profile containing insulin sensitivity factor (ISF), carb ratios, duration of insulin action 
            (DIA), and target glucose ranges. If None, defaults will be computed.
                
        Raises:
            ValueError: If required dataframes are None or empty, or if required columns are missing after preprocessing
            TypeError: If input arguments are not pandas DataFrames
            Exception: If preprocessing or data structure initialization fails
        """
        
        if profile_df is not None and not isinstance(profile_df, pd.DataFrame):
            raise TypeError("profile_df must be a pandas DataFrame or None")
        
        # Validate optional DataFrames - if provided, must be correct type
        optional_dfs = {
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
        self.carbs_df = carbs_df if carbs_df is not None else pd.DataFrame()
        self.cgm_df = cgm_df if cgm_df is not None else pd.DataFrame()
        self.basal_df = basal_df
        self.bolus_df = bolus_df
            
        # Initialize attributes that will be set during processing
        self.proc_basal = pd.DataFrame()
        self.proc_bolus = pd.DataFrame()
        self.proc_carbs = pd.DataFrame()
        self.proc_glucose = pd.DataFrame()
        self.proc_insulin = None
        self.glucose_data = None
        self.clock = None
        self.pumphistory = None
        self.pump_clock = None
        self.settings = None
        self.bg_targets = None
        self.basal_profile = None
        self.sensitivities = None
        self.profile_carbs = None
        self.profile = None
        self.autosens = None
        
        # Preprocess data into standardized dataframes
        # This normalizes column names and formats for oref0 compatibility
        try:
            # Process basal data if provided
            if basal_df is not None and not basal_df.empty:
                self.proc_basal = preprocess_basal_data(basal_df)
                if self.proc_basal is None:
                    raise ValueError("Basal preprocessing returned None")
            else:
                raise ValueError("Basal DataFrame cannot be empty")

            
            # Process bolus data if provided
            if bolus_df is not None and not bolus_df.empty:
                self.proc_bolus = preprocess_bolus_data(bolus_df)
                if self.proc_bolus is None:
                    raise ValueError("Bolus preprocessing returned None")
            else:
                raise ValueError("Bolus DataFrame cannot be empty")
            
            # Process carbs data if provided
            if carbs_df is not None and not carbs_df.empty:
                self.proc_carbs = preprocess_carbs_data(carbs_df)
                if self.proc_carbs is None:
                    logger.warning("Carbs preprocessing returned None, using empty DataFrame")
                    self.proc_carbs = pd.DataFrame()
            
            # Process glucose data (required)
            if cgm_df is not None and not cgm_df.empty:
                self.proc_glucose = preprocess_cgm_data(cgm_df)
                if self.proc_glucose is None or self.proc_glucose.empty:
                    logger.warning("CGM preprocessing failed or returned empty data")
                    self.proc_glucose = pd.DataFrame()        
            
            # Process combined insulin data if available
            if not self.proc_basal.empty or not self.proc_bolus.empty:
                self.proc_insulin = preprocess_insulin_data(self.proc_basal, self.proc_bolus)
                if self.proc_insulin is None:
                    logger.warning("Insulin preprocessing returned None despite valid input")
                    self.proc_insulin = pd.DataFrame()
            else:
                logger.info("No insulin data provided - predictions will be limited")
                self.proc_insulin = pd.DataFrame()
                
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Preprocessing failed - {type(e).__name__}: {e}", exc_info=True)
            raise ValueError(f"Data preprocessing error: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error during data preprocessing")
            raise Exception(f"Failed to preprocess user data: {e}") from e
        
        # Build core prediction structures by calling core utility functions
        try:
            # Extract glucose data and current timestamp from preprocessed glucose readings
            # glucose_data: list of dicts with keys glucose, date, dateString, display_time
            # clock: ISO timestamp string representing the most recent reading time
            self.glucose_data, self.clock = get_glucose_and_clock(self.proc_glucose)
            
            if not self.glucose_data:
                raise ValueError("No glucose data available after processing")
            if not self.clock:
                raise ValueError("Clock timestamp could not be determined from glucose data")
            
            # Extract pump history (basal and bolus events) formatted for oref0 API
            # pumphistory: list of treatment objects with timestamps and insulin amounts
            # pump_clock: ISO timestamp for synchronization
            self.pumphistory, self.pump_clock = get_pump_history(self.proc_insulin)
            
            if not self.pumphistory:
                logger.warning("Pump history is empty - predictions may be less accurate")
            if not self.pump_clock:
                raise ValueError("Pump clock timestamp could not be determined")
            
            # Process profile settings based on whether profile data was provided
            if self.profile_df is not None:
                # Parse user profile data into structured components
                # Returns settings dict, BG target ranges, basal schedule, ISF values, and carb ratios
                self.settings, self.bg_targets, self.basal_profile, self.sensitivities, self.profile_carbs = get_profile_inputs(self.profile_df, self.basal_df)
                
                # Validate profile components
                if not all([self.settings, self.bg_targets, self.basal_profile, self.sensitivities]):
                    raise ValueError("Profile parsing returned incomplete data")
                
                # Combine profile components into single profile object for oref0 API
                # profile includes dia, sens, carb_ratio, carb_ratios, min_bg, max_bg, etc.
                self.profile = get_profile_settings(self.settings, self.bg_targets, self.sensitivities, self.basal_profile, self.profile_carbs)
                
                if not self.profile:
                    raise ValueError("Profile settings generation failed")
                
                # Calculate autosensitivity ratio based on recent BG deviations
                # Autosens adjusts ISF and carb ratio based on observed insulin sensitivity
                # Returns dict with ratio and newisf keys
                self.autosens = get_autosens(self.pumphistory, self.profile, self.basal_profile, self.glucose_data)
                
                if not self.autosens or 'ratio' not in self.autosens:
                    logger.warning("Autosens calculation incomplete, using default values")
                    self.autosens = {'ratio': 1.0, 'newisf': self.profile.get('sens', 50)}
            else:
                # If no profile provided, compute average basal rate from insulin data
                # avg_basal_rate returns tuple (average_rate, profile_dict)
                logger.info("No profile data provided, computing defaults from insulin history")
                avg_basal_profile = avg_basal_rate(self.proc_insulin)
                
                if not avg_basal_profile or len(avg_basal_profile) < 2:
                    raise ValueError("Failed to compute average basal rate")
                
                self.profile = avg_basal_profile[1]
                
                # Set default autosens values when no profile is available
                # ratio of 1.0 means no sensitivity adjustment
                # newisf of 29 is a conservative default insulin sensitivity factor
                self.autosens = {'ratio': 1.0, 'newisf': 50}
                
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Data structure error during setup - {type(e).__name__}: {e}")
            raise ValueError(f"Failed to build prediction structures: {e}") from e
        except ValueError as e:
            logger.error(f"Validation error during setup: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during prediction structure initialization")
            raise Exception(f"Failed to initialize prediction structures: {e}") from e
        
        logger.info("CGMDataProcessor initialized successfully")
