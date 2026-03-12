import backend.constants
import numpy as np
import pandas as pd

from backend.data.data_tracker import data_tracker
from backend.data.data_calibration import data_calibration, HEAD_TILT_FEATURES, cleaned_series
from backend.settings.settings import settings

# Main Function, called by data_logging.py
def data_analysis(df):
    # df is data_tracker.working_data
    print("Analyzing data.")

    if settings.data['blink_rate']:
        # get the baseline from the calibration file
        baseline_blink_rate = data_calibration.get_baseline()

        if baseline_blink_rate != -1:
            # use baseline to compare
            detect_blinks(df, baseline_blink_rate)

    if settings.data["perclos"]:
        calculate_perclos(df)

    if settings.data["yawning"]:
        detect_yawns(df)
    
    if settings.data["head_tilt"]:
        detect_head_tilt(df)

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

    if blink_rate < baseline_blink_rate:
        print("Blink rate detected to be low.")
        data_tracker.try_triggering_alert('tone_blinks/tone_blinks.html')


def calculate_perclos(df):
    df_start_time = df['timestamp_s'].iloc[0]
    df_end_time = df['timestamp_s'].iloc[-1]
    df_duration = df_end_time - df_start_time

    if data_tracker.current_elapsed_time < backend.constants.PERCLOS_WINDOW_SECONDS:
        return

    avg_squint = (df['eyeSquintLeft'] + df['eyeSquintRight']) / 2
    eye_closed = (avg_squint >= backend.constants.PERCLOS_THRESHOLD).astype(int)

    perclos_transitions = np.diff(eye_closed.astype(int))
    perclos_starts = np.where(perclos_transitions == 1)[0] + 1
    perclos_ends = np.where(perclos_transitions == -1)[0] + 1

    closure_events = []
    closure_count = 0

    for start, end in zip(perclos_starts, perclos_ends):
        start_time = df['timestamp_s'].iloc[start]
        end_time = df['timestamp_s'].iloc[end]
        duration = end_time - start_time
        
        # checking if the sequence is valid to be a closure
        if backend.constants.MIN_CLOSED_SECONDS <= duration <= backend.constants.MAX_CLOSED_SECONDS:
            closure_count += 1
            closure_events.append({
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration
            })

    print(f"Eye Closures detected: {closure_count}")

    # calculate PERCLOS percentages
    iterations_per_sample = max(1, int(len(df) / df_duration))
    perclos_values = []
    perclos_timestamps = []

    print("Calculating PERCLOS percentages...")
    for i in range(0, len(avg_squint), iterations_per_sample):
        time_iteration = df['timestamp_s'].iloc[i] - df_start_time
        perclos = calculate_perclos_at_time(time_iteration, closure_events)
        
        perclos_values.append(perclos)
        perclos_timestamps.append(time_iteration)

    # print(f"Calculated {len(perclos_values)} PERCLOS values")
    print(f"Current PERCLOS: {perclos_values[-1]:.2f}%")

    if perclos_values[-1] > backend.constants.DROWSINESS_THRESHOLD_PERCENTAGE:
        print("Drowsiness detected.")
        data_tracker.try_triggering_alert('palming/palming.html')
        
    # print(f"Average PERCLOS: {np.mean(perclos_values):.2f}%")
    # print(f"Minimum PERCLOS: {np.min(perclos_values):.2f}%")
    # print(f"Maximum PERCLOS: {np.max(perclos_values):.2f}%")

    # classifying drowsiness
    # current_perclos = perclos_values[-1]
    # if current_perclos < 15:
    #     status = "ALERT"
    # elif current_perclos < 35:
    #     status = "DROWSY"
    # else:
    #     status = "VERY DROWSY"
    # print(f"Current Status: {status}")

    # # Show sample PERCLOS values
    # print("Sample PERCLOS Values:")
    # print("Time (s) | PERCLOS (%)")
    # print("---------|-----------")
    # for i in range(0, min(len(perclos_timestamps), 10)):
    #     print(f"{perclos_timestamps[i]:8.2f} | {perclos_values[i]:7.2f}%")


def detect_yawns(df):
    yawn_transitions = np.diff((df['jawOpen'] > backend.constants.JAW_OPEN_THRESHOLD).astype(int))
    yawn_starts = np.where(yawn_transitions == 1)[0] + 1
    yawn_ends = np.where(yawn_transitions == -1)[0] + 1
    yawn_count = 0

    for start, end in zip(yawn_starts, yawn_ends):
        duration = df['timestamp_s'].iloc[end] - df['timestamp_s'].iloc[start]
        if backend.constants.MIN_YAWN_SECONDS <= duration <= backend.constants.MAX_YAWN_SECONDS:
            print(f"ALERT: Yawn lasting {round(duration, 2)}s was Detected!")
            yawn_count += 1

    # 5 YAWNS IS ARBITRARY NUMBER, CHANGE LATER BASED ON LITERATURE AND TESTS
    if yawn_count > 5:
        print("More than 5 yawns detected. (FRONTEND NOT READY YET)")


def detect_head_tilt(df):
    baselines = data_calibration.get_head_tilt_baselines()
    if baselines is None:
        print("No head tilt calibration data found.")
        return

    # compute current means for each feature (with outlier removal)
    current_means = {}
    for feat in HEAD_TILT_FEATURES:
        cleaned = cleaned_series(df, feat, k=3.5)
        if len(cleaned) == 0:
            return
        current_means[feat] = float(cleaned.mean())

    # check if ALL features >= forward baseline means
    matches_forward = all(
        current_means[f] >= baselines['forward'][f]
        for f in HEAD_TILT_FEATURES
    )
    # check if ALL features >= back baseline means
    matches_back = all(
        current_means[f] >= baselines['back'][f]
        for f in HEAD_TILT_FEATURES
    )

    if matches_forward or matches_back:
        print("Poor posture detected.")
        data_tracker.try_triggering_alert('head_tilt/head_tilt.html')


# Helper Functions
def calculate_perclos_at_time(time_iteration, closure_events):
    window_start = time_iteration - backend.constants.PERCLOS_WINDOW_SECONDS
    total_closed_time = 0
    
    for event in closure_events:
        event_start = event['start_time']
        event_end = event['end_time']
        
        # if event is fully before window, ignore
        if event_end < window_start:
            continue
        
        # if event is fully after current time, ignore
        if event_start > time_iteration:
            continue
        
        # calculate overlapping time with window
        overlap_start = max(event_start, window_start)
        overlap_end = min(event_end, time_iteration)
        overlap_duration = overlap_end - overlap_start
        
        if overlap_duration > 0:
            total_closed_time += overlap_duration
    
    # calculate actual window size (for when not enough time has passed)
    actual_window = min(time_iteration, backend.constants.PERCLOS_WINDOW_SECONDS)
    
    if actual_window > 0:
        perclos = (total_closed_time / actual_window) * 100
    else:
        perclos = 0
    
    return perclos