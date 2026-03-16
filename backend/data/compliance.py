import backend.constants
import eel
import numpy as np

from backend.data.data_tracker import data_tracker

@eel.expose
def set_active_exercise(exercise_name):
    print(f"Starting compliance tracking for: {exercise_name}")
    data_tracker.active_exercise = exercise_name
    data_tracker.exercise_start_time = data_tracker.current_elapsed_time

@eel.expose
def finish_exercise(exercise_name):
    print(f"Finishing compliance tracking for: {exercise_name}")
    result = check_compliance()
    clear_active_exercise()
    return result 

@eel.expose
def clear_active_exercise():
    if data_tracker.active_exercise:
        data_tracker.active_exercise = None
        data_tracker.exercise_start_time = 0

def check_compliance():
    df = data_tracker.working_data
    # only runs when an exercise is active
    if not data_tracker.active_exercise:
        return False

    if data_tracker.active_exercise == "palming":
        if run_palming_algorithm(df):
            print("Palming compliance achieved!")
            return True
        else:
            print("Palming compliance not achieved, please repeat")
            return False
    elif data_tracker.active_exercise == "20-20-20":
        if run_20_20_20_algorithm(df):
            print("20-20-20 compliance achieved!")
            return True
        else:
            print("20-20-20 compliance not achieved, please repeat")
            return False

def run_palming_algorithm(df):
    df_exercise = df[df['timestamp_s'] >= data_tracker.exercise_start_time]

    if df_exercise.empty:
        return False
    
    df_features = df_exercise.drop(columns=['timestamp_ms', 'timestamp_s'], errors='ignore')

    row_changes = df_features.diff().abs()

    is_frozen = (row_changes < backend.constants.PALMING_TOLERANCE).all(axis=1).fillna(True)
    print(is_frozen)

    if is_frozen.mean() >= backend.constants.PALMING_COMPLIANCE_THRESHOLD:
        return True
    
    return False


def run_20_20_20_algorithm(df):
    """
    20-20-20 compliance would be based on looking at either end of the screen
    (eyeLookOutLeft, eyeLookOutRight)
    if either value > LOOKING_AWAY_THRESHOLD, the user is considered looking away.
    evaluates the entire df as the 20s game window — pass in only the
    data collected during the game session.
    """
    df_exercise = df[df['timestamp_s'] >= data_tracker.exercise_start_time]
    if len(df_exercise) < backend.constants.TWENTY_MINIMUM_ROWS:
        return False

    times = df_exercise['timestamp_s'].values
    looking_away = (
        (df_exercise['eyeLookOutLeft']  > backend.constants.LOOKING_AWAY_THRESHOLD) |
        (df_exercise['eyeLookOutRight'] > backend.constants.LOOKING_AWAY_THRESHOLD)
    ).astype(int).values

    # trapezoidal integration over the full window
    dt             = np.diff(times)
    mid            = (looking_away[:-1] + looking_away[1:]) / 2
    time_away      = np.sum(dt * mid)
    actual_window  = times[-1] - times[0]

    compliance_pct = (time_away / actual_window) * 100 if actual_window > 0 else 0.0
    is_compliant   = compliance_pct >= backend.constants.TWENTY_COMPLIANCE_THRESHOLD * 100

    return is_compliant
