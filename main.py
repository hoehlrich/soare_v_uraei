# !/usr/bin/env
# -*- coding: utf-8 -*-

import json
import string

def load_json(path):
    with open(path, 'r') as read_file:
        return dict(json.load(read_file))

def guess_total_points(guess, answers):
    points = 0

    for answer in answers:
        points += guess_points(guess, answer)
    
    return points

def guess_points(guess, answer):
    points = {
        'gv': 6,
        'gc': 5,
        'yv': 4,
        'yc': 3
    }

    vowels = ('a', 'e', 'i', 'o', 'u')

    score = 0

    # Yellow pass
    yellowed_letters = []
    for i, letter in enumerate(guess):
        if letter in answer and letter not in yellowed_letters:
            if letter != answer[i]: # If its not green
                yellowed_letters.append(letter)
                if letter in vowels:
                    score += points['yv']
                else:
                    score += points['yc']
    
    # Green pass
    for i, letter in enumerate(guess):
        if letter == answer[i]:
            if letter in vowels:
                score += points['gv']
            else:
                score += points['gc']

    return score
                

def main():
    # Load answers
    answers = load_json('Assets/answers.json')['data']
    
    soare_points = guess_total_points('soare', answers)
    uraei_points = guess_total_points('uraei', answers)

    print(soare_points, uraei_points)

if __name__ == '__main__':
    main()