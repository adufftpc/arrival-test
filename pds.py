import pandas as pd
import operator
from nltk_tst import get_similarity
from collections import Counter

lex_food = {
    'hamburger': {
        'en': 'хамбургэ',
        'ru': 'гамбургер',
        'ge': 'гамбургери'
    },
    'cheeseburger': {
        'en': 'чизбургэ',
        'ru': 'чизбургер',
        'ge': 'чизбургери'
    },
    'cheeseburger_d': {
        'en': 'дабл чизбургэ',
        'ru': 'двойной чизбургер',
        'ge': 'ормаги чизбургери'
    },
    'whopper': {
        'en': 'вопэ',
        'ru': 'вопер',
        'ge': 'вопери'
    },
    'whopper_d': {
        'en': 'дабл вопэ',
        'ru': 'двойной вопер',
        'ge': 'ормаги вопери'
    },
    'fries': {
        'en': 'фрайc/френч',
        'ru': 'картошка',
        'ge': 'картопили'
    },
}

lex_modifier = {
    'double': {
        'en': 'дабл',
        'ru': 'двойной',
        'ge': 'ормаги'
    }
}

lex_qty = {
    1: {
        'en': 'ван/сингл',
        'ru': 'один/одна',
        'ge': 'эрти'
    },
    2: {
        'en': 'ту/дуал',
        'ru': 'две/два',
        'ge': 'ори'
    },
    3: {
        'en': 'фри/трипл',
        'ru': 'три',
        'ge': 'сами'
    },
    4: {
        'en': 'фо/квад',
        'ru': 'четыре',
        'ge': 'отхи'
    }
}

def calc_weights(input:str, dataset:dict):
    lex_df = pd.DataFrame.from_dict(dataset, orient="index")
    is_non_zero = False

    for col in lex_df.columns:
        for row in lex_df.index:
            options = lex_df[col][row].split('/')
            simils = [get_similarity(x, input) for x in options]
            val = max(simils) if max(simils) > 0.15 else 0

            is_non_zero |= val > 0
            lex_df[col][row] = val

    return lex_df, is_non_zero


def detect_item(dataframe):
    print(dataframe)

    mean = dataframe.mean(axis='columns')
    item = mean.idxmax()
    lang = dataframe.loc[item].to_dict()

    return item, lang


def detect_lex(input):
    mod = None
    food = None
    qty = 1
    inp_cpy = input
    lang_probability = dict({
        'en': 0,
        'ru': 0,
        'ge': 0
    })
    # Check qty
    if len(input) > 1:
        qty_df, non_zero = calc_weights(input[0], lex_qty)
        if (non_zero):
            qty, lang = detect_item(qty_df)
            lang_probability = dict(Counter(lang_probability) + Counter(lang))
            input = input[1:]

    # Check modifier
    if len(input) > 1:
        mod_df, non_zero = calc_weights(input[0], lex_modifier)
        if (non_zero):
            mod, lang = detect_item(mod_df)
            lang_probability = dict(Counter(lang_probability) + Counter(lang))
            input = input[1:]

    # Check food
    for word in input:
        food_df, non_zero = calc_weights(word, lex_food)
        if non_zero:
            food, lang = detect_item(food_df)
            lang_probability = dict(Counter(lang_probability) + Counter(lang))

    if mod is not None:
        if f'{food}_d' in [*lex_food.keys()]:
            food += '_d'
    print(f'{qty} {food}')
    print(lang_probability)

line = 'картобургер'

weights = detect_lex(line.split())
#print(detect_item(weights))
