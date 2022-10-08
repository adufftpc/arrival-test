import json

class Speaker:
    def __init__(self, dictionary):
        self.dict = dictionary
        self.lang = None

    def translate(self, lex):
        '''Here to be a translator logic. Uses self.lang'''
        return lex

    def say(self, request):
        r = json.loads(request)
        self.lang = r['lang']

        if r['type'] == 'correct?':
            print(f"{self.translate(r['type'])} {self.translate(['qty'])} {self.translate(r['food'])}?")
        else:
            print(f"{self.translate(r['type'])}")
