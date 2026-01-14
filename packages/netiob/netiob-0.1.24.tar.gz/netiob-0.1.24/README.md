# NetIOB (`netiob`) Calculation and Blood Glucose Prediction Library

netiob is an advanced Python package for **automated blood glucose prediction and insulin-on-board (IOB) calculation** built upon the OpenAPS oref0 reference algorithm. This toolkit enables researchers, data scientists, and developers to preprocess diabetes management data, compute net IOB, forecast glucose, and visually analyze prediction scenarios.

## Core Features

- **Blood Glucose (BG) Prediction**: End-to-end pipeline using the OpenAPS oref0 determine-basal algorithm.
- **Net Insulin On Board (IOB)**: Robust IOB calculation incorporating basal rate variations, boluses, and autosensitivity analysis.
- **Data Preprocessing Utilities**: Transform raw pump, CGM, and nutrition logs into SDTM-compliant, validated formats.
- **Prediction Graphs**: Inbuilt support (via Matplotlib/Plotly) for visualizing BG forecasting results and insulin activity.
- **Core Utilities**: Comprehensive API bridge, datetime handling, profile assembly, autosensitivity computation, and more.

## Requirements

- Python >= 3.7
- Pandas
- NumPy
- Requests
- Plotly and/or Matplotlib
- Django (for server-side configuration/data access)
- OpenAPS oref0 API server (remote endpoint for core calculations)

_See `requirements.txt` or setup.py for exact dependency specifications._

- **Dependencies:**
Requires the ore0 repository, which should be configured correctly in the local environment. This repository is crucial for the script’s execution, specifically for the netIOB calculations which rely on JavaScript computations.

- **Note:**
Ensure all configurations and path settings are correctly set up before execution. The script includes conditional operations that may need modifications based on specific requirements, such as uncommenting certain blocks for full functionality. Get the oref0 repo here: https://github.com/openaps/oref0/tree/master

## Installation

### PyPI
pip install netiob

### From GitLab
```shell
git clone https://gitlab.com/CeADARIreland/UCD/con/netiob.git
cd netiob
pip install .
```

## Import
```python
# Core modules
from netiob.utils.coreutils import *
from netiob.utils.calculators import calculate_net_iob
from netiob.utils.openapsprediction import OpenapsPredictor
from netiob.utils.preprocessors import preprocess_basal_data, preprocess_bolus_data, preprocess_carbs_data, preprocess_cgm_data, preprocess_insulin_data
from netiob.utils.cgmdataprocessor import CGMDataProcessor
from netiob.utils.bgpredgraph import bg_prediction_graph
```
## Functionalities

### 1. Core Utilities (`coreutils.py`)
- **API Communication**: `call_api(endpoint, payload)`
- **Datetime Handling**: `parse_iso_utc`, `to_iso_z`, etc.
- **Profile Construction**: `get_profile_inputs`, `get_profile_settings`
- **Pump History Utilities**: `get_pump_history`, `get_carb_history`
- **Autosensitivity Calculation**: `get_autosens`
- **Data Serialization**: `make_json_serializable()`

### 2. NetIOB Calculator (`calculators.py`)
- Parallel net IOB calculation at 5-min intervals via OpenAPS oref0 API
- Handles both bolus and basal variabilities (including temp basals vs. scheduled)
- Example usage:
```python
from netiob.utils.calculators import calculatenetiob
iob_series = calculate_net_iob(basal_df, bolus_df, cgm_df, profile_df, autosens)
```
- Returns a list of dicts for each time point, including keys: `iob, activity, basaliob, bolusiob, time, lastTemp`

### 3. Preprocessors (`preprocessors.py`)
- Preprocesses CGM, basal, bolus, and meal data into standardized DataFrames
- Chunks long basal records; distributes extended boluses; aligns with OpenAPS SDTM data conventions
- Entry points: `preprocess_basal_data(basal_df)`, `preprocess_bolus_data(bolus_df)`, `preprocess_cgm_data(cgm_df)`, `preprocess_carbs_data(carbs_df)`
- Entry point to process insulin data ready for netiob calculation and prediction: `preprocess_insulin_data(processed_basal, processed_bolus)`
- Entry point to process and access all processed data at once: `preprocess_user_data(basal_df, bolus_df, carbs_df, cgm_df)`. Returns a tuple of 5 (objects) processed data.

### 4. CGM Data Processor (`cgmdataprocessor.py`)
- Orchestrates the transformation of raw user data into oref0-compatible input using the `preprocessor.py`
- Access processed DataFrames and prediction-ready structures:
- Pools and provides netiob and prediction required data as objects
```python
processor = CGMDataProcessor(basal_df, bolus_df, carbs_df, cgm_df, profile_df)
processed_glucose_data = processor.glucose_data  # ready for API call
processed_basal = processor.proc_basal
```

### 5. Blood Glucose Prediction (`openapsprediction.py`)
- **OpenapsPredictor**: Automated pipeline for forecasting BG, carbs-on-board (COB), IOB, insulin needs, and clinical recommendations using oref0 APIs
```python
from netiob.utils.openapsprediction import OpenapsPredictor
predictor = OpenapsPredictor(basal_df, bolus_df, carbs_df, cgm_df, profile_df)
result = predictor.predict_bg(currenttemp, clock, simcarb)
```
- Returns comprehensive prediction dict: `eventualBG`, `predBGs`, `rate`, `reason`, and more

### 6. Graph Plotting (`bgpredgraph.py`)
- **Plot BG prediction scenarios**:
```python
from netiob.utils.bgpredgraph import bg_prediction_graph
fig = bg_prediction_graph(result, scenario_label="BG Prediction", fig_show=True)
```
- Generates interactive or static charts using Plotly/Matplotlib, highlighting:
    - IOB activity
    - COB/UAM scenarios
    - Target BG lines
    - Safest prediction curves

### Example Pipeline Usage
- **Import and Load Dataframes**
```python
import pandas as pd
from netiob.utils.cgmdataprocessor import CGMDataProcessor
from netiob.utils.openapsprediction import OpenapsPredictor
from netiob.utils.bgpredgraph import bg_prediction_graph
from netiob.utils.calculators import calculate_net_iob

# Load user data into DataFrames
# Note: Data can be transformed from any data sources. Only ensure they are in DataFrame format
basal_df = pd.read_csv("basal.csv")
bolus_df = pd.read_csv("bolus.csv")
carbs_df = pd.read_csv("carbs.csv")
cgm_df = pd.read_csv("cgm.csv")
profile_df = pd.read_csv("profile.csv")
```
- **Preprocess**
```python
# Create an instance of CGMDataProcessor.
# See code file for full documentation on all objects of CGMDataProcessor
dataprocessor = CGMDataProcessor(basal_df, bolus_df, carbs_df, cgm_df, profile_df=profile)

# Get the objects of dataprocessor (Below are all the objects of CGMDataProcessor)
dataprocessor.proc_basal        # Processed basal data 
dataprocessor.proc_bolus        # Processed bolus data
dataprocessor.proc_carbs        # Processed carbs data
dataprocessor.proc_glucose      # Processed glucose data
dataprocessor.proc_insulin      # processed insulin data
dataprocessor.glucose_data      # Glucosed data structured in the required dict for OpenAPS prediction
dataprocessor.clock             # CGM last data event timestamp (for prediction)
dataprocessor.pumphistory       # Insulin data structured in the required dict (for netiob calculation and prediction)
dataprocessor.pump_clock        # Last insulin data event timestamp
dataprocessor.settings          # Useer settings in structured dict for prediction
dataprocessor.bg_targets        # BG target dict extracted from settings
dataprocessor.basal_profile     # 24-hours (hourly) baseline user basal profile dict extrapolated from user profile settings
dataprocessor.sensitivities     # Sensitivities data extracted from profile settings
dataprocessor.profile_carbs     # Carbs dict based on user profile
dataprocessor.profile           # Entire user profile structure dict needed for netiob calculation and prediction
datprocessor.autosens           # autosensitivity ratio dict calculated using oref0 API
```
- **Prediction**
```python
predictor = OpenapsPredictor(proc_basal, proc_bolus, proc_carbs, proc_cgm, profile_df)
prediction_result = predictor.predict_bg(currenttemp={}, clock="2025-11-07T16:00:00Z")
    
# Note: Synthetic carbs entry (in grams) can be simulated for prediction. In such case, pass (e.g., 5g) carbs as thus:
prediction_result = predictor.predict_bg(currenttemp={}, clock="2025-11-07T16:00:00Z", sim_carb=5)
```
- **Visualization**
```python
bg_prediction_graph(prediction_result, scenario_label="BG Prediction After Meal")
```
- **Calculate NetIOB**
```python
# Note, profile_df and autosens can be None. 
# In such case, a default baseline basal profile will be calculated based on insulin history and default auto sensitivity ratio will be used.
calculate_net_iob(basal_df, bolus_df, carbs_df, cgm_df, profile_df, austosens={})
```

## Graph Output

- The `bg_prediction_graph` function visualizes predicted curves (IOB, COB/UAM, ZT) and overlays "eventual BG" markers and target ranges.

## Contributing

- Create issues or merge requests on GitLab for improvements.
- Follow coding conventions and update docstrings.

## License

This project is licensed under the Apache License 2.0. For more details, please see the LICENSE file in the repository.

---

### Maintainers
CeADAR Connect Group @ CeADAR - Ireland's Centre for AI

**Contributors:**
- **Abiodun Solanke, Ph.D.** abiodun.solanke@ucd.ie
- **Ahtsham Zafar** ahtsham.zafar@ucd.ie
- **Saad Shahid** saad.shahid@ucd.ie
- **Dana Lewis** dana@openaps.org
- **Dr. Arsalan Shahid** arsalan.shahid@ucd.ie
