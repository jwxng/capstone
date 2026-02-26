import eel
from backend.settings.initialization import initialization as start
from backend.data import data_logging

eel.init('frontend')

if __name__ == "__main__":
    start()