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
    check_compliance()
    clear_active_exercise()

@eel.expose
def clear_active_exercise():
    if data_tracker.active_exercise:
        data_tracker.active_exercise = None
        data_tracker.exercise_start_time = 0

def check_compliance():
    df = data_tracker.working_data
    # only runs when an exercise is active
    if not data_tracker.active_exercise:
        return

    if data_tracker.active_exercise == "palming":
        if run_palming_algorithm(df):
            print("Palming compliance achieved!")
            data_tracker.active_exercise = None # comment this out later
        else:
            print("Palming compliance not achieved, please repeat")
            
    elif data_tracker.active_exercise == "20-20-20":
        if run_20_20_20_algorithm(df):
            print("20-20-20 compliance achieved!")
            data_tracker.active_exercise = None # comment this out later
        else:
            print("20-20-20 compliance not achieved, please repeat")

def run_palming_algorithm(df):
    # TODO: Implement your logic
    return True 

def run_20_20_20_algorithm(df):
    """
    detect if a user is looking away
    if either value > 0.5, then they are looking away
    """
    # break_start = None

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

    # for i in range(len(df)):
    #     current_time = df['timestamp_s'].iloc[i]

    #     if current_time < exercise_start_time:
    #         continue
    

    #     # if the user is complying and is looking away
    #     if looking_away:
    #         if break_start is None:
    #             break_start = current_time

    #         if current_time - break_start >= backend.constants.TWENTY_RULE:
    #             return True

    #     # user is not complying
    #     else:
    #         # restart the process since the user looked back
    #         if break_start is not None:
    #             print("Please look away for 20s")
    #             break_start = None
