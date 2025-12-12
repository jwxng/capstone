import eel
from backend.initialization import initialization as start
from backend.data_retrieval import data_retrieval

eel.init('frontend')

if __name__ == "__main__":
    eel.start('index.html', size=(1000, 800))
    start.initialization()