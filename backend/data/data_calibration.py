import os
import pandas as pd
import json
import numpy as np

CONFIG_FILE = 'calibration_data.csv'
REQUIRED_CALIBRATION_SECONDS = 300
HEAD_TILT_CALIBRATION_FILE = 'head_tilt_calibration.json'
HEAD_TILT_FEATURES = [
    'eyeLookDownLeft', 'eyeLookDownRight',
    'eyeLookInLeft', 'eyeLookInRight',
    'eyeLookOutLeft', 'eyeLookOutRight',
    'eyeSquintLeft', 'eyeSquintRight'
]
HEAD_TILT_DROP_RATE_THRESHOLD = 0.2

def mad_outlier_mask(series: pd.Series, k: float = 3.5) -> pd.Series:
        s = pd.to_numeric(series, errors="coerce").astype(float)
        m = s.median(skipna=True)
        mad = (s - m).abs().median(skipna=True)

        if pd.isna(mad) or mad == 0:
            return s.notna() & np.isfinite(s)

        robust_z = 0.6745 * (s - m) / mad
        return robust_z.abs() <= k
    
def summarize_clip(df: pd.DataFrame, cols, k: float = 3.5) -> pd.DataFrame:
    """
    Returns a summary table for one calibration clip dataframe.
    cols can be a string (single column) or a list of column names.
    """
    if isinstance(cols, str):
        cols = [cols]

    rows = []
    for c in cols:
        s = pd.to_numeric(df[c], errors="coerce").astype(float)
        keep = mad_outlier_mask(s, k=k)
        cleaned = s[keep].dropna()

        rows.append({
            "feature": c,
            "mean": float(cleaned.mean()) if len(cleaned) else np.nan,
            "std": float(cleaned.std(ddof=1)) if len(cleaned) > 1 else 0.0,
            "median": float(cleaned.median()) if len(cleaned) else np.nan,
            "kept": int(keep.sum()),
            "total": int(len(s)),
            "dropped": int((~keep).sum()),
            "drop_rate": float((~keep).sum() / max(len(s), 1)),
        })

    return pd.DataFrame(rows).set_index("feature")

def cleaned_series(df: pd.DataFrame, col: str, k: float = 3.5) -> pd.Series:
    s = pd.to_numeric(df[col], errors="coerce").astype(float)
    keep = mad_outlier_mask(s, k=k)
    return s[keep].dropna()

class DataCalibration:
    def __init__(self):
        self.data = pd.DataFrame()
        self.baseline_blink_rate = -1
        self.load_data()
        

    def load_data(self):
        print("Checking for existing calibration data...")
        if os.path.exists(CONFIG_FILE):
            try:
                existing_data = pd.read_csv(CONFIG_FILE)
                calibration_duration = existing_data['timestamp_s'].iloc[-1] - existing_data['timestamp_s'].iloc[0]

                if calibration_duration >= REQUIRED_CALIBRATION_SECONDS:
                    self.data = existing_data
                    #find the baseline blink rate
                    self.baseline_blink_rate = self.calc_baseline_blink_rate(existing_data)
                    print("Existing calibration data loaded.")
                    print(f"Blink rate: {self.baseline_blink_rate}")
                else:
                    print("Not enough existing calibration data; restarting calibration process.")

            except Exception as e:
                print(f"Error loading calibration data: {e}")
        else:
            print("No calibration data found.")


    def save_data(self, df: pd.DataFrame):
        current_duration = df['timestamp_s'].iloc[-1] - df['timestamp_s'].iloc[0]
        if current_duration >= REQUIRED_CALIBRATION_SECONDS and self.data.empty:
            print("Saving calibration data...")
            try:
                self.data = df
                self.baseline_blink_rate = self.calc_baseline_blink_rate(df)
                df.to_csv(CONFIG_FILE)
                print("Calibration data saved.")
            except Exception as e:
                print(f"Error saving calibration data: {e}")
    

    #Calibration 
    """
    The calibration function is only going to be done for the blink rate, where we will collect user data for about 5 minutes to establish what
    the users 'ideal' blink rate. The calibration value will then be compared against by the blink-rate being measured in real-time. If the real-time
    measurements detect that the users blink rate has fallen significantly below the established baseline, then the appropriate game will be called
    """
    def calc_baseline_blink_rate(self, df):

        BLINK_START_THRESHOLD = 0.6
        BLINK_END_THRESHOLD = 0.3

        #calibration will take 5 minutes (300s)
        df_start_time = df['timestamp_s'].iloc[0]
        calibration_end_time = df_start_time + REQUIRED_CALIBRATION_SECONDS
    
        avg_blink = (df['eyeBlinkLeft'] + df['eyeBlinkRight']) / 2
        blink_count = 0
        total_blinking_time = 0

        is_blinking = False
        blink_start_time = None
        blink_end_time = None
        prev_blink_val = avg_blink[0]

        for i in range(len(avg_blink)):
            curr_time = df['timestamp_s'].iloc[i]

            # break if timestamp surpasses calibration end time
            if curr_time > calibration_end_time:
                break

            curr_blink_val = avg_blink.iloc[i]

            if not is_blinking and prev_blink_val <= BLINK_START_THRESHOLD and curr_blink_val > BLINK_START_THRESHOLD:
                is_blinking = True
                blink_start_time = curr_time
        
            elif is_blinking and prev_blink_val >= BLINK_END_THRESHOLD and curr_blink_val < BLINK_END_THRESHOLD:
                is_blinking = False
                blink_end_time = curr_time
                curr_duration = blink_end_time - blink_start_time
                total_blinking_time += curr_duration
                blink_count += 1

            prev_blink_val = curr_blink_val

        return (blink_count / (REQUIRED_CALIBRATION_SECONDS / 60))


    def get_baseline(self):
        return self.baseline_blink_rate
    
    def save_head_tilt_calibration(self, neutral_df, forward_df, back_df):
        baselines = {}
        for label, df in [('neutral', neutral_df), ('forward', forward_df), ('back', back_df)]:
            posture_means = {}
            for feat in HEAD_TILT_FEATURES:
                summary = summarize_clip(df, feat, k=3.5)
                drop_rate = summary.loc[feat, 'drop_rate']
                if drop_rate >= HEAD_TILT_DROP_RATE_THRESHOLD:
                    print(f"Calibration failed: {feat} drop rate {drop_rate:.2f} in {label}")
                    return False
                posture_means[feat] = float(summary.loc[feat, 'mean'])
            baselines[label] = posture_means

        with open(HEAD_TILT_CALIBRATION_FILE, 'w') as f:
            json.dump(baselines, f, indent=4)
        self.head_tilt_baselines = baselines
        print("Head tilt calibration saved.")
        return True

    def get_head_tilt_baselines(self):
        if hasattr(self, 'head_tilt_baselines') and self.head_tilt_baselines:
            return self.head_tilt_baselines
        if os.path.exists(HEAD_TILT_CALIBRATION_FILE):
            with open(HEAD_TILT_CALIBRATION_FILE, 'r') as f:
                self.head_tilt_baselines = json.load(f)
                return self.head_tilt_baselines
        return None


data_calibration = DataCalibration()