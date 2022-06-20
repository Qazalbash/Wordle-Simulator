import pandas as pd

from wordle import *

if __name__ == '__main__':

    words_filename = './allowed_words.txt'
    json_filename = './stats.json'
    tree_filename = './game-tree.json'

    w = Wordle(words_filename, json_filename, tree_filename)

    start = pd.Timestamp.now()

    w.play(10**5)

    print(pd.Timestamp.now() - start)

    w.save()
    # w.graph()
