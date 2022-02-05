# !/usr/bin/env
# -*- coding: utf-8 -*-

from json import JSONDecodeError
import string
import time

from pyparsing import Word

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
                            '0': 0,
                            '1': 0,
                            '2': 0,
                            '3': 0,
                            '4': 0
                        }

        for answer in WordleLetter.answers:
            for i in range(5):
                try:
                    index = answer.index(self.letter)
                    self.frequencies[str(index)] += 1
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
    def generate_letter_data(cls, path=None):
        wordle_letters = {}

        # Calculate letter frequencies
        for letter in string.ascii_lowercase:
            wordle_letter = cls(letter)
            wordle_letter.calculate_frequencies()
            wordle_letters[letter] = wordle_letter

        cls.sort_letters()

        try:
            write_data(path, {letter.letter: letter.frequencies for letter in cls.letters}) # Write to file
        except TypeError:
            pass

    @classmethod
    def load_letter_data(cls, path):
        try:
            letters = load_asset(path)

            for name, frequencies in letters.items():
                letter = WordleLetter(name)
                letter.frequencies = frequencies
        except JSONDecodeError:
            cls.generate_letter_data(path)

    @classmethod
    def sort_letters(cls):
        cls.letters = [(letter, letter.frequencies['total']) for letter in cls.letters] # Change cls.letters to a tupled format in the form of (letter_obj, total_frequency)
        cls.letters.sort(key=lambda x: x[1], reverse=True) # Sort the tuples by the second item (frequency) reversely (greatest to least)
        cls.letters = [letter[0] for letter in cls.letters] # Change cls.letters back to an object format

class WordleWord():
    '''WordleWord Class'''

    words = []
    word_list = None

    def __init__(self, word):
        self.word = word
        WordleWord.words.append(self)
    
    def calculate_letter_score(self):
        score = 0
        
        for i, letter in enumerate(self.word):
            letter_obj = WordleLetter.get_letter(letter)
            score += letter_obj.frequencies['total']
            score += letter_obj.frequencies[str(i)]
        
        self.letter_score = score

        return score
    
    def calculate_reduction_score(self, answer_list=None):
        # Set answer list
        if answer_list == None:
            answer_list = WordleWord.answer_list

        score = 0
        answers_len = len(WordleWord.answer_list)
        
        for answer in answer_list:
            color_data = {i: {'letter': letter, 'color': 'b'} for i, letter in enumerate(self.word)}
            letters_changed = {letter: 0 for letter in self.word}

            # Green pass
            for i, letter in enumerate(self.word):
                if letter == answer[i]:
                    color_data[i]['color'] = 'g'
                    letters_changed[letter] += 1
            
            # Yellow pass
            for i, letter in enumerate(self.word):
                if letter != answer[i]:
                    if letter in answer:
                        if letters_changed[letter] < answer.count(letter):
                            color_data[i]['color'] = 'y'
                            letters_changed[letter] += 1
            
            updated_answer_list_size = len(trim_answers(answer_list, color_data))

            score += answers_len - updated_answer_list_size
        
        return score/answers_len       
    
    @classmethod
    def set_word_list(cls, word_list):
        cls.word_list = word_list

    @classmethod
    def set_answer_list(cls, answer_list):
        cls.answer_list = answer_list

    @classmethod
    def generate_word_data(cls, path=None):
        wordle_words = {}
        for word in cls.word_list:
            wordle_word = cls(word)
            wordle_word.calculate_letter_score()
            wordle_words[word] = wordle_word
        
        cls.sort_words()

        try:
            write_data(path, {word.word: {'ls': word.letter_score} for word in cls.words}) # Write to file
        except TypeError:
            pass

    @classmethod
    def load_word_data(cls, path):
        try:
            word_data = load_asset(path)
            for name, data in word_data.items():
                word_obj = WordleWord(name)
                word_obj.letter_score = data['ls']
        except JSONDecodeError:
            cls.generate_word_data(path)
        
    @classmethod
    def sort_words(cls):
        cls.words = [(word, word.letter_score) for word in cls.words] # Change cls.words to a tupled format in the form of (word_obj, letter_score)
        cls.words.sort(key=lambda x: x[1], reverse=True) # Sort the tuples by the second item (letter_score) reversely (greatest to least)
        cls.words = [word[0] for word in cls.words] # Change cls.words back to an object format

def trim_answers(answers, color_data):
    new_answers = list(answers)

    for answer in answers:
        for i, letter_data in color_data.items():
            # Check for blacks
            if letter_data['color'] == 'b' and letter_data['letter'] in answer:
                new_answers.remove(answer)
                break
                
            # Check for greens
            if letter_data['color'] == 'g' and letter_data['letter'] != answer[i]:
                new_answers.remove(answer)
                break
            
            # Check for yellows
            if letter_data['color'] == 'y':
                if letter_data['letter'] in answer:
                    if letter_data['letter'] == answer[i]:
                        new_answers.remove(answer)
                        break
                else:
                    new_answers.remove(answer)
                    break

    return new_answers
    

def main():
    start_time = time.time()

    '''Letters init'''
    WordleLetter.set_answers_list(load_asset('Assets/answers.json')['data']) # Sets letter list to letters

    WordleLetter.load_letter_data('Assets/letter_data.json') # Load letter data
    print(f'Letters len: {len(WordleLetter.letters)}')

    '''Words init'''
    WordleWord.set_word_list(load_asset('Assets/words.json')['data']) # Sets word list to words
    WordleWord.set_answer_list(load_asset('Assets/answers.json')['data']) # Sets word list to words

    WordleWord.load_word_data('Assets/word_data.json') # Load word data
    print(f'Words len: {len(WordleWord.words)}')

    soare = WordleWord('soare')
    uraei = WordleWord('uraei')

    soare_rs = soare.calculate_reduction_score()
    uraei_rs = uraei.calculate_reduction_score()

    print(f'Soare rs: {soare_rs}')
    print(f'Uraei rs: {uraei_rs}')

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
    main()