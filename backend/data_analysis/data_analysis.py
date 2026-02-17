import numpy as np
import pandas as pd

CAMERA_FPS = 60 # can make this dynamic based on camera being used
# PERCLOS Parameters
PERCLOS_THRESHOLD = 0.5
DROWSINESS_THRESHOLD_PERCENTAGE = 15
MIN_CLOSED_SECONDS = 0.5 
MAX_CLOSED_SECONDS = 15
PERCLOS_WINDOW_SECONDS = 60
FRAMES_IN_WINDOW = PERCLOS_WINDOW_SECONDS * CAMERA_FPS 
# Yawn Parameters
JAW_OPEN_THRESHOLD = 0.6
MIN_YAWN_SECONDS = 1.0
MAX_YAWN_SECONDS = 6.0
# Blink Parameters
BLINK_START_THRESHOLD = 0.6
BLINK_END_THRESHOLD = 0.3

# called by data_logging.py
def data_analysis(df):
    print("Analyzing data.")

    # create column for timestamps measured in seconds
    df['timestamp_s'] = df['timestamp_ms'].astype(float) / 1000.0

    # perform detections
    calculate_perclos(df)
    detect_yawns(df)
    detect_blinks(df)

def calculate_perclos(df):
    avg_squint = (df['eyeSquintLeft'] + df['eyeSquintRight']) / 2
    eye_closed = (avg_squint >= PERCLOS_THRESHOLD).astype(int)

    perclos_transitions = np.diff(eye_closed.astype(int))
    perclos_starts = np.where(perclos_transitions == 1)[0] + 1
    perclos_ends = np.where(perclos_transitions == -1)[0] + 1

    closure_events = []
    closure_count = 0

    for start, end in zip(perclos_starts, perclos_ends):
        duration = df['timestamp_s'].iloc[end] - df['timestamp_s'].iloc[start]
        duration = end - start
        
        # checking if the sequence is valid to be a closure
        if MIN_CLOSED_SECONDS <= duration <= MAX_CLOSED_SECONDS:
            closure_count += 1
            closure_events.append({
                'start_time': start,
                'end_time': end,
                'duration': duration
            })

    print(f"Eye Closures detected: {closure_count}")

def detect_yawns(df):
    yawn_transitions = np.diff((df['jawOpen'] > JAW_OPEN_THRESHOLD).astype(int))
    yawn_starts = np.where(yawn_transitions == 1)[0] + 1
    yawn_ends = np.where(yawn_transitions == -1)[0] + 1

    for start, end in zip(yawn_starts, yawn_ends):
        duration = df['timestamp_s'].iloc[end] - df['timestamp_s'].iloc[start]
        if MIN_YAWN_SECONDS <= duration <= MAX_YAWN_SECONDS:
            print(f"ALERT: Yawn lasting {round(duration, 2)}s was Detected!")

def detect_blinks(df):
    avg_blink = (df['eyeBlinkLeft'] + df['eyeBlinkRight']) / 2
    df_duration = df['timestamp_s'].iloc[-1] - df['timestamp_s'].iloc[0]

    blink_count = 0
    total_blinking_time = 0

    is_blinking = False
    blink_start_time = None
    blink_end_time = None
    prev_blink_val = avg_blink[0]
    for i in range(len(avg_blink)):
        curr_time = df['timestamp_s'].iloc[i]
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

    blink_rate = blink_count / (df_duration / 60)
    print(f"Current Blink Rate: {round(blink_rate, 2)} blinks/min")