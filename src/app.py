import os
from Loader import Load

DATA_RAW = '\\data\\raw\\'
DATA_CLEAN = '\\data\\clean\\'

DATA_PATH_WRITE = os.path.abspath(os.curdir) + DATA_RAW
DATA_PATH_READ = os.path.abspath(os.curdir) + DATA_CLEAN

if __name__ == "__main__":
    print(DATA_PATH_WRITE)
    print(DATA_PATH_READ)
    Load(DATA_PATH_WRITE + 'serie_a_players.csv');    