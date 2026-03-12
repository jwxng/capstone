import eel
from backend.data.data_tracker import data_tracker

@eel.expose
def set_active_exercise(exercise_name):
    print(f"Starting compliance tracking for: {exercise_name}")
    data_tracker.active_exercise = exercise_name
    data_tracker.exercise_start_time = data_tracker.current_elapsed_time

@eel.expose
def clear_active_exercise():
    if data_tracker.active_exercise:
        print("Stopping compliance tracking.")
        data_tracker.active_exercise = None

def check_compliance(df):
    # only runs when an exercise is active
    if not data_tracker.active_exercise:
        return

    if data_tracker.active_exercise == "palming":
        if run_palming_algorithm(df):
            print("Palming compliance achieved!")
            data_tracker.active_exercise = None # comment this out later
            
    elif data_tracker.active_exercise == "20-20-20":
        if run_20_20_20_algorithm(df):
            print("20-20-20 compliance achieved!")
            data_tracker.active_exercise = None # comment this out later

def run_palming_algorithm(df):
    # TODO: Implement your logic
    return True 

def run_20_20_20_algorithm(df):
    # TODO: Implement your logic
    return True