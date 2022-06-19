import pandas as pd

from wordle import *

if __name__ == '__main__':

    words_filename = './allowed_words.txt'
    json_filename = './stats.json'

    w = Wordle(words_filename, json_filename)

    start = pd.Timestamp.now()

    w.start(1000)

    print(pd.Timestamp.now() - start)

    w.save()

    w.graph()
