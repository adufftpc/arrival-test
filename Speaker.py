import json

class Speaker:
    def __init__(self, dictionary):
        self.dict = dictionary

    def translate(self, lang, lex):
        '''Here to be a translator logic'''
        return lex

    def say(self, request):
        r = json.loads(request)
        lang = r['lang']

        if r['type'] == 'correct?':
            print(f"{self.translate(r['type'])} {self.translate(r['qty'])} {self.translate(r['food'])}?")
        else:
            print(f"{self.translate(lang, r['type'])}")
