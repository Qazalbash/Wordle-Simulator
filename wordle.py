import json
import random

from matplotlib import pyplot as plt


class Wordle:

    def __init__(self, filename: str) -> None:
        self.all_words = list()
        # self.score = {}
        self.readfile(filename)

    def readfile(self, filename: str) -> None:
        with open(filename, 'r') as file:
            self.all_words = [word[:-1] for word in file]
        with open("stats.json", "r") as file:
            self.score = json.load(file)

    def evalute_guess(self, guess: str, color: str) -> None:
        for i in range(5):
            if color[i] == 'g':
                self.map[i] = set([guess[i]])
                self.allowed.add(guess[i])
            elif color[i] == 'y':
                self.map[i] = self.map.get(i).difference(guess[i])
                self.allowed.add(guess[i])
            elif guess[i] in self.allowed:
                self.map[i] = self.map.get(i).difference(guess[i])
            else:
                for j in range(5):
                    self.map[j] = self.map.get(j).difference(guess[i])

    def coloring(self, word: str, guess: str) -> str:
        color = ['*' for _ in range(5)]
        word = [i for i in word]
        letterPosition = 0
        for i in range(5):
            if guess[i] in word:
                if guess[i] == word[i]:
                    color[i] = 'g'
                    word[i] = "#"
            else:
                color[i] = 'b'

        for i in range(5):
            if color[i] == "*":
                try:
                    letterPosition = word.index(guess[i])
                    color[i] = 'y'
                    word[letterPosition] = '#'
                except:
                    color[i] = 'b'
        return "".join(color)

    def valid_word(self, word: str) -> bool:
        for i in range(5):
            if word[i] not in self.map[i]:
                return False
        for j in self.allowed:
            if j not in word:
                return False
        return True

    def possible_words(self) -> None:
        self.words = [word for word in self.words if self.valid_word(word)]

    def turn(self, num: int) -> bool:
        if num < 7:
            guess = random.choice(self.words)
            color = self.coloring(self._hidden_word, guess)
            if color == "ggggg":
                self.score["win"][str(num)] += 1
                return False
            self.evalute_guess(guess, color)
            self.possible_words()
            return True
        self.score["loss"] += 1
        return False

    def start(self, no_of_games: int = 100) -> None:
        for _ in range(no_of_games):
            i = 1
            self.allowed = set()
            self.words = self.all_words
            self._hidden_word = random.choice(self.all_words)
            self.map = {
                i: set([chr(j) for j in range(97, 123)])
                for i in range(5)
            }
            while self.turn(i):
                i += 1

    def graph(self) -> None:
        y = [self.score["win"][str(i)] for i in range(1, 7)]

        wins = sum(y)
        loss = self.score["loss"]

        fig, ax = plt.subplots(1, 2)

        ax[0].bar(
            ["lost", "win"],
            height=[loss, wins],
            color=['red', 'green'],
        )
        ax[0].set_title(f"Distribution of {wins+loss} games")

        ax[1].bar(range(1, 7), y)
        ax[1].set_title(f"Win distribution")

        plt.show()

    def save(self) -> None:
        with open("stats.json", "w") as outfile:
            json.dump(self.score, outfile)


import pandas as pd
if __name__ == '__main__':
    w = Wordle('./allowed_words.txt')
    start = pd.Timestamp.now()
    w.start(1000)
    print(pd.Timestamp.now() - start)
    w.save()
    w.graph()
