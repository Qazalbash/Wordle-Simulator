import json
import random
from functools import reduce
from typing import Optional

import numpy as np
from matplotlib import pyplot as plt


class Wordle:

    def __init__(self: "Wordle", words_filename: str, stats_filename: str,
                 tree_filename: str) -> None:
        """Constructor

        Args:
            self (Wordle): mandatory self object
            words_filename (str): name of file that contains words
            json_filename (str): name of file that contains stats
            tree_filename (str): name of file that contains all games
        """
        self.all_words = list()
        self.readfile(words_filename, stats_filename, tree_filename)
        self.stats_filename = stats_filename
        self.tree_filename = tree_filename

    def readfile(self: "Wordle", words_filename: str, stats_filename: str,
                 tree_filename: str) -> None:
        """read all necessary files

        Args:
            self (Wordle): mandatory self object
            words_filename (str): name of file that contains all words
            stats_filename (str): name of file that contains all stats
            tree_filename (str): name of file that contains all games
        """
        with open(words_filename, 'r') as file:
            self.all_words = [word[:-1] for word in file]
        with open(stats_filename, "r") as file:
            self.stats = json.load(file)
        with open(tree_filename, "r") as file:
            self.tree = json.load(file)

    def evalute_guess(self: "Wordle", guess: str, color: str) -> None:
        """manage the maps in accordance to color

        Args:
            self (Wordle): madatory self object
            guess (str): guessed word
            color (str): color of the word
        """
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

    def coloring(self: "Wordle", word: str, guess: str) -> str:
        """coloring the word in accordance to hidden word

        Args:
            self (Wordle): mandaotry self object
            word (str): hidden word
            guess (str): guessed word

        Returns:
            str: color of the word
        """
        color = ['*' for _ in range(5)]
        word = [i for i in word]

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
                    word[word.index(guess[i])] = '#'
                    color[i] = 'y'
                except:
                    color[i] = 'b'

        return "".join(color)

    def valid_word(self: "Wordle", word: str) -> bool:
        """check the word is appropriate (can win the game) to continue game

        Args:
            self (Wordle): mandatory self object
            word (str): word to be checked

        Returns:
            bool: True if it is appropriate else False
        """
        for i in range(5):
            if word[i] not in self.map[i]:
                return False
        for j in self.allowed:
            if j not in word:
                return False
        return True

    def possible_words(self: "Wordle") -> None:
        """upadte the list that contains all possible words

        Args:
            self (Wordle): mandatory self object
        """
        self.words = [word for word in self.words if self.valid_word(word)]

    def turn(self: "Wordle", num: int, game: Optional[str]) -> bool:
        """one turn of the game

        Args:
            self (Wordle): mandoatory self object
            num (int): turn number
            game (Optional[str]): words played in the game

        Returns:
            bool: True if game will continue to next trun else False
        """
        if num < 7:

            guess = random.choice(self.words)
            color = self.coloring(self._hidden_word, guess)
            game.append(guess)

            if color == "ggggg":
                self.stats["win"][str(num)] += 1
                return False

            self.evalute_guess(guess, color)
            self.possible_words()

            return True

        self.stats["loss"] += 1
        return False

    def start(self: "Wordle", no_of_games: int = 100) -> None:
        """starts the game and play it for multiple times in

        Args:
            self (Wordle): mandatory self object
            no_of_games (int, optional): no of times to play the game. Defaults to 100.
        """
        for _ in range(no_of_games):
            i = 1
            self.allowed = set()
            self.words = self.all_words
            self._hidden_word = random.choice(self.all_words)
            self.map = {
                i: set([chr(j) for j in range(97, 123)])
                for i in range(5)
            }

            game = []

            while self.turn(i, game):
                i += 1
            self.all_games.append(game)

    def play(self: "Wordle", no_of_games: int = 1000) -> None:
        self.all_games = []
        vecstart = np.vectorize(self.start, otypes=None)
        value = np.array([1000 for _ in range(no_of_games // 1000)] +
                         [no_of_games % 1000])
        vecstart(value)

    def graph(self: "Wordle") -> None:
        """generate a simple bar chart of the game stats

        Args:
            self (Wordle): mandatory self object
        """
        y = [self.stats["win"][str(i)] for i in range(1, 7)]

        wins = sum(y)
        loss = self.stats["loss"]

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

    def save(self: "Wordle") -> None:
        """save the stats

        Args:
            self (Wordle): mandatory self object
        """
        with open(self.stats_filename, "w") as outfile:
            json.dump(self.stats, outfile)

        self.game_tree()

        with open(self.tree_filename, "w") as outfile:
            json.dump(self.tree, outfile)

    def game_tree(self: "Wordle") -> None:
        """makes the game tree

        Args:
            self (Wordle): madatory self object
        """
        tree = [self.tree]
        for game in self.all_games:
            node = None
            for ele in game[::-1]:
                if node is None:
                    node = {ele: {}}
                else:
                    node = {ele: node}
            tree.append(node)
        reduce(self.recursive_merge, tree)

    @staticmethod
    def recursive_merge(d1: dict, d2: dict) -> dict:
        """update first dict with second recursively

        Args:
            d1 (dict): first dictionary
            d2 (dict): second dictionary

        Returns:
            dict: merged dictionary
        """
        for k, v in d1.items():
            if k in d2:
                d2[k] = Wordle.recursive_merge(v, d2[k])
        d1.update(d2)
        return d1
