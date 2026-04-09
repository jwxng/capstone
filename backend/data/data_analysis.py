import backend.constants
import numpy as np
import pandas as pd

from backend.data.data_tracker import data_tracker
from backend.data.blink_rate_calibration import blink_rate_calibration
from backend.data.head_tilt_calibration import head_tilt_calibration, HEAD_TILT_FEATURES, cleaned_series
from backend.settings.settings import settings
from scipy.ndimage import gaussian_filter1d

# Main Function, called by data_logging.py
def data_analysis(df):
    # df is data_tracker.working_data
    print("Analyzing data.")

    if settings.data['blink_rate']:
        # get the baseline from the calibration file
        baseline_blink_rate = blink_rate_calibration.get_baseline()

        if baseline_blink_rate != -1:
            # use baseline to compare
            detect_blinks(df, baseline_blink_rate)

    if settings.data["perclos"]:
        calculate_perclos(df)

    # if settings.data["head_tilt"]:
    #     detect_head_tilt(df)

    if settings.data["screen_time"]:
        data_tracker.check_screen_time()

    
# Main Calculation Functions
def detect_blinks(df, baseline_blink_rate):
    df_start_time = df['timestamp_s'].iloc[0]
    df_end_time = df['timestamp_s'].iloc[-1]
    df_duration = df_end_time - df_start_time

    if data_tracker.current_elapsed_time < backend.constants.BLINK_STARTUP_BUFFER_SECONDS:
        return

    avg_blink = (df['eyeBlinkLeft'] + df['eyeBlinkRight']) / 2
    blink_count = 0
    total_blinking_time = 0

    is_blinking = False
    blink_start_time = None
    blink_end_time = None
    prev_blink_val = avg_blink[0]

    for i in range(len(avg_blink)):
        curr_time = df['timestamp_s'].iloc[i]
        curr_blink_val = avg_blink.iloc[i]

        if not is_blinking and prev_blink_val <= backend.constants.BLINK_START_THRESHOLD and curr_blink_val > backend.constants.BLINK_START_THRESHOLD:
            is_blinking = True
            blink_start_time = curr_time
       
        elif is_blinking and prev_blink_val >= backend.constants.BLINK_END_THRESHOLD and curr_blink_val < backend.constants.BLINK_END_THRESHOLD:
            is_blinking = False
            blink_end_time = curr_time
            curr_duration = blink_end_time - blink_start_time
            total_blinking_time += curr_duration
            blink_count += 1

        prev_blink_val = curr_blink_val

    blink_rate = blink_count / (df_duration / 60)
    print(f"Current Blink Rate: {round(blink_rate, 2)} blinks/min")

    if blink_rate < 0.7*baseline_blink_rate:
        print("Blink rate detected to be low.")
        data_tracker.try_triggering_alert('tone_blinks/tone_blinks.html')


def calculate_perclos(df):
    if data_tracker.current_elapsed_time < backend.constants.PERCLOS_WINDOW_SECONDS:
        return

    avg_squint = (df['eyeSquintLeft'] + df['eyeSquintRight']) / 2

    # Soft threshold ramp: 0 at p50 (eyes relaxed/open) → 1 at p95 (eyes near-closed)
    soft_low  = np.percentile(avg_squint, 50)   # starts counting here
    soft_high = np.percentile(avg_squint, 95)   # fully closed here

    # Continuous closure score: 0 = open, 1 = fully closed
    closure_score = np.clip(
        (avg_squint.values - soft_low) / (soft_high - soft_low),
        0, 1
    )

    times = df['timestamp_s'].values
    perclos_values = np.zeros(len(times))

    for i in range(len(times)):
        t_now   = times[i]
        t_start = t_now - backend.constants.PERCLOS_WINDOW_SECONDS

        # All frames inside the rolling window
        mask = (times >= t_start) & (times <= t_now)
        wt = times[mask]
        wc = closure_score[mask]

        if len(wt) < 2:
            perclos_values[i] = backend.constants.FLOOR_PERCENTAGE
            continue

        # Trapezoidal integration: time-weighted closure fraction
        dt  = np.diff(wt)
        mid = (wc[:-1] + wc[1:]) / 2
        closed_time   = np.sum(dt * mid)
        actual_window = wt[-1] - wt[0]

        raw = (closed_time / actual_window) * 100 if actual_window > 0 else 0.0

        # Apply physiological floor
        perclos_values[i] = max(raw, backend.constants.FLOOR_PERCENTAGE)

    # Gaussian smoothing — preserves peaks/valleys, removes frame jitter
    perclos_smooth = gaussian_filter1d(perclos_values, sigma=backend.constants.SMOOTH_SIGMA)
    perclos_smooth = np.maximum(perclos_smooth, backend.constants.FLOOR_PERCENTAGE)

    current_perclos = perclos_smooth[-1]

    if current_perclos < backend.constants.DROWSINESS_THRESHOLD_PERCENTAGE:
        status = "ALERT"
    elif current_perclos < backend.constants.VERY_DROWSINESS_THRESHOLD_PERCENTAGE:
        status = "DROWSY"
    else:
        status = "VERY DROWSY"

    print(f"Current PERCLOS : {current_perclos:.2f}%")
    print(f"Current Status  : {status}")

    if current_perclos > backend.constants.DROWSINESS_THRESHOLD_PERCENTAGE:
        data_tracker.try_triggering_alert('palming/palming.html')


# def detect_head_tilt(df):
#     baselines = head_tilt_calibration.get_head_tilt_baselines()
#     if baselines is None:
#         print("No head tilt calibration data found.")
#         return

#     # compute current means for each feature (with outlier removal)
#     current_means = {}
#     for feat in HEAD_TILT_FEATURES:
#         cleaned = cleaned_series(df, feat, k=3.5)
#         if len(cleaned) == 0:
#             return
#         current_means[feat] = float(cleaned.mean())

#     # check if ALL features >= forward baseline means
#     matches_forward = all(
#         current_means[f] >= baselines['forward'][f]
#         for f in HEAD_TILT_FEATURES
#     )
#     # check if ALL features >= back baseline means
#     matches_back = all(
#         current_means[f] >= baselines['back'][f]
#         for f in HEAD_TILT_FEATURES
#     )

#     if matches_forward or matches_back:
#         print("Poor posture detected.")
#         data_tracker.try_triggering_alert('head_tilt/head_tilt.html')


# Helper Functions
# def calculate_perclos_at_time(time_iteration, closure_events):
#     window_start = time_iteration - backend.constants.PERCLOS_WINDOW_SECONDS
#     total_closed_time = 0
    
#     for event in closure_events:
#         event_start = event['start_time']
#         event_end = event['end_time']
        
#         # if event is fully before window, ignore
#         if event_end < window_start:
#             continue
        
#         # if event is fully after current time, ignore
#         if event_start > time_iteration:
#             continue
        
#         # calculate overlapping time with window
#         overlap_start = max(event_start, window_start)
#         overlap_end = min(event_end, time_iteration)
#         overlap_duration = overlap_end - overlap_start
        
#         if overlap_duration > 0:
#             total_closed_time += overlap_duration
    
#     # calculate actual window size (for when not enough time has passed)
#     actual_window = min(time_iteration, backend.constants.PERCLOS_WINDOW_SECONDS)
    
#     if actual_window > 0:
#         perclos = (total_closed_time / actual_window) * 100
#     else:
#         perclos = 0
    
#     return perclos