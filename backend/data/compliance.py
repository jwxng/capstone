import backend.constants
import eel

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

    if is_frozen.mean() >= backend.constants.COMPLIANCE_PERCENTAGE:
        return True
    
    return False


def run_20_20_20_algorithm(df):
    """
    detect if a user is looking away
    if either value > 0.5, then they are looking away
    """
    df_exercise = df[df['timestamp_s'] >= data_tracker.exercise_start_time]

    if df_exercise.empty:
        return False
    
    looking_away = (
        (df_exercise['eyeLookOutLeft'] > backend.constants.LOOKING_AWAY_THRESHOLD) |
        (df_exercise['eyeLookOutRight'] > backend.constants.LOOKING_AWAY_THRESHOLD)
    )

    if looking_away.mean() <= backend.constants.COMPLIANCE_PERCENTAGE:
        return False
    
    return True
