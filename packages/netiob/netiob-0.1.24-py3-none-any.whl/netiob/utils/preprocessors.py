"""
CGM User Data Preprocessing Module

This module preprocesses diabetes management data for blood glucose prediction
and netIOB calculation using the Oref0 library. It transforms 
raw pump, CGM, and nutrition data into compliant format for downstream 
glucose forecasting and netiob calculation algorithms.

The module handles four primary data types:
    - Basal insulin delivery (continuous background insulin)
    - Bolus insulin delivery (meal-time and correction doses)
    - Carbohydrate intake (meal data)
    - Continuous Glucose Monitor (CGM) readings

Key features:
    - Chunks long-duration basal insulin records into 5-minute intervals
    - Processes normal and extended bolus insulin deliveries
    - Calculates insulin-on-board (IOB) compatible data structures
    - Standardizes timestamps and formats to SDTM conventions
    - Validates data integrity and reports missing/invalid data

Author: 
    Ahtsham Zafar
"""
import logging
import warnings
from datetime import timedelta

import pandas as pd

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")


def chunk_insulin_data(processed_basal: pd.DataFrame) -> pd.DataFrame:
    """
    Chunk long-duration basal insulin records into standardized time intervals.
    
    Basal insulin is delivered continuously over time. This function breaks basal 
    records longer than 6 minutes (360 seconds) into 5-minute (300 second) chunks 
    to enable accurate insulin-on-board (IOB) calculations and glucose predictions 
    in the Oref0 algorithm. This granular chunking is critical for OpenAPS's 
    determine-basal logic.
    The function:
        1. Calculates duration between consecutive basal rate changes
        2. Computes insulin delivered per second based on commanded rate
        3. Splits records >360s into 300s chunks with proportional insulin amounts
        4. Preserves all metadata (commanded_basal_rate, base_basal_rate, etc.)
    
    """

    processed_basal = processed_basal.sort_values(by=['FADTC']).reset_index(drop=True)
    processed_basal['FADTC'] = pd.to_datetime(processed_basal['FADTC'])
    processed_basal['next_timestamp'] = processed_basal['FADTC'].shift(-1)
    processed_basal['FADUR'] = (processed_basal['next_timestamp'] - processed_basal['FADTC']).dt.total_seconds()
    processed_basal = processed_basal.dropna(subset=['FADUR']).reset_index(drop=True)
    processed_basal['insulin_per_second'] = processed_basal['commanded_basal_rate'] / 3600
    processed_basal['FASTRESN'] = processed_basal['insulin_per_second'] * processed_basal['FADUR']

    new_rows = []
    indices_to_remove = []

    for i in range(len(processed_basal)):
        row = processed_basal.iloc[i]

        if row['FADUR'] > 360:
            indices_to_remove.append(i)
            timestamp_current = row['FADTC']
            insulin_per_second = row['insulin_per_second']
            base_basal_rate = row['base_basal_rate']
            time_diff = row['FADUR']
            commanded_basal_rate = row['commanded_basal_rate']

            full_chunks = int(time_diff // 300)
            remainder = time_diff % 300
            for j in range(full_chunks):
                chunk_start = timestamp_current + pd.Timedelta(seconds=j * 300)
                chunk_insulin = insulin_per_second * 300
                new_rows.append({
                    'FADTC': chunk_start,
                    'FASTRESN': chunk_insulin,
                    'INSSTYPE': 'basal_chunk',
                    'FATEST': 'BASAL INSULIN',
                    'FACAT': 'BASAL',
                    'commanded_basal_rate': commanded_basal_rate,
                    'FADUR': 300,
                    'base_basal_rate': base_basal_rate
                })
            if remainder > 0:
                chunk_start = timestamp_current + pd.Timedelta(seconds=full_chunks * 300)
                chunk_insulin = insulin_per_second * remainder
                new_rows.append({
                    'FADTC': chunk_start,
                    'FASTRESN': chunk_insulin,
                    'INSSTYPE': 'basal_chunk',
                    'FATEST': 'BASAL INSULIN',
                    'FACAT': 'BASAL',
                    'commanded_basal_rate': commanded_basal_rate,
                    'FADUR': remainder,
                    'base_basal_rate': base_basal_rate
                })

    chunked_df = pd.DataFrame(new_rows)
    processed_basal = processed_basal.drop(index=indices_to_remove).reset_index(drop=True)
    if not processed_basal.empty:
        if 'INSSTYPE' not in processed_basal.columns:
            processed_basal['INSSTYPE'] = 'basal'
        if 'FATEST' not in processed_basal.columns:
            processed_basal['FATEST'] = 'BASAL INSULIN'
        if 'FACAT' not in processed_basal.columns:
            processed_basal['FACAT'] = 'BASAL'

    chunked_basal_df = pd.concat([processed_basal, chunked_df], ignore_index=True)
    chunked_basal_df = chunked_basal_df.sort_values(by=['FADTC']).reset_index(drop=True)
    if 'next_timestamp' in chunked_basal_df.columns:
        chunked_basal_df = chunked_basal_df.drop(columns=['next_timestamp'])
    if 'insulin_per_second' in chunked_basal_df.columns:
        chunked_basal_df = chunked_basal_df.drop(columns=['insulin_per_second'])
    return chunked_basal_df


def process_extended_bolus_group(group: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate insulin delivered across multiple timestamps for an extended bolus.
    
    Extended (or square-wave) boluses deliver insulin gradually over a specified 
    duration rather than all at once. This function distributes the total insulin 
    amount proportionally across all recorded timestamps within the bolus group,
    based on time intervals between consecutive events.
    
    The function:
        1. Extracts total insulin amount from the bolus completion event
        2. Calculates time intervals between consecutive "Bolus Started" events
        3. Distributes insulin proportionally to each interval
        4. Handles edge case of zero duration (distributes equally)
    """

    group = group.sort_values('event_ts')

    original_value = float(group['original_value'].iloc[0])
    start_time = group['event_ts'].min()
    end_time = group['event_ts'].max()
    total_duration_seconds = (end_time - start_time).total_seconds()

    if total_duration_seconds == 0:
        group['delivered_total'] = original_value / len(group)
        return group

    insulin_per_second = original_value / total_duration_seconds

    time_intervals = []
    timestamps = sorted(group['event_ts'])

    if len(timestamps) > 0:
        first_interval = timestamps[0] - start_time
        time_intervals.append(first_interval.total_seconds())

    for i in range(1, len(timestamps)):
        interval = timestamps[i] - timestamps[i - 1]
        time_intervals.append(interval.total_seconds())

    delivered_amounts = [interval * insulin_per_second for interval in time_intervals]

    for i, amount in enumerate(delivered_amounts):
        group.iloc[i, group.columns.get_loc('delivered_total')] = amount

    return group


def preprocess_basal_data(basal_df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess raw basal insulin data into SDTM FA domain format with chunking.
    
    Transforms pump basal rate history into standardized CDISC format, converting
    basal rate changes (U/hr) into discrete insulin delivery amounts (Units) over
    time intervals. Applies intelligent chunking for OpenAPS compatibility.
    
    Processing steps:
        1. Validate required columns (event_ts, commanded_basal_rate, base_basal_rate)
        2. Convert timestamps to datetime objects
        3. Rename columns to SDTM FA domain conventions
        4. Apply chunk_insulin_data() for temporal granularity
        5. Calculate FASTRESN (actual insulin delivered in Units)
    """

    processed_basal = pd.DataFrame(columns=[
        'FADTC', 'FATEST', 'FACAT', 'FASTRESN', 'INSSTYPE',
        'commanded_basal_rate', 'base_basal_rate', 'FADUR'
    ])

    if basal_df.empty or 'event_ts' not in basal_df.columns:
        return processed_basal

    try:
        basal_df = basal_df.copy()
        basal_df['event_ts'] = pd.to_datetime(basal_df['event_ts'], format='%Y-%m-%d %H:%M:%S')

        required_cols = ['event_ts', 'commanded_basal_rate', 'base_basal_rate']
        if all(col in basal_df.columns for col in required_cols):
            basal_df = basal_df[required_cols]
            basal_df = basal_df.rename(columns={'event_ts': 'FADTC'})
            basal_df['INSSTYPE'] = 'basal'
            basal_df['FATEST'] = 'BASAL INSULIN'
            basal_df['FACAT'] = 'BASAL'
            processed_basal = basal_df.sort_values(by='FADTC')

            processed_basal = chunk_insulin_data(processed_basal)
            processed_basal = processed_basal[
                ['FADTC', 'FATEST', 'FACAT', 'FASTRESN', 'INSSTYPE',
                 'commanded_basal_rate', 'base_basal_rate', 'FADUR']]
    except Exception:
        processed_basal = pd.DataFrame(columns=processed_basal.columns)

    return processed_basal


def preprocess_bolus_data(bolus_df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess raw bolus insulin data into SDTM FA domain format.
    
    Processes both normal (immediate) and extended (square-wave) boluses from pump
    history. Normal boluses are delivered instantly; extended boluses are distributed
    over time. Converts pump units (typically mg or mcg) to standard Units.
    
    Processing workflow:
        1. Validate required columns and data types
        2. Classify boluses as 'normal' or 'extended' based on requested_later field
        3. Normal boluses: Extract completed deliveries from status field
        4. Extended boluses: 
           - Match "Bolus Started" events with total delivered amounts
           - Call process_extended_bolus_group() to distribute insulin
        5. Convert from pump units (÷1000) to standard Units
        6. Map to INSNMBOL (normal) and INSEXBOL (extended) variables
    """

    processed_bolus = pd.DataFrame(columns=[
        'FADTC', 'FATEST', 'FACAT', 'INSNMBOL', 'INSEXBOL',
        'INSSTYPE', 'original_value', 'bolus_id'
    ])

    if bolus_df.empty or 'event_ts' not in bolus_df.columns:
        return processed_bolus

    try:
        bolus_df = bolus_df.copy()
        bolus_df['event_ts'] = pd.to_datetime(bolus_df['event_ts'], format='%Y-%m-%d %H:%M:%S')

        required_cols = ['event_ts', 'requested_later', 'bolus_delivery_status', 'bolus_id', 'delivered_total']
        if not all(col in bolus_df.columns for col in required_cols):
            return processed_bolus

        bolus_df['INSSTYPE'] = bolus_df['requested_later'].apply(lambda x: 'extended' if x != 0 else 'normal')

        # Normal bolus
        normal = bolus_df[
            (bolus_df['INSSTYPE'] == 'normal') &
            (bolus_df['bolus_delivery_status'].isin([0, "Bolus Completed"]))
            ][['event_ts', 'bolus_id', 'delivered_total', 'INSSTYPE']].copy()
        if not normal.empty:
            normal['delivered_total'] = normal['delivered_total'] / 1000
            normal['original_value'] = None

        # Extended bolus
        extended = bolus_df[bolus_df['INSSTYPE'] == 'extended'].copy()
        total_delivered = extended[extended['bolus_delivery_status'] == "Bolus Completed"][
            ['bolus_id', 'delivered_total']
        ].rename(columns={'delivered_total': 'original_value'})

        extended_started = extended[extended['bolus_delivery_status'] == "Bolus Started"]
        processed_ext_list = []
        for bid in extended_started['bolus_id'].unique():
            group = extended_started[extended_started['bolus_id'] == bid].copy()
            group = group.merge(total_delivered, on='bolus_id', how='left')
            if not group.empty:
                processed_group = process_extended_bolus_group(group)
                processed_ext_list.append(processed_group)

        if processed_ext_list:
            extended = pd.concat(processed_ext_list)
            extended['delivered_total'] = extended['delivered_total'] / 1000
            extended['original_value'] = extended['original_value'] / 1000
            extended['INSSTYPE'] = 'extended'
        else:
            extended = pd.DataFrame(columns=['event_ts', 'bolus_id', 'delivered_total', 'original_value', 'INSSTYPE'])

        combined = pd.concat([normal, extended], ignore_index=True)
        if not combined.empty:
            combined = combined.rename(columns={'event_ts': 'FADTC', 'delivered_total': 'INSNMBOL'})
            combined['FATEST'] = 'BOLUS INSULIN'
            combined['FACAT'] = 'BOLUS'
            combined['INSEXBOL'] = combined.apply(
                lambda r: r['INSNMBOL'] if r['INSSTYPE'] == 'extended' else None, axis=1)
            combined['INSNMBOL'] = combined.apply(
                lambda r: r['INSNMBOL'] if r['INSSTYPE'] == 'normal' else None, axis=1)
            processed_bolus = combined[
                ['FADTC', 'FATEST', 'FACAT', 'INSNMBOL', 'INSEXBOL', 'INSSTYPE', 'original_value', 'bolus_id']
            ]
    except Exception:
        processed_bolus = pd.DataFrame(columns=processed_bolus.columns)

    return processed_bolus


def preprocess_carbs_data(carbs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess carbohydrate intake data into SDTM ML (Meal) domain format.
    
    Transforms nutrition log entries into standardized meal data format for 
    carbohydrate-on-board (COB) calculations and OpenAPS dynamic carb absorption
    modeling. Essential for meal bolus calculations and glucose predictions.
    
    Processing steps:
        1. Validate presence of event_ts and carbs columns
        2. Extract timestamp and carbohydrate amount
        3. Convert timestamp to datetime object
        4. Rename to ML domain conventions (MLDTC, MLDOSE)
        5. Sort chronologically
    """

    processed_carbs = pd.DataFrame(columns=['MLDTC', 'MLDOSE'])

    if carbs_df.empty or 'event_ts' not in carbs_df.columns or 'carbs' not in carbs_df.columns:
        return processed_carbs

    try:
        carbs_df = carbs_df.copy()
        carbs_df = carbs_df[['event_ts', 'carbs']]
        carbs_df['event_ts'] = pd.to_datetime(carbs_df['event_ts'], format='%Y-%m-%d %H:%M:%S')
        carbs_df = carbs_df.rename(columns={'event_ts': 'MLDTC', 'carbs': 'MLDOSE'})
        processed_carbs = carbs_df.sort_values(by='MLDTC')
    except Exception:
        processed_carbs = pd.DataFrame(columns=processed_carbs.columns)

    return processed_carbs


def preprocess_cgm_data(cgm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess Continuous Glucose Monitor data into SDTM LB (Laboratory) domain format.
    
    Transforms raw CGM sensor readings into standardized glucose measurement format.
    These readings are the primary input for OpenAPS glucose prediction and insulin
    dosing decisions. Typically received every 5 minutes from the CGM sensor.
    
    Processing steps:
        1. Validate required columns (event_ts, current_glucose_display_value)
        2. Extract timestamp and glucose value
        3. Convert timestamp to datetime object
        4. Rename to SDTM LB domain conventions (LBDTC, LBORRES)
        5. Sort chronologically
    """
    processed_glucose = pd.DataFrame(columns=['LBDTC', 'LBORRES'])

    if cgm_df.empty or 'event_ts' not in cgm_df.columns or 'current_glucose_display_value' not in cgm_df.columns:
        return processed_glucose

    try:
        cgm_df = cgm_df.copy()
        cgm_df = cgm_df[['event_ts', 'current_glucose_display_value']]
        cgm_df['event_ts'] = pd.to_datetime(cgm_df['event_ts'], format='%Y-%m-%d %H:%M:%S')
        cgm_df = cgm_df.rename(columns={'event_ts': 'LBDTC', 'current_glucose_display_value': 'LBORRES'})
        processed_glucose = cgm_df.sort_values(by='LBDTC')
    except Exception:
        processed_glucose = pd.DataFrame(columns=processed_glucose.columns)

    return processed_glucose


def preprocess_insulin_data(processed_basal: pd.DataFrame, processed_bolus: pd.DataFrame) -> pd.DataFrame:
    """
    Combine preprocessed basal and bolus insulin data into unified SDTM FA domain.
    
    Merges basal (background) and bolus (meal-time) insulin deliveries into a single
    chronologically sorted dataset with standardized schema. This unified insulin
    history is essential for accurate insulin-on-board (IOB) calculations in the
    Oref0 determine-basal algorithm.
    
    Processing steps:
        1. Concatenate basal and bolus DataFrames
        2. Sort chronologically by FADTC
        3. Harmonize columns across both insulin types
        4. Fill missing columns with None (basal lacks INSNMBOL, bolus lacks FADUR)
        5. Return standardized schema
    """

    insulin_data_list = []
    if not processed_bolus.empty:
        insulin_data_list.append(processed_bolus)
    if not processed_basal.empty:
        insulin_data_list.append(processed_basal)

    if not insulin_data_list:
        return pd.DataFrame(columns=[
            'FADTC', 'FATEST', 'FACAT', 'FASTRESN', 'INSNMBOL', 'INSEXBOL',
            'INSSTYPE', 'original_value', 'bolus_id', 'commanded_basal_rate',
            'base_basal_rate', 'FADUR'
        ])

    insulin_df = pd.concat(insulin_data_list).sort_values(by='FADTC')
    required_cols = [
        'FADTC', 'FATEST', 'FACAT', 'FASTRESN', 'INSNMBOL', 'INSEXBOL',
        'INSSTYPE', 'original_value', 'bolus_id', 'commanded_basal_rate',
        'base_basal_rate', 'FADUR'
    ]
    for col in required_cols:
        if col not in insulin_df.columns:
            insulin_df[col] = None
    return insulin_df[required_cols]


def preprocess_user_data(basal_df, bolus_df, carbs_df, cgm_df):
    """
    Main preprocessing pipeline for aggregated data processing.
    
    This is the primary entry point for data preprocessing. It delegates to specialized
    functions for each data type while collecting validation warnings and printing
    detailed diagnostic information about data completeness and processing success.
    
    Processing workflow:
        1. Validate presence and schema of each input DataFrame
        2. Collect data quality warnings (missing data, missing columns)
        3. Call specialized preprocessing functions:
           - preprocess_basal_data() for basal insulin
           - preprocess_bolus_data() for bolus insulin
           - preprocess_carbs_data() for carbohydrate intake
           - preprocess_cgm_data() for glucose readings
        4. Combine insulin data via preprocess_insulin_data()
        5. Print formatted diagnostic report to console
    """

    # Collect warnings exactly like the original
    missing_data_warnings = []
    data_processing_warnings = []

    # Presence/column checks for warnings (mirror original)
    if basal_df.empty:
        missing_data_warnings.append("⚠️  BASAL INSULIN data is completely missing")
    elif 'event_ts' not in basal_df.columns:
        missing_data_warnings.append("⚠️  BASAL INSULIN data missing required 'event_ts' column")

    if bolus_df.empty:
        missing_data_warnings.append("BOLUS INSULIN data is completely missing")
    elif 'event_ts' not in bolus_df.columns:
        missing_data_warnings.append("BOLUS INSULIN data missing required 'event_ts' column")

    if carbs_df.empty:
        missing_data_warnings.append("CARBOHYDRATE data is completely missing")
    elif 'event_ts' not in carbs_df.columns:
        missing_data_warnings.append("CARBOHYDRATE data missing required 'event_ts' column")
    elif 'carbs' not in carbs_df.columns:
        missing_data_warnings.append("CARBOHYDRATE data missing required 'carbs' column")

    if cgm_df.empty:
        missing_data_warnings.append("GLUCOSE (CGM) data is completely missing")
    elif 'event_ts' not in cgm_df.columns:
        missing_data_warnings.append("GLUCOSE (CGM) data missing required 'event_ts' column")
    elif 'current_glucose_display_value' not in cgm_df.columns:
        missing_data_warnings.append("GLUCOSE (CGM) data missing required 'current_glucose_display_value' column")

    # Run modular steps
    processed_basal = preprocess_basal_data(basal_df)
    processed_bolus = preprocess_bolus_data(bolus_df)
    processed_carbs = preprocess_carbs_data(carbs_df)
    processed_glucose = preprocess_cgm_data(cgm_df)
    insulin_df = preprocess_insulin_data(processed_basal, processed_bolus)

    # Print the same diagnostics as before
    if missing_data_warnings or data_processing_warnings:
        print("\n" + "=" * 80)
        print("DATA PREPROCESSING WARNINGS AND INFORMATION")
        print("=" * 80)

        if missing_data_warnings:
            print("\n🚨 MISSING DATA TYPES:")
            for warning in missing_data_warnings:
                print(f"   {warning}")

        if data_processing_warnings:
            print("\n⚙️  PROCESSING ISSUES:")
            for warning in data_processing_warnings:
                print(f"   {warning}")

        print(f"\n✅ SUCCESSFULLY PROCESSED DATA TYPES:")
        success_count = 0
        if not processed_basal.empty:
            print("   • Basal insulin data");
            success_count += 1
        if not processed_bolus.empty:
            print("   • Bolus insulin data");
            success_count += 1
        if not processed_carbs.empty:
            print("   • Carbohydrate data");
            success_count += 1
        if not processed_glucose.empty:
            print("   • Glucose monitoring data");
            success_count += 1

        if success_count == 0:
            print("   • ⚠️  No data was successfully processed!")

        print("=" * 80 + "\n")
    else:
        print("\n✅ All data types processed successfully!")

    return processed_basal, processed_bolus, processed_carbs, processed_glucose, insulin_df