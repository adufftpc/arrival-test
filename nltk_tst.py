import nltk
from nltk.translate import bleu
from nltk.translate.bleu_score import SmoothingFunction
smoothie = SmoothingFunction().method4


def remove_vowels(text):
   '''text = list(text)
   for i in text[::-1]:
       if i in 'аяуюоеёэиы':
          text.remove(i)
   return str(''.join(text))'''
   return text

def get_similarity(s0, s1):
    similarity = bleu([remove_vowels(s0)], remove_vowels(s1), smoothing_function=smoothie)
    # print(similarity)
    return similarity


