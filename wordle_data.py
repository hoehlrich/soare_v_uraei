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
        self.letter_score = None
        self.reduction_score = None
        WordleWord.words.append(self)
    
    def calculate_letter_score(self):
        score = 0
        
        for i, letter in enumerate(self.word):
            letter_obj = WordleLetter.get_letter(letter)
            score += letter_obj.frequencies['total']
            score += letter_obj.frequencies[str(i)]
        
        score = int(score/len(self.word)) # Average letter score

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
        
        score = score/answers_len # Average reduction score

        self.reduction_score = score

        return score
    
    def calculate_answer_score(self):
        '''
        Scores:
        green: 3
        yellow: 2
        grey: 1
        double grey: 0
        '''
        
        score = 0

        for answer in WordleWord.answer_list:
            # Init letters dict
            letters = {}
            for letter in string.ascii_lowercase:
                letters[letter] = 0
            
            # Green pass
            for i, letter in enumerate(self.word):
                if letter == answer[i]:
                    letters[letter] += 1
                    score += 3

            # Yellow pass
            for i, letter in enumerate(self.word):
                if letter != answer[i]:
                    if letters[letter] < answer.count(letter):
                        score += 2
                        letters[letter] += 1
            
            # Grey pass
            for i, letter in enumerate(self.word):
                if letter not in answer:
                    # Check if it is a repeated grey
                    if letters[letter] == 0:
                        score += 1
            
        # Remove score for really bad letters
        bad_letters = ['z', 'q', 'x']
        for bad_letter in bad_letters:
            if bad_letter in self.word:
                score -= 4000

        score = int(score/3) # Reduce and round score

        self.answer_score = score

        return score

    def calculate_weighted_score(self):
        weights = {
            'ls': .30,
            'as': .70
        }

        weighted_score = 0

        weighted_score += self.letter_score * weights['ls'] # Add letter score
        weighted_score += self.answer_score * weights['as'] # Add answer score

        weighted_score = int(weighted_score) # Convert ws to an int

        self.weighted_score = weighted_score

        return weighted_score

    def __str__(self, ls=True, _as=True, ws=True):
        print(f'{self.word.title()}:')
        print(f'  ls: {self.letter_score}')
        print(f'  as: {self.answer_score}')
        print(f'  ws: {self.weighted_score}')

        return ''

    @classmethod
    def set_word_list(cls, word_list):
        cls.word_list = word_list

    @classmethod
    def set_answer_list(cls, answer_list):
        cls.answer_list = answer_list

    @classmethod
    def generate_word_data(cls, path=None):
        wordle_words = {}
        start_time = time.time()
        for i, word in enumerate(cls.word_list):
            seconds_remaing = int(((time.time() - start_time)/(i+.00001)) * (len(cls.word_list)-i))
            print(f'Generating word data: {i}/{len(cls.word_list)} --- Time remaining: {int(seconds_remaing/60)}m {seconds_remaing % 60}s   ', end='\r')
            wordle_word = cls(word)
            wordle_word.calculate_letter_score()
            wordle_word.calculate_answer_score()
            wordle_word.calculate_weighted_score()
            wordle_words[word] = wordle_word
        
        print()
        cls.sort_words()

        try:
            write_data(path, {word.word: {'ls': word.letter_score, 'as': word.answer_score, 'ws': word.weighted_score} for word in cls.words}) # Write to file
        except TypeError:
            pass

    @classmethod
    def load_word_data(cls, path):
        try:
            word_data = load_asset(path)
            for name, data in word_data.items():
                word_obj = WordleWord(name)
                word_obj.letter_score = data['ls']
                word_obj.answer_score = data['as']
                word_obj.weighted_score = data['ws']
        except JSONDecodeError:
            cls.generate_word_data(path)
        
    @classmethod
    def sort_words(cls):
        cls.words = [(word, word.letter_score, word.answer_score, word.weighted_score) for word in cls.words] # Change cls.words to a tupled format in the form of (word_obj, letter_score)
        cls.words.sort(key=lambda x: x[2], reverse=True) # Sort the tuples by the second item (letter_score) reversely (greatest to least)
        cls.words = [word[0] for word in cls.words] # Change cls.words back to an object format

    @classmethod
    def get_word(cls, word):
        for word_obj in cls.words:
            if word_obj.word == word:
                return word_obj
        
        return None
    
class WordleData():
    '''WordleData Class'''

    def __init__(self, debug=False, answer_list=load_asset('Assets/answers.json')['data'], word_list=load_asset('Assets/words.json')['data'], word_data_path='Assets/word_data.json', letter_data_path='Assets/letter_data.json'):
        start_time = time.time()

        '''Letters init'''
        WordleLetter.set_answers_list(answer_list) # Sets letter list to letters

        WordleLetter.load_letter_data(letter_data_path) # Load letter data

        '''Words init'''
        WordleWord.set_word_list(word_list) # Sets word list to words
        WordleWord.set_answer_list(answer_list) # Sets word list to words

        WordleWord.load_word_data(word_data_path) # Load word data
        
        if debug:
            print('--- debug ---')

            print(f'Word data path: {word_data_path}')
            print(f'Letter data path: {letter_data_path}')

            print()

            print(f'Letters len: {len(WordleLetter.letters)}')
            print(f'Words len: {len(WordleWord.words)}')
            print(f'Answers len: {len(WordleWord.answer_list)}')

            print('--- %s seconds ---' % (time.time() - start_time))

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
    WordleData()

if __name__ == '__main__':
    main()