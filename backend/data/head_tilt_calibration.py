import os
import pandas as pd
import json
import numpy as np

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


class HeadTiltCalibration:
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
    
head_tilt_calibration = HeadTiltCalibration()