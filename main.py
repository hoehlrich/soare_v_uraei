# !/usr/bin/env
# -*- coding: utf-8 -*-

import string

from json_helpers import *

class WordleLetter():
    '''WordleLetter Class'''

    letters = []
    answers = []

    def __init__(self, letter):
        self.letter = letter
        WordleLetter.letters.append(self)
    
    def calculate_frequencies(self):
        self.frequencies = {
                            'total': 0,
                            0: 0,
                            1: 0,
                            2: 0,
                            3: 0,
                            4: 0
                        }

        for answer in WordleLetter.answers:
            for i in range(5):
                try:
                    index = answer.index(self.letter)
                    self.frequencies[index] += 1
                    self.frequencies['total'] += 1
                except ValueError:
                    break
                
    def __str__(self):
        return f'{self.letter}: {self.frequencies}'

    @classmethod
    def get_letter(self, letter_str):
        for letter in WordleLetter.letters:
            if letter.letter == letter_str:
                return letter

    @classmethod
    def set_answers_list(cls, answers):
        WordleLetter.answers = answers

    @classmethod
    def generate_letter_data(cls, output_path=None):
        if len(cls.letters) == 0:
            wordle_letters = {}

            # Calculate letter frequencies
            for letter in string.ascii_lowercase:
                wordle_letter = cls(letter)
                wordle_letter.calculate_frequencies()
                wordle_letters[letter] = wordle_letter

            cls.sort_letters()

            try:
                write_data(output_path, {letter.letter: letter.frequencies for letter in cls.letters}) # Write to file
            except TypeError:
                pass

    @classmethod
    def load_letter_data(cls, input_path):
        if len(cls.letters) == 0:
            letters = load_asset(input_path)

            for name, frequencies in letters.items():
                letter = WordleLetter(name)
                letter.frequencies = frequencies

    @classmethod
    def sort_letters(cls):
        cls.letters = [(letter, letter.frequencies['total']) for letter in cls.letters] # Change cls.letters to a tupled format in the form of (letter_obj, total_frequency)
        cls.letters.sort(key=lambda x: x[1], reverse=True) # Sort the tuples by the second item (frequency) reversely (greatest to least)
        cls.letters = [letter[0] for letter in cls.letters] # Change cls.letters back to an object format

class WordleWord():
    '''WordleWord Class'''

    words = []

    def __init__(self, word):
        self.word = word
        WordleWord.words.append(self)
    
    def calculate_score(self):
        score = 0
        
        for i, letter in enumerate(self.word):
            letter_obj = WordleLetter.get_letter(letter)
            score += letter_obj.frequencies['total']
            score += letter_obj.frequencies[str(i)]
        
        self.score = score

        return score

def main():
    WordleLetter.set_answers_list(load_asset('Assets/answers.json')['data']) # Set answers list for letters
    
    # WordleLetter.generate_letter_data('Assets/letter_data.json') # Generate letter data

    WordleLetter.load_letter_data('Assets/letter_data.json') # Load letter data

    soare = WordleWord('soare')
    soare.calculate_score()
    print(soare.score)

    uraei = WordleWord('uraei')
    uraei.calculate_score()
    print(uraei.score)

if __name__ == '__main__':
    main()