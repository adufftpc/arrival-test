from nltk_tst import get_similarity
import operator
from collections import Counter
import pandas as pd
import json
import Speaker


class DialogModule:
    def __init__(self, food_dict, modifier_dict, qty_dict, yesno_dict):
        super().__init__()
        self.speaker = Speaker.Speaker({})
        self.handlers = {}
        self.startState = None
        self.endStates = []

        self.repetitions = 0
        self.empty = None
        self.refinement = None
        self.question = None
        self.input_line = None
        self.order = None
        self.lang = None
        self.food = None
        self.qty = None
        self.yesno = None
        self.lex_food = pd.DataFrame.from_dict(food_dict, orient="index")
        self.lex_mod = pd.DataFrame.from_dict(modifier_dict, orient="index")
        self.lex_qty = pd.DataFrame.from_dict(qty_dict, orient="index")
        self.lex_yesno = pd.DataFrame.from_dict(yesno_dict, orient="index")
        self.reset()
        self.init_state_machine()

    def reset(self):
        self.repetitions = 0
        self.refinement = None
        self.question = None
        self.input_line = None
        self.order = None
        self.food = None
        self.qty = None
        self.yesno = None
        self.lang = dict({
            'en': 0,
            'ru': 0,
            'ge': 0
        })

    def read_input(self, data):
        self.input_line = input().lower().strip()
        if self.input_line:
            return 'parse', data
        else:
            return 'read', data

    def add_state(self, name, handler, end_state=0):
        name = name.upper()
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def set_start(self, name):
        self.startState = name.upper()

    def run(self, cargo):
        try:
            handler = self.handlers[self.startState]
        except:
            raise Exception("must call .set_start() before .run()")
        while True:
            (newState, cargo) = handler(cargo)
            if newState.upper() in self.endStates:
                print("on ", newState)
                break
            else:
                handler = self.handlers[newState.upper()]

    def init_state_machine(self):
        self.add_state('read', self.read_input)
        self.add_state('parse', self.parse)
        self.add_state('process', self.process)
        self.add_state('refine', self.refine)
        self.add_state('serve', self.send_to_server)
        self.add_state('add', self.add_to_order)
        self.set_start('read')
        self.run(self.empty)


    def refine(self, data):
        lang = max(self.lang, key=self.lang.get)
        out = {
            'lang': lang
        }

        if data == 'correct?':
            out['type'] = data
            out['food'] = self.food
            out['qty'] = self.qty
        else:
            out['type'] = data

        out_json = json.dumps(out)

        self.speaker.say(out_json)

        return 'read', data

    def calc_weights(self, word, dataset):
        df = dataset.copy()
        is_non_zero = False
        for col in df.columns:
            for row in df.index:
                options = df[col][row].split('/')
                simils = [get_similarity(x, word) for x in options]
                val = max(simils) if max(simils) > 0.15 else 0

                is_non_zero |= val > 0
                df[col][row] = val

        return is_non_zero, df

    def detect_item(self, word, dataset):
        item = None
        lang = None
        non_zero, dataframe = self.calc_weights(word, dataset)
        probability = 0
        if non_zero:
            mean = dataframe.mean(axis='columns')
            item = mean.idxmax()
            probability = dataframe.loc[item].max()
            lang = dataframe.loc[item].to_dict()
        return item, lang, probability

    def parse(self, data):
        if not self.input_line:
            return None, None

        self.probability = 0
        yesno = None
        food = None
        qty = None
        mod = None
        for word in self.input_line.lower().split():
            if data == 'more?':
                if yesno is None and food is None and qty is None and mod is None:
                    yesno, lang, probability = self.detect_item(word, self.lex_yesno)
                    if lang:
                         self.lang = dict(Counter(self.lang) + Counter(lang))
                         self.yesno = yesno
                         self.probability += probability
                         if self.probability > probability:
                             self.probability /= 2
                         continue
            if qty is None and food is None:
                qty, lang, probability = self.detect_item(word, self.lex_qty)
                if lang:
                     self.lang = dict(Counter(self.lang) + Counter(lang))
                     self.qty = qty
                     self.probability += probability
                     if self.probability > probability:
                         self.probability /= 2
                     continue
            if mod is None and food is None:
                mod, lang, probability = self.detect_item(word, self.lex_mod)
                if lang:
                    self.lang = dict(Counter(self.lang) + Counter(lang))
                    self.mod = mod
                    self.probability += probability
                    if self.probability > probability:
                        self.probability /= 2
                    continue
            if food is None:
                food, lang, probability = self.detect_item(word, self.lex_food)
                if lang:
                    self.lang = dict(Counter(self.lang) + Counter(lang))
                    self.food = food
                    self.probability += probability
                    if self.probability > probability:
                        self.probability /= 2



        if mod is not None:
            if f'{food}_d' in [*self.lex_food.index.tolist()]:
                self.food += '_d'
        if qty is None:
            self.qty = 1
            qty = 1

        if qty and food:
            data = 'new'

        return 'process', data

    def process(self, data):
        # something else?
        if data == 'more?' and self.yesno == 'no':
            return 'serve', 'serve'

        if data == 'correct?':
            if self.yesno == 'yes':
                return 'add', 'serve'

        if data == 'new' and self.food and self.qty:
            if self.probability > 0.2:
                return 'add', 'serve'
            elif self.probability > 0.15:
                self.repetitions += 1
                if self.repetitions < 2:
                    return 'refine', 'again'
                else:
                    self.repetitions = 0
                    return 'refine', 'unknown'
            else:
                self.repetitions = 0
                return 'refine', 'unknown'

        return 'refine', 'unknown'

    def add_to_order(self, data):
        if self.order is None:
            self.order = {}
        if self.food in [*self.order.keys()]:
            self.order[self.food] += int(self.qty)
        else:
            self.order[self.food] = int(self.qty)

        print(self.order)

        return 'refine', 'more?'

    def send_to_server(self, data):
        order = json.dumps(self.order)
        print(order)
        self.reset()

        return 'read', data
